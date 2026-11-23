"""Fight 09: "RONIN vs 4 BANDITS" (the ambush).

The first fight that is not a 1v1 duel. A lone ronin crossing the meadow is
surrounded by four masked bandits, each with a different weapon, and cuts
through them one at a time, with the story turning back and forth:

  0-5 s    the ambush: Daggers drops from above, Brute stomps in, Spear runs in
           behind him, the Chief strolls up last, blade on his shoulder.
           The ronin looks both ways and draws.
  5-8 s    first blood: Spear stabs at his back (parried), Daggers' slash goes
           over his head (front kick), he jumps the low thrust and cuts Spear down.
  8-16 s   overwhelmed: Brute's overhead pins him, Daggers flips over and cuts
           his shoulder. He kicks free, holds off a three-cut flurry, then ducks
           Brute's sweep, which cleaves Daggers instead (friendly fire). He cuts
           Brute's leg, gets backhanded across the meadow, gets up, dodges a
           crater slam, jumps the next sweep and takes Brute's head in the air.
  16-27 s  the Chief: calm, much faster. Three clashes, a kick, a cut to the
           ronin's leg; the ronin answers with a cut to the Chief's arm; the
           Chief's fury combo knocks the katana out of his hands. A finishing
           blow at a kneeling man misses (he rolls to his sword), he sheathes,
           waits, and ends it with one quick-draw straight through him.
           Freeze-frame, the Chief falls, the ronin sheathes and walks on.

Fighters: R ronin, S spear, D daggers, B brute, C chief. Every clash names its
pair (a=, b=) and every hit its victim (on=), so the contact solver works on
the right two fighters; "frame" events tell the camera who is in the shot.
"""
from rig import P, Track, pose
import choreo_spear  # noqa: F401  (sp_* spear poses, sw_chiburi)
import choreo_chain2  # noqa: F401  (t_* twin-blade poses)

NAVY = "#1f2d4d"
CRIMSON = "#8e1c24"
MASK = "#2a2420"

RONIN = dict(name="RONIN", body=NAVY, back="#5a6c93", band="#d8323c", hat="#d9b26a",
             scabbard=True, scab="#4a2626", steel="#eef2f6", ghost="#5a6c93",
             trail="#e6ecff", limb=8.5, size=1.0, blade=66)
SPEARMAN = dict(name="SPEAR", body="#7a5a32", back="#a88a60", mask=MASK,
                sword="spear", blade=112, butt=88, grip_off=-36, head_len=28,
                cut=30, wood="#6e4a2a", tassel="#3a3a3a", steel="#dde3e8",
                ghost="#a88a60", trail="#f2e8d8", limb=8.3, size=0.98,
                springs={"sw": (62, 0.62)})
DAGGERS = dict(name="DAGGERS", body="#4f5d2f", back="#8a9860", mask=MASK, twin=True,
               sword="katana", blade=40, butt=6, steel="#dde3e8", ghost="#8a9860",
               trail="#eef4dc", limb=8.0, size=0.94)
BRUTE = dict(name="BRUTE", body="#5e3a2a", back="#94705c", mask=MASK,
             limb=11.5, torso=1.6, head=1.08, size=1.38, blade=104,
             sword="cleaver", steel="#cfd4d9", ghost="#94705c", trail="#f2e2d8")
CHIEF = dict(name="CHIEF", body=CRIMSON, back="#c2565c", mask="#e3b341",
             sword="longsword", blade=88, steel="#eef2f6", ghost="#c2565c",
             trail="#ffe0e0", limb=8.8, size=1.06)

# ---------------------------------------------------------------- hero poses
pose("h_walk1", "stand_sheathed", T=4, thf=158, shf=186, thb=202, shb=214)
pose("h_walk2", "stand_sheathed", T=4, thf=198, shf=188, thb=162, shb=176)
pose("h_hand", "stand_sheathed", T=8, H=4, uaf=150, faf=100, uab=185, fab=95,
     thf=150, shf=180, thb=212, shb=196)
pose("h_duck", T=64, H=44, uaf=150, faf=100, sw=62, grip=1,
     thf=92, shf=200, thb=232, shb=268, sq=-0.1)
pose("h_pant", T=22, H=16, uaf=160, faf=110, sw=72, grip=1,
     thf=140, shf=185, thb=222, shb=212)
pose("h_getup", T=24, H=14, uaf=150, faf=95, sw=62, grip=1,
     thf=95, shf=185, thb=150, shb=265)
pose("h_kneel_block", T=6, H=-2, uaf=60, faf=-10, sw=95, grip=1,
     thf=95, shf=185, thb=150, shb=265)
pose("h_kneel_cut", T=30, H=18, uaf=100, faf=95, sw=95, grip=1,
     thf=95, shf=185, thb=150, shb=265)
pose("h_tuck_wind", T=-4, H=-4, uaf=225, faf=-30, sw=-95, grip=1,
     thf=92, shf=212, thb=140, shb=232)
pose("h_tuck_cut", T=22, H=14, uaf=100, faf=95, sw=95, grip=1,
     thf=100, shf=200, thb=150, shb=228)
pose("h_low_cut", T=50, H=36, uaf=100, faf=100, sw=118, grip=1,
     thf=100, shf=176, thb=250, shb=264, sq=-0.06)
