#!/usr/bin/env python3
"""Regenerate portfolio JPEG derivatives on macOS; never modifies originals.

Optional maintenance utility using Python's standard library and macOS `sips`.
An existing Ghostscript installation handles rotated JPEGs that Apple's decoder
cannot resize correctly; Swift/AVFoundation optionally produces a video poster.
These tools are not build steps or website runtime dependencies. Run from the
repository with `python3 scripts/optimize-media.py`.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets" / "optimized"
WIDTHS = (640, 1280, 1920)


def run(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def dimensions(path: Path) -> tuple[int, int]:
    result = run("sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path))
    return tuple(int(re.search(rf"{key}: (\d+)", result).group(1))
                 for key in ("pixelWidth", "pixelHeight"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def orientation(path: Path) -> int:
    """Read a JPEG EXIF orientation tag without third-party dependencies."""
    data = path.read_bytes()
    marker = data.find(b"Exif\x00\x00")
    if marker < 0:
        return 1
    try:
        tiff = marker + 6
        order = "<" if data[tiff:tiff + 2] == b"II" else ">"
        directory = tiff + struct.unpack_from(order + "I", data, tiff + 4)[0]
        count = struct.unpack_from(order + "H", data, directory)[0]
        for index in range(count):
            entry = directory + 2 + index * 12
            if struct.unpack_from(order + "H", data, entry)[0] == 274:
                return struct.unpack_from(order + "H", data, entry + 8)[0]
    except (struct.error, IndexError):
        pass
    return 1


def software_jpeg_variant(source: Path, target: Path, width: int, quality: str,
                          rotation: int, source_width: int, source_height: int) -> None:
    """Decode a JPEG in software and bake its EXIF orientation into pixels."""
    gs = shutil.which("gs")
    if not gs:
        raise SystemExit(f"Image {source.name} needs existing Ghostscript (gs); originals are untouched.")
    w, h = source_width, source_height
    matrices = {1: (w, 0, 0, -h, 0, h), 2: (-w, 0, 0, -h, w, h),
                3: (-w, 0, 0, h, w, 0), 4: (w, 0, 0, h, 0, 0),
                5: (0, h, -w, 0, w, 0), 6: (0, -h, -w, 0, w, h),
                7: (0, -h, w, 0, 0, h), 8: (0, h, w, 0, 0, 0)}
    display_width, display_height = (h, w) if rotation >= 5 else (w, h)
    height = round(width * display_height / display_width)
    escaped = str(source).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    matrix = " ".join(str(value) for value in matrices[rotation])
    postscript = (f"{width} {height} scale /input ({escaped}) (r) file /DCTDecode filter def "
                  f"{w} {h} 8 [{matrix}] input false 3 colorimage showpage")
    run(gs, "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", "-dDOINTERPOLATE", "-sDEVICE=jpeg",
        f"-dJPEGQ={quality}", "-r72", f"-g{width}x{height}", f"-sOutputFile={target}",
        f"--permit-file-read={source}", "-c", postscript)


def repair_flat_derivatives(manifest: dict) -> None:
    """Catch native decoder failures that can silently produce black JPEGs."""
    if not shutil.which("swift"):
        print("Swift unavailable; manually inspect the generated images for decoding problems.")
        return
    swift = r'''
import Foundation
import ImageIO
for path in CommandLine.arguments.dropFirst() {
    if let source = CGImageSourceCreateWithURL(URL(fileURLWithPath: path) as CFURL, nil),
       let image = CGImageSourceCreateThumbnailAtIndex(source, 0,
           [kCGImageSourceCreateThumbnailFromImageAlways: true,
            kCGImageSourceThumbnailMaxPixelSize: 16] as CFDictionary),
       let data = image.dataProvider?.data {
        if Set(data as Data).count <= 3 { print(path) }
    } else { print(path) }
}
'''
    paths = [str(ROOT / variant["src"]) for info in manifest.values() for variant in info["variants"]]
    suspects = set(run("swift", "-module-cache-path",
                       str(Path(tempfile.gettempdir()) / "portfolio-media-swift-cache"),
                       "-e", swift, *paths).splitlines())
    for original, info in manifest.items():
        source = ROOT / original
        if source.suffix.lower() not in (".jpg", ".jpeg"):
            continue
        for variant in info["variants"]:
            target = ROOT / variant["src"]
            if str(target) not in suspects:
                continue
            w, h = dimensions(source)
            software_jpeg_variant(source, target, variant["width"], "78", orientation(source), w, h)
            variant["width"], variant["height"] = dimensions(target)
            variant["bytes"] = target.stat().st_size
            print("Repaired native JPEG decoding:", variant["src"])


def make_poster() -> bool:
    """Export a transformed frame one second into the existing demonstration."""
    if not shutil.which("swift"):
        return False
    video = ROOT / "assets/projects/hugmae/scan-patient-medgo.mp4"
    target = DEST / "projects/hugmae/preview.jpg"
    target.parent.mkdir(parents=True, exist_ok=True)
    swift = r'''
import Foundation
import AVFoundation
import ImageIO
import UniformTypeIdentifiers

let asset = AVURLAsset(url: URL(fileURLWithPath: CommandLine.arguments[1]))
let generator = AVAssetImageGenerator(asset: asset)
generator.appliesPreferredTrackTransform = true
generator.maximumSize = CGSize(width: 1280, height: 1280)
do {
let frame = try generator.copyCGImage(at: CMTime(seconds: 1, preferredTimescale: 600), actualTime: nil)
let destination = CGImageDestinationCreateWithURL(
    URL(fileURLWithPath: CommandLine.arguments[2]) as CFURL,
    UTType.jpeg.identifier as CFString, 1, nil)!
CGImageDestinationAddImage(destination, frame, [kCGImageDestinationLossyCompressionQuality: 0.84] as CFDictionary)
guard CGImageDestinationFinalize(destination) else { fatalError("Could not save poster") }
} catch {
    FileHandle.standardError.write(Data("Video poster unavailable: \(error.localizedDescription)\n".utf8))
    exit(1)
}
'''
    cache = Path(tempfile.gettempdir()) / "portfolio-media-swift-cache"
    try:
        run("swift", "-module-cache-path", str(cache), "-e", swift,
            str(video), str(target))
    except subprocess.CalledProcessError as error:
        print("Poster generation unavailable:", error.stderr.strip().splitlines()[-1])
        return False
    return target.is_file()


def main() -> None:
    if not shutil.which("sips"):
        raise SystemExit("This optional utility requires macOS and its built-in sips tool.")
    sources = sorted(path for folder in ("projects", "experience")
                     for path in (ROOT / "assets" / folder).rglob("*")
                     if path.suffix.lower() in (".jpg", ".jpeg", ".png"))
    before = {path: digest(path) for path in sources}
    manifest = {}
    for source in sources:
        quality = "84" if source.suffix.lower() == ".png" else "78"
        folder = DEST / source.relative_to(ROOT / "assets").parent
        folder.mkdir(parents=True, exist_ok=True)
        variants = []
        source_width, source_height = dimensions(source)
        rotation = orientation(source)
        display_width = source_height if rotation >= 5 else source_width
        for width in sorted({min(width, display_width) for width in WIDTHS}):
            target = folder / f"{source.stem}-{width}.jpg"
            if rotation != 1:
                software_jpeg_variant(source, target, width, quality, rotation, source_width, source_height)
            else:
                run("sips", "-s", "format", "jpeg", "-s", "formatOptions", quality,
                    "--resampleWidth", str(width), str(source), "--out", str(target))
            actual_width, actual_height = dimensions(target)
            variants.append({"src": target.relative_to(ROOT).as_posix(),
                             "width": actual_width, "height": actual_height,
                             "bytes": target.stat().st_size})
        manifest[source.relative_to(ROOT).as_posix()] = {
            "originalBytes": source.stat().st_size, "variants": variants}
    repair_flat_derivatives(manifest)
    assert all(digest(path) == checksum for path, checksum in before.items()), "An original changed"
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    poster = make_poster()
    originals = sum(item["originalBytes"] for item in manifest.values())
    derivatives = sum(variant["bytes"] for item in manifest.values() for variant in item["variants"])
    gallery = sum(item["variants"][-1]["bytes"] for item in manifest.values())
    print(f"{len(sources)} original images preserved; {sum(len(item['variants']) for item in manifest.values())} JPEG derivatives")
    print(f"Original image bytes: {originals}; all derivative bytes: {derivatives}; largest-variant bytes: {gallery}")
    print(f"Largest-variant reduction: {100 * (1 - gallery / originals):.1f}%; poster: {poster}")


if __name__ == "__main__":
    main()
