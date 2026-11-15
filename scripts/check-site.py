#!/usr/bin/env python3
"""Check the static site's paths and HTML contracts without dependencies."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.refs = []
        self.images = []
        self.projects = []
        self.triggers = []
        self.headings = []
        self.handlers = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        for name in ('href', 'src', 'poster'):
            if attrs.get(name):
                self.refs.append(attrs[name])
        for source in attrs.get('srcset', '').split(','):
            if source.strip():
                self.refs.append(source.strip().split()[0])
        if tag == 'img' and attrs.get('src'):
            self.images.append(attrs)
        if attrs.get('data-project'):
            self.projects.append(attrs['data-project'])
        if attrs.get('data-open-gallery'):
            self.triggers.append(attrs['data-open-gallery'])
        if re.fullmatch(r'h[1-6]', tag):
            self.headings.append(tag)
        self.handlers.extend(key for key in attrs if key.startswith('on'))


def main():
    page = SiteParser()
    page.feed((ROOT / 'index.html').read_text())
    script = (ROOT / 'script.js').read_text()
    # Capture assets in both standalone strings and srcset strings.
    page.refs.extend(re.findall(r'assets/[A-Za-z0-9_./-]+', script))
    problems = []
    checked = set()
    for ref in page.refs:
        parts = urlsplit(ref)
        if parts.scheme or parts.netloc:
            continue
        if not parts.path:
            if parts.fragment and parts.fragment not in page.ids:
                problems.append('Missing section: ' + ref)
            continue
        path = unquote(parts.path)
        if path.startswith('/'):
            problems.append('Root-relative path breaks project hosting: ' + ref)
            continue
        checked.add(path)
        current = ROOT
        for part in Path(path).parts:
            if not current.is_dir() or part not in {p.name for p in current.iterdir()}:
                problems.append('Missing file or incorrect capitalization: ' + path)
                break
            current /= part
        else:
            if not current.is_file():
                problems.append('File required: ' + path)
    problems.extend('Duplicate ID: ' + key for key, count in Counter(page.ids).items() if count > 1)
    if page.headings.count('h1') != 1:
        problems.append('Expected exactly one h1')
    if page.handlers:
        problems.append('Inline event handlers duplicate behavior: ' + ', '.join(page.handlers))
    for img in page.images:
        if not img.get('alt') or not img.get('width') or not img.get('height'):
            problems.append('Image needs alt text and dimensions: ' + img['src'])
    for key in page.triggers:
        if key not in page.projects or not re.search(r'"' + re.escape(key) + r'"\s*:', script):
            problems.append('Gallery trigger has no matching content/media: ' + key)
    if problems:
        print('\n'.join(sorted(set(problems))))
        return 1
    print(f'PASS: {len(checked)} local files, section anchors, image dimensions, unique IDs, and {len(page.projects)} galleries.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
