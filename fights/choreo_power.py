"""Fight 02: "SPEED vs POWER".

SPEED (small, blue, yellow scarf) is a blur: dashes, flips, eight-hit flurries.
POWER (huge, red, horned, giant cleaver) barely moves, shrugs off the hits,
and every swing shakes the ground. Twist: SPEED's final flurry does nothing,
his katana snaps, and POWER sends him flying out of the arena.
"""
from rig import Track

SPEED = dict(name="SPEED", body="#1c86d1", back="#6db4e6", band="#ffc531",
             limb=7.5, size=0.95, blade=80, steel="#eef3f7", ghost="#5fc2ff",
             trail="#d6f0ff", fast=True)
POWER = dict(name="POWER", body="#a3222b", back="#c95a60", horns="#3a2a1a",
             eye="#ffe08a", limb=11.5, torso=1.7, head=1.1, size=1.42, blade=118,
             sword="cleaver", steel="#d9dde2", ghost="#ff7b7b", trail="#ffe0e0")
TITLE = (("SPEED", SPEED["body"]), ("POWER", POWER["body"]))


def shift(S, P, ev, t_from, dt):
    """Push every key and event at or after t_from later by dt seconds."""
    for tr in (S, P):
        tr.keys = [(t + dt if t >= t_from else t, p, x, e) for t, p, x, e in tr.keys]
        tr.facing_keys = [(t + dt if t >= t_from else t, f) for t, f in tr.facing_keys]
    for i, (t, k, kw) in enumerate(ev):
        kw = dict(kw)
        for key in ("a0", "a1", "until"):
            if key in kw and kw[key] >= t_from:
                kw[key] += dt
        ev[i] = (t + dt if t >= t_from else t, k, kw)