pose("h_reach", T=66, H=42, uaf=178, faf=178, uab=230, fab=250, nosw=1,
     thf=100, shf=196, thb=220, shb=262)
pose("h_bare_ready", T=12, H=6, uaf=135, faf=70, uab=160, fab=100, nosw=1,
     thf=140, shf=182, thb=218, shb=200)
pose("h_lie", "fallen", T=-88, H=-92, uaf=-40, faf=-60, uab=-10, fab=-30, sw=-80,
     thf=96, shf=92, thb=104, shb=96)

# ---------------------------------------------------------------- brute poses
pose("br_back_wind", T=-10, H=-6, uaf=200, faf=205, sw=200, grip=0, uab=290, fab=300,
     thf=95, shf=185, thb=150, shb=265)
pose("br_backhand", T=26, H=16, uaf=200, faf=205, sw=200, grip=0, uab=70, fab=80,
     thf=95, shf=185, thb=150, shb=265)
pose("br_roar", T=-16, H=-26, uaf=110, faf=60, sw=30, grip=0, uab=250, fab=230,
     thf=140, shf=182, thb=220, shb=200)
pose("br_press", "slam", T=40, H=30, sw=96)

# ---------------------------------------------------------------- chief poses
pose("c_point", T=0, H=-4, uaf=92, faf=90, sw=90, grip=0, uab=195, fab=180,
     thf=158, shf=182, thb=204, shb=188)
pose("c_walk1", "guard", T=4, thf=160, shf=185, thb=200, shb=215)
pose("c_walk2", "guard", T=4, thf=200, shf=188, thb=162, shb=176)
pose("c_lunge", "side_cut", T=36, H=24, thf=108, shf=172, thb=248, shb=250)
pose("c_hurt_arm", T=-14, H=-12, uaf=150, faf=70, sw=60, grip=0, uab=120, fab=60,
     thf=152, shf=182, thb=212, shb=196)
pose("c_cut_thru", T=-6, H=-22, uaf=150, faf=120, sw=90, grip=0, uab=60, fab=70,
     thf=146, shf=182, thb=216, shb=200, sq=-0.04)


