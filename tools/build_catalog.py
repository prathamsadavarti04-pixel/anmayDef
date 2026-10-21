#!/usr/bin/env python3
"""Rebuild docs/assets-catalog.{csv,json} and docs/assets-index.md from
tools/asset_descriptions.py.

    python3 tools/build_catalog.py            # write the catalogue
    python3 tools/build_catalog.py --check    # fail if any asset lacks a description

Every file under assets/ (except the generated assets/web/ tree) must have an
entry in DESCRIPTIONS. Add new assets by describing them there, then re-run.
"""
import csv
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from asset_descriptions import DESCRIPTIONS  # noqa: E402

LFS_RE = re.compile(r"oid sha256:([0-9a-f]{64})")
COLS = ["path", "filename", "folder", "extension", "kind", "status", "bytes_in_repo",
        "lfs_size_bytes", "lfs_oid", "md5", "role", "quality", "page", "tags", "alt",
        "description", "duplicate_of"]


def lfs_info(p):
    if os.path.getsize(p) < 200:
        t = open(p, "r", errors="ignore").read()
        m, s = LFS_RE.search(t), re.search(r"size (\d+)", t)
        if m:
            return m.group(1), int(s.group(1))
    return None, None


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def assets():
    for dirpath, dirnames, filenames in os.walk("assets"):
        dirnames[:] = [d for d in sorted(dirnames) if not (dirpath == "assets" and d == "web")]
        for f in sorted(filenames):
            yield os.path.join(dirpath, f)


def main():
    files = list(assets())
    missing = [f for f in files if f not in DESCRIPTIONS]
    stale = [k for k in DESCRIPTIONS if k not in files]
    if missing or stale:
        print("Assets without a description:")
        for m in missing:
            print("  +", m)
        print("Descriptions with no file (renamed or deleted?):")
        for s in stale:
            print("  -", s)
        return 1
    if "--check" in sys.argv:
        print(f"ok: {len(files)} assets, all described")
        return 0

    rows = []
    for p in files:
        e = DESCRIPTIONS[p]
        oid, lsize = lfs_info(p)
        is_pointer = oid is not None
        rows.append({
            "path": p,
            "filename": os.path.basename(p),
            "folder": os.path.dirname(p),
            "extension": os.path.splitext(p)[1].lstrip(".").lower(),
            "kind": "lfs-pointer" if is_pointer else "in-repo-bytes",
            "status": "pending-visual-review" if e["quality"] == "pending" else "visually-reviewed",
            "bytes_in_repo": os.path.getsize(p),
            "lfs_size_bytes": lsize if is_pointer else "",
            "lfs_oid": oid if is_pointer else "",
            "md5": "" if is_pointer else md5(p),
            "role": e["role"],
            "quality": e["quality"],
            "page": e["page"],
            "tags": "; ".join(e["tags"]),
            "alt": e["alt"],
            "description": e["desc"],
            "duplicate_of": e.get("dup_of", ""),
        })

    os.makedirs("docs", exist_ok=True)
    with open("docs/assets-catalog.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    json.dump(rows, open("docs/assets-catalog.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    with open("docs/assets-index.md", "w", encoding="utf-8") as fh:
        fh.write("# Anmay Defence – asset index\n\n"
                 "Every file under `assets/`, renamed from its original camera/WhatsApp name to a\n"
                 "content description. `reviewed` = the pixels/bytes were opened and described here;\n"
                 "`pending` = only a Git LFS pointer is present, so the name is inferred from folder,\n"
                 "date and neighbouring reviewed files.\n\n")
        for r in sorted(rows, key=lambda x: (x["folder"], x["filename"])):
            mark = "reviewed" if r["status"] == "visually-reviewed" else "pending"
            fh.write(f"- `{r['filename']}` — {r['alt']} **[{mark}; {r['role']}; {r['tags']}]**\n")

    from collections import Counter
    print(f"{len(rows)} assets catalogued")
    print("  by extension:", dict(Counter(r["extension"] for r in rows)))
    print("  reviewed:", sum(1 for r in rows if r["status"] == "visually-reviewed"),
          " pending:", sum(1 for r in rows if r["status"] == "pending-visual-review"))
    print("  duplicates flagged:", sum(1 for r in rows if r["duplicate_of"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
