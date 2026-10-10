#!/usr/bin/env python3
"""Grade every real association photo the site shows into one warm, colourful film look.

    python3 tools/photo-grade.py            write assets/brand/photos/ from the originals (only what changed; --force for all)
    python3 tools/photo-grade.py --sheet P  also write a before/after contact sheet to P
    python3 tools/photo-grade.py --extend [name ...]
                                            widen too-tight portraits by AI outpainting of the margin only
                                            (all that need it, or the ones named), then run it plain again

Why: the photos come from a dozen phones with different white balance, and the first brand pass
printed them as a grey ink/paper duotone. Tim, 2026-09-16: "we'd also need a different, warmer effect
for the photos ... either keep em colored or find a nice warmed colorful effect". This keeps the colour,
takes out each phone's cast, then applies one shared grade: warm highlights, brown (never blue) shadows,
lifted blacks, a gentle S-curve, colours pulled slightly together, fine grain. Hero photos are graded too.
The originals are never modified; outputs keep the paths in assets/brand/photos/map.json.
"""
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps, ImageStat

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


# ------------------------------------------------------------------------------------------ portraits
# One format for every person: upright 4:5, the same head size, the same eye line, the head centred.
# Measured 2026-09-29 (Tim: "center all the faces equally, use AI if needed to complete a pic"): the old
# target (face box 34% of the frame, centred 42% down) needed 1.5x more photo than 20 of the 21 400px
# headshots have, so the crop clamped silently and heads came out 30-80% too big, too low, some cut off.
# The values below are the framing most of the real photos already have, so those stay 100% photograph and
# only the ones that lack pixels are widened, by AI outpainting of the margin (extend(), assets/adv/extended/).
PORTRAIT = (440, 550)     # 4:5
FACE_H = 0.54             # the face box fills this much of the frame height, in every portrait
EYE_Y = 0.47              # ...with the eye line this far down
TURN = 0.35               # a turned head is centred on the skull, not the face (see frame())
NUDGE = 0.02              # a crop may slide or shrink this much of its size to stay inside the photo
EXTENDED = ROOT / "assets/adv/extended"    # AI-widened copies; only the margin is AI (extended.json says where)
TRIM = {"dirk-moosmayer": (21, 0, 355, 400)}   # a web screenshot: white page margins and a black bar, not photo

PROBE = r"""
// Largest face: box, eye line and head turn (Apple Vision, on this Mac). One JSON line per image.
import Foundation
import Vision
import CoreImage
for path in CommandLine.arguments.dropFirst() {
    guard let img = CIImage(contentsOf: URL(fileURLWithPath: path)) else { continue }
    let handler = VNImageRequestHandler(ciImage: img, options: [:])
    let marks = VNDetectFaceLandmarksRequest(), rects = VNDetectFaceRectanglesRequest()
    rects.revision = VNDetectFaceRectanglesRequestRevision3
    guard (try? handler.perform([marks])) != nil,        // alone: its own detector + landmark-aligned box
          (try? VNImageRequestHandler(ciImage: img, options: [:]).perform([rects])) != nil,   // rev. 3: fine head turn
          let f = marks.results?.max(by: { $0.boundingBox.width * $0.boundingBox.height < $1.boundingBox.width * $1.boundingBox.height })
    else { continue }
    let b = f.boundingBox
    var ey = 1 - Double(b.midY) - 0.12 * Double(b.height)
    if let lm = f.landmarks, let l = lm.leftPupil ?? lm.leftEye, let r = lm.rightPupil ?? lm.rightEye {
        let ys = (l.normalizedPoints + r.normalizedPoints).map { Double($0.y) }
        ey = 1 - (Double(b.minY) + Double(b.height) * ys.reduce(0, +) / Double(ys.count))
    }
    let turn = rects.results?.min(by: { hypot($0.boundingBox.midX - b.midX, $0.boundingBox.midY - b.midY) < hypot($1.boundingBox.midX - b.midX, $1.boundingBox.midY - b.midY) })
    let yaw = (turn?.yaw?.doubleValue ?? 0) * 180 / .pi
    print(String(format: "{\"path\":\"%@\",\"bx\":%.4f,\"by\":%.4f,\"fw\":%.4f,\"fh\":%.4f,\"ey\":%.4f,\"yaw\":%.1f}",
                 path, Double(b.midX), 1 - Double(b.midY), Double(b.width), Double(b.height), ey, yaw))
}
"""


