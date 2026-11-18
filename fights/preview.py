"""Fast review sheets: render a span of video frames to one contact-sheet PNG
(no audio, no encode), or a short silent MP4 clip.

python3 fights/preview.py --fight scythe --t0 2.6 --t1 3.6 --every 2 --out sheet.png
python3 fights/preview.py --fight scythe --t0 2.6 --t1 3.6 --clip clip.mp4
    --frames 160,161,162   exact frame numbers instead of a span
    --cols 6 --cell 300    sheet layout; --crop y0,y1 keeps a band (fractions of H)
    --onion                also draw the previous 2 frames faintly (spacing check)
"""
import argparse
import os
import subprocess
import sys

import numpy as np
import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import FPS, Renderer  # noqa: E402


def frame_image(r, surf, i):
    c = surf.getCanvas()
    r.render_frame(c, i)
    return surf.makeImageSnapshot()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fight", default="scythe")
    ap.add_argument("--t0", type=float, default=0)
    ap.add_argument("--t1", type=float, default=1)
    ap.add_argument("--every", type=int, default=2)
    ap.add_argument("--frames", default="")
    ap.add_argument("--out")
    ap.add_argument("--clip")
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--cell", type=int, default=300)
    ap.add_argument("--crop", default="0.30,0.72")
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--onion", action="store_true")
    ap.add_argument("--classic", action="store_true")
    a = ap.parse_args()
    r = Renderer(fight=a.fight, scale=a.scale, classic=a.classic)
    W, H = r.W, r.H
    if a.frames:
        idx = [int(x) for x in a.frames.split(",")]
    else:
        idx = list(range(int(a.t0 * FPS), min(r.n, int(a.t1 * FPS)), a.every if not a.clip else 1))
    surf = skia.Surface(W, H)
    if a.clip:
        p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                              "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                              "-crf", "20", "-pix_fmt", "yuv420p", a.clip], stdin=subprocess.PIPE)
        for i in idx:
            p.stdin.write(frame_image(r, surf, i).toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
        p.stdin.close()
        p.wait()
        print("wrote", a.clip, len(idx), "frames")
        return
    y0, y1 = (float(v) for v in a.crop.split(","))
    ch = int((y1 - y0) * H)
    cw = a.cell
    chh = int(ch * cw / W)
    rows = (len(idx) + a.cols - 1) // a.cols
    sheet = skia.Surface(cw * a.cols, chh * rows)
    sc = sheet.getCanvas()
    sc.clear(skia.Color4f(1, 1, 1, 1))
    font = skia.Font(None, 14)
    for n, i in enumerate(idx):
        img = frame_image(r, surf, i)
        if a.onion:
            ghost = skia.Surface(W, H)
            gimgs = [frame_image(r, ghost, max(0, i - k)) for k in (2, 1)]
            img2 = skia.Surface(W, H)
            c2 = img2.getCanvas()
            c2.drawImage(img, 0, 0)
            for g, al in zip(gimgs, (0.18, 0.3)):
                c2.drawImage(g, 0, 0, skia.SamplingOptions(), skia.Paint(Alphaf=al))
            img = img2.makeImageSnapshot()
        x, y = (n % a.cols) * cw, (n // a.cols) * chh
        sc.drawImageRect(img, skia.Rect(0, y0 * H, W, y1 * H), skia.Rect(x, y, x + cw, y + chh),
                         skia.SamplingOptions(skia.FilterMode.kLinear))
        sc.drawString(f"{i} ({i / FPS:.2f}s)", x + 4, y + 15, font, skia.Paint(Color=skia.ColorRED))
    sheet.makeImageSnapshot().save(a.out)
    print("wrote", a.out, len(idx), "frames")


if __name__ == "__main__":
    main()
