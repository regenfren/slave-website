#!/usr/bin/env python3
"""Grade every real association photo the site shows into one warm, colourful film look.

    python3 tools/photo-grade.py            write assets/brand/photos/ from the originals
    python3 tools/photo-grade.py --sheet P  also write a before/after contact sheet to P

Why: the photos come from a dozen phones with different white balance, and the first brand pass
printed them as a grey ink/paper duotone. Tim, 2026-09-16: "we'd also need a different, warmer effect
for the photos ... either keep em colored or find a nice warmed colorful effect". This keeps the colour,
takes out each phone's cast, then applies one shared grade: warm highlights, brown (never blue) shadows,
lifted blacks, a gentle S-curve, colours pulled slightly together, fine grain. Hero photos are graded too.
The originals are never modified; outputs keep the paths in assets/brand/photos/map.json.
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageOps, ImageStat

ROOT = Path(__file__).resolve().parent.parent
MAP = ROOT / "assets/brand/photos/map.json"


def curve(lo, hi, gamma=1.0, s=0.0):
    """Lift blacks to lo, roll highlights to hi, optional gamma and S-contrast. Returns a 256 LUT."""
    lut = []
    for i in range(256):
        x = i / 255
        x = x ** gamma
        if s:
            x = x + s * (x - 0.5) * (1 - abs(2 * x - 1))
        lut.append(round(lo + (hi - lo) * min(1, max(0, x))))
    return lut


def grade(im):
    im = ImageOps.exif_transpose(im).convert("RGB")
    # 1. take out most of the phone's colour cast (gray world, 70%)
    r, g, b = im.split()
    means = ImageStat.Stat(im).mean
    avg = sum(means) / 3
    chans = []
    for ch, m in zip((r, g, b), means):
        k = 1 + 0.7 * (avg / max(m, 1) - 1)
        chans.append(ch.point(lambda v, k=k: min(255, round(v * k))))
    im = Image.merge("RGB", chans)
    # 2. tame extremes so a red tulip and a blue wall sit in one palette
    im = ImageOps.autocontrast(im, cutoff=0.6)
    im = ImageEnhance.Color(im).enhance(0.96)
    # 3. warm film curve per channel: warm highlights, brown shadows, lifted blacks
    r, g, b = im.split()
    r = r.point(curve(26, 255, 0.91, 0.22))
    g = g.point(curve(19, 243, 0.96, 0.22))
    b = b.point(curve(12, 214, 1.07, 0.2))
    im = Image.merge("RGB", (r, g, b))
    # 4. a touch of glow in the highlights and fine grain
    soft = im.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(6))
    im = ImageChops.screen(im, ImageEnhance.Brightness(soft).enhance(0.12))
    noise = Image.effect_noise(im.size, 18).convert("L").point(lambda v: 128 + (v - 128) // 3)
    im = ImageChops.overlay(im, Image.merge("RGB", [noise] * 3))
    return im


def original(src):
    stem = re.sub(r"\.(webp|jpe?g|png)$", "", src.lstrip("/"))
    cands = [ROOT / (stem + e) for e in (".jpg", ".jpeg", ".png", ".webp") if (ROOT / (stem + e)).exists()]
    return max(cands, key=lambda c: Image.open(c).size[0] * Image.open(c).size[1])


def main():
    mapping = json.loads(MAP.read_text())
    sheet_rows = []
    for src, out in mapping.items():
        portrait = "/people/" in out
        im = Image.open(original(src))
        im.thumbnail((640, 640) if portrait else (1800, 1800), Image.LANCZOS)
        g = grade(im)
        g.save(ROOT / out.lstrip("/"), quality=82, method=6)
        if len(sheet_rows) < 8 and not portrait:
            sheet_rows.append((im.convert("RGB"), g))
    heroes = {"asso": "assets/cinema-event-4ffR4bAi.jpg", "dignity": "assets/team-meeting-Bf_2ngHD.jpeg"}
    for key, src in heroes.items():
        im = Image.open(ROOT / src)
        for w in (1920, 960):
            c = im.copy(); c.thumbnail((w, w), Image.LANCZOS)
            grade(c).save(ROOT / f"assets/brand/hero/{key}-{w}.webp", quality=80, method=6)
    print(len(mapping), "photos graded, 2 heroes")
    if "--sheet" in sys.argv:
        path = sys.argv[sys.argv.index("--sheet") + 1]
        W = 520
        tiles = []
        for a, b in sheet_rows:
            a = a.copy(); a.thumbnail((W, W)); b = b.copy(); b.thumbnail((W, W))
            row = Image.new("RGB", (W * 2 + 10, max(a.height, b.height)), (255, 255, 255))
            row.paste(a, (0, 0)); row.paste(b, (W + 10, 0)); tiles.append(row)
        H = sum(t.height + 10 for t in tiles)
        sheet = Image.new("RGB", (W * 2 + 10, H), (255, 255, 255)); y = 0
        for t in tiles:
            sheet.paste(t, (0, y)); y += t.height + 10
        sheet.save(path, quality=80)


if __name__ == "__main__":
    main()