def probe(paths):
    """Face box, eye line (landmarks) and head turn for each file, 0..1 with y from the top."""
    binary = Path(f"/tmp/portraitprobe-{hashlib.sha1(PROBE.encode()).hexdigest()[:10]}")
    if not binary.exists():
        binary.with_suffix(".swift").write_text(PROBE)
        subprocess.run(["swiftc", "-O", str(binary.with_suffix(".swift")), "-o", str(binary)], check=True)
    out = subprocess.run([str(binary), *map(str, paths)], capture_output=True, text=True, check=True)
    return {d["path"]: d for d in map(json.loads, out.stdout.splitlines())}


def frame(face, W, H, at=(0, 0)):
    """The crop (x, y, w, h in pixels) that gives this face the house size, eye line and centre. The face
    was measured on a W x H photo; `at` is where that photo's corner sits in a widened copy.
    A head turned by `yaw` shows its face off the skull's centre, by about sin(yaw) of the head's
    half-width; centring the face box then reads as off centre (Timur Drezov, Kristian Feigelson,
    Tim Dort-Golts), so the crop centres the head instead."""
    h = face["fh"] * H / FACE_H
    w = h * PORTRAIT[0] / PORTRAIT[1]
    head_x = face["bx"] - TURN * face["fw"] * math.sin(math.radians(face["yaw"]))
    return at[0] + head_x * W - w / 2, at[1] + face["ey"] * H - EYE_Y * h, w, h


def fit(box, bounds):
    """Slide or barely shrink the crop (by at most NUDGE) to stay inside the photo. Returns the crop and
    the pixels still missing on each side (left, top, right, bottom); nothing is ever clamped silently."""
    x, y, w, h = box
    L, T, R, B = bounds
    k = min(1, (R - L) / w, (B - T) / h)
    if 1 - NUDGE <= k < 1:                              # keep the eye point where it was
        ex, ey = x + w / 2, y + EYE_Y * h
        w, h = w * k, h * k
        x, y = ex - w / 2, ey - EYE_Y * h
    slide = lambda lo, hi, a, size: min(lo - a, NUDGE * size) if a < lo else -min(a + size - hi, NUDGE * size) if a + size > hi else 0
    x += slide(L, R, x, w)
    y += slide(T, B, y, h)
    return (x, y, w, h), (max(0, L - x), max(0, T - y), max(0, x + w - R), max(0, y + h - B))


def mirror_pad(im, missing, feather=8):
    """No-AI fallback: continue the edges as a soft blurred mirror so the crop can still be centred."""
    l, t, r, b = (math.ceil(m) + 2 if m > 0 else 0 for m in missing)
    W, H = im.size
    canvas = Image.new("RGB", (W + l + r, H + t + b))
    for fx in (-1, 0, 1):
        for fy in (-1, 0, 1):
            tile = ImageOps.mirror(im) if fx else im
            canvas.paste(ImageOps.flip(tile) if fy else tile, (l + fx * W, t + fy * H))
    soft = canvas.filter(ImageFilter.GaussianBlur(10))
    mask = Image.new("L", canvas.size, 0)
    mask.paste(255, (l + feather, t + feather, l + W - feather, t + H - feather))
    return Image.composite(canvas, soft, mask.filter(ImageFilter.GaussianBlur(feather / 2))), (l, t)


def portrait_source(src):
    """The photo a portrait is cut from: its AI-widened copy when there is one, else the original."""
    wide = EXTENDED / (Path(src).stem + ".png")
    return wide if wide.exists() else original(src)


