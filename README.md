# Anmay Defence — website and asset library

This repository holds two things:

1. **The website** — a static, multi-page site at the repository root (`index.html`,
   `strike.html`, `technology.html`, `work.html`, `about.html`, `contact.html`),
   written to be served by GitHub Pages with no build step.
2. **The asset library** — every photograph, video, presentation and script Anmay
   Defence has produced, renamed to describe what it actually shows, plus a
   catalogue you can search.

---

## 1. The site

| Page | What it is for |
|---|---|
| `index.html` | Positioning, the threat, the workflow, the platform family, use cases, CTA |
| `strike.html` | STRIKE Gen1 (with the spec table), mission packages, STRIKE Gen2 concept, STRIKE M, deployment options |
| `technology.html` | How detection and tracking work, the engineering of the actuation and drives, command & control, roadmap |
| `work.html` | The build archive: a filterable image library (64 frames), video inventory, document inventory |
| `about.html` | The company story, the build timeline taken from the archive's own dates, brand marks |
| `contact.html` | Briefing request form (front-end stub), what to include, direct channels |
| `legacy/index-single-page-v1.html` | The original one-page site, kept untouched for reference |

Shared pieces:

```
site/site.css        design system (same type, accent colour and hover language as v1)
site/site.js          mobile nav, reveal-on-scroll, gallery filter, lightbox, form stub
assets/web/                1600 px web derivatives of the curated images (+ 700 px thumbs)
assets/web/curated.json    the curated set: which original maps to which web file
tools/curate.py            the curated list itself (edit this, not the HTML)
tools/build_site.py        writes the six pages from the page bodies in that file
tools/make_web_images.py   regenerates assets/web from the curated list
```

### Rebuilding

```bash
pip install pillow                     # one dependency, only for image derivatives
python3 tools/make_web_images.py       # only needed when the curated list changes
python3 tools/build_site.py            # regenerate the six HTML pages
python3 -m http.server 8000            # preview at http://localhost:8000
```

Copy lives in `tools/build_site.py`; page structure is generated so the header,
footer and nav stay consistent. **Do not hand-edit the HTML** — edit the builder
and re-run it, or the next build will overwrite your changes.

### Before going live

- [ ] Replace the contact placeholders (`<span class="todo">…</span>`) in `contact.html`
      via the builder with a real email, phone and WhatsApp link.
- [ ] Point the briefing form at a real endpoint (Formspree, Netlify Forms, your own).
- [ ] Replace the work-in-progress emblem and Robonut exports in `assets/web/` with
      final logo files.
- [ ] Confirm the specification figures with the engineering team — they are taken
      from the programme documents in the archive and marked as indicative.

---

## 2. The asset library

Descriptions live in `tools/asset_descriptions.py`, keyed by current path. Run
`python3 tools/build_catalog.py` to refresh the outputs, or `--check` to prove every
file in `assets/` is described:

| File | Contents |
|---|---|
| `docs/assets-index.md` | One line per file: new name, short description, tags, review state |
| `docs/assets-catalog.csv` | Full catalogue: path, kind, LFS oid/size, md5, role, quality, page, tags, alt text, long description, duplicate flag |
| `docs/assets-catalog.json` | The same, for scripting |
| `docs/shortlist.md` | The 64 frames chosen for the site, grouped by subject, with the page each one serves |

### Naming convention

Every filename now answers "what is in this file?" rather than "what did the camera
call it". The pattern is:

```
<subject>-<what it shows>-<distinguishing detail>-<view-or-setting>-<qualifier>.<ext>
```

Examples:

```
strike-vehicle-on-barracks-road-dusk-overhead-drone-two-people-talking.jpg
ak-trigger-servo-linkage-with-ruler-and-green-sling-closeup.jpg
cad-strike-gen1-turret-exploded-assembly-labelled-diagram.jpg
strike-gen2-concept-tubular-frame-eo-ir-gimbal-desert-outpost-render.jpg
drone-tracker-app-screen-recording-grid-hud-live-acquisition-1080p.webm
```

Rules applied throughout:

- lowercase ASCII, hyphen-separated, extension preserved, no spaces;
- subject first (`strike-...`, `ak-...`, `robonut-...`, `drone-tracker-...`);
- view and setting stated when they matter (`overhead-drone`, `low-angle`,
  `closeup`, `cutout-black-bg`, `portrait`);
- dates kept where the folder was date-organised (`2026-09-18`);
- near-duplicates and true duplicates are labelled (`-02`, `duplicate`, `burst-03`)
  and cross-referenced in the `duplicate_of` column;
