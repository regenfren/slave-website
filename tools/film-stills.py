#!/usr/bin/env python3
"""Cut the site's film stills from the original student films, reproducibly.

    python3 tools/film-stills.py <dropbox-dump dir>

Writes assets/film-stills/*.jpg. photo-grade.py then grades them like every other photo (the
Contact header via its `heroes`, the Rails of Time card via map.json). Tim, 2026-09-29: the old
Contact header was a 960px frame ("ass both quality and context") and the Rails of Time card was an
AI-looking exhibition render; both now come from the films' own originals.

apex-handshake: APEX (CNAM, 2560x1440) at 0:26, before the name titles animate in. The TV-channel
  bug is cropped off the top. The left of the frame is plain wall and decking, so it is extended by
  reflecting that empty strip (no AI, no people touched), which puts the handshake in the right half
  of a wide header, clear of the headline that sits bottom-left.
stage-echo-filming: Stage Echo (CAFA, 1906x1080) at 2:18, a student filming an interview, cropped
  above the burned-in subtitles.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/film-stills"


def frame(src, t):
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1", f.name], check=True)
        return Image.open(f.name).convert("RGB").copy()


def extend_left(im, clean, add):
    """Add `add` px on the left by reflecting the people-free strip [0, clean) outwards, twice if needed."""
    strip = im.crop((0, 0, clean, im.height))
    parts, need, flip = [], add, True
    while need > 0:
        piece = ImageOps.mirror(strip) if flip else strip
        take = min(need, clean)
        parts.insert(0, piece.crop((piece.width - take, 0, piece.width, im.height)))
        need -= take
        flip = not flip
    out = Image.new("RGB", (im.width + add, im.height))
    x = 0
    for p in parts:
        out.paste(p, (x, 0)); x += p.width
    out.paste(im, (x, 0))
    return out


def main():
    dump = Path(sys.argv[1])
    OUT.mkdir(exist_ok=True)
    a = frame(dump / "VIDEO CNAM SPRING 2026/APEX.mov", 26).crop((0, 150, 2560, 1440))
    a = extend_left(a.crop((0, 0, 2250, a.height)), clean=560, add=860)
    a.save(OUT / "apex-handshake.jpg", quality=95)
    s = frame(dump / "VIDEO CHINA SUMMER 2026/1. fnal video/G2 - SG4 stage echo.mp4", 138).crop((330, 0, 1770, 900))
    s.save(OUT / "stage-echo-filming.jpg", quality=95)
    print("apex-handshake", a.size, "stage-echo-filming", s.size)


if __name__ == "__main__":
    main()