def replate(path, face, photo_size):
    """One portrait format: same head size, same eye line, head centred, whatever the photographer framed.
    `face` is always measured on the photograph itself, never on an AI-widened copy: the face detector's
    box moves by up to 5% between the two (Marie-France Zimmer), and the AI margin must not steer the crop."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    at = (0, 0)
    if path.parent == EXTENDED:
        wide = json.loads((EXTENDED / "extended.json").read_text())[path.stem]
        at = (wide["photo_at"][0] - wide["trim"][0], wide["photo_at"][1] - wide["trim"][1])
    bounds = (0, 0, *im.size) if path.parent == EXTENDED else TRIM.get(path.stem, (0, 0, *im.size))
    (x, y, w, h), missing = fit(frame(face, *photo_size, at), bounds)
    if any(m > 0.5 for m in missing):
        print(f"  {path.stem}: photo {'/'.join(str(round(m)) for m in missing)} px short (left/top/right/bottom);"
              f" blurred-mirror fill used. `python3 tools/photo-grade.py --extend {path.stem}` widens it properly")
        im, (ox, oy) = mirror_pad(im.crop(bounds), missing)
        x, y = x - bounds[0] + ox, y - bounds[1] + oy
    w, h = min(w, im.width), min(h, im.height)            # what is left is under half a pixel
    x, y = min(max(x, 0), im.width - w), min(max(y, 0), im.height - h)
    enlarge = PORTRAIT[1] / h
    if enlarge > 1.5:                                   # a small face blown up: soften the JPEG blocks first
        im = im.filter(ImageFilter.GaussianBlur(0.3 * (enlarge - 1)))
    return im.resize(PORTRAIT, Image.LANCZOS, box=(x, y, x + w, y + h))


IMAGEGEN = Path.home() / ".agents/skills/imagegen/scripts/generate_image.py"
OUTPAINT = ("This portrait photo sits on a larger canvas; the flat mid-grey bands around it are blank canvas. "
            "Outpaint ONLY those grey bands so the photo simply continues past its old edges: the same background, "
            "and where the frame cut them, the rest of the hair or head outline, shoulders and clothing, exactly as "
            "they would continue. Do not change anything inside the original photo: same person, same face, same "
            "expression, same pose, same position and size. Match its lighting, colour, focus, blur and grain. "
            "Photorealistic. No new people, objects, text, frames or borders.")


def extend(names, force=False):
    """Widen portraits whose photo is too tight for the house framing, by AI outpainting (Gemini 3 Pro Image,
    the imagegen skill; Tim allowed AI for this, 2026-09-29). The model paints only the margin: the original
    pixels are pasted back over its result, so the face and everything the photographer caught stay untouched.
    Writes assets/adv/extended/<name>.png and records in extended.json where the original sits inside it."""
    import datetime, os, tempfile
    mapping = json.loads(MAP.read_text())
    people = {Path(s).stem: s for s, o in mapping.items() if "/people/" in o}
    record_path = EXTENDED / "extended.json"
    record = json.loads(record_path.read_text()) if record_path.exists() else {}
    key = next(l.split("=", 1)[1].strip().strip('"\'') for l in (Path.home() / ".agents/.env/credentials.env").read_text().splitlines()
               if l.startswith("GEMINI_API_KEY="))
    EXTENDED.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="outpaint-"))
    for name in names or people:
        src = original(people[name])
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        im = im.crop(TRIM.get(name, (0, 0, *im.size)))
        im.save(tmp / f"{name}.png")
        face = probe([tmp / f"{name}.png"])[str(tmp / f"{name}.png")]
        W, H = im.size
        (x, y, w, h), missing = fit(frame(face, W, H), (0, 0, W, H))
        if not any(m > 0.5 for m in missing) or (not force and not names and (EXTENDED / f"{name}.png").exists()):
            continue
        pad = [math.ceil(m + 0.06 * h) if m > 0.5 else 0 for m in missing]          # room for the seam
        cw, ch = W + pad[0] + pad[2], H + pad[1] + pad[3]
        ratio = min((1, 4 / 5, 3 / 4, 2 / 3, 5 / 4, 4 / 3), key=lambda r: abs(math.log(cw / ch / r)))
        if cw / ch < ratio:                             # grow to a ratio the model draws natively
            extra = round(ch * ratio) - cw; pad[0] += extra // 2; pad[2] += extra - extra // 2
        else:
            extra = round(cw / ratio) - ch; pad[1] += extra // 2; pad[3] += extra - extra // 2
        size = (W + pad[0] + pad[2], H + pad[1] + pad[3])
        canvas = Image.new("RGB", size, (128, 128, 128)); canvas.paste(im, (pad[0], pad[1]))
        canvas.save(tmp / f"{name}-canvas.png")
        print(f"{name}: {W}x{H} -> {size[0]}x{size[1]}, outpainting {pad} px (left/top/right/bottom)")
        # The model redraws the whole picture, sometimes moved or retouched: find where it put the original,
        # and ask again (at most 3 times) when its copy strays, since that is where a seam would show.
        tries = []
        for attempt in range(3):
            run = subprocess.run(["uv", "run", str(IMAGEGEN), "--prompt", OUTPAINT, "--input-image", str(tmp / f"{name}-canvas.png"),
                                  "--filename", str(tmp / f"{name}-ai{attempt}.png"), "--resolution", "1K"],
                                 env={**os.environ, "GEMINI_API_KEY": key}, capture_output=True, text=True)
            if run.returncode:                          # the plain run then falls back to the blurred mirror
                sys.exit(f"{name}: imagegen failed, nothing written.\n{run.stderr[-600:]}")
            ai = Image.open(tmp / f"{name}-ai{attempt}.png").convert("RGB").resize(size, Image.LANCZOS)
            ref, grey = im.convert("L").resize((W // 2, H // 2)), ai.convert("L")
            err, dx, dy = min((ImageStat.Stat(ImageChops.difference(ref, grey.crop((pad[0] + dx, pad[1] + dy, pad[0] + dx + W, pad[1] + dy + H)).resize((W // 2, H // 2)))).mean[0], dx, dy)
                              for dx in range(-12, 13) for dy in range(-12, 13))
            tries.append((err, dx, dy, ai))
            print(f"  attempt {attempt + 1}: original found {dx:+d},{dy:+d} px off, difference {err:.1f}")
            if err <= 8:
                break
        err, dx, dy, ai = min(tries, key=lambda t: t[0])
        shift = (1, 0, dx, 0, 1, dy)                    # move it back; keep the unshifted edge where it vacates
        ai = Image.composite(ai.transform(size, Image.AFFINE, shift, Image.BICUBIC), ai,
                             Image.new("L", size, 255).transform(size, Image.AFFINE, shift))
        seen = ai.crop((pad[0], pad[1], pad[0] + W, pad[1] + H))
        chans = []
        for a, b, c in zip(ImageStat.Stat(seen).mean, ImageStat.Stat(im).mean, ai.split()):
            chans.append(c.point(lambda v, k=b / max(a, 1): min(255, round(v * k))))
        ai = Image.merge("RGB", chans)
        mask = Image.new("L", size, 0)
        mask.paste(255, (pad[0] + 6, pad[1] + 6, pad[0] + W - 6, pad[1] + H - 6))
        out = Image.composite(canvas, ai, mask.filter(ImageFilter.GaussianBlur(3)))
        out.save(EXTENDED / f"{name}.png")
        record[name] = {"from": people[name].lstrip("/"), "trim": list(TRIM.get(name, (0, 0, W, H))),
                        "photo_at": [pad[0], pad[1], W, H], "ai_margin_px": pad,
                        "model": "gemini-3-pro-image-preview (Nano Banana Pro), imagegen skill",
                        "made": datetime.date.today().isoformat(), "match_error": round(err, 1),
                        "note": "only pixels outside photo_at (plus a 6px blended seam) are AI; the rest is the original"}
        print(f"  -> {EXTENDED.relative_to(ROOT)}/{name}.png")
    record_path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")


def original(src):
    stem = re.sub(r"\.(webp|jpe?g|png)$", "", src.lstrip("/"))
    cands = [ROOT / (stem + e) for e in (".jpg", ".jpeg", ".png", ".webp") if (ROOT / (stem + e)).exists()]
    return max(cands, key=lambda c: Image.open(c).size[0] * Image.open(c).size[1])


def focal_points(paths, originals=False):
    """Where the faces are, as CSS object-position percentages, so no crop cuts a face off.
    Apple's Vision framework, compiled on demand; nothing leaves the Mac. No faces: no entry."""
    binary = Path("/tmp/facepoint")
    src = ROOT / "tools/faces/facepoint.swift"
    if not binary.exists() or binary.stat().st_mtime < src.stat().st_mtime:
        subprocess.run(["swiftc", "-O", str(src), "-o", str(binary)], check=True)
    files = [original(p) if originals else ROOT / p.lstrip("/") for p in paths]
    back = {str(f): p for f, p in zip(files, paths)}
    out = subprocess.run([str(binary), *[str(f) for f in files]], capture_output=True, text=True)
    points = {}
    for line in out.stdout.splitlines():
        d = json.loads(line)
        key = back.get(d["path"], "/" + str(Path(d["path"]).relative_to(ROOT)))
        points[key] = d if originals else [round(d["x"] * 100, 1), round(d["y"] * 100, 1), d["faces"]]
    return points


