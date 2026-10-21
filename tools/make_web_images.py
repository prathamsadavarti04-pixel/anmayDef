#!/usr/bin/env python3
"""Regenerate the web-optimised copies in assets/web/ from the originals in assets/.

Usage:
    python3 tools/make_web_images.py            # all images
    python3 tools/make_web_images.py --max 1600 # different long-edge size

Requires Pillow:  pip install pillow
Originals are never modified. Output uses the same filename as the original, with a
.jpg extension for photographs (1200 px long edge, quality 80, progressive).
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets")
OUT = os.path.join(SRC, "web")
EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=1200, help="long edge in pixels (default 1200)")
    ap.add_argument("--quality", type=int, default=80)
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    count = 0
    total = 0

    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if os.path.join(root, d) != OUT]
        for name in sorted(files):
            if os.path.splitext(name)[1].lower() not in EXTS:
                continue
            src = os.path.join(root, name)
            if os.path.getsize(src) < 4096:  # skip Git LFS pointers / stubs
                continue
            try:
                im = ImageOps.exif_transpose(Image.open(src))
            except Exception as exc:  # pragma: no cover
                print(f"skip {src}: {exc}")
                continue
            im.thumbnail((args.max, args.max), Image.LANCZOS)
            if im.mode in ("RGBA", "LA", "P") and "transparency" in im.info or im.mode in ("RGBA", "LA"):
                # flatten cut-outs onto white so the JPEG has no black halo
                rgba = im.convert("RGBA")
                flat = Image.new("RGB", rgba.size, (255, 255, 255))
                flat.paste(rgba, mask=rgba.split()[-1])
                im = flat
            dst = os.path.join(OUT, os.path.splitext(name)[0] + ".jpg")
            im.convert("RGB").save(dst, quality=args.quality, optimize=True, progressive=True)
            count += 1
            total += os.path.getsize(dst)

    print(f"{count} derivatives written to assets/web ({total / 1048576:.1f} MB)")


if __name__ == "__main__":
    main()