def build():
    S = Track(facing=1)
    P = Track(facing=-1)
    ev = []

    def E(t, kind, **kw):
        ev.append((t, kind, kw))

    def hit(t):
        E(t, "hit", by="S", on="P", v=0.8, dmg=4)
        E(t, "hitstop", dur=0.035)

    px = 215  # where POWER stands when the fight starts

    # ---------------- flurry #1: two blocked, three land
    S.key(2.18, "guard_low", -150)
    S.key(2.26, "dash", 40, "lin")
    E(2.19, "zip", v=0.8)
    P.key(2.18, "shoulder", px)
    P.key(2.30, "block_mid", px, "out")
    seq = [("side", 2.30), ("rise", 2.42), ("high", 2.54), ("side", 2.66),
           ("rise", 2.78)]
    sx = 40
    for i, (kind, t) in enumerate(seq):
        sx += 6 if i % 2 == 0 else -3
        S.key(t, f"{kind}_wind", sx, "out")
        S.key(t + 0.05, f"{kind}_cut", sx + 8, "snap")
        if i < 2:
            E(t + 0.05, "clash", v=0.7)
            E(t + 0.05, "hitstop", dur=0.03)
        else:
            hit(t + 0.05)
            P.key(t + 0.06, "block_mid", px + 4, "snap", T=-12, H=-14, dy=-3)
            P.key(t + 0.11, "block_mid", px + 2, "io")
    # POWER's slow sweep. SPEED back-flips over it.
    P.key(2.95, "shoulder", px)
    P.key(3.40, "sweep_wind", px + 10, "back")
    P.key(3.52, "sweep", px - 20, "snap")
    E(3.53, "gust", x=px - 160, v=1.0)
    S.key(2.95, "guard_low", 56)
    S.key(3.36, "crouch", 50)
    S.key(3.62, "jump_tuck", -40, "out", air=115, rot=-200, T=20)
    S.key(3.82, "jump_tuck", -150, "in", air=10, rot=-360, T=20)
    S.key(3.88, "guard_low", -160, "snap")
    E(3.86, "skid", x=-160, v=0.7)
    S.key(3.95, "guard_low", -160)

    # ---------------- dash THROUGH him, flurry from behind
    S.key(4.00, "dash", -150, "snap")
    S.key(4.07, "side_cut", 470, "lin")
    E(4.01, "zip", v=1.0)
    hit(4.04)
    S.face(4.08, -1)
    S.key(4.20, "guard_low", 480, "out")
    E(4.10, "skid", x=470, v=0.8)
    P.key(3.90, "sweep", px - 15)
    P.key(4.20, "shoulder", px)
    P.face(4.42, 1)
    P.key(4.45, "shoulder", px + 5, "snap")
    S.key(4.48, "dash", 480, "snap")
    S.key(4.53, "guard", 360, "lin")
    E(4.48, "zip", v=0.8)
    for i, (kind, t) in enumerate([("high", 4.55), ("side", 4.66), ("rise", 4.77)]):
        S.key(t, f"{kind}_wind", 360 - i * 3, "out")
        S.key(t + 0.05, f"{kind}_cut", 352 - i * 3, "snap")
        hit(t + 0.05)
        P.key(t + 0.06, "shoulder", px + 5, "snap", T=-8, H=-10)
        P.key(t + 0.10, "shoulder", px + 5)

    # ---------------- the ground slam (SPEED zips away just in time)
    P.key(4.90, "shoulder", px + 5)
    P.key(5.35, "heavy_wind", px + 15, "io")
    P.key(5.46, "slam", px + 50, "snap")
    E(5.47, "slam", by="P", v=1.0)
    E(5.47, "hitstop", dur=0.12)
    S.key(4.90, "guard_low", 345)
    S.key(5.30, "guard_low", 345, T=10)
    S.key(5.34, "dash", 345, "snap", T=-30)
    S.key(5.40, "guard_low", 600, "lin")
    E(5.34, "zip", v=0.8)
    E(5.42, "skid", x=600, v=0.8)
    P.key(5.80, "slam", px + 50, dy=-3)
    P.key(6.10, "shoulder", px + 40)
    S.key(5.95, "guard_low", 600)

    # ---------------- clash, then the counter that launches SPEED
    S.key(6.10, "dash", 590, "snap")
    S.key(6.17, "high_wind", 400, "lin")
    S.key(6.22, "high_cut", 385, "snap")
    E(6.11, "zip", v=0.8)
    P.key(6.14, "block_high", px + 40, "snap")
    E(6.22, "clash", v=1.0, big=True)
    E(6.22, "hitstop", dur=0.08)
    S.key(6.32, "guard", 410, "out")
    P.key(6.32, "sweep_wind", px + 30, "io")
    P.key(6.50, "sweep", px + 70, "snap")
    S.key(6.43, "block_mid", 405, "snap")
    E(6.50, "clash", v=1.0, big=True)
    E(6.50, "hitstop", dur=0.14)
    E(6.50, "dmg", who="S", by="P", amt=40)
    E(6.52, "shout", v=0.6)
    S.key(6.51, "tumble", 430, "snap", air=30, rot=40)
    S.key(6.85, "tumble", 760, "lin", air=150, rot=420)
    S.key(7.08, "fallen", 900, "in", rot=0)
    E(7.08, "thud", v=1.0)
    E(7.08, "skid", x=900, v=1.2)
    S.key(7.35, "fallen", 950, "out")
    P.key(6.80, "sweep", px + 70)

    # ---------------- SPEED gets up, POWER drags his blade closer
    S.key(7.75, "kneel", 950)
    S.key(8.10, "guard_low", 952)
    P.key(7.10, "shoulder", px + 70)
    x = px + 70
    for i, t in enumerate([7.45, 7.85, 8.25, 8.65]):
        x += 70
        P.key(t, "drag1" if i % 2 == 0 else "drag2", x, "io")
        E(t, "stomp", x=x, v=0.8)
    P.key(8.85, "guard", x, T=4)
    pxx = x  # about 565
    # SPEED charges up
    S.key(8.55, "crouch", 952, T=40, dy=-6)
    E(8.55, "charge", dur=0.45)

    # ---------------- ultimate flurry: eight hits from every side
    S.key(8.98, "crouch", 952, T=45, dy=-8)
    E(8.98, "zip", v=1.0)
    spots = [  # dt, x offset from POWER, air, facing, pose, rot
        (9.05, -95, 50, 1, "high_cut", 0),
        (9.13, 120, 0, -1, "side_cut", 0),
        (9.21, -80, 120, 1, "rise_cut", -40),
        (9.29, 110, 80, -1, "high_cut", 30),
        (9.37, -100, 0, 1, "side_cut", 0),
        (9.45, 105, 150, -1, "high_cut", -30),
        (9.53, -60, 190, 1, "land_cut", 0),
    ]
    for t, off, air, f, ps, rot in spots:
        S.key(t - 0.045, "dash", pxx + off * 1.6, "lin", air=air, rot=rot)
        S.face(t - 0.045, f)
        S.key(t, ps, pxx + off, "snap", air=air, rot=rot)
        hit(t)
    S.face(9.60, -1)
    S.key(9.60, "dash", pxx - 60, "lin", air=60)
    S.key(9.66, "iai_cut", pxx - 260, "snap")
    E(9.62, "zip", v=1.0)
    E(9.64, "hit", by="S", on="P", v=0.8, dmg=2)
    E(9.64, "hitstop", dur=0.035)
    E(9.66, "skid", x=pxx - 260, v=1.0)
    P.key(9.0, "guard", pxx, T=4)
    P.key(9.7, "guard", pxx, T=6, dy=-2)

    # ---------------- ...nothing. The katana snaps.
    S.key(10.45, "iai_hold", pxx - 262)
    S.key(10.50, "iai_hold", pxx - 262, broken=1)
    E(10.50, "break", who="S")
    S.key(10.95, "broken_look", pxx - 262)
    P.key(10.55, "shoulder", pxx)
    P.face(10.80, -1)
    P.key(10.82, "shoulder", pxx - 5, "snap")
    E(10.85, "heart", v=1.0)
    S.face(11.10, 1)
    S.key(11.12, "stagger", pxx - 262, "snap", broken=1)
    S.key(11.35, "block_mid", pxx - 255, "out", broken=1)
    P.key(11.10, "shoulder", pxx - 5)
    P.key(11.48, "sweep_wind", pxx, "back")
    P.key(11.60, "sweep", pxx - 40, "snap")
    # the cleaver goes clean through: off comes the head
    E(11.60, "decap", who="S", by="P")
    E(11.60, "dmg", who="S", by="P", amt=60, big=True)
    E(11.60, "hitstop", dur=0.22)
    E(11.62, "slowmo", a0=11.62, a1=12.35, rate=0.35)
    S.key(11.61, "stagger", pxx - 262, "snap", broken=1, headless=1)
    S.key(12.05, "stagger", pxx - 280, "io", broken=1, headless=1, T=-20)
    S.key(12.45, "kneel", pxx - 280, "in", broken=1, headless=1)
    E(12.45, "thud", v=0.8)
    S.key(13.05, "fallen", pxx - 300, "in", broken=1, headless=1)
    E(13.05, "thud", v=1.0)
    E(13.05, "dust", x=pxx - 330, v=0.8)
    P.key(12.0, "sweep", pxx - 40)
    P.key(12.6, "shoulder", pxx - 30)
    E(13.4, "winner", name="POWER WINS", color=POWER["body"])
    # ---------------- round 2 (inserted): SPEED cuts POWER down further
    shift(S, P, ev, 8.54, 2.2)
    S.key(8.10, "guard_low", 952)
    S.key(8.52, "guard_low", 952)
    S.key(8.55, "dash", 945, "snap")
    S.key(8.62, "guard_low", 705, "lin")
    E(8.55, "zip", v=0.9)
    P.key(8.85, "guard", pxx, T=4)
    P.key(8.62, "guard", pxx, T=4)
    P.key(8.70, "sweep_wind", pxx - 10, "out")
    P.key(8.84, "sweep", pxx + 20, "snap")
    S.key(8.76, "crouch", 700, "snap", dy=-28, T=55)      # ducks under it
    S.key(8.86, "rise_wind", 690, "out")
    S.key(8.91, "rise_cut", 680, "snap")
    hit(8.91)
    S.key(8.99, "side_wind", 684, "out")
    S.key(9.04, "side_cut", 676, "snap")
    hit(9.04)
    P.key(9.10, "stagger", pxx - 15, "out", grip=1, sw=60)
    S.key(9.12, "crouch", 690)
    S.key(9.28, "jump_tuck", 660, "out", air=125, rot=-200)
    S.key(9.38, "high_cut", 645, "snap", air=70, rot=-360)
    hit(9.38)
    S.key(9.50, "guard_low", 700, "in", rot=-360)
    S.key(9.51, "guard_low", 700, "snap")
    E(9.50, "skid", x=700, v=0.7)
    # POWER's second slam; SPEED is already gone
    P.key(9.45, "guard", pxx - 10)
    P.key(9.95, "heavy_wind", pxx - 5, "io")
    P.key(10.06, "slam", pxx + 40, "snap")
    E(10.07, "slam", by="P", v=1.0)
    E(10.07, "hitstop", dur=0.1)
    S.key(9.88, "guard_low", 705)
    S.key(9.92, "dash", 705, "snap", T=-30)
    S.key(9.98, "guard_low", 905, "lin")
    E(9.92, "zip", v=0.8)
    E(9.99, "skid", x=905, v=0.8)
    # straight back in, through him, and back again
    S.key(10.20, "dash", 900, "snap")
    S.key(10.27, "side_cut", 360, "lin")
    E(10.20, "zip", v=1.0)
    hit(10.24)
    S.face(10.28, 1)
    S.key(10.38, "rise_wind", 410, "out")
    S.key(10.43, "rise_cut", 420, "snap")
    hit(10.43)
    S.key(10.50, "dash", 425, "snap")
    S.key(10.57, "side_cut", 950, "lin")
    E(10.50, "zip", v=1.0)
    hit(10.53)
    S.face(10.58, -1)
    S.key(10.70, "guard_low", 952, "out")
    E(10.60, "skid", x=952, v=0.9)
    P.key(10.30, "slam", pxx + 40, dy=-3)
    P.key(10.45, "slam", pxx + 40, "snap", T=40, dy=-8)
    P.key(10.75, "shoulder", pxx)

    # ---------------- long intro: POWER stomps in, SPEED arrives, stare-down
    INTRO = 3.82
    shift(S, P, ev, 2.1, INTRO)
    x = 760
    P.key(0.0, "heavy1", x)
    steps = [0.45 + i * 0.52 for i in range(7)]
    for i, t in enumerate(steps):
        x -= (760 - px) / len(steps)
        P.key(t, "heavy2" if i % 2 == 0 else "heavy1", x, "io")
        E(t, "stomp", x=x, v=1.0)
    P.key(4.3, "shoulder", px)
    P.key(5.2, "shoulder", px, dy=-3)
    P.key(5.95, "shoulder", px)
    S.key(0.0, "dash", -1300)
    S.key(4.00, "dash", -1300)
    S.key(4.10, "dash", -180, "lin")
    S.key(4.21, "guard_low", -150, "snap")
    S.key(5.2, "guard_low", -150, dy=-2)
    S.key(5.95, "guard_low", -150)
    E(4.02, "zip", v=1.0)
    E(0.0, "focus", who="P", until=4.05)
    E(4.12, "skid", x=-160, v=1.0)
    E(4.6, "heart", v=0.8)
    E(5.15, "heart", v=0.9)
    E(5.55, "banner", text="FIGHT!")
    E(5.55, "drum", v=1.0)

    end = 15.6 + 2.2 + INTRO
    S.key(end, "fallen", pxx - 300, broken=1, headless=1)
    P.key(end, "shoulder", pxx - 30, dy=-2)
    return dict(fighters=[("P", P, POWER), ("S", S, SPEED)], events=ev, end=end,
                hp=[("S", SPEED["name"], SPEED["body"]), ("P", POWER["name"], POWER["body"])],
                title=TITLE)
