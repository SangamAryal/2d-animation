"""Animation quality review: measures motion problems frame by frame.

python3 fights/qc.py --fight scythe [--json OUT.json] [--top 12]

Works on the solved joints of every rendered frame (same time map as the
renderer, so hit-stops and slow-mo are included), without drawing anything.
Units are world units (a fighter is ~160 tall; 1 unit ~ 1.4 px at 1080x1920).

Checks
  pops         a joint jumps far more in one frame than it moved the frame
               before and after (sudden position jumps, missing in-betweens)
  hip_jerk     hip acceleration spikes outside impacts (robotic starts/stops)
  facing_pops  the whole figure mirrors in a single frame
  knee_rev     knee bent backwards (fraction of frames) and knee side flips
  elbow_hyper  elbow bent past straight the wrong way by > 15 deg
  grip_err     two-handed grip: back hand further than 3 units from the shaft
  foot_slide   a foot on the ground skating more than 1.5 units per frame
  ground       any joint below the ground line
  bone_var     torso/limb length change vs rest (proportion consistency)
  dead_holds   runs of frames where nothing moves at all (outside hit-stops)
  air_bumps    vertical hip direction reversals while airborne (flips that
               bounce instead of following one arc)
"""
import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rig import L_FARM, L_SHIN, L_THIGH, L_TORSO, L_UARM  # noqa: E402

FPS = 60
KEYS = ["hip", "neck", "head", "elf", "haf", "elb", "hab", "knf", "ftf", "knb", "ftb", "tip"]


def _ang(v):
    return math.degrees(math.atan2(v[0], v[1]))


def _rel_bend(J, a, b, c, fc):
    """Signed bend at joint b (degrees). Positive = toward the figure's front."""
    u = (J[b][0] - J[a][0], J[b][1] - J[a][1])
    w = (J[c][0] - J[b][0], J[c][1] - J[b][1])
    cr = u[0] * w[1] - u[1] * w[0]
    dt = u[0] * w[0] + u[1] * w[1]
    return math.degrees(math.atan2(cr, dt)) * (1 if fc > 0 else -1)


def collect(fight_name, fight=None, classic=False):
    import render
    from render import Fight, build_timemap
    f = fight or Fight(fight_name, classic=classic)
    frames = build_timemap(f.ev, f.end)
    stops = set()
    for i in range(1, len(frames)):
        if frames[i] == frames[i - 1]:
            stops.add(i)
    hits = []
    for t, k, kw in f.ev:
        if k in ("hit", "clash", "decap", "dmg", "armor", "shieldhit", "kill"):
            hits.append(render.video_time(frames, t))
    data = {}
    for who in f.ids:
        rows = []
        for t in frames:
            J = f.joints(who, t)
            rows.append(J)
        data[who] = rows
    return f, frames, stops, hits, data


