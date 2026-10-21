#!/usr/bin/env python3
"""Build contact sheets for every video so the ones stored in Git LFS can be reviewed
and named from their actual content.

Usage:
    git lfs install && git lfs pull      # fetch the media first
    python3 tools/make_video_sheets.py   # writes review/video-NN.jpg + review/index.csv

Requires ffmpeg on PATH and Pillow (`pip install pillow`).
Each sheet shows three frames (12%, 45%, 80% of the duration) with the source path and
duration, and review/index.csv lists the proposed rename target for each file.
"""
import csv
import json
import os
import shutil
import subprocess
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    sys.exit("Pillow is required: pip install pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "review")
VIDEO_EXTS = (".mp4", ".mov", ".avi", ".mkv", ".webm")


def ffmpeg_bin() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # pragma: no cover
        sys.exit("ffmpeg not found. Install ffmpeg or `pip install imageio-ffmpeg`.")


def ffprobe_duration(path: str, ffmpeg: str) -> float:
    probe = shutil.which("ffprobe")
    if probe:
        out = subprocess.run(
            [probe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", path],
            capture_output=True, text=True,
        ).stdout.strip()
        try:
            return float(out)
        except ValueError:
            return 0.0
    # fall back to parsing ffmpeg's stderr
    out = subprocess.run([ffmpeg, "-i", path], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            stamp = line.split("Duration:")[1].split(",")[0].strip()
            try:
                h, m, s = stamp.split(":")
                return int(h) * 3600 + int(m) * 60 + float(s)
            except ValueError:
                return 0.0
    return 0.0


def main() -> None:
    ffmpeg = ffmpeg_bin()
    os.makedirs(OUT, exist_ok=True)
    videos = []
    for root, _, files in os.walk(ASSETS):
        for name in sorted(files):
            if name.lower().endswith(VIDEO_EXTS):
                videos.append(os.path.join(root, name))
    videos.sort()

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    except Exception:  # pragma: no cover
        font = ImageFont.load_default()

    rows = []
    for i, path in enumerate(videos):
        rel = os.path.relpath(path, ROOT)
        if os.path.getsize(path) < 4096:
            print(f"pointer, run `git lfs pull` first: {rel}")
            continue
        duration = ffprobe_duration(path, ffmpeg)
        frames = []
        stamps = [duration * f for f in (0.12, 0.45, 0.80)] if duration > 1 else [1.0, 5.0, 10.0]
        for at in stamps:
            tmp = os.path.join(OUT, "_frame.jpg")
            subprocess.run(
                [ffmpeg, "-y", "-v", "error", "-ss", f"{at:.2f}", "-i", path,
                 "-frames:v", "1", "-vf", "scale=640:-2", tmp],
                capture_output=True,
            )
            if os.path.exists(tmp) and os.path.getsize(tmp) > 500:
                frames.append(Image.open(tmp).copy())
        if not frames:
            print(f"no frames extracted: {rel}")
            continue

        w = max(f.width for f in frames)
        h = sum(f.height for f in frames) + 100
        sheet = Image.new("RGB", (w, h), "white")
        y = 0
        for f in frames:
            sheet.paste(f, (0, y))
            y += f.height
        draw = ImageDraw.Draw(sheet)
        draw.rectangle([0, 0, w, 100], fill="black")
        draw.text((12, 10), f"video-{i:03d}  ·  {duration:.1f}s", fill="yellow", font=font)
        draw.text((12, 44), rel[:90], fill="white", font=font)
        draw.text((12, 72), rel[90:180] if len(rel) > 90 else "", fill="white", font=font)
        out = os.path.join(OUT, f"video-{i:03d}.jpg")
        sheet.save(out, quality=88)
        rows.append({"sheet": os.path.relpath(out, ROOT), "video": rel,
                     "duration_s": round(duration, 1)})
        print(f"video-{i:03d}  {duration:6.1f}s  {rel}")

    tmp = os.path.join(OUT, "_frame.jpg")
    if os.path.exists(tmp):
        os.remove(tmp)
    with open(os.path.join(OUT, "index.csv"), "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["sheet", "video", "duration_s"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n{len(rows)} sheets in review/. Open them, then refine the subject/context groups "
          f"of each filename.")


if __name__ == "__main__":
    main()
