#!/usr/bin/env python3
"""Make a labelled contact sheet per video so every clip can be reviewed fast.

    git lfs install && git lfs pull            # first: get the real bytes
    python3 tools/video_contact_sheets.py      # writes review/video-sheets/*.jpg
    open review/video-sheets                  # then rename each clip from what you see

Each sheet shows four evenly spaced frames plus the filename, duration and size, so
one glance is usually enough to write the real description and drop the
`pending-review` marker from the filename.

Requires ffmpeg (the script falls back to the binary bundled with imageio-ffmpeg)
and Pillow for the labels.

    pip install pillow imageio-ffmpeg
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
OUT = os.path.join("review", "video-sheets")
FRAMES = 4


def ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit("ffmpeg not found: install ffmpeg, or `pip install imageio-ffmpeg`")


def ffprobe():
    exe = shutil.which("ffprobe")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return os.path.join(os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe()), "ffprobe-linux-x86_64-v7.0.2")
    except Exception:
        return None


def duration(ff, path):
    try:
        p = subprocess.run([ff, "-hide_banner", "-i", path], capture_output=True, text=True)
        m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", p.stderr)
        if m:
            h, mi, s = m.groups()
            return int(h) * 3600 + int(mi) * 60 + float(s)
    except Exception:
        pass
    return None


def is_pointer(path):
    return os.path.getsize(path) < 200 and open(path, "r", errors="ignore").read().startswith("version https://git-lfs")


def main():
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except Exception:
        font = small = ImageFont.load_default()

    ff = ffmpeg()
    os.makedirs(OUT, exist_ok=True)
    videos, skipped = [], []
    for dirpath, dirnames, filenames in os.walk("assets"):
        if dirpath.startswith(os.path.join("assets", "web")):
            continue
        for f in sorted(filenames):
            if f.lower().endswith((".mp4", ".mov", ".webm", ".mkv", ".avi")):
                p = os.path.join(dirpath, f)
                (skipped if is_pointer(p) else videos).append(p)

    print(f"{len(videos)} playable videos, {len(skipped)} still LFS pointers")
    if skipped:
        print("  run `git lfs pull` to materialise:", *["  " + s for s in skipped[:5]], sep="\n")
        if len(skipped) > 5:
            print(f"  … and {len(skipped) - 5} more")

    for p in videos:
        dur = duration(ff, p)
        thumbs = []
        with tempfile.TemporaryDirectory() as td:
            if dur:
                for i in range(FRAMES):
                    t = max(0.2, dur * (i + 0.5) / FRAMES)
                    dst = os.path.join(td, f"f{i}.jpg")
                    subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-ss", str(t), "-i", p,
                                    "-frames:v", "1", "-vf", "scale=640:-2", "-q:v", "4", dst, "-y"],
                                   capture_output=True)
            else:
                # container carries no duration (common for webm screen captures):
                # decode and pick every 15th second, then keep four spread evenly.
                subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-i", p,
                                "-vf", "fps=1/15,scale=640:-2", "-q:v", "4",
                                os.path.join(td, "f%04d.jpg"), "-y"], capture_output=True)
            found = sorted(f for f in os.listdir(td) if f.endswith(".jpg"))
            if not dur and found:
                step = max(1, len(found) // FRAMES)
                found = found[::step][:FRAMES]
            for f in found:
                thumbs.append(Image.open(os.path.join(td, f)).convert("RGB"))
        if not thumbs:
            print("  could not decode", p)
            continue
        tw, th = 640, int(640 * thumbs[0].height / thumbs[0].width)
        cols = 2
        rows = (len(thumbs) + cols - 1) // cols
        head = 62
        sheet = Image.new("RGB", (cols * tw, head + rows * th), (14, 14, 16))
        for i, im in enumerate(thumbs):
            im = im.resize((tw, th))
            sheet.paste(im, ((i % cols) * tw, head + (i // cols) * th))
        d = ImageDraw.Draw(sheet)
        mb = os.path.getsize(p) / 1048576
        d.text((12, 8), os.path.basename(p), font=font, fill=(255, 255, 255))
        length = f"{dur:0.1f}s" if dur else "duration n/a"
        d.text((12, 32), f"{length} · {mb:.1f} MB · {p}", font=small, fill=(160, 170, 185))
        dst = os.path.join(OUT, os.path.splitext(os.path.basename(p))[0] + ".jpg")
        sheet.save(dst, quality=82)
        print(f"  {dst}")

    manifest = os.path.join(OUT, "sheets.json")
    json.dump({"sheets": sorted(os.listdir(OUT))}, open(manifest, "w"), indent=1)
    print(f"\ndone — {len(videos)} sheets in {OUT}")


if __name__ == "__main__":
    main()
