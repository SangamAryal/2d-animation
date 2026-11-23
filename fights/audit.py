"""Whole-fight audit: checks every frame for things that look wrong on screen,
not only the contact windows.

python3 fights/audit.py --fight cliff

Flags (story time, video time):
  HANDS    a clash whose contact point sits near a hand (must be blade on blade)
  THROUGH  a blade passing through the other fighter's body or limbs with no
           hit / decap / kill event near that moment
  WEAPONS  the two weapons crossing outside any clash / lock window
  CLOSE    hips closer than --close units (bodies overlapping, or standing
           inside the other's reach doing nothing)
and a table of every contact with the hip distance and the reach of each
fighter, so strike spacing can be checked: the long weapon should strike from
near its full reach, the short one only once it has closed in.
"""
import argparse
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import contact  # noqa: E402
from render import FPS, Renderer, video_time  # noqa: E402

LIMBS = (("hip", "neck"), ("neck", "head"), ("hip", "knf"), ("knf", "ftf"),
         ("hip", "knb"), ("knb", "ftb"), ("sho", "elf"), ("sho", "elb"))


def dseg(a, b):
    return contact._seg_seg(a[0], a[1], b[0], b[1])[0]


def runs(frames, gap=2):
    """Group sorted frame indices into (first, last) runs."""
    out = []
    for fi in frames:
        if out and fi - out[-1][1] <= gap:
            out[-1][1] = fi
        else:
            out.append([fi, fi])
    return out


def reach(J, st):
    """How far in front of the hips this fighter's weapon end reaches now."""
    segs = contact.weapon_segs(J, st)
    if not segs:
        return 0.0
    return max(abs(s[1][0] - J["hip"][0]) for s in segs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fight", default="cliff")
    ap.add_argument("--close", type=float, default=70)
    ap.add_argument("--hand", type=float, default=24)
    ap.add_argument("--win", type=float, default=0.10, help="event window (story s)")
    a = ap.parse_args()
    r = Renderer(fight=a.fight, scale=0.25)
    f = r.f
    ids = f.ids
    if len(ids) != 2:
        print("audit: two-fighter fights only")
        return
    st = {w: f.tracks[w][1] for w in ids}
    hits = [(t, kw.get("by")) for t, k, kw in f.ev if k in ("hit", "decap", "kill")]
    clashes = [t for t, k, kw in f.ev if k in ("clash", "lock", "scrape")]
    # deliberate pass-bys (a dive under the swing, a leap over him)
    passes = [(t, t + kw.get("dur", 0.4)) for t, k, kw in f.ev if k == "pass"]
    bad = {"HANDS": [], "THROUGH": [], "WEAPONS": [], "CLOSE": []}
    why = {}
    seen = set()
    for fi, t in enumerate(r.frames):
        if t in seen:
            continue
        seen.add(t)
        J = {w: f.joints(w, t) for w in ids}
        if any(p0 <= t <= p1 for p0, p1 in passes):
            continue
        for att in ids:
            vic = ids[1] if att == ids[0] else ids[0]
            if not any(abs(t - th) < a.win * 2 and (by in (att, None)) for th, by in hits):
                for s in contact.weapon_segs(J[att], st[att]):
                    if not s[2]:
                        continue
                    for p, q in LIMBS:
                        if J[vic]["p"].get("headless", 0) > 0.5 and q == "head":
                            continue
                        if dseg((s[0], s[1]), (J[vic][p], J[vic][q])) < 4:
                            bad["THROUGH"].append(fi)
                            why[("THROUGH", fi)] = f"{att} blade through {vic} {p}-{q}"
                            break
        if not any(-a.win < t - tc < 0.25 for tc in clashes):   # a bind may hold briefly
            sa = contact.clash_segs(J[ids[0]], st[ids[0]])
            sb = contact.clash_segs(J[ids[1]], st[ids[1]])
            if sa and sb and contact.gap(sa, sb)[0] < 3:
                bad["WEAPONS"].append(fi)
                pt = contact.gap(sa, sb)[1]
                why[("WEAPONS", fi)] = f"at ({pt[0]:.0f},{pt[1]:.0f})"
        dx = abs(J[ids[0]]["hip"][0] - J[ids[1]]["hip"][0])
        dy = abs(J[ids[0]]["hip"][1] - J[ids[1]]["hip"][1])
        if dx < a.close and dy < 80 and not any(abs(t - th) < a.win for th, _ in hits):
            bad["CLOSE"].append(fi)
            why[("CLOSE", fi)] = f"dx={dx:.0f}"
    print(f"== contacts ({a.fight}) ==")
    print(" story  video  kind    by/pair     hip dx   dy  reachA reachB  hand-dist")
    for t, k, kw in f.ev:
        if k not in ("clash", "lock", "hit", "decap"):
            continue
        J = {w: f.joints(w, t) for w in ids}
        pa, pb = f.pair(k, kw)
        dx = J[pb]["hip"][0] - J[pa]["hip"][0]
        dy = J[pb]["hip"][1] - J[pa]["hip"][1]
        hand = ""
        if k in ("clash", "lock"):
            g, pt = contact.gap(*contact.shapes(f, k, kw, J[pa], J[pb], pa, pb), cross=False)
            dh = min(math.dist(pt, J[w][h]) for w in ids for h in ("haf", "hab"))
            hand = f"{dh:5.0f}  gap={g:.0f}"
            if dh < a.hand:
                bad["HANDS"].append(int(round(video_time(r.frames, t) * FPS)))
                why[("HANDS", bad["HANDS"][-1])] = f"clash {dh:.0f} from a hand"
        print(f"{t:6.2f} {video_time(r.frames, t):6.2f}  {k:6s}  {pa}->{pb}  {dx:8.0f} {dy:4.0f}"
              f"  {reach(J[pa], st[pa]):6.0f} {reach(J[pb], st[pb]):6.0f}  {hand}")
    n = 0
    for key, fr in bad.items():
        for f0, f1 in runs(sorted(set(fr))):
            n += 1
            print(f"{key:8s} video {f0 / FPS:6.2f}-{f1 / FPS:6.2f} s  story {r.frames[f0]:6.2f}"
                  f"  {why.get((key, f0), '')}")
    print(f"{n} flagged run(s)")


if __name__ == "__main__":
    main()
