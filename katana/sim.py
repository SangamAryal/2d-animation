"""Katana ball sim: a spinning katana inside a ring; every ball it cuts splits in two.

Deterministic for a given config + seed. Produces per-frame snapshots used by
render.py (pictures) and audio.py (sound).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from numba import njit


@dataclass
class SimConfig:
    fps: int = 60
    substeps: int = 8
    ring_radius: float = 470.0
    ball_radius: float = 9.0
    gravity: float = 2200.0          # px/s^2, straight down
    wall_restitution: float = 0.96
    # cutter: a set of blades sharing one pivot. Each blade is (angle offset, start, end)
    # measured along its direction from the pivot; start < 0 gives a handle on the far side.
    blades: tuple = ((0.0, -95.0, 455.0),)
    cut_from: float = 12.0           # cuts only happen past this distance from the pivot
    blade_half_width: float = 5.0
    spin_start: float = 1.0          # revolutions per second
    spin_end: float = 1.6
    spin_ramp: float = 30.0          # seconds to reach spin_end
    # moving cutter (pivot falls and bounces around the ring like a heavy ball)
    pivot_moves: bool = False
    pivot_radius: float = 0.0        # collision radius of the moving cutter vs. the ring
    pivot_start: tuple = (0.0, 0.0)
    pivot_vel: tuple = (0.0, 0.0)
    split_into: int = 2              # pieces per cut
    cut_cooldown: float = 1.4        # seconds a new ball is immune to cuts (and passes through)
    split_kick: float = 380.0        # px/s pushing halves apart
    # wall splitting + black hole (used by the black-hole scenario)
    wall_split: bool = False
    wall_split_speed: float = 300.0  # min impact speed that splits a ball on the wall
    hole_radius: float = 0.0         # 0 = no hole
    hole_growth: float = 0.0         # area of each eaten ball added to the hole, as a fraction
    hole_pull: float = 0.0           # px/s^2 pull toward the hole (replaces gravity)
    swirl_drag: float = 0.0          # 1/s drag on sideways speed around the hole
    max_balls: int = 2200
    min_balls_end: bool = False      # end when every ball is gone
    hold_after_full: float = 3.0     # seconds to keep running after the end condition
    max_seconds: float = 75.0
    seed: int = 7
    start_balls: tuple = ((130.0, -260.0, -260.0, 0.0),)   # x, y, vx, vy


@njit(cache=True)
def _collide(x, y, n, r, iters, cell, gw, off, head, nxt):
    d2min = (2 * r) * (2 * r)
    for _ in range(iters):
        for i in range(gw * gw):
            head[i] = -1
        for i in range(n):
            cx = int((x[i] + off) / cell)
            cy = int((y[i] + off) / cell)
            cx = min(max(cx, 0), gw - 1)
            cy = min(max(cy, 0), gw - 1)
            k = cy * gw + cx
            nxt[i] = head[k]
            head[k] = i
        for i in range(n):
            cx = int((x[i] + off) / cell)
            cy = int((y[i] + off) / cell)
            cx = min(max(cx, 0), gw - 1)
            cy = min(max(cy, 0), gw - 1)
            for oy in range(-1, 2):
                yy = cy + oy
                if yy < 0 or yy >= gw:
                    continue
                for ox in range(-1, 2):
                    xx = cx + ox
                    if xx < 0 or xx >= gw:
                        continue
                    j = head[yy * gw + xx]
                    while j != -1:
                        if j > i:
                            dx = x[j] - x[i]
                            dy = y[j] - y[i]
                            d2 = dx * dx + dy * dy
                            if d2 < d2min and d2 > 1e-9:
                                d = math.sqrt(d2)
                                p = 0.5 * (2 * r - d) / d
                                x[i] -= dx * p
                                y[i] -= dy * p
                                x[j] += dx * p
                                y[j] += dy * p
                        j = nxt[j]


def simulate(cfg: SimConfig):
    rng = np.random.default_rng(cfg.seed)
    cap = cfg.max_balls + 256
    x = np.zeros(cap); y = np.zeros(cap)
    vx = np.zeros(cap); vy = np.zeros(cap)
    gen = np.zeros(cap, np.int32)
    cool = np.zeros(cap)
    n = 0
    for (bx, by, bvx, bvy) in cfg.start_balls:
        x[n], y[n], vx[n], vy[n] = bx, by, bvx, bvy
        n += 1

    r = cfg.ball_radius
    R = cfg.ring_radius
    cell = 2 * r
    gw = int(math.ceil(2 * R / cell)) + 2
    off = R + cell
    head = np.full(gw * gw, -1, np.int64)
    nxt = np.full(cap, -1, np.int64)

    dt = 1.0 / (cfg.fps * cfg.substeps)
    angle = math.pi
    pvx_, pvy_ = cfg.pivot_vel
    pxp, pyp = cfg.pivot_start
    hole_r = cfg.hole_radius
    t = 0.0
    end_at = None
    end_kind = None
    eaten_total = 0

    out = dict(pos=[], gen=[], angle=[], omega=[], pivot=[], hole=[], cuts=[], bounces=[], eats=[], eaten=[])

    total_frames = int(cfg.max_seconds * cfg.fps)
    for f in range(total_frames):
        cuts, bounces, eats = [], [], []
        prog = min(1.0, t / cfg.spin_ramp)
        spin = cfg.spin_start + (cfg.spin_end - cfg.spin_start) * prog * prog
        omega = -2 * math.pi * spin
        for _ in range(cfg.substeps):
            t += dt
            angle += omega * dt
            # moving cutter
            if cfg.pivot_moves:
                pvy_ += cfg.gravity * dt
                pxp += pvx_ * dt; pyp += pvy_ * dt
                pd = math.hypot(pxp, pyp)
                lim = R - cfg.pivot_radius
                if pd > lim:
                    nx_, ny_ = pxp / pd, pyp / pd
                    pxp, pyp = nx_ * lim, ny_ * lim
                    vn = pvx_ * nx_ + pvy_ * ny_
                    if vn > 0:
                        pvx_ -= 2 * vn * nx_; pvy_ -= 2 * vn * ny_
                        bounces.append(vn * 0.5)
            m = slice(0, n)
            if cfg.gravity and not cfg.hole_pull:
                vy[m] += cfg.gravity * dt
            if cfg.hole_pull:
                d = np.hypot(x[m], y[m]) + 1e-6
                ux, uy = x[m] / d, y[m] / d
                vx[m] -= ux * cfg.hole_pull * dt
                vy[m] -= uy * cfg.hole_pull * dt
                # tangential drag so orbits decay and balls spiral into the hole
                vt = -vx[m] * uy + vy[m] * ux
                vx[m] -= -uy * vt * cfg.swirl_drag * dt
                vy[m] -= ux * vt * cfg.swirl_drag * dt
            xp = x[m].copy(); yp = y[m].copy()
            x[m] += vx[m] * dt
            y[m] += vy[m] * dt
            _collide(x, y, n, r, 2, cell, gw, off, head, nxt)

            new_balls = []
            for (aoff, b0, b1) in cfg.blades:
                ca, sa = math.cos(angle + aoff), math.sin(angle + aoff)
                rx = x[:n] - pxp; ry = y[:n] - pyp
                s = rx * ca + ry * sa
                s_cl = np.clip(s, b0, b1)
                qx = rx - s_cl * ca; qy = ry - s_cl * sa
                dist = np.hypot(qx, qy)
                hit = np.nonzero(dist < r + cfg.blade_half_width)[0]
                for i in hit:
                    if cool[i] > 0:
                        continue  # freshly cut balls pass through the blade
                    d = dist[i] if dist[i] > 1e-6 else 1e-6
                    nx_, ny_ = qx[i] / d, qy[i] / d
                    surf_vx = -omega * s_cl[i] * sa + (pvx_ if cfg.pivot_moves else 0)
                    surf_vy = omega * s_cl[i] * ca + (pvy_ if cfg.pivot_moves else 0)
                    can_cut = (abs(s[i]) > cfg.cut_from and n + len(new_balls) + cfg.split_into <= cfg.max_balls
                               and end_at is None)
                    if can_cut:
                        g = gen[i] + 1
                        bx, by = x[i], y[i]
                        pad = r + cfg.blade_half_width + 0.5
                        cx_, cy_ = pxp + s_cl[i] * ca, pyp + s_cl[i] * sa
                        k = cfg.split_into
                        # piece 0 reuses ball i on the near side; others fan out on the far side
                        x[i] = cx_ + nx_ * pad; y[i] = cy_ + ny_ * pad
                        jx = rng.normal() * 40
                        vx[i] = surf_vx * 0.8 + nx_ * cfg.split_kick + ca * jx
                        vy[i] = surf_vy * 0.8 + ny_ * cfg.split_kick + sa * jx
                        gen[i] = g; cool[i] = cfg.cut_cooldown
                        for p in range(1, k):
                            along = (p - (k) / 2.0) * 2.2 * r if k > 2 else 0.0
                            ex = cx_ - nx_ * pad + ca * along
                            ey = cy_ - ny_ * pad + sa * along
                            spread = (p - k / 2.0) * 0.6 * cfg.split_kick if k > 2 else 0.0
                            new_balls.append((ex, ey,
                                              surf_vx * 0.8 - nx_ * cfg.split_kick + ca * spread,
                                              surf_vy * 0.8 - ny_ * cfg.split_kick + sa * spread, g))
                        cuts.append((bx, by, g))
                    else:
                        push = r + cfg.blade_half_width - d
                        x[i] += nx_ * push; y[i] += ny_ * push
                        rel = (vx[i] - surf_vx) * nx_ + (vy[i] - surf_vy) * ny_
                        if rel < 0:
                            vx[i] -= rel * nx_ * 1.15; vy[i] -= rel * ny_ * 1.15
            # moving cutter body pushes balls (hub)
            if cfg.pivot_moves and cfg.pivot_radius > 0:
                rx = x[:n] - pxp; ry = y[:n] - pyp
                dd = np.hypot(rx, ry) + 1e-6
                hub = cfg.pivot_radius * 0.35
                inside = np.nonzero(dd < hub + r)[0]
                for i in inside:
                    nx_, ny_ = rx[i] / dd[i], ry[i] / dd[i]
                    x[i] = pxp + nx_ * (hub + r); y[i] = pyp + ny_ * (hub + r)
                    vn = (vx[i] - pvx_) * nx_ + (vy[i] - pvy_) * ny_
                    if vn < 0:
                        vx[i] -= 1.5 * vn * nx_; vy[i] -= 1.5 * vn * ny_

            for (bx, by, bvx, bvy, g) in new_balls:
                x[n], y[n], vx[n], vy[n], gen[n], cool[n] = bx, by, bvx, bvy, g, cfg.cut_cooldown
                n += 1
            m = slice(0, n)

            k = len(xp)
            vx[:k] = 0.5 * vx[:k] + 0.5 * (x[:k] - xp) / dt
            vy[:k] = 0.5 * vy[:k] + 0.5 * (y[:k] - yp) / dt

            # ring wall
            dd = np.hypot(x[m], y[m])
            outside = np.nonzero(dd > R - r)[0]
            wall_new = []
            for i in outside:
                nx_, ny_ = x[i] / dd[i], y[i] / dd[i]
                x[i], y[i] = nx_ * (R - r), ny_ * (R - r)
                vn = vx[i] * nx_ + vy[i] * ny_
                if vn > 0:
                    e = cfg.wall_restitution if (n < 40 or cfg.wall_split) else 0.35
                    vx[i] -= (1 + e) * vn * nx_
                    vy[i] -= (1 + e) * vn * ny_
                    if n >= 40 and not cfg.wall_split:
                        vt = -vx[i] * ny_ + vy[i] * nx_
                        vx[i] -= -ny_ * vt * 0.08
                        vy[i] -= nx_ * vt * 0.08
                    if (cfg.wall_split and vn > cfg.wall_split_speed and cool[i] <= 0 and end_at is None
                            and n + len(wall_new) < cfg.max_balls):
                        g = gen[i] + 1
                        tx, ty = -ny_, nx_
                        sp = math.hypot(vx[i], vy[i])
                        # two halves leave the wall in a V
                        for sgn, idx in ((1, i), (-1, None)):
                            ang = math.atan2(vy[i], vx[i]) + sgn * 0.35
                            nvx, nvy = sp * math.cos(ang), sp * math.sin(ang)
                            px_ = x[i] + tx * sgn * r * 1.05; py_ = y[i] + ty * sgn * r * 1.05
                            if idx is None:
                                wall_new.append((px_, py_, nvx, nvy, g))
                            else:
                                x[i], y[i], vx[i], vy[i] = px_, py_, nvx, nvy
                        gen[i] = g; cool[i] = cfg.cut_cooldown
                        cuts.append((x[i], y[i], g))
                    elif n < 24 and vn > 250:
                        bounces.append(vn)
            for (bx, by, bvx, bvy, g) in wall_new:
                x[n], y[n], vx[n], vy[n], gen[n], cool[n] = bx, by, bvx, bvy, g, cfg.cut_cooldown
                n += 1

            # black hole eats
            if hole_r > 0 and n:
                dd = np.hypot(x[:n], y[:n])
                eat = dd < hole_r + r * 0.2
                if eat.any():
                    ids = np.nonzero(eat)[0]
                    for i in ids[:4]:
                        eats.append((x[i], y[i], gen[i]))
                    ne = int(eat.sum())
                    eaten_total += ne
                    hole_r = math.sqrt(hole_r ** 2 + cfg.hole_growth * ne * r * r)
                    keep = np.nonzero(~eat)[0]
                    nk = len(keep)
                    for arr in (x, y, vx, vy, cool):
                        arr[:nk] = arr[keep]
                    gen[:nk] = gen[keep]
                    n = nk
            cool[:n] -= dt

        if end_at is None and n >= cfg.max_balls - cfg.split_into:
            end_at, end_kind = t, "full"
        if end_at is None and cfg.min_balls_end and n == 0:
            end_at, end_kind = t, "empty"
        out["pos"].append(np.stack([x[:n], y[:n]], 1).astype(np.float32))
        out["gen"].append(gen[:n].astype(np.int16).copy())
        out["angle"].append(angle)
        out["omega"].append(omega)
        out["pivot"].append((pxp, pyp))
        out["hole"].append(hole_r)
        out["cuts"].append(cuts)
        out["bounces"].append(bounces)
        out["eats"].append(eats)
        out["eaten"].append(eaten_total)
        if end_at is not None and t - end_at >= cfg.hold_after_full:
            break
    if end_at is None:
        end_kind = "time"
    out["angle"] = np.array(out["angle"]); out["omega"] = np.array(out["omega"])
    out["full_frame"] = None if end_at is None else int(end_at * cfg.fps)
    out["end_kind"] = end_kind
    out["cfg"] = cfg
    return out


if __name__ == "__main__":
    import sys
    import time
    from scenarios import SCENARIOS
    name = sys.argv[1] if len(sys.argv) > 1 else "katana"
    t0 = time.time()
    o = simulate(SCENARIOS[name].sim)
    counts = [len(p) for p in o["pos"]]
    print(name, "frames", len(counts), "secs", round(len(counts) / 60, 1), "end", o["end_kind"], o["full_frame"],
          "time", round(time.time() - t0, 1))
    print(" ".join(f"{s // 60}s:{counts[s]}" for s in range(0, len(counts), 120)))
