#!/usr/bin/env python3
"""Build the home-page reel from the original student films, in one lossy encode per output.

    python3 tools/reel/build.py <media dir> [--stage master|encode|all]

1. every shot is cut from its original file into a lossless 1920x1080 30 fps clip
2. the clips are joined with 0.35 s dissolves into a lossless master
3. the master is slowed 10% (Tim, 2026-09-16) keeping every frame (27.27 fps, no duplicates), then
   cropped twice: 1920x816 cinema crop for wide screens (also removes burned-in subtitles and TV
   logos) and 642x856 portrait crop for phones, so a phone never upscales a wide frame
4. each crop is encoded as AV1 (smallest at high quality), HEVC (Safari and Apple devices without
   AV1 decode) and H.264 (last fallback). assets/brand/site.js picks the first one the browser plays.

Before 2026-09-16 evening the reel went through three lossy generations and a 1280-wide, heavily
denoised final encode; Tim: "way too low quality". Never encode from an already encoded reel.
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "assets/brand/reel"
WORK = Path("/tmp/slave-reel")
FADE, SLOW = 0.35, 1.10
FPS_OUT = "300/11"  # 30 fps slowed by 10%


def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def shots():
    rows = []
    for line in (HERE / "shots.txt").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            i, src, t, d, film, school = line.split("|")
            rows.append((i, src, float(t), float(d), film, school))
    return rows


def master(media):
    WORK.mkdir(exist_ok=True)
    S = shots()
    for i, src, t, d, *_ in S:
        run(["-ss", str(t), "-i", str(Path(media) / src), "-t", str(d), "-an",
             "-vf", "fps=30,scale=1920:1080:force_original_aspect_ratio=increase:flags=lanczos,crop=1920:1080,format=yuv420p",
             "-c:v", "libx264", "-qp", "0", "-preset", "ultrafast", str(WORK / f"{i}.mp4")])
    inputs, parts, prev, off, cuts = [], [], "[0:v]", 0.0, [0.0]
    for i, *_ in S:
        inputs += ["-i", str(WORK / f"{i}.mp4")]
    for k in range(1, len(S)):
        off += S[k - 1][3] - FADE
        cuts.append(round(off * SLOW, 2))
        parts.append(f"{prev}[{k}:v]xfade=transition=fade:duration={FADE}:offset={off:.3f}[v{k}]")
        prev = f"[v{k}]"
    run([*inputs, "-filter_complex", ";".join(parts) + f";{prev}format=yuv420p[out]", "-map", "[out]",
         "-c:v", "libx264", "-qp", "0", "-preset", "ultrafast", str(WORK / "master.mp4")])
    (HERE / "cuts.json").write_text(json.dumps([[c, s[4], s[5]] for c, s in zip(cuts, S)], ensure_ascii=False) + "\n")
    print("master ready; cut points in tools/reel/cuts.json")


CROPS = {"wide": "crop=1920:816:0:80,scale=1600:680:flags=lanczos", "phone": "crop=642:856:639:40"}
CODECS = {
    # film-grain-denoise=1 matters: without it AV1 spends its bits encoding phone-camera noise (18 MB).
    "av1": ["-c:v", "libsvtav1", "-preset", "5", "-crf", "{av1}", "-g", "240", "-pix_fmt", "yuv420p10le",
            "-svtav1-params", "tune=0:film-grain=10:film-grain-denoise=1"],
    "hevc": ["-c:v", "libx265", "-preset", "slow", "-crf", "{hevc}", "-tag:v", "hvc1", "-pix_fmt", "yuv420p",
             "-x265-params", "log-level=error:aq-mode=3"],
    "h264": ["-c:v", "libx264", "-preset", "slow", "-tune", "film", "-crf", "{h264}", "-profile:v", "high", "-pix_fmt", "yuv420p"],
}
# Calibrated 2026-09-16 on an 8 s grass-and-foliage slice against the lossless master (SSIM Y):
# av1 40 = 0.962 with synthesized grain (visually equal to the master at 100%), hevc 29 = 0.968,
# h264 27 = 0.965. At 1920 wide those gave 8.1 / 9.9 / 12.5 MB and 4-6 MB on phones, too heavy; the
# final trades 1920 for 1600 wide (gentler than stronger compression) and compresses the phone crop harder.
QUALITY = {"wide": {"av1": 42, "hevc": 30, "h264": 28}, "phone": {"av1": 46, "hevc": 32, "h264": 30}}


def encode(only=None):
    OUT.mkdir(parents=True, exist_ok=True)
    for crop, vf in CROPS.items():
        base = f"setpts={SLOW}*PTS,{vf}"
        for codec, args in CODECS.items():
            if only and codec not in only:
                continue
            q = QUALITY[crop]
            run(["-i", str(WORK / "master.mp4"), "-an", "-vf", base, "-r", FPS_OUT,
                 *[a.format(**q) for a in args], "-movflags", "+faststart", str(OUT / f"reel-{crop}.{codec}.mp4")])
            print("wrote", f"reel-{crop}.{codec}.mp4", round((OUT / f"reel-{crop}.{codec}.mp4").stat().st_size / 1e6, 2), "MB")
        run(["-ss", "1.5", "-i", str(WORK / "master.mp4"), "-frames:v", "1", "-vf", vf, str(WORK / f"poster-{crop}.png")])


if __name__ == "__main__":
    stage = sys.argv[sys.argv.index("--stage") + 1] if "--stage" in sys.argv else "all"
    if stage in ("master", "all"):
        master(sys.argv[1])
    if stage in ("encode", "all"):
        encode()
