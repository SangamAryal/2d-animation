"""Contact review sheets: for every clash / hit / kill / blade lock, render the
frames around it (before, on, after) in one row, so each contact can be
checked by eye: blades must cross, blows must land, sparks must sit on the
crossing.

python3 fights/review_contacts.py --fight scythe --out DIR [--before 6 --after 14 --step 2]
    writes DIR/contacts-1.png, contacts-2.png, ... (6 contacts per sheet)
python3 fights/review_contacts.py --fight scythe --video OUT.mp4 --out DIR
    same, but frames are pulled from a rendered video (what the viewer sees)
"""
import argparse
import os
import subprocess
import sys

import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import FPS, Renderer  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fight", default="scythe")
    ap.add_argument("--out", required=True)
    ap.add_argument("--video")
    ap.add_argument("--before", type=int, default=6)
    ap.add_argument("--after", type=int, default=14)
    ap.add_argument("--step", type=int, default=2)
    ap.add_argument("--per", type=int, default=6)
    ap.add_argument("--cell", type=int, default=230)
    ap.add_argument("--zoom", type=float, default=0,
                    help="crop this many px wide around each contact point (0 = whole band)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    r = Renderer(fight=a.fight, scale=1.0)
    W, H = r.W, r.H
    contacts = []
    for vt, k, d in r.fx:
        if k not in ("clash", "hit", "decap", "scrape"):
            continue
        fi = int(round(vt * FPS))
        pt = d.get("pt")
        if pt is None:
            J = r.f.joints(d.get("who", r.f.ids[0]), r.frames[fi])
            pt = J["neck"]
        cx, z = r.cams[fi]
        sx, sy = W / 2 + (pt[0] - cx) * z, r.gy - pt[1] * z
        contacts.append((fi, k, sx, sy))
    contacts.sort()
    offs = list(range(-a.before, a.after + 1, a.step))
    if a.video:
        # pull the windows straight out of the encoded video (what viewers see)
        tmp = os.path.join(a.out, "_v")
        os.makedirs(tmp, exist_ok=True)
        rows = []
        for n_, (fi, k, sx, sy) in enumerate(contacts):
            z = a.zoom or 600
            x0 = int(max(0, min(W - z, sx - z / 2)))
            y0_ = int(max(0, min(H - z, sy - z / 2)))
            start = max(0, fi - a.before)
            p = os.path.join(tmp, f"row{n_:02d}.png")
            vf = (f"select=between(n\\,{start}\\,{fi + a.after})*not(mod(n-{start}\\,{a.step})),"
                  f"crop={int(z)}:{int(z)}:{x0}:{y0_},scale={a.cell}:{a.cell},"
                  f"drawtext=fontfile=/usr/share/fonts/opentype/inter/Inter-Bold.otf:text='%{{n}}':x=4:y=4:fontsize=13:fontcolor=red,"
                  f"tile={len(offs)}x1")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-vf", vf,
                            "-vsync", "0", "-frames:v", "1", p], check=True)
            rows.append((p, fi, k))
        for si in range(0, len(rows), a.per):
            grp = rows[si:si + a.per]
            imgs = [skia.Image.open(p) for p, _, _ in grp]
            sheet = skia.Surface(max(i.width() for i in imgs), sum(i.height() + 18 for i in imgs))
            sc = sheet.getCanvas()
            sc.clear(skia.Color4f(1, 1, 1, 1))
            y = 0
            fnt = skia.Font(skia.Typeface("sans-serif"), 14)
            for img, (p, fi, k) in zip(imgs, grp):
                sc.drawString(f"{k} at frame {fi} ({fi / FPS:.2f}s): frames {fi - a.before}..{fi + a.after} step {a.step}",
                              4, y + 14, fnt, skia.Paint(Color=skia.ColorBLACK))
                sc.drawImage(img, 0, y + 18)
                y += img.height() + 18
            out = os.path.join(a.out, f"video-contacts-{si // a.per + 1}.png")
            sheet.makeImageSnapshot().save(out)
            print("wrote", out)
        return
    y0, y1 = 0.30, 0.66
    cw = a.cell
    ch = int((y1 - y0) * H * cw / W * 1.0)
    # crop the middle 70% of the width (fighters live there)
    x0f, x1f = 0.10, 0.90
    ch = int((y1 - y0) * H * cw / ((x1f - x0f) * W)) if not a.zoom else cw
    font = skia.Font(skia.Typeface("sans-serif"), 13)
    surf = skia.Surface(W, H)
    for si in range(0, len(contacts), a.per):
        grp = contacts[si:si + a.per]
        sheet = skia.Surface(cw * len(offs), (ch + 4) * len(grp))
        sc = sheet.getCanvas()
        sc.clear(skia.Color4f(1, 1, 1, 1))
        for row, (fi, k, sx, sy) in enumerate(grp):
            half = a.zoom / 2
            src = skia.Rect(sx - half, sy - half * ch / cw, sx + half, sy + half * ch / cw)
            for col_, o in enumerate(offs):
                i = min(r.n - 1, max(0, fi + o))
                if a.video:
                    png = os.path.join(a.out, "_f.png")
                    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.video, "-vf",
                                    f"select=eq(n\\,{i})", "-frames:v", "1", png], check=True)
                    img = skia.Image.open(png)
                else:
                    c = surf.getCanvas()
                    r.render_frame(c, i)
                    img = surf.makeImageSnapshot()
                x, y = col_ * cw, row * (ch + 4)
                sc.drawImageRect(img, src if a.zoom else skia.Rect(x0f * W, y0 * H, x1f * W, y1 * H),
                                 skia.Rect(x, y, x + cw, y + ch),
                                 skia.SamplingOptions(skia.FilterMode.kLinear))
                lab = f"{k} {i}" if o == 0 else f"{o:+d}"
                sc.drawString(lab, x + 3, y + 13, font,
                              skia.Paint(Color=skia.ColorRED if o == 0 else skia.ColorBLUE))
        p = os.path.join(a.out, f"contacts-{si // a.per + 1}.png")
        sheet.makeImageSnapshot().save(p)
        print("wrote", p)


if __name__ == "__main__":
    main()