def analyse(f, frames, stops, hits, data):
    n = len(frames)
    near_hit = np.zeros(n, bool)
    for vt in hits:
        i = int(vt * FPS)
        near_hit[max(0, i - 3):min(n, i + 10)] = True
    rep = {}
    for who, rows in data.items():
        st = f.tracks[who][1]
        S = st.get("size", 1.0)
        P = {k: np.array([r[k] for r in rows]) for k in KEYS}
        hidden = np.array([r["p"].get("hidden", 0) > 0.5 for r in rows])
        fc = np.array([r["facing"] for r in rows])
        fxs = np.array([r.get("fx", r["facing"]) for r in rows])
        turning = np.abs(fxs) < 0.999      # mid-turn in-betweens are foreshortened on purpose
        r_ = {}
        # ---- pops: one-frame jump much larger than neighbours, body-relative
        pops = []
        for k in KEYS[1:]:
            rel = P[k] - P["hip"]
            dv = np.linalg.norm(np.diff(rel, axis=0), axis=1)        # i -> i+1
            for i in range(2, len(dv) - 2):
                if hidden[i] or hidden[i + 1] or fc[i] != fc[i + 1] or turning[i] or turning[i + 1]:
                    continue
                nb = max(dv[i - 1], dv[i + 1], 1.0)
                if dv[i] > 18 * S and dv[i] > 2.6 * nb:
                    pops.append((round((i + 1) / FPS, 3), k, round(float(dv[i]), 1)))
        r_["pops"] = pops
        # ---- hip jerk outside impacts
        hv = np.diff(P["hip"], axis=0)
        ha = np.linalg.norm(np.diff(hv, axis=0), axis=1)
        jerk = []
        for i in range(len(ha)):
            if near_hit[i + 1] or (i + 1) in stops or (i + 2) in stops or hidden[i + 1]:
                continue
            if fc[i] != fc[i + 2]:
                continue
            if ha[i] > 9 * S:
                jerk.append((round((i + 1) / FPS, 3), round(float(ha[i]), 1)))
        r_["hip_jerk"] = jerk
        # ---- facing pops
        flips = [round(i / FPS, 3) for i in range(1, n) if abs(fxs[i] - fxs[i - 1]) > 1.0]
        r_["facing_pops"] = flips
        # ---- knees / elbows
        krev, kflip, ehyp = 0, [], 0
        prev = {}
        for i, J in enumerate(rows):
            if hidden[i]:
                continue
            sgn = 1 if J["facing"] >= 0 else -1
            for s in "fb":
                b = _rel_bend(J, "hip", "kn" + s, "ft" + s, sgn)
                # knee forward = shin rotates back relative to thigh = negative bend
                rev = b > 8
                krev += rev
                if s in prev and prev[s] != rev and abs(b) > 20:
                    kflip.append((round(i / FPS, 3), s))
                prev[s] = rev
            for s, (a, e, h) in (("f", ("sho", "elf", "haf")), ("b", ("sho", "elb", "hab"))):
                b = _rel_bend(J, a, e, h, sgn)
                if b < -15:
                    ehyp += 1
        r_["knee_rev_frac"] = round(krev / (2 * n), 3)
        r_["knee_flips"] = kflip
        r_["elbow_hyper_frac"] = round(ehyp / (2 * n), 3)
        # ---- grip error (back hand off the shaft)
        ge = []
        for i, J in enumerate(rows):
            if J["p"].get("grip", 0) < 0.9 or hidden[i]:
                continue
            a, b = np.array(J["hilt0"]), np.array(J["tip"])
            h = np.array(J["hab"])
            ab = b - a
            u = np.clip(np.dot(h - a, ab) / max(1e-6, np.dot(ab, ab)), 0, 1)
            dist = float(np.linalg.norm(a + ab * u - h))
            if dist > 3 * S:
                ge.append(dist)
        r_["grip_err_frames"] = len(ge)
        r_["grip_err_max"] = round(max(ge), 1) if ge else 0.0
        # ---- foot slide: foot on the ground in both frames, moving sideways
        slide = 0
        worst = 0.0
        for s in "fb":
            ft = P["ft" + s]
            for i in range(1, n):
                if hidden[i] or (i in stops):
                    continue
                if ft[i][1] < 5.5 * S and ft[i - 1][1] < 5.5 * S:
                    dx = abs(ft[i][0] - ft[i - 1][0])
                    if dx > 1.5 * S:
                        slide += 1
                        worst = max(worst, dx)
        r_["foot_slide_frames"] = slide
        r_["foot_slide_max"] = round(worst, 1)
        # ---- ground penetration
        low = min(float(P[k][~hidden, 1].min()) for k in KEYS if k != "tip")
        r_["lowest_joint"] = round(low, 1)
        # ---- proportions (torso and limb lengths)
        var = {}
        for name, (a, b, L) in dict(torso=("hip", "neck", L_TORSO), uarm=("sho", "elf", L_UARM),
                                    uarm_b=("sho", "elb", L_UARM), farm_b=("elb", "hab", L_FARM),
                                    farm=("elf", "haf", L_FARM), thigh=("hip", "knf", L_THIGH),
                                    shin=("knf", "ftf", L_SHIN)).items():
            ls = [math.dist(J[a], J[b]) / (L * S) for J, h, tn in zip(rows, hidden, turning)
                  if not h and not tn]
            var[name] = (round(min(ls), 3), round(max(ls), 3))
        r_["bone_ratio_range"] = var
        # ---- dead holds: >= 10 frames with nothing moving, not in hit-stop
        allp = np.concatenate([P[k] for k in KEYS], axis=1)
        mv = np.abs(np.diff(allp, axis=0)).max(axis=1)
        dead, run, holds = 0, 0, []
        for i, m in enumerate(mv):
            if m < 0.05 and (i + 1) not in stops and not hidden[i]:
                run += 1
            else:
                if run >= 10:
                    holds.append((round((i - run) / FPS, 2), run))
                run = 0
        r_["dead_holds"] = holds
        # ---- airborne bumps
        hy = P["hip"][:, 1]
        air = np.array([max(J["ftf"][1], 0) > 8 * S and J["ftb"][1] > 8 * S for J in rows])
        bumps = []
        dy = np.diff(hy)
        for i in range(1, len(dy)):
            if air[i] and air[i + 1] and air[i - 1] and i not in stops and (i + 1) not in stops:
                if dy[i - 1] < -0.4 and dy[i] > 0.4:      # was falling, now rising, mid-air
                    bumps.append(round(i / FPS, 3))
        r_["air_bumps"] = bumps
        rep[who] = r_
    return rep


def summary(rep):
    out = {}
    for who, r in rep.items():
        out[who] = dict(
            pops=len(r["pops"]), hip_jerk=len(r["hip_jerk"]), facing_pops=len(r["facing_pops"]),
            knee_rev_frac=r["knee_rev_frac"], knee_flips=len(r["knee_flips"]),
            elbow_hyper_frac=r["elbow_hyper_frac"], grip_err_frames=r["grip_err_frames"],
            grip_err_max=r["grip_err_max"], foot_slide_frames=r["foot_slide_frames"],
            foot_slide_max=r["foot_slide_max"], lowest_joint=r["lowest_joint"],
            dead_holds=len(r["dead_holds"]), air_bumps=len(r["air_bumps"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fight", default="scythe")
    ap.add_argument("--json")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--classic", action="store_true")
    a = ap.parse_args()
    rep = analyse(*collect(a.fight, classic=a.classic))
    sm = summary(rep)
    for who, s in sm.items():
        print(who, json.dumps(s))
        r = rep[who]
        print("   worst pops:", sorted(r["pops"], key=lambda q: -q[2])[:a.top])
        print("   hip jerk  :", sorted(r["hip_jerk"], key=lambda q: -q[1])[:a.top])
        print("   facing    :", r["facing_pops"])
        print("   air bumps :", r["air_bumps"][:a.top])
        print("   holds     :", r["dead_holds"][:a.top])
        print("   bones     :", r["bone_ratio_range"])
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(dict(summary=sm, detail=rep), fh, indent=1)


if __name__ == "__main__":
    main()