def main():
    mapping = json.loads(MAP.read_text())
    sources = {src: portrait_source(src) for src, out in mapping.items() if "/people/" in out}
    faces = probe([original(src) for src in sources])
    sheet_rows = []
    # Make-style: an output newer than its original and than this script is left alone. The grain is random
    # (Image.effect_noise), so regrading an unchanged photo rewrote every file with a new binary diff; adding one
    # portrait on 2026-10-08 touched all three headers. --force regrades everything.
    force = "--force" in sys.argv
    me = Path(__file__).stat().st_mtime
    def fresh(srcs, outp):
        o = ROOT / outp.lstrip("/")
        return (not force) and o.exists() and all(o.stat().st_mtime > max(Path(x).stat().st_mtime, me) for x in srcs)
    for src, out in mapping.items():
        portrait = "/people/" in out
        # the AI-widened copy counts too: an --extend run writes it after the output already exists
        if fresh([original(src)] + ([sources[src]] if sources.get(src) else []), out):
            continue
        im = ImageOps.exif_transpose(Image.open(sources.get(src) or original(src))).convert("RGB")
        face = faces.get(str(original(src))) if portrait else None
        if face:
            im = replate(sources[src], face, Image.open(original(src)).size)
        else:
            im.thumbnail((640, 640) if portrait else (1800, 1800), Image.LANCZOS)
        g = grade(im)
        g.save(ROOT / out.lstrip("/"), quality=82, method=6)
        if len(sheet_rows) < 8 and not portrait:
            sheet_rows.append((im.convert("RGB"), g))
    # Contact is a still from the Apex film (CNAM), cut from the 2560x1440 original with the TV-channel
    # bug cropped off; the old header was a 960px frame (Tim, 2026-09-29: "ass both quality and context").
    heroes = {"asso": "assets/cinema-event-4ffR4bAi.jpg", "dignity": "assets/team-meeting-Bf_2ngHD.jpeg",
              "contact": "assets/film-stills/apex-handshake.jpg"}
    for key, src in heroes.items():
        if all(fresh([ROOT / src], f"assets/brand/hero/{key}-{w}.webp") for w in (1920, 960)):
            continue
        im = Image.open(ROOT / src)
        for w in (1920, 960):
            c = im.copy(); c.thumbnail((w, w), Image.LANCZOS)
            grade(c).save(ROOT / f"assets/brand/hero/{key}-{w}.webp", quality=80, method=6)
    points = focal_points(list(mapping.values()))
    (ROOT / "assets/brand/photos/focal.json").write_text(json.dumps(points, indent=1) + "\n")
    print(len(mapping), "photos graded,", len(heroes), "heroes,", len(points), "with faces found")
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
    if "--extend" in sys.argv:
        extend([a for a in sys.argv[sys.argv.index("--extend") + 1:] if not a.startswith("--")], "--force" in sys.argv)
    else:
        main()
