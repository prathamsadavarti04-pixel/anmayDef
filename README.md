# Anmay Defence — website and asset library

Multi-page website for Anmay Defence and a visually-described asset library for the
STRIKE counter-UAS platform family.

```
index.html            Home
strike.html           STRIKE Gen 1 · Gen 2 concept · STRIKE-M · C-UAS rover
technology.html       Detection → tracking → prioritisation → response
use-cases.html        Deployment contexts and configurations
gallery.html          All 134 photographs, filterable, with lightbox
about.html            Robonut Project and the build approach
contact.html          Briefing request

assets/               original media (renamed, described)
assets/web/           1200 px web derivatives used by the pages
assets/css, assets/js shared design system and behaviour
docs/                 asset manifest, naming convention, site notes
tools/                regenerate derivatives, video contact sheets
```

Documentation:

* [`docs/ASSET-LIBRARY.md`](docs/ASSET-LIBRARY.md) — naming convention and how to search the library
* [`docs/ASSET-MANIFEST.csv`](docs/ASSET-MANIFEST.csv) — every file: original path, new path, category, date, description
* [`docs/WEBSITE.md`](docs/WEBSITE.md) — pages, design notes, how to add a photograph, deployment

## Serve locally

```bash
python3 -m http.server 8080
# http://localhost:8080
```

## Git LFS

Video, presentation and archive files are stored in Git LFS (`.gitattributes`). Clone with
Git LFS installed, or those files arrive as small pointer files:

```bash
git lfs install
git clone <repo>
```
