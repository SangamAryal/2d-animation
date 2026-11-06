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
    gravity: float = 2200.0          # px/s^2
    wall_restitution: float = 0.96
    blade_length: float = 455.0      # from pivot to tip
    blade_half_width: float = 5.0
    hilt_length: float = 95.0        # handle on the other side of the pivot
    spin_start: float = 1.0          # revolutions per second
    spin_end: float = 1.6
    cut_cooldown: float = 1.4        # seconds a new ball is immune to cuts
    split_kick: float = 380.0        # px/s pushing halves apart
    max_balls: int = 2200
    hold_after_full: float = 3.0     # seconds to keep running after the cap
    max_seconds: float = 75.0
    seed: int = 7
    start_pos: tuple = (130.0, -260.0)
    start_vel: tuple = (-260.0, 0.0)


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
    cap = cfg.max_balls + 64
    x = np.zeros(cap); y = np.zeros(cap)
    vx = np.zeros(cap); vy = np.zeros(cap)
    gen = np.zeros(cap, np.int32)
    cool = np.zeros(cap)
    x[0], y[0] = cfg.start_pos
    vx[0], vy[0] = cfg.start_vel
    n = 1

    r = cfg.ball_radius
    R = cfg.ring_radius
    cell = 2 * r
    gw = int(math.ceil(2 * R / cell)) + 2
    off = R + cell
    head = np.full(gw * gw, -1, np.int64)
    nxt = np.full(cap, -1, np.int64)

    dt = 1.0 / (cfg.fps * cfg.substeps)
    angle = math.pi  # blade starts pointing left
    t = 0.0
    full_at = None

    frames_pos, frames_gen, frames_angle, frames_omega = [], [], [], []
    frame_events = []   # per frame: list of (x, y, gen) cuts
    frame_bounces = []  # per frame: list of wall-hit speeds (only when few balls)

    total_frames = int(cfg.max_seconds * cfg.fps)
    for f in range(total_frames):
        cuts = []
        bounces = []
        prog = min(1.0, t / 30.0)
        spin = cfg.spin_start + (cfg.spin_end - cfg.spin_start) * prog * prog
        omega = -2 * math.pi * spin  # clockwise on screen (y down)
        for _ in range(cfg.substeps):
            t += dt
            angle += omega * dt
            ca, sa = math.cos(angle), math.sin(angle)
            m = slice(0, n)
            vy[m] += cfg.gravity * dt
            xp = x[m].copy(); yp = y[m].copy()
            x[m] += vx[m] * dt
            y[m] += vy[m] * dt
            _collide(x, y, n, r, 2, cell, gw, off, head, nxt)

            # blade: segment from -hilt to +blade along (ca, sa)
            px = x[m]; py = y[m]
            s = px * ca + py * sa
            s_cl = np.clip(s, -cfg.hilt_length, cfg.blade_length)
            qx = px - s_cl * ca; qy = py - s_cl * sa
            dist = np.hypot(qx, qy)
            hit = np.nonzero(dist < r + cfg.blade_half_width)[0]
            new_balls = []
            for i in hit:
                d = dist[i] if dist[i] > 1e-6 else 1e-6
                nx_, ny_ = qx[i] / d, qy[i] / d
                # side of blade: normal points from blade to ball
                surf_vx = -omega * s_cl[i] * sa
                surf_vy = omega * s_cl[i] * ca
                can_cut = (s[i] > 12 and cool[i] <= 0 and n + len(new_balls) < cfg.max_balls
                           and full_at is None)
                if can_cut:
                    # split: both halves sit on either side of the blade
                    g = gen[i] + 1
                    bx, by = x[i], y[i]
                    tx, ty = ca, sa  # along blade
                    pad = r + cfg.blade_half_width + 0.5
                    # ball i -> leading side, new ball -> trailing side
                    lead = 1.0 if (nx_ * surf_vx + ny_ * surf_vy) >= 0 else -1.0
                    x[i] = bx - s[i] * ca + 0 + nx_ * pad; y[i] = by - s[i] * sa + ny_ * pad
                    x[i] = s_cl[i] * ca + nx_ * pad; y[i] = s_cl[i] * sa + ny_ * pad
                    jx = rng.normal() * 40
                    vx[i] = surf_vx * 0.8 + nx_ * cfg.split_kick + tx * jx
                    vy[i] = surf_vy * 0.8 + ny_ * cfg.split_kick + ty * jx
                    gen[i] = g; cool[i] = cfg.cut_cooldown
                    new_balls.append((s_cl[i] * ca - nx_ * pad, s_cl[i] * sa - ny_ * pad,
                                      vx[i] - nx_ * 2 * cfg.split_kick - 2 * tx * jx,
                                      vy[i] - ny_ * 2 * cfg.split_kick - 2 * ty * jx, g))
                    cuts.append((bx, by, g))
                    _ = lead
                elif cool[i] > 0:
                    continue  # freshly cut balls pass through the blade
                else:
                    push = r + cfg.blade_half_width - d
                    x[i] += nx_ * push; y[i] += ny_ * push
                    rel = (vx[i] - surf_vx) * nx_ + (vy[i] - surf_vy) * ny_
                    if rel < 0:
                        vx[i] -= rel * nx_ * 1.15; vy[i] -= rel * ny_ * 1.15
            for (bx, by, bvx, bvy, g) in new_balls:
                x[n], y[n], vx[n], vy[n], gen[n], cool[n] = bx, by, bvx, bvy, g, cfg.cut_cooldown
                n += 1
            m = slice(0, n)

            # velocity from positional correction (only for pre-existing balls)
            k = len(xp)
            vx[:k] = 0.5 * vx[:k] + 0.5 * (x[:k] - xp) / dt * 1.0
            vy[:k] = 0.5 * vy[:k] + 0.5 * (y[:k] - yp) / dt * 1.0

            # ring wall
            dd = np.hypot(x[m], y[m])
            out = np.nonzero(dd > R - r)[0]
            for i in out:
                nx_, ny_ = x[i] / dd[i], y[i] / dd[i]
                x[i], y[i] = nx_ * (R - r), ny_ * (R - r)
                vn = vx[i] * nx_ + vy[i] * ny_
                if vn > 0:
                    e = cfg.wall_restitution if n < 40 else 0.35
                    vx[i] -= (1 + e) * vn * nx_
                    vy[i] -= (1 + e) * vn * ny_
                    if n >= 40:
                        vt = -vx[i] * ny_ + vy[i] * nx_
                        vx[i] -= -ny_ * vt * 0.08
                        vy[i] -= nx_ * vt * 0.08
                    if n < 24 and vn > 250:
                        bounces.append(vn)
            cool[m] -= dt

        if full_at is None and n >= cfg.max_balls - 1:
            full_at = t
        frames_pos.append(np.stack([x[:n], y[:n]], 1).astype(np.float32))
        frames_gen.append(gen[:n].astype(np.int16).copy())
        frames_angle.append(angle)
        frames_omega.append(omega)
        frame_events.append(cuts)
        frame_bounces.append(bounces)
        if full_at is not None and t - full_at >= cfg.hold_after_full:
            break

    return dict(pos=frames_pos, gen=frames_gen, angle=np.array(frames_angle),
                omega=np.array(frames_omega), cuts=frame_events, bounces=frame_bounces,
                full_frame=None if full_at is None else int(full_at * cfg.fps), cfg=cfg)


if __name__ == "__main__":
    import time
    t0 = time.time()
    out = simulate(SimConfig())
    counts = [len(p) for p in out["pos"]]
    print("frames", len(counts), "secs", len(counts) / 60, "full_frame", out["full_frame"],
          "time", round(time.time() - t0, 1))
    for s in range(0, len(counts), 120):
        print(s // 60, counts[s], max(out["gen"][s]))
