#!/usr/bin/env python3
"""Shrink the site's images to what the pages actually display, and repoint every reference.

Run from the repo root:  python3 tools/optimize-images.py [--dry-run]

- Photos over ~120 KB become WebP (quality 80, max 1600 px wide), same aspect ratio, so no
  layout changes. The original is deleted once nothing references it any more.
- Logos are resized to a few times their displayed size (the header emblem shows at 56 px
  high, the footer logo at 64 px; both shipped at 768 to 1024 px).
- Film posters (assets/films/*.jpg) become 800 px WebP; films.json is repointed.
- The favicon gets its own 64 px file instead of the 299 KB og:image PNG.

Idempotent: files already converted are skipped. Prints a before/after table.
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DRY = "--dry-run" in sys.argv
PAGES = list(ROOT.glob("*.html")) + list((ROOT / "fr").glob("*.html"))
TEXT_FILES = PAGES + [ASSETS / "clone-fixes.css", ASSETS / "films.css", ASSETS / "clone.js", ASSETS / "films.js"]

PHOTO_MIN_BYTES = 120_000
PHOTO_MAX_W = 1600
PHOTO_Q = 80
POSTER_W = 800
LOGOS = {  # file -> (target height px, output name)
    "slave-emblem.png": (224, "slave-emblem-224.webp"),
    "logo-Dyiem0iL.png": (192, "logo-192.webp"),
}
KEEP = {"logo.png"}  # og:image; stays PNG at full size


def log(*a):
    print(*a)


def save_webp(img: Image.Image, dest: Path, max_w: int | None = None, height: int | None = None, q: int = PHOTO_Q):
    im = img
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if "A" in im.getbands() or im.mode == "P" else "RGB")
    if height and im.height > height:
        im = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
    elif max_w and im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    if not DRY:
        im.save(dest, "WEBP", quality=q, method=6)
    return im.size


def replace_refs(old: str, new: str) -> int:
    n = 0
    for f in TEXT_FILES:
        if not f.exists():
            continue
        s = f.read_text(encoding="utf-8")
        if old in s:
            n += s.count(old)
            if not DRY:
                f.write_text(s.replace(old, new), encoding="utf-8")
    return n


def still_referenced(name: str) -> bool:
    stem = Path(name).stem
    for f in TEXT_FILES + [ASSETS / "films.json"]:
        if f.exists() and stem in f.read_text(encoding="utf-8"):
            return True
    return False


def main():
    rows = []
    # 1. photos
    for p in sorted(ASSETS.glob("*")):
        if p.suffix.lower() not in (".jpg", ".jpeg", ".png") or p.name in KEEP or p.name in LOGOS:
            continue
        if p.stat().st_size < PHOTO_MIN_BYTES:
            continue
        dest = p.with_suffix(".webp")
        if dest.exists():
            continue
        with Image.open(p) as im:
            size = save_webp(im, dest, max_w=PHOTO_MAX_W)
        refs = replace_refs(p.name, dest.name)
        after = dest.stat().st_size if dest.exists() else 0
        rows.append((p.name, p.stat().st_size, dest.name, after, size, refs))
        if not DRY and refs and not still_referenced(p.name):
            p.unlink()
    # 2. logos
    for name, (h, out) in LOGOS.items():
        src, dest = ASSETS / name, ASSETS / out
        if not src.exists() or dest.exists():
            continue
        with Image.open(src) as im:
            size = save_webp(im, dest, height=h, q=90)
        refs = replace_refs(name, out)
        rows.append((name, src.stat().st_size, out, dest.stat().st_size if dest.exists() else 0, size, refs))
        if not DRY and refs and not still_referenced(name):
            src.unlink()
    # 3. favicon + apple touch icon from logo.png
    logo = ASSETS / "logo.png"
    for out, px in (("favicon-64.png", 64), ("apple-touch-icon.png", 180)):
        dest = ASSETS / out
        if logo.exists() and not dest.exists():
            with Image.open(logo) as im:
                im = im.convert("RGBA").resize((px, px), Image.LANCZOS)
                if not DRY:
                    im.save(dest, "PNG", optimize=True)
            rows.append(("logo.png (icon)", logo.stat().st_size, out, dest.stat().st_size if dest.exists() else 0, (px, px), 0))
    # 4. posters
    manifest = ASSETS / "films.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    changed = False
    for f in data["films"]:
        poster = f.get("poster") or ""
        if not poster.endswith(".jpg"):
            continue
        src = ROOT / poster
        dest = src.with_suffix(".webp")
        if src.exists() and not dest.exists():
            with Image.open(src) as im:
                size = save_webp(im, dest, max_w=POSTER_W)
            rows.append((poster, src.stat().st_size, dest.name, dest.stat().st_size if dest.exists() else 0, size, 1))
            if not DRY:
                src.unlink()
        if dest.exists() or DRY:
            f["poster"] = poster[:-4] + ".webp"
            changed = True
    if changed and not DRY:
        manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    total_before = sum(r[1] for r in rows)
    total_after = sum(r[3] for r in rows)
    log(f"{'file':44} {'before':>8} {'after':>8}  size        refs")
    for name, b, out, a, size, refs in rows:
        log(f"{name[:44]:44} {b/1024:7.0f}K {a/1024:7.0f}K  {size[0]}x{size[1]:<6} {refs}")
    log(f"{'TOTAL':44} {total_before/1024:7.0f}K {total_after/1024:7.0f}K  ({(1 - total_after / max(total_before, 1)) * 100:.0f}% smaller){'  [dry run]' if DRY else ''}")


if __name__ == "__main__":
    main()
