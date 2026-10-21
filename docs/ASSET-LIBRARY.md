# Anmay Defence — asset library

Every file under `assets/` has been renamed so the filename itself describes what is in
the file. The full before/after record is in [`ASSET-MANIFEST.csv`](ASSET-MANIFEST.csv).

## Naming convention

```
<category>__<subject>__<context or detail>__<YYYY-MM-DD>.<ext>
```

* `__` (double underscore) separates the four groups. Everything inside a group uses
  hyphens, so the name stays one long, searchable token.
* The **category** is the first word and is the fastest way to filter:

  | category | what it covers |
  | --- | --- |
  | `strike-gen1` | STRIKE Gen 1 turret hardware, product cut-outs, field shots |
  | `strike-m` | truck / vehicle-mounted STRIKE-M, aerial views of the deployment |
  | `strike-gen2` | Gen 2 concept work |
  | `rover` | tracked C-UAS rover concept |
  | `hardware` | build close-ups: trigger actuators, servos, gears, driver boards, consoles, wiring |
  | `crew` | people operating or posing with the system |
  | `field-trial` | trial scenes where the system is incidental |
  | `doc` | posters, specification sheets, scripts and process notes |
  | `brand` | logos and emblems |
  | `ui` | software screens and screen recordings |

* **Subject** names the main object, in reading order foreground → background where it matters.
* **Context** carries the setting, the camera angle, the people, and the background elements.
* **Date** is the capture date recovered from the original filename or EXIF, in ISO order so
  that a plain alphabetical sort is also a chronological sort within a category.

Examples:

```
strike-m__camo-truck-with-5-rifle-turret__rear-view-yard-road-two-crew__2025-10-02.jpg
strike-gen1__upward-view-of-camo-rifle-barrels__sun-cloud-silhouette__2025-10-02.jpg
hardware__trigger-guard-servo-linkage__pushrod-ruler-top-view.jpg
```

## Searching

```bash
# every STRIKE-M photo
ls assets/**/strike-m__* 2>/dev/null

# every hardware close-up, newest last
ls assets/**/hardware__* | sort -t_ -k4

# everything from one date
ls assets/**/*__2025-10-02.*

# everything that mentions a setting
ls assets/**/*yard* assets/**/*sky* 2>/dev/null
```

The manifest can be filtered with any spreadsheet tool or with `csvkit`:

```bash
csvcut -c new_path,category,capture_date docs/ASSET-MANIFEST.csv | csvgrep -c category -m hardware
```

## Web derivatives

`assets/web/` holds a 1200 px, web-optimised copy of every photograph, under the same
filename as the original. The site uses these; the originals stay untouched as the archive.
Regenerate them after adding new photographs:

```bash
python3 tools/make_web_images.py
```

## A note on Git LFS

`*.mp4`, `*.pptx`, `*.zip`, `*.mov`, `*.avi` and `*.mkv` are stored in Git LFS
(see `.gitattributes`). In a checkout without Git LFS installed, those files exist only as
small text pointers, so their **content could not be viewed while naming them**. They were
named from what is verifiable without the media: the original filename, the capture date,
the source (WhatsApp, Android camera, DJI drone, screen recording) and the folder they were
filed in. The manifest marks these rows `metadata-only` in the `how_named` column.

One video is fully verified because it is not stored in LFS: the screen recording of the
Drone Tracker interface (`assets/Videos/ui__drone-tracker-live-view__raspberry-pi-camera-screen-recording.webm`).

To finish the video pass, install Git LFS and pull the media:

```bash
git lfs install
git lfs pull
python3 tools/make_video_sheets.py      # writes contact sheets to review/
```

Review the sheets, then adjust the filename's subject/context groups — the date and the
category prefix are already correct.
