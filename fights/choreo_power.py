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


def build():
    S = Track(facing=1)
    P = Track(facing=-1)
    ev = []

    def E(t, kind, **kw):
        ev.append((t, kind, kw))

    def hit(t):
        E(t, "hit", by="S", on="P", v=0.8)
        E(t, "hitstop", dur=0.035)

    # ---------------- intro: POWER stomps in, SPEED zips in
    x = 470
    P.key(0.0, "heavy1", x)
    for i, t in enumerate([0.5, 1.0, 1.5]):
        x -= 85
        P.key(t, "heavy2" if i % 2 == 0 else "heavy1", x, "io")
        E(t, "stomp", x=x, v=1.0)
    P.key(1.85, "shoulder", x)
    px = x  # 215
    S.key(0.0, "dash", -1300)
    S.key(1.15, "dash", -1300)
    S.key(1.25, "dash", -180, "lin")
    S.key(1.36, "guard_low", -150, "snap")
    E(1.17, "zip", v=1.0)
    E(0.0, "focus", who="P", until=1.2)
    E(1.27, "skid", x=-160, v=1.0)
    E(1.9, "heart", v=0.8)

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
    hit(9.64)
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
    S.key(11.35, "block_high", pxx - 255, "out", broken=1)
    P.key(11.10, "shoulder", pxx - 5)
    P.key(11.48, "sweep_wind", pxx, "back")
    P.key(11.60, "sweep", pxx - 40, "snap")
    E(11.60, "clash", v=1.0, big=True, final=True)
    E(11.60, "hitstop", dur=0.2)
    S.key(11.61, "tumble", pxx - 300, "snap", air=40, rot=-30, broken=1)
    S.key(12.40, "tumble", pxx - 2300, "out", air=1100, rot=-1500, broken=1)
    E(11.62, "focus", who="P")
    E(12.55, "twinkle")
    P.key(12.0, "sweep", pxx - 40)
    P.key(12.5, "shoulder", pxx - 30)
    E(12.9, "winner", name="POWER WINS", color=POWER["body"])
    end = 15.0
    S.key(end, "tumble", pxx - 2400, "lin", air=1200, rot=-1700, broken=1)
    P.key(end, "shoulder", pxx - 30, dy=-2)
    return dict(fighters=[("P", P, POWER), ("S", S, SPEED)], events=ev, end=end,
                title=TITLE)
