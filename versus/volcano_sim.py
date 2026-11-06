"""Volcano vs snowstorm: an event-level tug-of-war with real particle motion for the picture.

Rules shown on screen:
  every snowflake that lands in the crater cools the lava 10%;
  every lava bomb that falls back in heats it 50% and launches 2 more.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

W, H = 1080, 1920


@dataclass
class VolcanoConfig:
    fps: int = 60
    seed: int = 5
    crater_x: float = 540.0
    crater_y: float = 1060.0
    crater_half: float = 95.0        # half-width of the crater opening
    slope: float = 1.05               # drop in y per px away from the rim
    ground_y: float = 1640.0
    gravity: float = 1500.0
    cool: float = 0.90                # heat multiplier per snowflake
    heat_up: float = 1.5              # heat multiplier per returning bomb
    spawn_per_return: int = 2
    p_return: float = 0.48            # chance a launched bomb falls back in
    p_return_late: float = 0.62       # ...once the lava is roaring
    auto_launch_every: float = 2.6    # seconds between "breathing" bombs from the crater
    flake_rate: tuple = (1.1, 2.4)    # counting flakes per second (start, end of ramp)
    flake_ramp: float = 30.0
    deco_flakes: float = 40.0         # background flakes per second
    melt_heat: float = 400.0          # above this %, flakes melt into steam before landing
    max_bombs: int = 650
    end_heat: float = 5e7             # eruption when heat passes this
    hold: float = 4.5
    max_seconds: float = 70.0


def slope_y(cfg, x):
    d = np.maximum(np.abs(x - cfg.crater_x) - cfg.crater_half, 0)
    return np.minimum(cfg.crater_y + 8 + d * cfg.slope, cfg.ground_y)


def simulate(cfg: VolcanoConfig):
    rng = np.random.default_rng(cfg.seed)
    dt = 1.0 / cfg.fps
    g = cfg.gravity
    heat = 100.0
    t = 0.0

    # bombs: x, y, vx, vy, state (0 flying, 1 rolling, 2 cooling dead), age_since_land, returns(bool)
    B = np.zeros((0, 7))
    deco = np.zeros((0, 4))     # decorative flakes
    steam = []                  # (x, y, t0, size)
    splashes = []               # (x, y, t0)
    # a few counting flakes already on their way so the snow starts biting early
    k0 = 6
    flakes = np.column_stack([cfg.crater_x + rng.uniform(-1.25, 1.25, k0) * cfg.crater_half,
                              np.linspace(cfg.crater_y - 150, -20, k0), rng.uniform(0, 6.28, k0),
                              rng.uniform(5.5, 8, k0)])
    next_auto = 0.8
    flake_acc = 0.0
    deco_acc = 0.0
    erupt_at = None
    frames = []

    # pre-fill decorative snow so the first frame isn't empty
    n0 = int(cfg.deco_flakes * 9)
    deco = np.column_stack([rng.uniform(0, W, n0), rng.uniform(-50, H, n0),
                            rng.uniform(0, 6.28, n0), rng.uniform(1.5, 3.5, n0)])

    def launch(k, x0):
        nonlocal B
        if k <= 0:
            return 0
        k = min(k, cfg.max_bombs - int((B[:, 4] < 2).sum()) if len(B) else k)
        if k <= 0:
            return 0
        p = cfg.p_return if heat < 300 else cfg.p_return_late
        ret = rng.random(k) < p
        vy = -rng.uniform(1000, 1550, k)
        T = 2 * -vy / g
        vx_in = rng.uniform(-0.75, 0.75, k) * cfg.crater_half / T
        side = np.where(rng.random(k) < 0.5, -1, 1)
        vx_out = side * rng.uniform(150, 420, k)
        vx = np.where(ret, vx_in, vx_out)
        nb = np.column_stack([np.full(k, x0) + rng.uniform(-30, 30, k), np.full(k, cfg.crater_y + 4),
                              vx, vy, np.zeros(k), np.zeros(k), ret.astype(float)])
        B = np.vstack([B, nb]) if len(B) else nb
        return k

    total = int(cfg.max_seconds * cfg.fps)
    for f in range(total):
        t += dt
        ev_cool, ev_heat, ev_launch, ev_land, ev_melt = [], [], 0, 0, 0

        # breathing bombs
        if t >= next_auto and erupt_at is None:
            ev_launch += launch(1, cfg.crater_x)
            next_auto += cfg.auto_launch_every

        # counting flakes
        prog = min(1.0, t / cfg.flake_ramp)
        rate = cfg.flake_rate[0] + (cfg.flake_rate[1] - cfg.flake_rate[0]) * prog
        if erupt_at is None:
            flake_acc += rate * dt
        while flake_acc >= 1:
            flake_acc -= 1
            x = cfg.crater_x + rng.uniform(-1.25, 1.25) * cfg.crater_half
            flakes = np.vstack([flakes, [x, -20.0, rng.uniform(0, 6.28), rng.uniform(5.5, 8)]])
        deco_acc += cfg.deco_flakes * dt
        while deco_acc >= 1:
            deco_acc -= 1
            deco = np.vstack([deco, [rng.uniform(0, W), -10.0, rng.uniform(0, 6.28), rng.uniform(1.5, 3.5)]])

        # move flakes (counting flakes fall a bit faster so they arrive in ~6 s)
        if len(flakes):
            flakes[:, 1] += 300 * dt
            flakes[:, 2] += 1.6 * dt
            flakes[:, 0] += np.sin(flakes[:, 2]) * 22 * dt
            keep = np.ones(len(flakes), bool)
            for i in range(len(flakes)):
                fx, fy = flakes[i, 0], flakes[i, 1]
                # melt into steam high above a roaring crater
                if heat > cfg.melt_heat and fy > cfg.crater_y - 260 and abs(fx - cfg.crater_x) < cfg.crater_half * 1.6:
                    keep[i] = False; ev_melt += 1
                    steam.append((fx, fy, t, 1.0))
                    continue
                if fy >= cfg.crater_y + 2 and abs(fx - cfg.crater_x) <= cfg.crater_half:
                    keep[i] = False
                    heat *= cfg.cool
                    ev_cool.append(fx)
                    steam.append((fx, cfg.crater_y, t, 1.6))
                elif fy >= slope_y(cfg, np.array([fx]))[0]:
                    keep[i] = False
            flakes = flakes[keep]
        if len(deco):
            deco[:, 1] += (70 + deco[:, 3] * 25) * dt
            deco[:, 2] += 1.2 * dt
            deco[:, 0] += np.sin(deco[:, 2]) * 18 * dt
            deco = deco[deco[:, 1] < slope_y(cfg, deco[:, 0])]

        # bombs
        returns = []
        if len(B):
            fly = B[:, 4] == 0
            B[fly, 3] += g * dt
            B[fly, 0] += B[fly, 2] * dt
            B[fly, 1] += B[fly, 3] * dt
            # falling back through the crater opening
            down = fly & (B[:, 3] > 0) & (B[:, 1] >= cfg.crater_y + 4) & (np.abs(B[:, 0] - cfg.crater_x) <= cfg.crater_half)
            for i in np.nonzero(down)[0]:
                returns.append(B[i, 0])
            B[down, 4] = 3  # remove
            # landing on the slopes
            sy = slope_y(cfg, B[:, 0])
            land = (B[:, 4] == 0) & (B[:, 3] > 0) & (B[:, 1] >= sy) & (np.abs(B[:, 0] - cfg.crater_x) > cfg.crater_half)
            ev_land = int(land.sum())
            B[land, 4] = 1
            B[land, 1] = sy[land]
            B[land, 2] = np.sign(B[land, 0] - cfg.crater_x) * np.abs(B[land, 2]) * 0.6 + np.sign(B[land, 0] - cfg.crater_x) * 60
            # rolling down the slope, slowing and cooling
            roll = B[:, 4] == 1
            B[roll, 5] += dt
            B[roll, 2] *= (1 - 1.2 * dt)
            B[roll, 0] += B[roll, 2] * dt
            B[roll, 1] = slope_y(cfg, B[roll, 0])
            B[roll & (B[:, 5] > 2.4), 4] = 3
            B = B[B[:, 4] < 3]
        for x in returns:
            if erupt_at is None:
                heat *= cfg.heat_up
                ev_heat.append(x)
                splashes.append((x, cfg.crater_y, t))
                ev_launch += launch(cfg.spawn_per_return, x)

        if erupt_at is None and heat >= cfg.end_heat:
            erupt_at = t
        steam = [s for s in steam if t - s[2] < 1.4]
        splashes = [s for s in splashes if t - s[2] < 0.5]
        frames.append(dict(
            t=t, heat=heat, bombs=B[:, [0, 1, 4, 5]].astype(np.float32).copy(),
            flakes=flakes[:, [0, 1, 3]].astype(np.float32).copy(), deco=deco[:, [0, 1, 3]].astype(np.float32).copy(),
            steam=list(steam), splashes=list(splashes),
            cool=ev_cool, heatup=ev_heat, launch=ev_launch, land=ev_land, melt=ev_melt,
            erupt=None if erupt_at is None else t - erupt_at,
        ))
        if erupt_at is not None and t - erupt_at >= cfg.hold:
            break
    return dict(frames=frames, cfg=cfg, erupt_frame=None if erupt_at is None else int(erupt_at * cfg.fps))


if __name__ == "__main__":
    import sys
    seeds = range(int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else [1]
    for s in seeds:
        o = simulate(VolcanoConfig(seed=s))
        fr = o["frames"]
        hs = [x["heat"] for x in fr]
        mn = min(hs[: (o["erupt_frame"] or len(hs))])
        imin = hs.index(mn)
        print(s, "len", round(len(fr) / 60, 1), "erupt", None if o["erupt_frame"] is None else round(o["erupt_frame"] / 60, 1),
              "min", round(mn, 1), "@", round(imin / 60, 1),
              " ".join(f"{h:.0f}" for h in hs[::300]))