def build(drawn=True):
    ids = ["C", "S", "B", "D", "R"]          # draw order: the ronin on top
    face0 = dict(R=1, S=1, C=1, D=-1, B=-1)
    T = {w: Track(facing=face0[w]) for w in ids}
    X = {}
    ev = []
    ST = {w: [] for w in ids}    # state windows (t0, t1, dict)
    ROT = {w: 0.0 for w in ids}  # whole turns already spun (flips, rolls), so nothing unwinds

    def E(t, kind, **kw):
        ev.append((t, kind, kw))

    def K(w, t, name, x=None, e="io", **kw):
        if x is None:
            x = X[w]
        X[w] = x
        kw["rot"] = ROT[w] + kw.get("rot", 0)
        for a, b, d in ST[w]:
            if a <= t < b:
                for k, v in d.items():
                    kw.setdefault(k, v)
        T[w].key(t, name, x, e, **kw)

    def face(w, t, f):
        T[w].face(t, f)

    def stop(t, d):
        E(t, "hitstop", dur=d)

    # ---------------------------------------------------------------- who holds what
    T_DISARM = 26.05         # the Chief's fury combo knocks the katana away
    T_PICK = 27.95           # ...the ronin pulls it out of the ground
    ST["R"].append((0.0, 4.55, dict(sheath=1)))
    ST["R"].append((T_DISARM, T_PICK, dict(nosw=1)))
    ST["R"].append((29.10, 99, dict(sheath=1)))

    # =========================================================== 0-5 the ambush
    E(0.0, "frame", ids=["R"])
    rx = -150
    K("R", 0.0, "h_walk1", rx)
    for i in range(6):
        tt = 0.34 * (i + 1)
        rx += 26
        K("R", tt, "h_walk2" if i % 2 == 0 else "h_walk1", rx)
        E(tt, "step", who="R", v=0.35)
    K("R", 2.30, "h_hand", rx + 4)            # stops: something is wrong
    rx += 4                                     # 10
    # Daggers drops out of the sky in front of him
    K("D", 0.0, "t_tuck", 210, air=520)
    K("D", 1.00, "t_tuck", 210, air=520)
    K("D", 1.30, "t_ready", 190, "in", air=0, sq=-0.18, T=30)
    E(1.30, "ground", x=190, v=0.8)
    E(1.30, "dust", x=190, v=0.7)
    K("D", 1.60, "t_ready", 188, "out")
    E(1.05, "frame", ids=["R", "D"])
    E(1.55, "twirl", dur=0.4)
    K("D", 1.95, "t_ready", 186, sw=55 + 360, sw2=100 - 360)
    # Brute stomps in behind Daggers, cleaver on his shoulder
    bx = 554
    K("B", 0.0, "heavy1", bx)
    K("B", 1.40, "heavy1", bx)
    for i in range(4):
        tt = 1.40 + 0.42 * (i + 1)
        bx -= 62
        K("B", tt, "heavy2" if i % 2 == 0 else "heavy1", bx)
        E(tt, "step", who="B", v=0.9)
        E(tt, "dust", x=bx, v=0.35)
    K("B", 3.40, "shoulder", bx - 6)            # 386
    bx -= 6
    E(1.95, "frame", ids=["R", "D", "B"])
    # Spear runs in behind him from the left and twirls
    sx = -574
    K("S", 0.0, "sp_run1", sx)
    K("S", 1.80, "sp_run1", sx)
    for i in range(5):
        tt = 1.80 + 0.16 * (i + 1)
        sx += 72
        K("S", tt, "sp_run2" if i % 2 == 0 else "sp_run1", sx)
        E(tt, "step", who="S", v=0.4)
    K("S", 2.85, "sp_twirl", sx + 14)           # -246
    sx += 14
    E(2.85, "twirl", dur=0.5)
    K("S", 3.35, "sp_guard", sx, sw=84 + 360)
    E(2.35, "frame", ids=["R", "D", "B", "S"])
    # the ronin turns at the footsteps behind him, then back
    face("R", 2.70, -1)
    K("R", 2.75, "h_hand", rx, T=4)
    # the Chief strolls up last
    cx = -600
    K("C", 0.0, "shoulder", cx)
    K("C", 2.60, "shoulder", cx)
    for i in range(5):
        tt = 2.60 + 0.30 * (i + 1)
        cx += 48
        K("C", tt, "c_walk2" if i % 2 == 0 else "c_walk1", cx, uaf=165, faf=25, sw=-130, grip=0)
        E(tt, "step", who="C", v=0.35)
    K("C", 4.35, "shoulder", cx)                # -530
    E(2.95, "frame", ids=["R", "D", "B", "S", "C"])
    face("R", 3.55, 1)
    K("R", 3.60, "h_hand", rx)
    E(0.05, "drum", v=0.8)
    # hand to the hilt... draw
    K("R", 3.95, "iai", rx, "io")
    K("R", 4.40, "iai_deep", rx - 4, "out")
    E(4.40, "heart", v=0.8)
    K("R", 4.62, "guard", rx - 4, "snap")
    E(4.55, "draw", v=1.0)
    rx -= 4                                     # 6
    E(4.62, "banner", text="FIGHT!")
    E(4.62, "fight")
    E(4.90, "frame", ids=["R", "S", "D"])
    # INTERWORLD-style aura phonk: the drop lands on the final quick-draw
    K("D", 4.62, "t_ready", 186, sw=55 + 360, sw2=100 - 360)
    K("B", 4.62, "shoulder", bx)
    K("C", 4.62, "shoulder", cx)

    # D keeps his twirl offset from here on
    def DK(t, name, x=None, e="io", **kw):
        base = P[name]
        kw["sw"] = kw.get("sw", base["sw"]) + 360
        kw["sw2"] = kw.get("sw2", base["sw2"]) - 360
        K("D", t, name, x, e, **kw)

    def SK(t, name, x=None, e="io", **kw):
        kw["sw"] = kw.get("sw", P[name]["sw"]) + 360
        K("S", t, name, x, e, **kw)

    # =========================================================== 5-8 first blood
    # beat 1: Spear stabs at his back; he spins and parries
    t = 5.10
    SK(t - 0.18, "sp_wind", sx + 6, "back")
    SK(t, "sp_thrust", sx + 60, "snap")
    E(t - 0.06, "thrust", v=0.9)
    face("R", t - 0.12, -1)
    K("R", t - 0.10, "guard", rx + 4, "io")
    K("R", t - 0.01, "parry", rx + 10, "snap")
    E(t, "clash", a="R", b="S", v=1.0)
    stop(t, 0.07)
    SK(t + 0.22, "sp_guard", sx + 40, "out")
    sx += 40                                    # -206
    K("R", t + 0.20, "guard", rx + 14, "out")
    rx += 14                                    # 20
    # beat 2: Daggers rushes his back; he ducks the slash, turns, front kick
    t = 5.70
    DK(t - 0.22, "t_ready", 186, "back", sq=-0.14, T=24)
    DK(t - 0.08, "t_dash", 150, "lin")
    E(t - 0.20, "zip", v=0.8)
    DK(t, "t_h1_wind", 132, "out")
    DK(t + 0.10, "t_h1", 112, "snap")
    K("R", t + 0.02, "h_duck", rx - 6, "snap")
    face("R", t + 0.20, 1)
    k = t + 0.38
    K("R", k - 0.12, "kick_wind", rx - 4, "back")
    K("R", k, "kick", rx + 20, "snap")
    E(k, "hit", by="R", on="D", v=1.0, part="ftf")
    stop(k, 0.07)
    DK(k + 0.02, "t_hurt", 150, "snap")
    DK(k + 0.30, "t_hurt", 236, "out", T=-14)
    E(k + 0.30, "skid", x=236, v=0.8)
    DK(k + 0.60, "t_ready", 240, "io")
    K("R", k + 0.26, "guard", rx + 6, "out")
    rx += 6                                     # 26
    # beat 3: Spear's low thrust at his legs: he jumps it and cuts down
    t = 6.65
    SK(t - 0.20, "sp_guard_lo", sx + 6, "io")
    SK(t, "sp_thrust_lo", sx + 70, "snap")
    E(t - 0.06, "thrust", v=0.9)
    face("R", t - 0.24, -1)
    K("R", t - 0.14, "crouch", rx, "back", sq=-0.14)
    K("R", t + 0.04, "jump_tuck", rx - 40, "out", air=64)
    E(t - 0.14, "dust", x=rx, v=0.5)
    sx += 70                                    # -136
    c1 = t + 0.30
    K("R", c1, "land_cut", sx + 150, "snap")
    E(c1, "hit", by="R", on="S", v=1.2, big=True, blood=20)
    E(c1, "ground", x=sx + 150, v=0.6)
    stop(c1, 0.11)
    E(c1 - 0.06, "slowmo", a0=c1 - 0.06, a1=c1 + 0.16, rate=0.4)
    rx = sx + 150                               # 14
    SK(c1 + 0.03, "sp_hurt", sx - 10, "snap")
    SK(c1 + 0.55, "kneel", sx - 16, "in")
    E(c1 + 0.55, "thud", v=0.7)
    SK(c1 + 1.15, "fallen", sx - 10, "in")
    E(c1 + 1.15, "thud", v=0.9)
    E(c1 + 1.15, "dust", x=sx + 30, v=0.7)
    K("R", c1 + 0.45, "guard", rx, "out")
    E(c1 + 0.35, "frame", ids=["R", "D", "B"])

    # =========================================================== 8-16 overwhelmed
    # beat 4: Brute charges and brings the cleaver down; the ronin blocks, pinned
    face("R", 7.45, 1)
    t = 8.20
    for i in range(3):
        tt = 7.20 + 0.24 * i
        bx -= 15
        K("B", tt, "heavy2" if i % 2 == 0 else "heavy1", bx)
        E(tt, "step", who="B", v=1.0)
    K("B", t - 0.24, "heavy_wind", bx - 10, "back")
    K("B", t, "slam", bx - 70, "snap", sw=96)
    bx -= 70                                    # 170
    E(t, "riser", dur=0.3)
    K("R", t - 0.14, "guard", rx + 4, "io")
    K("R", t - 0.03, "block_high", rx + 6, "snap")
    E(t, "clash", a="R", b="B", v=1.3, big=True)
    stop(t, 0.10)
    K("R", t + 0.16, "brace", rx - 8, "snap", sq=-0.12)
    E(t + 0.16, "skid", x=rx - 8, v=0.9)
    K("B", t + 0.16, "br_press", bx - 40, "snap")
    E(t + 0.16, "scrape", a="R", b="B", dur=0.55, v=0.8)
    rx -= 8                                     # 6
    # beat 5: Daggers flips over them both and cuts his shoulder from behind
    DK(t - 0.10, "t_ready", 236, "io")
    DK(t + 0.02, "t_ready", 230, "back", sq=-0.16, T=24)
    DK(t + 0.30, "t_tuck", 80, "out", air=150, rot=-180)
    face("D", t + 0.32, 1)
    DK(t + 0.52, "t_tuck", -100, "in", air=40, rot=-360)
    DK(t + 0.60, "t_ready", -110, "out", sq=-0.16, rot=-360)
    ROT["D"] = -360
    E(t + 0.60, "ground", x=-110, v=0.6)
    E(t + 0.30, "zip", v=0.7)
    h = t + 0.84
    DK(h - 0.12, "t_h2_wind", -90, "back")
    DK(h, "t_h2", -64, "snap")
    E(h, "hit", by="D", on="R", v=1.1, big=True, limb=("sho", "elb", 0.25), blood=14, dmg=0)
    stop(h, 0.09)
    K("R", h - 0.10, "brace", rx, "io")
    K("R", h + 0.04, "brace", rx + 6, "snap", T=-6, H=-16)
    K("B", h, "br_press", bx - 42, "io")
    # beat 6: he kicks the Brute off and spins to Daggers
    k = h + 0.32
    K("R", k - 0.12, "kick_wind", rx + 4, "back", uaf=60, faf=-10, sw=95)
    K("R", k, "kick", rx + 22, "snap", uaf=60, faf=-10, sw=95)
    E(k, "hit", by="R", on="B", v=1.2, part="ftf")
    stop(k, 0.08)
    K("B", k + 0.02, "stagger", bx + 20, "snap")
    K("B", k + 0.40, "stagger", bx + 96, "out")
    E(k + 0.40, "skid", x=bx + 96, v=1.0)
    bx += 96                                    # 266
    K("B", k + 0.80, "guard", bx, "io")
    face("R", k + 0.14, -1)
    K("R", k + 0.22, "guard", rx + 10, "out")
    rx += 10                                    # 16
    # beat 7: Daggers' three-cut flurry, every one blocked, he gives ground
    dx = -64
    f0 = k + 0.42
    for i, (wd, st_, blk, bkw) in enumerate((("t_h1_wind", "t_h1", "block_mid", {}),
                                             ("t_h2_wind", "t_h2", "block_high", {}),
                                             ("t_high1_wind", "t_high1", "parry", {}))):
        ti = f0 + 0.30 * i
        DK(ti - 0.12, wd, dx + 8, "back")
        DK(ti, st_, dx + 26, "snap")
        dx += 18
        K("R", ti - 0.08, "guard", rx + 6, "io")
        K("R", ti - 0.01, blk, rx + 12, "snap", **bkw)
        rx += 12
        E(ti, "clash", a="R", b="D", v=0.9, blade=2 if i == 1 else 1)
        stop(ti, 0.05)
    # beat 8: Brute's sweep: the ronin ducks, Daggers takes it
    t = f0 + 0.98                               # ~10.05
    K("B", t - 0.50, "heavy1", bx - 40)
    E(t - 0.50, "step", who="B", v=1.0)
    K("B", t - 0.24, "sweep_wind", bx - 70, "back")
    K("B", t, "sweep", bx - 120, "snap")
    bx -= 120                                   # 146
    DK(t - 0.20, "t_h1_wind", dx + 10, "back")
    DK(t - 0.04, "t_h1", dx + 34, "snap")
    dx += 34
    K("R", t - 0.16, "guard", rx, "io")
    K("R", t - 0.05, "h_duck", rx - 4, "snap")
    E(t, "hit", by="B", on="D", v=1.4, big=True, blood=26, dmg=0)
    stop(t, 0.13)
    E(t - 0.12, "slowmo", a0=t - 0.12, a1=t + 0.12, rate=0.35)
    DK(t + 0.04, "t_hurt", dx - 30, "snap")
    DK(t + 0.40, "t_hurt", dx - 120, "out", air=30, T=-40)
    DK(t + 0.70, "fallen", dx - 150, "in")
    E(t + 0.70, "thud", v=1.0)
    E(t + 0.70, "dust", x=dx - 150, v=0.9)
    E(t + 0.55, "frame", ids=["R", "B"])
    # beat 9: from the crouch, he cuts the Brute's front leg
    face("R", t + 0.08, 1)
    c2 = t + 0.30
    K("R", c2 - 0.12, "h_duck", rx, "io", uaf=225, faf=-30, sw=-95)
    K("R", c2, "h_low_cut", rx + 30, "snap")
    E(c2, "hit", by="R", on="B", v=1.2, limb=("knf", "ftf", 0.3), blood=14)
    stop(c2, 0.08)
    rx += 30
    K("B", c2 + 0.04, "stagger", bx + 6, "snap")
    K("B", c2 + 0.36, "kneel", bx + 10, "in", sw=150)
    E(c2 + 0.36, "thud", v=0.9)
    bx += 10                                    # 156
    # beat 10: on one knee, the Brute backhands him across the meadow
    b_ = c2 + 0.62
    K("R", c2 + 0.36, "guard", rx + 8, "out")
    rx += 8                                     # ~54
    K("B", b_ - 0.20, "br_back_wind", bx, "back")
    K("B", b_, "br_backhand", bx - 4, "snap")
    E(b_, "hit", by="B", on="R", v=1.5, big=True, part="hab")
    stop(b_, 0.10)
    K("R", b_ + 0.02, "recoil", rx - 40, "snap")
    K("R", b_ + 0.30, "tumble", rx - 220, "out", air=70, rot=-200)
    K("R", b_ + 0.56, "h_lie", rx - 330, "in", rot=-360)
    E(b_ + 0.56, "thud", v=1.0)
    E(b_ + 0.56, "dust", x=rx - 330, v=1.0)
    K("R", b_ + 0.80, "h_lie", rx - 350, "out", rot=-360)
    ROT["R"] = -360
    E(b_ + 0.80, "skid", x=rx - 350, v=0.8)
    rx -= 350                                   # ~-296
    # Brute gets up and roars; the ronin pushes himself up
    K("B", b_ + 0.50, "kneel", bx, "io", sw=150)
    K("B", b_ + 0.95, "guard", bx - 6, "io")
    K("B", b_ + 1.35, "br_roar", bx - 10, "out")
    E(b_ + 1.35, "roar", v=1.0)
    E(b_ + 1.35, "radial", v=0.6)
    K("B", b_ + 1.85, "guard", bx - 14, "io")
    bx -= 14                                    # 142
    K("R", b_ + 1.30, "h_getup", rx + 6, "io")
    K("R", b_ + 1.85, "h_pant", rx + 10, "io")
    rx += 10
    # beat 11: overhead slam #1, he hops back, the ground breaks
    t = b_ + 2.40                               # ~13.7
    for i in range(2):
        tt = b_ + 1.95 + 0.20 * i
        bx -= 48
        K("B", tt, "heavy2" if i % 2 == 0 else "heavy1", bx, uaf=150, faf=95, sw=52, grip=1)
        E(tt, "step", who="B", v=1.0)
    K("B", t - 0.26, "heavy_wind", bx - 10, "back")
    K("B", t, "slam", bx - 60, "snap")
    bx -= 60
    E(t, "slam", by="B", v=1.3)
    stop(t, 0.08)
    K("R", t - 0.20, "h_pant", rx, "io")
    K("R", t - 0.08, "crouch", rx - 10, "back")
    K("R", t + 0.08, "jump_tuck", rx - 60, "out", air=26)
    K("R", t + 0.24, "guard", rx - 80, "in", sq=-0.1)
    E(t + 0.24, "ground", x=rx - 80, v=0.4)
    rx -= 80
    # beat 12: he jumps the low sweep and takes the head in the air
    t2 = t + 0.80
    K("B", t + 0.30, "slam", bx, "io", T=40)
    K("B", t2 - 0.26, "sweep_wind", bx + 4, "back", T=22, thf=125, thb=235)
    K("B", t2, "sweep", bx - 40, "snap", T=40, thf=110, thb=246, shb=250, sw=96)
    bx -= 40
    K("R", t2 - 0.22, "guard", rx + 6, "io")
    K("R", t2 - 0.12, "crouch", rx + 10, "back", sq=-0.16)
    E(t2 - 0.12, "dust", x=rx + 10, v=0.6)
    K("R", t2 + 0.04, "h_tuck_wind", rx + 80, "out", air=96)
    E(t2 + 0.02, "zip", v=0.9)
    kd = t2 + 0.16
    K("R", kd, "h_tuck_cut", rx + 150, "snap", air=110)
    E(kd, "decap", who="B", by="R")
    stop(kd, 0.14)
    E(kd - 0.10, "slowmo", a0=kd - 0.10, a1=kd + 0.20, rate=0.3)
    K("R", kd + 0.30, "land_cut", rx + 200, "in", air=0, sq=-0.12)
    E(kd + 0.30, "ground", x=rx + 200, v=0.6)
    rx += 200
    K("R", kd + 0.80, "h_pant", rx + 4, "io")
    ST["B"].append((kd + 0.001, 99, dict(headless=1)))
    K("B", kd + 0.04, "sweep", bx - 4, "io", T=30)
    K("B", kd + 0.70, "kneel", bx, "in", sw=150)
    E(kd + 0.70, "thud", v=1.0)
    K("B", kd + 1.40, "fallen", bx - 20, "in", sw=100)
    E(kd + 1.40, "thud", v=1.2)
    E(kd + 1.40, "dust", x=bx - 60, v=1.2)
    T_BDEAD = kd

    # =========================================================== 16-27 the Chief
    E(kd + 1.10, "frame", ids=["R", "C"])
    face("R", kd + 1.50, -1)
    K("R", kd + 1.60, "h_pant", rx + 2, "io")
    K("R", kd + 1.95, "sw_chiburi", rx + 2, "snap")    # flicks the blood off
    E(kd + 1.95, "swoosh", v=0.7)
    K("R", kd + 2.40, "guard", rx, "io")
    # he backs away from the bodies, eyes on the Chief
    for i in range(5):
        tt = kd + 2.70 + 0.30 * (i + 1)
        rx += 50
        K("R", tt, "walk2" if i % 2 == 0 else "walk1", rx)
        E(tt, "step", who="R", v=0.35)
    K("R", kd + 4.40, "h_pant", rx + 4, "io")
    rx += 4
    # the Chief takes the blade off his shoulder and walks in, calm
    ch = kd + 1.40
    K("C", ch, "shoulder", cx)
    K("C", ch + 0.40, "c_point", cx + 6, "out")
    E(ch + 0.40, "swoosh", v=0.6)
    K("C", ch + 1.05, "guard", cx + 6, "io")
    for i in range(8):
        tt = ch + 1.05 + 0.30 * (i + 1)
        cx += 52
        K("C", tt, "c_walk2" if i % 2 == 0 else "c_walk1", cx)
        E(tt, "step", who="C", v=0.4)
    K("C", ch + 3.55, "guard", cx + 6, "io")
    cx += 6
    # beat 13: three fast cuts, all clash
    t = ch + 4.00                               # ~19.0
    E(t - 0.30, "zip", v=1.0)
    K("C", t - 0.36, "guard", cx, "back", sq=-0.14, T=20)
    K("C", t - 0.14, "dash", rx - 150, "lin", sw=-80, grip=1, uaf=225, faf=-30)
    K("C", t - 0.06, "side_wind", rx - 150, "out")
    K("C", t, "side_cut", rx - 140, "snap")
    cx = rx - 140
    K("R", t - 0.06, "guard", rx, "io")
    K("R", t - 0.01, "block_mid", rx + 4, "snap")
    E(t, "clash", a="R", b="C", v=1.2, big=True)
    stop(t, 0.08)
    for i, (wd, st_, blk) in enumerate((("rise_wind", "rise_cut", "block_high"),
                                        ("high_wind", "high_cut", "block_high"))):
        ti = t + 0.32 * (i + 1)
        K("C", ti - 0.13, wd, cx + 6, "back")
        K("C", ti, st_, cx + 20, "snap")
        cx += 20
        K("R", ti - 0.08, "guard", rx + 8, "io")
        K("R", ti - 0.01, blk, rx + 14, "snap")
        rx += 14
        E(ti, "clash", a="R", b="C", v=1.0)
        stop(ti, 0.06)
    # beat 14: kick, then the cut gets through: his thigh
    k = t + 0.98
    K("C", k - 0.12, "kick_wind", cx + 4, "back")
    K("C", k, "kick", cx + 30, "snap")
    E(k, "hit", by="C", on="R", v=1.1, part="ftf")
    stop(k, 0.07)
    K("R", k + 0.02, "stagger", rx + 30, "snap")
    K("R", k + 0.26, "stagger", rx + 70, "out")
    rx += 70
    cx += 30
    h = k + 0.50
    K("C", h - 0.14, "side_wind", cx + 30, "back")
    K("C", h, "c_lunge", cx + 90, "snap")
    cx += 90
    E(h - 0.10, "zip", v=0.8)
    K("R", h - 0.06, "stagger", rx, "io")
    E(h, "hit", by="C", on="R", v=1.3, big=True, limb=("knf", "ftf", 0.2), blood=16)
    stop(h, 0.10)
    E(h - 0.06, "slowmo", a0=h - 0.06, a1=h + 0.12, rate=0.4)
    K("R", h + 0.04, "stagger", rx + 10, "snap")
    K("R", h + 0.36, "h_getup", rx + 16, "in")
    E(h + 0.36, "thud", v=0.7)
    rx += 16
    # beat 15: he answers from his knee: a cut to the Chief's arm
    K("C", h + 0.30, "guard", cx - 10, "out")
    cx -= 10
    a_ = h + 0.80
    K("C", a_ - 0.20, "high_wind", cx + 4, "back")
    K("C", a_, "high_cut", cx + 24, "snap")
    cx += 24
    K("R", a_ - 0.08, "h_getup", rx, "io")
    K("R", a_ - 0.01, "h_kneel_block", rx, "snap")
    E(a_, "clash", a="R", b="C", v=1.1, big=True)
    stop(a_, 0.08)
    a2 = a_ + 0.30
    K("R", a2 - 0.10, "h_kneel_block", rx, "back", uaf=225, faf=-30, sw=-95)
    K("R", a2, "h_kneel_cut", rx + 6, "snap")
    E(a2, "hit", by="R", on="C", v=1.2, limb=("sho", "elf", 0.6), blood=14)
    stop(a2, 0.08)
    K("C", a2 + 0.02, "c_hurt_arm", cx - 30, "snap")
    K("C", a2 + 0.40, "c_hurt_arm", cx - 90, "out")
    E(a2 + 0.40, "skid", x=cx - 90, v=0.7)
    cx -= 90
    K("R", a2 + 0.50, "h_getup", rx, "io")
    K("R", a2 + 1.00, "h_pant", rx + 4, "io")
    rx += 4
    # the Chief looks at the cut... and gets angry
    K("C", a2 + 0.95, "c_hurt_arm", cx, "io", H=10)
    K("C", a2 + 1.35, "guard", cx + 4, "snap", T=24, sq=-0.08)
    E(a2 + 1.35, "heart", v=0.8)
    cx += 4
    # beat 16: fury combo, the fourth cut knocks the katana away
    f0 = T_DISARM - 0.96
    E(f0 - 0.30, "zip", v=0.9)
    K("C", f0 - 0.30, "guard", cx + 30, "back", sq=-0.14)
    combo = (("side_wind", "side_cut", "block_mid"), ("rise_wind", "rise_cut", "block_high"),
             ("high_wind", "high_cut", "block_high"), ("side_wind", "c_lunge", "block_mid"))
    for i, (wd, st_, blk) in enumerate(combo):
        ti = f0 + 0.32 * i
        K("C", ti - 0.13, wd, rx - 172 + 8 * i, "back")
        K("C", ti, st_, rx - 150 + 8 * i, "snap")
        K("R", ti - 0.08, "h_pant" if i == 0 else "guard", rx + 6, "io")
        K("R", ti - 0.01, blk, rx + 14, "snap")
        rx += 14
        if i < 3:
            E(ti, "clash", a="R", b="C", v=1.0 + 0.1 * i)
            stop(ti, 0.06)
    cx = rx - 150 + 24
    E(T_DISARM, "clash", a="R", b="C", v=1.4, big=True)
    stop(T_DISARM, 0.10)
    E(T_DISARM, "loose", id=1, lk="fling", who="R", second=False, tl=T_DISARM + 0.62,
      xl=rx + 250, land_ang=200, spin=2, tp=T_PICK)
    E(T_DISARM + 0.62, "swordland", v=1.0)
    K("R", T_DISARM + 0.001, "block_mid", rx)
    K("R", T_DISARM + 0.02, "recoil", rx + 20, "snap")
    K("R", T_DISARM + 0.40, "h_getup", rx + 40, "in", uaf=170, faf=150)
    E(T_DISARM + 0.40, "thud", v=0.6)
    rx += 40
    # beat 17: finishing blow at a kneeling, unarmed man... he rolls to his sword
    K("C", T_DISARM + 0.30, "guard", cx + 10, "out")
    cx += 10
    K("C", T_DISARM + 0.65, "c_walk1", cx + 40)
    E(T_DISARM + 0.65, "step", who="C", v=0.5)
    K("C", T_DISARM + 0.95, "high_wind", cx + 70, "io")
    cx += 70
    fb = T_DISARM + 1.25
    K("C", fb, "high_cut", cx + 50, "snap", T=40)
    E(fb, "ground", x=cx + 160, v=1.0)
    E(fb, "dust", x=cx + 160, v=1.0)
    stop(fb, 0.06)
    cx += 50
    K("R", fb - 0.24, "h_getup", rx, "io")
    K("R", fb - 0.08, "tumble", rx + 70, "out", rot=-120, air=30)
    K("R", fb + 0.20, "tumble", rx + 170, "lin", rot=-300, air=20)
    K("R", fb + 0.40, "h_reach", rx + 220, "in", rot=-360)
    ROT["R"] -= 360
    E(fb + 0.40, "dust", x=rx + 220, v=0.7)
    rx += 220
    face("R", fb + 0.30, -1)
    K("R", T_PICK, "h_reach", rx + 6, "io", nosw=0, sw=200)
    K("R", T_PICK + 0.30, "guard", rx + 10, "out")
    rx += 10
    # he puts it away and waits
    K("C", fb + 0.40, "high_cut", cx, "io", T=30)
    K("C", fb + 0.90, "guard", cx - 10, "io")
    cx -= 10
    K("R", T_PICK + 0.70, "sheathing", rx, "io")
    K("R", 29.10, "iai", rx - 4, "snap")
    E(29.10, "sheathe", v=0.9)
    K("R", 30.20, "iai_deep", rx - 8, "io")
    E(29.60, "heart", v=1.0)
    E(30.40, "heart", v=1.0)
    E(29.20, "cam", until=32.9, zoom=1.25, who="R", pull=0.4, rate=0.04)
    # the Chief walks in, angry, then charges
    for i in range(4):
        tt = 29.20 + 0.42 * (i + 1)
        cx += 28
        K("C", tt, "c_walk2" if i % 2 == 0 else "c_walk1", cx)
        E(tt, "step", who="C", v=0.45)
    K("C", 31.20, "guard", cx + 4, "io")
    cx += 4
    E(31.20, "heart", v=1.1)
    E(31.90, "heart", v=1.2)
    # =========================================================== the quick-draw
    tc = 32.70
    K("C", tc - 0.30, "guard", cx, "back", sq=-0.16, T=24)
    E(tc - 0.30, "zip", v=1.1)
    K("C", tc - 0.06, "dash", cx + 70, "lin", sw=-115, uaf=15, faf=-15, grip=1)
    K("C", tc + 0.10, "high_wind", cx + 120, "out", air=40)
    E(tc - 0.10, "dust", x=cx, v=0.8)
    cx += 120
    K("R", tc - 0.10, "iai_deep", rx - 10, "io")
    tk = tc + 0.22
    E(tc + 0.02, "slowmo", a0=tc + 0.02, a1=tk + 0.02, rate=0.28)
    K("R", tk - 0.02, "iai_deep", rx - 12, "io")
    K("R", tk + 0.04, "iai_cut", cx - 170, "lin", sheath=0)
    E(tk - 0.02, "iai")
    K("C", tk - 0.02, "high_cut", cx + 10, "io", air=10, T=10)
    K("C", tk + 0.06, "c_cut_thru", cx + 14, "snap", air=0)
    E(tk + 0.04, "hit", by="R", on="C", v=1.4, big=True, blood=26, nosolve=True,
      contact=None)
    E(tk + 0.05, "kill", song=True)
    E(4.62, "song", name="song_murder_in_my_mind", drop=17.03, drop_at=tk + 0.04,
      duck_at=tc - 0.9, pre=0.34, duck=0.12, post=0.95)
    stop(tk + 0.04, 0.06)
    rx = cx - 170
    fz = tk + 0.18
    K("R", fz, "iai_hold", rx - 6, "out", sheath=0)
    K("C", fz, "c_cut_thru", cx + 12)
    E(fz, "freezeframe", dur=1.3, zoom=0.20, x=(rx + cx) / 2)
    # the frame lets go: blood, he drops
    E(fz + 0.04, "dmg", who="C", by="R", amt=0, big=True)
    K("C", fz + 0.55, "kneel", cx + 8, "in", sw=150, uaf=170, faf=150)
    E(fz + 0.55, "thud", v=0.8)
    K("C", fz + 1.30, "fallen", cx + 24, "in", sw=100)
    E(fz + 1.30, "thud", v=1.0)
    E(fz + 1.30, "dust", x=cx + 60, v=1.0)
    K("R", fz + 0.70, "iai_hold", rx - 6, "io", sheath=0)
    K("R", fz + 1.25, "sw_chiburi", rx - 6, "snap", sheath=0)
    E(fz + 1.25, "swoosh", v=0.8)
    K("R", fz + 1.85, "sheathing", rx - 6, "io", sheath=0)
    K("R", fz + 2.25, "stand_sheathed", rx - 6, "snap", sheath=1)
    E(fz + 2.25, "sheathe", v=1.0, final=True)
    E(fz + 1.0, "winner", name="RONIN WINS", color="#d8323c")
    # he walks on, limping a little
    face("R", fz + 2.70, -1)
    x_ = rx - 6
    for i in range(4):
        tt = fz + 2.70 + 0.40 * (i + 1)
        x_ -= 24
        K("R", tt, "h_walk2" if i % 2 == 0 else "h_walk1", x_, sheath=1)
    end = fz + 4.40
    K("R", end, "h_walk1", x_ - 6, sheath=1)
    E(fz + 0.2, "frame", ids=["R", "C"])
    for w in ids:
        T[w].key(end, T[w].keys[-1][1], T[w].keys[-1][2])
    title = (("RONIN", NAVY), ("4 BANDITS", CRIMSON))
    return dict(fighters=[(w, T[w], dict(RONIN=RONIN, S=SPEARMAN, D=DAGGERS, B=BRUTE,
                                         C=CHIEF)["RONIN" if w == "R" else w]) for w in ids],
                events=ev, end=end, title=title,
                springy=True, fluid=True, drawn=drawn, theme="meadow", red_hits=True)
