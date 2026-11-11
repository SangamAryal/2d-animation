"""Fight 04: "TIME STOP vs FUTURE SIGHT".

TIME STOP (violet, gold headband) can freeze the world for two seconds.
FUTURE SIGHT (teal, straw hat) sees a moment ahead. The first stop lands and
cuts him badly. He sees the second one coming and cuts the hand mid-gesture.
The third stop is cast from too far away: the two seconds run out a step
short, and the quick-draw he already saw finishes it.
Original characters; only the general idea of a time stop is used.
"""
from rig import Track

STOP = dict(name="TIME STOP", body="#2b2140", back="#5c4d80", band="#f2c14e",
            steel="#eef0f7", ghost="#9b7bff", trail="#efe3ff", accent="#7a5ad8")
SIGHT = dict(name="FUTURE SIGHT", body="#14595f", back="#3f8a90", hat="#d9b26a",
             eye="#7ff7ff", scabbard=True, scab="#2c3e44", steel="#eef7f8",
             ghost="#7ff7ff", trail="#dffcff", accent="#1d9aa3")
TITLE = (("TIME STOP", STOP["accent"]), ("FUTURE SIGHT", SIGHT["accent"]))


def build():
    T = Track(facing=1)
    F = Track(facing=-1)
    ev = []

    def E(t, kind, **kw):
        ev.append((t, kind, kw))

    def walk(tr, a, b, t0, t1, x0, x1, step, who):
        n = max(1, round((t1 - t0) / step))
        tr.key(t0, a, x0)
        for i in range(1, n + 1):
            t = t0 + (t1 - t0) * i / n
            tr.key(t, b if i % 2 else a, x0 + (x1 - x0) * i / n, "io")
            E(t, "step", who=who, v=0.4)

    # ---------------- intro: both walk in
    walk(T, "walk1", "walk2", 0.0, 3.6, -560, -170, 0.36, "T")
    walk(F, "swalk1", "swalk2", 0.0, 3.6, 560, 170, 0.40, "F")
    T.key(4.0, "guard", -170)
    T.key(4.5, "taunt", -170, "io")
    T.key(5.2, "taunt", -170, dy=-2)
    T.key(5.6, "guard", -170, "io")
    F.key(4.0, "stand_sheathed", 170)
    F.key(4.4, "iai", 170, "io")
    F.key(4.75, "block_mid", 170, "snap", sheath=0)
    E(4.73, "draw")
    F.key(5.6, "guard", 170, "io")
    E(4.9, "heart", v=0.8)
    E(5.3, "heart", v=0.9)
    E(5.55, "banner", text="FIGHT!")
    E(5.55, "drum", v=1.0)

    # ---------------- round 1: every attack is seen before it comes
    T.key(6.0, "guard", -170)
    F.key(6.0, "guard", 170)
    E(6.0, "vision", who="F", on="T", dur=0.40, lead=0.40)
    T.key(6.22, "high_wind", -10, "out")
    T.key(6.42, "high_cut", 30, "snap")
    F.key(6.25, "guard", 160)
    F.key(6.40, "block_high", 150, "snap")
    E(6.42, "clash", v=0.9)
    E(6.42, "hitstop", dur=0.05)
    T.key(6.55, "guard", 20, "io")
    F.key(6.55, "guard", 155, "io")
    E(6.55, "vision", who="F", on="T", dur=0.35, lead=0.35)
    T.key(6.72, "side_wind", 25, "io")
    T.key(6.86, "side_cut", 45, "snap")
    F.key(6.80, "recoil", 215, "snap", T=-30, H=-30)   # leans back, the blade misses
    F.key(6.98, "guard_low", 205, "io")
    # counter
    F.key(7.06, "side_wind", 170, "out")
    F.key(7.14, "side_cut", 120, "snap")
    E(7.14, "hit", by="F", on="T", v=0.9, dmg=12)
    E(7.14, "hitstop", dur=0.06)
    T.key(7.0, "side_cut", 45)
    T.key(7.15, "recoil", 15, "snap")
    T.key(7.40, "guard", 0, "io")
    F.key(7.40, "guard", 135, "io")
    E(7.42, "vision", who="F", on="T", dur=0.35, lead=0.35)
    T.key(7.58, "rise_wind", 10, "io")
    T.key(7.74, "rise_cut", 30, "snap")
    F.key(7.70, "block_mid", 140, "snap")
    E(7.74, "clash", v=1.0)
    E(7.74, "hitstop", dur=0.05)
    F.key(7.90, "high_wind", 140, "io")
    F.key(8.02, "high_cut", 105, "snap")
    E(8.02, "hit", by="F", on="T", v=1.0, dmg=10)
    E(8.02, "hitstop", dur=0.07)
    T.key(7.9, "rise_cut", 30)
    T.key(8.04, "stagger", 0, "snap")
    T.key(8.30, "crouch", -40, "io")
    T.key(8.55, "jump_tuck", -120, "out", air=90, rot=-200)
    T.key(8.72, "guard_low", -190, "in", air=0, rot=-360)
    T.key(8.721, "guard_low", -190, rot=0)
    E(8.72, "skid", x=-190, v=0.6)
    F.key(8.20, "guard", 110, "io")

    # ---------------- TIME STOP #1
    T.key(8.85, "guard", -190, "io")
    T.key(9.15, "tcast", -190, "out")
    F.key(8.80, "guard", 110)
    F.key(9.15, "run1_g", 70, "io")         # he starts to rush in... and freezes
    E(9.15, "tstop", who="T", dur=2.0, windup=0.32)
    F.key(11.15, "run1_g", 70)
    T.key(9.40, "guard", -190, "io")
    walk(T, "walk1", "walk2", 9.50, 10.45, -190, 175, 0.24, "T")
    T.face(10.48, -1)
    T.key(10.50, "guard", 178, "snap")
    T.key(10.62, "side_wind", 180, "io")
    T.key(10.72, "side_cut", 168, "snap")
    E(10.72, "hit", by="T", on="F", v=0.9, dmg=18)
    T.key(10.84, "high_wind", 172, "io")
    T.key(10.94, "high_cut", 160, "snap")
    E(10.94, "hit", by="T", on="F", v=1.0, dmg=20)
    T.key(11.10, "guard", 215, "io")
    # time flows again: it all lands at once
    E(11.15, "dmg", who="F", by="T", amt=0, big=True)
    E(11.15, "hitstop", dur=0.12)
    F.key(11.17, "recoil", 40, "snap", T=40, H=40)
    F.key(11.45, "stagger", -10, "out")
    F.key(11.75, "kneel", -20, "in")
    E(11.75, "thud", v=0.6)
    T.key(11.6, "guard", 215)
    T.key(12.0, "taunt", 220, "io")
    T.key(12.7, "taunt", 220, dy=-2)

    # ---------------- he sees the second stop coming
    F.key(12.3, "kneel", -20)
    F.face(12.35, 1)
    F.key(12.6, "guard_low", -10, "io")
    F.key(12.9, "guard_low", -10)
    E(12.85, "vision", who="F", on="T", dur=0.40, lead=0.45)
    T.key(12.95, "guard", 220, "io")
    T.key(13.25, "tcast", 220, "out")     # would freeze time at ~13.35
    F.key(12.98, "crouch", -5, "io")
    F.key(13.06, "dash", 60, "snap")
    F.key(13.18, "dash", 110, "lin")
    E(13.04, "zip", v=0.9)
    F.key(13.24, "side_cut", 135, "snap")
    E(13.24, "tbreak", who="T")
    E(13.24, "hit", by="F", on="T", v=1.0, dmg=25, big=True)
    E(13.24, "hitstop", dur=0.14)
    T.key(13.26, "recoil", 260, "snap")
    T.key(13.55, "tumble", 380, "out", air=70, rot=200)
    T.key(13.80, "stagger", 470, "in", rot=360)
    T.key(13.801, "stagger", 470, rot=0)
    E(13.80, "skid", x=470, v=0.9)
    T.key(14.2, "guard_low", 480, "io")
    # space opens up: he walks back and sheathes
    F.key(13.6, "side_cut", 135)
    F.key(13.9, "guard", 120, "io")
    F.key(14.4, "guard", 30, "io")
    F.key(14.75, "sheathing", 10, "io")
    F.key(15.0, "iai", 0, "snap", sheath=1)
    E(15.0, "sheathe")
    F.key(15.35, "iai_deep", -5, "io")
    T.key(14.6, "guard_low", 560, "io")
    T.key(15.0, "guard", 600, "io")
    E(15.2, "heart", v=0.9)

    # ---------------- TIME STOP #2, from too far away
    E(15.45, "vision", who="F", on="T", dur=0.55, lead=1.9)
    T.key(15.45, "guard", 600)
    T.key(15.80, "tcast", 600, "out")
    E(15.80, "tstop", who="T", dur=2.0, windup=0.32)
    F.key(15.80, "iai_deep", -5)
    F.key(17.80, "iai_deep", -5)
    T.key(15.98, "crouch", 595, "io", grip=1, sw=60)
    t, x, i = 15.98, 595, 0
    while t < 17.50:
        t += 0.13
        x -= 32
        T.key(t, "run2_g" if i % 2 == 0 else "run1_g", x, "lin")
        E(t, "step", who="T", v=0.6)
        i += 1
    tx = x
    T.key(17.62, "high_wind", tx - 12, "out")
    E(17.35, "slowmo", a0=17.35, a1=17.80, rate=0.3)
    # time resumes a step short; the quick draw he already saw
    t_cut = 17.84
    T.key(t_cut - 0.02, "high_wind", tx - 14)
    F.key(t_cut - 0.04, "iai_deep", -5)
    F.key(t_cut + 0.05, "iai_cut", tx + 180, "snap", sheath=0)
    E(t_cut, "iai", x0=-5, x1=tx + 180)
    E(t_cut + 0.02, "decap", who="T", by="F")
    E(t_cut + 0.02, "dmg", who="T", by="F", amt=60, big=True)
    E(t_cut + 0.02, "hitstop", dur=0.2)
    T.key(t_cut + 0.03, "stagger", tx - 14, "snap", headless=1)
    T.key(t_cut + 0.5, "stagger", tx - 30, "io", headless=1, T=-20)
    T.key(t_cut + 0.9, "kneel", tx - 30, "in", headless=1)
    E(t_cut + 0.9, "thud", v=0.8)
    T.key(t_cut + 1.5, "fallen", tx - 50, "in", headless=1)
    E(t_cut + 1.5, "thud", v=1.0)
    E(t_cut + 1.5, "dust", x=tx - 80, v=0.8)
    F.key(t_cut + 0.6, "iai_hold", tx + 180)
    F.key(t_cut + 1.6, "sheathing", tx + 180)
    F.key(t_cut + 2.05, "stand_sheathed", tx + 182, "snap")
    E(t_cut + 2.05, "sheathe", final=True)
    E(t_cut + 2.2, "winner", name="FUTURE SIGHT WINS", color=SIGHT["accent"])
    end = t_cut + 4.3
    F.key(end, "stand_sheathed", tx + 182)
    T.key(end, "fallen", tx - 50, headless=1)
    return dict(fighters=[("T", T, STOP), ("F", F, SIGHT)], events=ev, end=end,
                hp=[("T", STOP["name"], STOP["accent"]), ("F", SIGHT["name"], SIGHT["accent"])],
                title=TITLE)