- **files whose pixels could not be opened carry `pending-review` in the name**
  (see below) — never a guessed description.

Folders were normalised to kebab-case at the same time
(`assets/strike-gen1-shots/`, `assets/drone-detection-videos-photos/shortlisted-photo-video/`, …).

### Review state: reviewed vs pending

| State | Meaning |
|---|---|
| `visually-reviewed` (139 files) | The pixels were opened, described, and the file was renamed from that description — subject, foreground, background, view, setting, colours and any legible text. |
| `pending-visual-review` (92 files) | The file is a **Git LFS pointer** — only 130 bytes of text in this checkout. The name is derived from folder, timestamp and neighbouring reviewed stills, and ends in `pending-review`. |

### Git LFS

Video, PPTX and ZIP files are stored with Git LFS (see `.gitattributes`). A plain
clone gives you pointer files:

```
version https://git-lfs.github.com/spec/v1
oid sha256:84dd6cc1b7fd7f2be35d50c3239f51cd5b7b70dea159a1b5728a246594435f32
size 141011432
```

To materialise the real bytes:

```bash
git lfs install
git lfs pull                 # or: git lfs fetch --all && git lfs checkout
git lfs ls-files             # list what is tracked
du -sh .git/lfs              # how much is on disk
```

Total LFS payload is **≈2.05 GB across 92 files**, including one 439 MB DJI flight
and a 141 MB trial-footage compilation. If bandwidth matters, pull selectively:

```bash
git lfs pull --include="assets/videos/strike-m-videos/**"
```

**After pulling, the video descriptions still need a human pass.** The 87 MP4s were
never opened here, so their names are structured but provisional. Each one is listed
in `docs/assets-index.md` with its LFS oid; watch the clip, then rename — the pattern
to follow is already established by the images, e.g.

```
strike-gen1-trial-clip-2026-09-18-seq012-pending-review.mp4
        ↓
strike-turret-360-rotation-rifles-traversing-trial-ground-overcast.mp4
```

and flip its `status` to `visually-reviewed` in the catalogue.

### Known duplicates (safe to retire)

| Duplicate | Of | Evidence |
|---|---|---|
| `assets/drone-detection-videos-photos/shortlisted-photo-video/cad-...-duplicate.jpg` | `assets/drone-detection-videos-photos/cad-...-diagram.jpg` | identical MD5 |
| `assets/strike-gen1-shots/strike-gen1-rifle-mounting-automation-clip-2026-07-05-pending-review.mp4` | `assets/videos/truck-rifle-mounting-automation-clip-41mb-pending-review.mp4` | identical LFS oid |
| `assets/videos/photos/drone-tracker-app-screen-recording-duplicate-webm.webm` | `assets/videos/drone-tracker-app-screen-recording-grid-hud-live-acquisition-1080p.webm` | identical MD5 |

Near-duplicates (bursts and same-scene frames) are flagged with `near-duplicate`
in the `tags` column — useful when picking a single hero frame.

### Shortlisting images for the website

Filter the catalogue instead of browsing folders:

- `role` — `hero`, `product`, `detail`, `engineering`, `ui`, `poster`, `doc`, `brand`, `video`, `support`, `reference`
- `quality` — `hero`, `good`, `reference`, `pending`
- `page` — the page on this site the asset was shortlisted for (`strike`, `technology`, `engineering`, `gallery`, `about`)
- `tags` — subject and view keywords, plus `pending-review` when unreviewed

Handy one-liners:

```bash
# every hero-quality image currently shortlisted for the STRIKE page
python3 - <<'EOF'
import json
for r in json.load(open('docs/assets-catalog.json')):
    if r['quality']=='hero' and r['page']=='strike':
        print(r['path'])
EOF

# everything that mentions a console, controller or operator
grep -i "console\|controller\|operator" docs/assets-index.md

# video sorted by size, biggest first
python3 - <<'EOF'
import json
v=[r for r in json.load(open('docs/assets-catalog.json')) if r['extension']=='mp4']
for r in sorted(v,key=lambda x:-int(x['lfs_size_bytes'] or 0))[:15]:
    print(round(int(r['lfs_size_bytes'])/1048576,1),'MB',r['filename'])
EOF
```

---

## 3. Housekeeping

- `.nojekyll` is present so GitHub Pages serves files verbatim.
- `assets/web/` is a build product: regenerate it, do not edit it.
- Originals are never modified — only renamed (with `git mv`, so history follows).
