#!/usr/bin/env python3
"""Generate web-optimised derivatives (max 1600px + 700px thumbnail) for the
curated asset set used by the site, and print the curated map for review.

Run:  python3 tools/make_web_images.py
Output: assets/web/<name>.jpg|png  and  assets/web/thumbs/<name>.jpg
Originals stay untouched in their folders.
"""
import os, sys, json
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from curate import CURATED  # noqa: E402

OUT = "assets/web"
THUMBS = os.path.join(OUT, "thumbs")
os.makedirs(THUMBS, exist_ok=True)


def has_alpha(im):
    return im.mode in ("RGBA", "LA") and im.getchannel("A").getextrema()[0] < 250


def convert(src, stem):
    """Write assets/web/<stem>.png (if transparency is needed) or .jpg, plus a thumb."""
    im = Image.open(src)
    im.load()
    keep_png = src.lower().endswith(".png") and has_alpha(im)
    ext = ".png" if keep_png else ".jpg"
    dst_full = os.path.join(OUT, stem + ext)
    dst_thumb = os.path.join(THUMBS, stem + ".jpg")

    if keep_png:
        base = Image.new("RGBA", im.size, (255, 255, 255, 0))
        base.alpha_composite(im.convert("RGBA"))
        im = base
    else:
        im = im.convert("RGB")

    big = im.copy()
    big.thumbnail((1600, 1600), Image.LANCZOS)
    if keep_png:
        big.save(dst_full, optimize=True)
    else:
        big.save(dst_full, "JPEG", quality=80, optimize=True, progressive=True)

    th = im.copy()
    th.thumbnail((700, 700), Image.LANCZOS)
    th.convert("RGB").save(dst_thumb, "JPEG", quality=76, optimize=True, progressive=True)
    return dst_full, dst_thumb


# resolve sources by filename stem, so .jpg/.jpeg changes never break the build
STEMS = {}
for dirpath, dirnames, filenames in os.walk("assets"):
    if dirpath.startswith(os.path.join("assets", "web")):
        continue
    for f in filenames:
        STEMS.setdefault(os.path.splitext(f)[0], os.path.join(dirpath, f))


def resolve(src):
    if os.path.exists(src):
        return src
    stem = os.path.splitext(os.path.basename(src))[0]
    if stem in STEMS:
        return STEMS[stem]
    raise SystemExit(f"curate.py references a file that does not exist: {src}")


rows = []
for item in CURATED:
    src = resolve(item["src"])
    stem = os.path.splitext(os.path.basename(src))[0]
    full, thumb = convert(src, stem)
    rows.append(dict(stem=stem, full=full, thumb=thumb,
                     category=item["category"], title=item["title"], note=item.get("note", "")))
    print(f"{os.path.getsize(full)/1024:7.0f} KB  {full}")

json.dump(rows, open(os.path.join(OUT, "curated.json"), "w"), indent=1)
print(f"\n{len(rows)} derivatives written")
