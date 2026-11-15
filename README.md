# Min Thway Khant — Computer Engineering Portfolio

A responsive, buildless portfolio for networking, infrastructure, software, and automation opportunities. Uses HTML, CSS, and vanilla JavaScript; compatible with GitHub Pages.

## Run locally

Open `index.html`, use VS Code Live Server, or run:

```sh
python3 -m http.server 4173 --bind 127.0.0.1
```

Then visit http://127.0.0.1:4173. HTTPS or localhost supports the copy-email enhancement; a selectable email address and normal email link are always available.

## Features

- Balanced engineering introduction and early competition/certification highlights
- Four existing projects, multi-category filters, and native expandable case studies
- All eight existing galleries: 42 images and three videos, with captions and original-file links
- Native modal dialog, focus wrapping/return, Escape and arrow navigation
- Responsive mobile navigation and keyboard focus indicators
- Light/dark themes, system preference, and optional local preference storage
- Reduced-motion support, one-time reveals, and active-section navigation
- Copy email, résumé viewing/download, and existing certificate links
- Responsive JPEG derivatives and a still poster instead of a video download on the project card

## Content maintenance

- **index.html:** the canonical titles, descriptions, roles, case studies, skills, and credentials. Gallery text is read from the corresponding `data-project` article.
- **styles.css:** shared color tokens, components, responsive layouts, and reduced-motion rules. Dark mode changes the tokens.
- **script.js:** gallery media/captions, navigation, filtering, theme, and other progressive enhancements. It has no runtime dependencies or fetch-based content loading.
- **assets/:** all original media and documents remain intact. Display derivatives live in `assets/optimized/`; direct original links remain available.

To add a project, add its article with a unique `data-project` key and space-separated `data-categories`, then add the matching media entries in `galleryMedia`. Reuse the existing card classes and case-study structure. Add filter categories only when supported by the actual work.

The networking filter is labelled **Networking education** because the existing project demonstrates educational software. OSPF automation and MATLAB digit recognition are not published as projects until their scope, supporting material, personal contribution, and status have been reviewed.

HCIP-Datacom is listed from the supplied upgrade brief without an invented issue date or certificate link. The existing HCIA and cloud certificate links are retained. The supplied résumé PDF is unchanged and still uses its original software/AI internship wording; update it separately when revised résumé content is ready.

Canonical and social-sharing metadata use the confirmed public address: https://minthwaykhant711.github.io/min-thway-khant-portfolio/. The social preview is `assets/social-preview.jpg`. Update those absolute metadata URLs if the deployment address changes; regular site assets remain relative.

## Images

The site serves pre-generated JPEG variants at up to 640, 1280, and 1920 pixels wide, selected using `srcset`. Originals are retained for viewing/download. The manifest records original sizes and generated variants; it is maintenance data, not loaded by the website.

An optional macOS regeneration utility is included:

```sh
python3 scripts/optimize-media.py
```

It uses native `sips`, and existing Ghostscript (`gs`) to handle two source photographs that the native decoder renders incorrectly. Swift provides extra image checks and optional poster extraction. These are maintenance tools only: visitors and GitHub Pages need none of them. Check generated images visually and update HTML/media paths when adding new sources. Preserve the existing video poster if native video decoding is unavailable.

## Checks

```sh
python3 scripts/check-site.py
node --check script.js
```

The static checker verifies relative file paths and capitalization, anchors, unique IDs, image dimensions, and gallery/content matches.

Before publishing, check:

- Filters, native case studies, all image/video galleries, counters, and original-file links
- Keyboard opening, Tab/Shift+Tab wrapping, Escape, focus return, and native video controls
- Mobile menu opening/closing, section navigation, and resize behavior
- Light/dark themes, reduced motion, unavailable storage, and clipboard denial
- Phone/tablet/desktop layouts, JavaScript-disabled navigation/content, and the repository URL subdirectory
- The résumé, certificates, external profiles, and public metadata

## Publishing

The repository root is the static site; no install, build, server, API key, authentication, database, or paid service is needed. Keep asset links relative so GitHub Pages project URLs work. Review and push through your existing GitHub Pages workflow when ready; local edits do not publish themselves.
