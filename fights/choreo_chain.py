"""Fight 08: "CHAIN SICKLE vs TWIN SWORDS" (Sangam's choreography, 18 beats).

KUSARI (slate body, orange scarf) fights with a kusarigama: a sickle in the
front hand, a chain from the sickle's butt through the back hand to an iron
weight. Calm and tactical: circles, spins, feints, counters, keeps range.
TWIN (red body, black band) carries two katanas, one per hand, each keyed on
its own angle (sw / sw2): aggressive, fast, relentless.

Twin gets close twice (the cheek graze at the end of his rush, and the fourth
strike of the five-hit combo that stops an inch from Kusari's eye) before the
chain takes both swords away and the sickle ends at his neck.

The chain is simulated (chain.py): ``chain`` events only steer the weight;
the links trail, sag, go taut and recoil on their own.
"""
from rig import Track, pose

KUSARI = dict(name="KUSARI", body="#26303d", back="#55657a", band="#f08a24", sword="sickle",
              blade=24, butt=6, grip_off=9, blade_len=30, blade_ang=96, hold_len=62,
              wood="#6b4a2e", wrap="#1c2129", steel="#eef3f7", edge="#ffb347",
              ghost="#55657a", trail="#ffe4c2", limb=8.5, size=1.0,
              springs={"sw": (70, 0.55), "uab": (40, 0.55), "fab": (36, 0.5)})
TWIN = dict(name="TWIN", body="#b81f2e", back="#e0707a", band="#141414", twin=True,
            sword="katana", blade=62, butt=8, steel="#eef2f6", ghost="#e0707a",
            trail="#ffe0e0", limb=8.3, size=0.98)
ORANGE = "#e8771c"
RED = "#d22a38"

# ---------------------------------------------------------------- twin poses
L_READY = dict(thf=140, shf=180, thb=218, shb=200)
L_LUNGE = dict(thf=112, shf=172, thb=244, shb=232)
L_CROUCH = dict(thf=105, shf=200, thb=225, shb=262)
pose("t_ready", T=12, H=8, uaf=125, faf=60, sw=55, uab=150, fab=95, sw2=100, **L_READY)
pose("t_walk1", "t_ready", T=6, thf=160, shf=186, thb=200, shb=214)
pose("t_walk2", "t_ready", T=6, thf=198, shf=188, thb=162, shb=176)
pose("t_dash", T=55, H=40, uaf=225, faf=250, sw=250, uab=235, fab=262, sw2=240,
     thf=110, shf=160, thb=250, shb=268)
pose("t_h1_wind", T=-14, H=-4, uaf=235, faf=-35, sw=-95, uab=125, fab=70, sw2=60,
     thf=140, shf=182, thb=215, shb=198)
pose("t_h1", T=26, H=16, uaf=92, faf=90, sw=93, uab=205, fab=228, sw2=250, **L_LUNGE)
pose("t_h2_wind", T=20, H=12, uaf=105, faf=96, sw=105, uab=250, fab=290, sw2=-88, **L_LUNGE)
pose("t_h2", T=30, H=18, uaf=215, faf=232, sw=228, uab=92, fab=88, sw2=92,
     thf=108, shf=170, thb=246, shb=236)
pose("t_high1_wind", T=-8, H=-6, uaf=10, faf=-20, sw=-120, uab=135, fab=80, sw2=70,
     thf=145, shf=182, thb=210, shb=192)
pose("t_high1", T=30, H=22, uaf=118, faf=138, sw=140, uab=205, fab=220, sw2=248, **L_LUNGE)
pose("t_low2_wind", T=30, H=20, uaf=140, faf=80, sw=40, uab=230, fab=250, sw2=-110, **L_CROUCH)
pose("t_low2", T=46, H=32, uaf=165, faf=110, sw=60, uab=115, fab=110, sw2=100, **L_CROUCH)
pose("t_thrust_wind", T=-6, H=-2, uaf=205, faf=105, sw=92, uab=140, fab=90, sw2=80,
     thf=150, shf=182, thb=212, shb=196)
pose("t_thrust", T=32, H=22, uaf=88, faf=90, sw=91, uab=232, fab=252, sw2=232,
     thf=100, shf=168, thb=252, shb=262)
pose("t_cross", T=18, H=10, uaf=62, faf=40, sw=32, uab=58, fab=42, sw2=148,
     thf=100, shf=210, thb=140, shb=230)
pose("t_tuck", T=24, H=10, uaf=80, faf=50, sw=40, uab=230, fab=180, sw2=200,
     thf=62, shf=200, thb=100, shb=222)
pose("t_throw_wind", T=-10, H=-4, uaf=120, faf=60, sw=50, uab=-25, fab=-55, sw2=-70,
     thf=70, shf=200, thb=110, shb=222)
pose("t_throw", T=26, H=14, uaf=150, faf=90, sw=60, uab=105, fab=118, sw2=125,
     thf=110, shf=205, thb=150, shb=226)
pose("t_land", T=36, H=26, uaf=140, faf=70, sw=50, uab=40, fab=20, sw2=40, **L_CROUCH)
pose("t_catch", T=8, H=-6, uaf=140, faf=70, sw=50, uab=15, fab=0, sw2=30, **L_READY)
pose("t_rise2_wind", T=28, H=18, uaf=140, faf=75, sw=45, uab=205, fab=225, sw2=232, **L_CROUCH)
pose("t_rise2", T=-8, H=-6, uaf=170, faf=120, sw=110, uab=42, fab=30, sw2=22,
     thf=150, shf=180, thb=205, shb=192, air=4)
pose("t_over2_wind", T=-10, H=-6, uaf=150, faf=95, sw=80, uab=-2, fab=-28, sw2=-120,
     thf=145, shf=182, thb=210, shb=192)
pose("t_over2", T=30, H=22, uaf=200, faf=215, sw=245, uab=118, fab=140, sw2=140, **L_LUNGE)
pose("t_lean_back", T=-24, H=-28, uaf=160, faf=100, sw=70, uab=170, fab=120, sw2=120,
     thf=150, shf=178, thb=225, shb=205, sq=-0.06)
pose("t_overreach", T=40, H=30, uaf=140, faf=160, sw=160, uab=232, fab=252, sw2=245,
     thf=112, shf=174, thb=236, shb=240, sq=0.03)
pose("t_desp_wind", T=-16, H=-12, uaf=200, faf=235, sw=200, uab=-12, fab=-38, sw2=-105,
     thf=140, shf=182, thb=218, shb=200, sq=0.1)
pose("t_desp", T=32, H=24, uaf=230, faf=250, sw=230, uab=112, fab=132, sw2=138, **L_LUNGE)
pose("t_lost", T=-12, H=-38, uaf=160, faf=125, uab=178, fab=145, sw=60, sw2=60,
     thf=152, shf=182, thb=210, shb=196, nosw=1, nosw2=1)
pose("t_hurt", T=-22, H=-24, uaf=180, faf=120, sw=80, uab=215, fab=240, sw2=245,
     thf=158, shf=178, thb=214, shb=198, sq=-0.08)
pose("t_trip", T=40, H=20, uaf=110, faf=70, sw=60, uab=230, fab=260, sw2=230,
     thf=200, shf=150, thb=150, shb=215)

# ---------------------------------------------------------------- kusari poses
pose("k_idle", T=4, H=2, uaf=150, faf=70, sw=35, uab=172, fab=160, reel=62,
     thf=160, shf=182, thb=202, shb=188)
pose("k_ready", T=10, H=6, uaf=140, faf=62, sw=28, uab=150, fab=110, reel=58,
     thf=142, shf=182, thb=218, shb=200)
pose("k_walk1", "k_ready", thf=160, shf=186, thb=200, shb=214)
pose("k_walk2", "k_ready", thf=198, shf=188, thb=162, shb=176)
pose("k_sway", T=-30, H=-30, uaf=165, faf=115, sw=60, uab=205, fab=195, reel=58,
     thf=152, shf=178, thb=228, shb=206, sq=-0.06)
pose("k_hop", T=-10, H=-8, uaf=150, faf=90, sw=45, uab=200, fab=170, reel=58,
     thf=130, shf=210, thb=170, shb=228)
pose("k_spin_over", T=-4, H=-8, uaf=140, faf=72, sw=30, uab=-4, fab=6, reel=70,
     thf=140, shf=182, thb=220, shb=200)
pose("k_sling", T=26, H=14, uaf=170, faf=110, sw=60, uab=82, fab=86, reel=70, **L_LUNGE)
pose("k_throw", T=32, H=20, uaf=200, faf=150, sw=80, uab=88, fab=90, reel=70,
     thf=104, shf=170, thb=250, shb=246)
pose("k_block_hi", T=-6, H=-4, uaf=70, faf=20, sw=40, uab=150, fab=100, reel=58,
     thf=145, shf=180, thb=215, shb=198)
pose("k_block_lo", T=18, H=10, uaf=150, faf=120, sw=150, uab=160, fab=110, reel=58,
     thf=128, shf=185, thb=225, shb=212)
pose("k_deflect", T=14, H=6, uaf=120, faf=70, sw=130, uab=190, fab=170, reel=58,
     thf=135, shf=180, thb=222, shb=205)
pose("k_slip", T=-22, H=-38, uaf=150, faf=70, sw=25, uab=200, fab=180, reel=58,
     thf=150, shf=182, thb=226, shb=212, sq=-0.12)
pose("k_yank", T=-20, H=-12, uaf=120, faf=60, sw=30, uab=248, fab=268, reel=58,
     thf=124, shf=180, thb=232, shb=212, sq=-0.08)
pose("k_low", T=58, H=44, uaf=200, faf=175, sw=150, uab=105, fab=98, reel=70,
     thf=100, shf=205, thb=228, shb=264, sq=-0.15)
pose("k_lock", T=-8, H=-4, uaf=92, faf=48, sw=62, uab=110, fab=70, reel=58,
     thf=128, shf=180, thb=232, shb=212)
pose("k_slide", T=34, H=24, uaf=140, faf=90, sw=40, uab=225, fab=240, reel=58,
     thf=104, shf=160, thb=244, shb=258, sq=-0.12)
pose("k_taut", T=-6, H=-8, uaf=35, faf=28, sw=8, uab=-22, fab=-32, reel=50,
     thf=140, shf=182, thb=222, shb=204)
pose("k_taut_v", T=4, H=0, uaf=140, faf=110, sw=200, uab=60, fab=30, reel=50,
     thf=135, shf=182, thb=224, shb=205)
pose("k_twist", T=12, H=4, uaf=110, faf=100, sw=150, uab=40, fab=60, reel=50,
     thf=132, shf=182, thb=226, shb=206)
pose("k_point", T=30, H=18, uaf=105, faf=100, sw=8, uab=200, fab=180, reel=64,
     thf=138, shf=180, thb=232, shb=215)


def build(drawn=True):
    A = Track(facing=1)    # KUSARI, left
    B = Track(facing=-1)   # TWIN, right
    ev = []
    RA, RB = [0], [0]

    def E(t, kind, **kw):
        ev.append((t, kind, kw))

    def stop(t, d):
        E(t, "hitstop", dur=d)

    REEL = []     # (t0, t1, length): chain left paid out on the ground

    def AK(t, name, x, e="io", **kw):
        kw["rot"] = RA[0] + kw.get("rot", 0)
        for a, b, L in REEL:
            if a <= t <= b:
                kw.setdefault("reel", L)
        A.key(t, name, x, e, **kw)

    def BK(t, name, x, e="io", **kw):
        kw["rot"] = RB[0] + kw.get("rot", 0)
        B.key(t, name, x, e, **kw)

    # =========================================================== intro (0 - 2.0)
    ax, bx = -190, 440
    AK(0.0, "k_idle", ax)
    AK(0.9, "k_idle", ax, T=6, uab=150, fab=120)
    E(0.55, "chain", mode="spin", dur=1.15, r=34, turns=1.3, plane="side", c=(18, -6))
    E(0.55, "chainspin", dur=1.1, v=0.5)
    E(1.70, "chain", mode="free")
    AK(1.55, "k_ready", ax + 4)
    # twin strolls in, spinning both swords in turn
    BK(0.0, "t_walk1", bx)
    for i in range(5):
        tt = 0.28 * (i + 1)
        bx -= 42
        BK(tt, "t_walk2" if i % 2 == 0 else "t_walk1", bx, sw=55 + 360 * min(i, 2),
           sw2=100 - 360 * min(max(0, i - 2), 2))
        E(tt, "step", who="B", v=0.5)
    E(0.30, "twirl", dur=0.5)
    E(0.86, "twirl", dur=0.5)
    BK(1.62, "t_ready", bx - 6, sw=55 + 720, sw2=100 - 720)
    bx -= 6           # 224
    E(0.05, "drum", v=1.0)
    E(1.75, "banner", text="FIGHT!")
    E(1.75, "fight")
    # Mr.Kitty "After Dark": its drop lands on the final trap (the `kill` cue)
    E(1.75, "song", name="song_after_dark", drop=30.85, duck_at=13.0,
      pre=0.36, duck=0.14, post=0.95)

    # =========================================================== 1. dash + alternating slashes
    t = 2.05
    BK(t, "t_ready", bx + 8, sq=-0.16, T=24)               # coil
    BK(t + 0.16, "t_dash", ax + 215, "lin")
    E(t + 0.02, "zip", v=1.0)
    E(t + 0.02, "dust", x=bx, v=0.9)
    BK(t + 0.24, "t_h1_wind", ax + 192, "out")
    BK(t + 0.33, "t_h1", ax + 160, "snap")                  # front blade sweeps chest height
    AK(t + 0.20, "k_ready", ax - 6, "out")
    AK(t + 0.31, "k_sway", ax - 26, "snap")                 # leans back: misses by a hair
    BK(t + 0.42, "t_h2_wind", ax + 150, "out")
    BK(t + 0.52, "t_h2", ax + 118, "snap")
    AK(t + 0.40, "k_hop", ax - 60, "out", air=26)
    AK(t + 0.56, "k_hop", ax - 110, "io", air=6)
    ax -= 112        # -302
    AK(t + 0.64, "k_ready", ax, "in", sq=-0.12)
    E(t + 0.64, "ground", x=ax, v=0.4)
    BK(t + 0.70, "t_h2", ax + 205, "out", T=20)
    BK(t + 0.95, "t_ready", ax + 255, "io")
    bx = ax + 255

    # =========================================================== 2. dodge done, spin overhead
    t = 2.75
    AK(t + 0.05, "k_spin_over", ax + 4, "out")
    E(t + 0.02, "chain", mode="spin", dur=0.78, r=74, turns=2.4, plane="over", c=(-4, 14))
    E(t + 0.02, "chainspin", dur=0.78, v=1.0)
    AK(t + 0.45, "k_spin_over", ax + 10, T=-8)
    BK(t + 0.30, "t_walk1", bx - 14)
    E(t + 0.30, "step", who="B", v=0.4)
    BK(t + 0.62, "t_ready", bx - 24, T=16)
    bx -= 24         # -136

    # =========================================================== 3. weight swings out, twin retreats
    t = 3.55
    AK(t - 0.04, "k_spin_over", ax + 12, "back", T=-14)
    AK(t + 0.10, "k_sling", ax + 34, "snap")
    E(t, "chain", mode="path", dur=0.24, ease="out",
      pts=[(ax + 150, 150), ("Jf", "B", "head", 30, 2), (bx + 40, 120)])
    E(t, "chainthrow", v=0.8)
    BK(t + 0.06, "t_ready", bx + 4, "back")
    BK(t + 0.17, "t_lean_back", bx + 40, "snap")            # head snaps back from it
    BK(t + 0.40, "t_ready", bx + 60, "out")
    E(t + 0.26, "chain", mode="free")
    # recoil, second swing low at his knees: he hops back
    AK(t + 0.40, "k_ready", ax + 26, "io", uab=210, fab=200)
    AK(t + 0.62, "k_sling", ax + 40, "snap", uab=110, fab=120, T=30)
    E(t + 0.52, "chain", mode="path", dur=0.26, ease="out",
      pts=[(ax + 80, 50), ("Jf", "B", "knf", 26, -6), (bx + 150, 40)], lead=0.1)
    E(t + 0.52, "chainthrow", v=0.7)
    BK(t + 0.62, "t_ready", bx + 66, "back", sq=-0.12)
    BK(t + 0.74, "t_tuck", bx + 112, "out", air=52)
    BK(t + 0.92, "t_ready", bx + 130, "in", sq=-0.1)
    E(t + 0.92, "ground", x=bx + 130, v=0.4)
    E(t + 0.80, "chain", mode="free")
    bx += 130        # -6
    ax += 40         # -262
    AK(t + 0.95, "k_ready", ax, "out")

    # =========================================================== 4. the throw; 5. duck and rush
    t = 4.75
    REEL.append((t + 0.29, 6.32 - 0.01, 330))
    AK(t - 0.20, "k_ready", ax - 6, "back", uab=230, fab=-40, T=-10)   # cocks the chain back
    AK(t, "k_throw", ax + 30, "snap")
    E(t - 0.20, "chain", mode="path", dur=0.2, ease="io", pts=[(ax - 70, 150)])
    E(t, "chain", mode="path", dur=0.30, ease="out",
      pts=[(bx - 20, 132), (bx + 110, 100), (bx + 175, 4)])
    E(t, "chainthrow", v=1.2)
    AK(t + 0.30, "k_throw", ax + 30, "out")
    AK(t + 0.55, "k_ready", ax + 20, "io")
    E(t + 0.30, "chain", mode="free")
    E(t + 0.34, "chaindrop", v=0.8)
    BK(t + 0.04, "t_ready", bx + 2, "back")
    BK(t + 0.10, "t_low2_wind", bx + 4, "snap", T=60, H=50, sq=-0.16)  # ducks under it
    E(t + 0.12, "zip", v=0.8)
    # rush
    t = 5.12
    BK(t, "t_dash", ax + 230, "lin")
    E(t, "zip", v=1.0)
    E(t, "dust", x=bx, v=0.8)
    ax += 20         # -242
    bx = ax + 185
    BK(t + 0.10, "t_high1_wind", bx + 6, "out")
    BK(t + 0.20, "t_high1", bx - 12, "snap")                # 1: overhead diagonal
    AK(t + 0.18, "k_block_hi", ax - 6, "snap")
    E(t + 0.20, "clash", v=1.0)
    stop(t + 0.20, 0.07)
    AK(t + 0.24, "k_block_hi", ax - 14, "snap", T=-14)
    BK(t + 0.30, "t_low2_wind", bx - 8, "out")
    BK(t + 0.40, "t_low2", bx - 24, "snap")                 # 2: low cut from the back hand
    AK(t + 0.34, "k_ready", ax - 16, "out")
    AK(t + 0.40, "k_deflect", ax - 18, "snap")              # sickle sweeps it down and out
    E(t + 0.40, "clash", v=0.9, blade=2)
    stop(t + 0.40, 0.05)
    BK(t + 0.50, "t_thrust_wind", bx - 18, "out")
    BK(t + 0.60, "t_thrust", bx - 50, "snap")               # 3: thrust at the face
    AK(t + 0.56, "k_slip", ax - 26, "snap")                 # slips it, but it grazes him
    E(t + 0.60, "hit", by="B", on="A", v=0.9, dmg=7)
    stop(t + 0.60, 0.09)
    bx -= 50
    # 6. ...and answers with a push kick to the chest
    AK(t + 0.72, "kick_wind", ax + 40, "back", uaf=140, faf=60, sw=30, uab=200, fab=170)
    AK(t + 0.82, "kick", ax + 112, "snap", uaf=150, faf=70, sw=40, uab=210, fab=180)
    E(t + 0.82, "hit", by="A", on="B", v=1.0, dmg=8, part="ftf")
    stop(t + 0.82, 0.08)
    BK(t + 0.66, "t_thrust", bx - 20, "out")
    BK(t + 0.83, "t_hurt", bx + 50, "snap")
    BK(t + 1.05, "t_hurt", bx + 110, "out", T=-14)
    E(t + 1.05, "skid", x=bx + 110, v=0.9)
    AK(t + 1.00, "k_ready", ax + 10, "out")
    bx += 110        # ax + 196 = -46

    # =========================================================== 7. the yank takes his legs
    t = 6.32
    AK(t - 0.12, "k_ready", ax + 8, "back", T=20, uab=120, fab=95)
    AK(t, "k_yank", ax - 18, "snap", reel=60)
    E(t, "chainyank", v=1.0)
    E(t, "chain", mode="path", dur=0.34, ease="io",
      pts=[("J", "B", "ftb", -16, -6), ("J", "B", "ftf", 6, -2), (ax + 90, 30), (ax + 60, 70)])
    E(t + 0.17, "hit", by="A", on="B", v=0.9, dmg=6, part="chain", nosolve=True, at_weight=True)
    stop(t + 0.17, 0.06)
    BK(t + 0.18, "t_trip", bx - 10, "snap", rot=-24)
    BK(t + 0.40, "kneel", bx - 30, "io", sw=60, sw2=90, uab=120, fab=80)
    E(t + 0.40, "thud", v=0.7)
    BK(t + 0.70, "t_ready", bx - 30, "out", sq=-0.08)
    bx -= 30         # -76
    E(t + 0.34, "chain", mode="spin", dur=0.62, r=34, turns=1.7, plane="side", c=(14, -4))
    E(t + 0.34, "chainspin", dur=0.6, v=0.55)
    AK(t + 0.40, "k_ready", ax - 10, "out")
    AK(t + 0.80, "k_ready", ax - 8, "io", T=12)

    # =========================================================== 8-11. leap, sweep, throw, deflect
    t = 7.40
    BK(t - 0.14, "t_ready", bx + 8, "back", sq=-0.16, T=26)
    BK(t + 0.10, "t_cross", bx - 70, "out", air=80)
    E(t, "zip", v=1.0)
    E(t, "dust", x=bx, v=0.9)
    # Kusari drops and turns underneath; the chain sweeps for his legs
    AK(t + 0.04, "k_ready", ax - 2, "back", sq=-0.1)
    AK(t + 0.16, "k_low", ax + 18, "snap")                  # drops and pivots right round
    A.face(t + 0.13, -1)
    A.face(t + 0.27, 1)
    AK(t + 0.34, "k_low", ax + 30, "io", T=50)
    E(t + 0.08, "chain", mode="path", dur=0.30, ease="io",
      pts=[(ax + 70, 26), ("J", "B", "ftf", 0, -26), (bx - 120, 40)])
    E(t + 0.08, "chainthrow", v=0.9)
    BK(t + 0.20, "t_tuck", bx - 130, "io", air=112)         # tucks over the chain
    E(t + 0.40, "chain", mode="free")
    # at the top he throws the back-hand sword down at him
    tr = t + 0.32
    BK(tr - 0.07, "t_throw_wind", bx - 160, "io", air=112)
    BK(tr, "t_throw", bx - 180, "snap", air=108)
    E(tr, "loose", id=0, lk="throw", who="B", second=True, td=tr + 0.13, tc=tr + 0.70,
      at="A", spin1=1, spin2=-1)
    E(tr, "thrust", v=0.9)
    BK(tr + 0.01, "t_throw", bx - 182, nosw2=1, air=106)
    ax += 30         # -232 after the spin
    AK(tr + 0.06, "k_ready", ax, "out", sq=-0.06)
    AK(tr + 0.13, "k_deflect", ax - 4, "snap", T=-4, uaf=60, faf=25, sw=-20)  # bats it away
    E(tr + 0.13, "clash", v=1.1, big=True, nosolve=True, at_loose=0)
    stop(tr + 0.13, 0.10)
    # he comes down behind him; the deflected sword drops back into his hand
    xl = ax - 175
    BK(tr + 0.30, "t_throw", xl + 50, "io", air=60, nosw2=1, rot=-30)
    B.face(tr + 0.36, 1)
    BK(tr + 0.48, "t_land", xl, "in", nosw2=1, rot=0)
    E(tr + 0.48, "ground", x=xl, v=0.7)
    E(tr + 0.48, "stomp", x=xl, v=0.5)
    BK(tr + 0.70, "t_catch", xl + 6, "out", nosw2=0)
    E(tr + 0.70, "catch", v=1.0)
    A.face(tr + 0.40, -1)
    AK(tr + 0.42, "k_ready", ax - 2, "snap")
    bx = xl + 6      # ax - 169

    # =========================================================== 12-13. five-hit combo, lock
    t = tr + 0.95     # ~9.02
    BK(t - 0.10, "t_ready", bx + 4, "back", sq=-0.12)
    BK(t + 0.05, "t_high1_wind", ax - 190, "out")
    E(t - 0.06, "zip", v=0.8)
    s1 = t + 0.14
    BK(s1, "t_high1", ax - 168, "snap")                     # 1: overhead diagonal
    AK(s1 - 0.03, "k_block_hi", ax + 4, "snap")
    E(s1, "clash", v=1.0, blade=1)
    stop(s1, 0.06)
    ax += 14
    s2 = s1 + 0.17
    BK(s2 - 0.09, "t_rise2_wind", ax - 130, "out")
    BK(s2, "t_rise2", ax - 112, "snap")                     # 2: rising cut, other hand
    AK(s2 - 0.03, "k_block_lo", ax + 2, "snap")
    E(s2, "clash", v=0.9, blade=2)
    stop(s2, 0.05)
    ax += 12
    s3 = s2 + 0.18
    BK(s3 - 0.09, "t_h1_wind", ax - 160, "out")
    BK(s3, "t_h1", ax - 150, "snap")                        # 3: flat cut at the ribs
    AK(s3 - 0.04, "k_taut_v", ax + 2, "snap")               # chain pulled taut, upright
    E(s3, "clash", v=1.0, blade=1, chain=True)
    stop(s3, 0.06)
    ax += 14
    s4 = s3 + 0.22                                          # 4: the one that almost lands
    BK(s4 - 0.12, "t_over2_wind", ax - 150, "out")
    BK(s4, "t_over2", ax - 138, "snap", sw2=72, uab=95, fab=80)
    BK(s4 + 0.16, "t_over2", ax - 160, "out", sw2=120)
    AK(s4 - 0.03, "k_block_hi", ax + 6, "snap", T=-22, H=-30, uaf=50, faf=5, sw=60, sq=-0.1)
    E(s4, "clash", v=1.2, big=True, blade=2)
    stop(s4, 0.12)
    E(s4 - 0.06, "slowmo", a0=s4 - 0.06, a1=s4 + 0.12, rate=0.35)
    AK(s4 + 0.10, "k_ready", ax + 20, "out", T=-10)
    ax += 20
    s5 = s4 + 0.34                                          # 5: heavy cut, he hooks it
    BK(s5 - 0.16, "t_high1_wind", ax - 175, "back", T=-14)
    BK(s5, "t_high1", ax - 160, "snap", sw=55, uaf=70, faf=60, T=16)
    AK(s5 - 0.04, "k_lock", ax, "snap", sw=100)
    E(s5, "clash", v=1.1, big=True, blade=1)
    stop(s5, 0.10)
    E(s5 + 0.06, "scrape", dur=0.55)
    E(s5 + 0.06, "slowmo", a0=s5 + 0.06, a1=s5 + 0.61, rate=0.5)
    BK(s5 + 0.06, "t_high1", ax - 160, sw=55, uaf=70, faf=60, T=16)
    BK(s5 + 0.61, "t_high1", ax - 148, "lin", sw=66, uaf=78, faf=70, T=30)   # bearing down
    AK(s5 + 0.06, "k_lock", ax, sw=100)
    AK(s5 + 0.61, "k_lock", ax + 8, "lin", T=-18, sq=-0.12, sw=104)
    bx = ax - 148

    # =========================================================== 14. lets go, slides; 15. disarm
    t = s5 + 0.70
    AK(t, "k_slide", ax - 40, "snap")                       # gives way and slips under
    E(t, "zip", v=0.9)
    E(t, "dust", x=ax, v=0.9)
    BK(t + 0.04, "t_overreach", bx + 60, "snap")            # his weight carries him through
    E(t + 0.12, "ground", x=bx + 150, v=0.6)
    AK(t + 0.20, "k_slide", bx - 50, "out", rot=0)
    E(t + 0.20, "skid", x=bx - 50, v=1.0)
    BK(t + 0.30, "t_overreach", bx + 66, "out", T=56)
    # spins up behind him, chain out
    A.face(t + 0.26, 1)
    xa = bx - 60
    AK(t + 0.36, "k_ready", xa, "out", rot=0)
    A.face(t + 0.40, -1)                                  # pirouette, chain whirling
    A.face(t + 0.48, 1)
    AK(t + 0.50, "k_sling", xa + 10, "snap", reel=90)
    E(t + 0.28, "chain", mode="spin", dur=0.22, r=50, turns=2.5, plane="side", c=(0, 10))
    tw = t + 0.62
    E(t + 0.50, "chain", mode="path", dur=tw - (t + 0.50), ease="out",
      pts=[("J", "B", "hilt0", 0, 22)])
    E(tw, "chain", mode="attach", dur=0.24, to=("B", "hilt0", "guard", 0.45), blend=0.03)
    E(tw, "chainwrap", v=1.0)
    E(tw, "hit", by="A", on="B", v=0.6, dmg=4, part="chain", nosolve=True, at_weight=True)
    stop(tw, 0.07)
    BK(tw + 0.02, "t_ready", bx + 50, "snap", T=-6, uaf=170, faf=110, sw=60)
    ty = tw + 0.24
    AK(ty - 0.06, "k_sling", xa + 4, "out")
    AK(ty + 0.06, "k_yank", xa - 26, "snap")
    E(ty, "chainyank", v=1.2)
    E(ty, "loose", id=1, lk="fling", who="B", second=False, tl=ty + 0.62, xl=xa - 190, spin=-2,
      land_ang=200)
    E(ty, "chain", mode="loose", sword=1, dur=0.12)
    E(ty + 0.62, "swordland", v=1.0)
    BK(ty, "t_hurt", bx + 40, "snap", nosw=1, T=6)
    E(ty + 0.12, "chain", mode="free")
    B.face(ty + 0.30, -1)
    BK(ty + 0.36, "t_ready", bx + 50, "out", nosw=1)
    bx += 50

    # =========================================================== 16-17. last strike, trapped, sickle at the neck
    t = ty + 0.70
    AK(t - 0.30, "k_ready", xa - 20, "out")
    AK(t + 0.30, "k_ready", xa - 22, "io", T=4)
    BK(t - 0.14, "t_ready", bx + 4, "io", nosw=1)
    BK(t, "t_desp_wind", bx + 6, "back", nosw=1)
    E(t, "heart", v=1.1)
    E(t + 0.10, "slowmo", a0=t + 0.10, a1=t + 0.42, rate=0.45)
    tc = t + 0.50
    BK(tc - 0.05, "t_desp_wind", bx + 2, "lin", nosw=1, T=-20)
    BK(tc, "t_desp", bx - 50, "snap", nosw=1)
    AK(tc - 0.05, "k_taut", xa - 16, "snap")
    E(tc, "clash", v=1.2, big=True, blade=2, chain=True)
    stop(tc, 0.14)
    AK(tc + 0.14, "k_twist", xa - 10, "snap")
    BK(tc + 0.14, "t_desp", bx - 46, "snap", nosw=1, uab=100, fab=100, sw2=150)
    E(tc + 0.14, "chainwrap", v=0.8)
    tp = tc + 0.30
    AK(tp, "k_yank", xa - 30, "snap")
    E(tp, "chainyank", v=1.2)
    E(tp, "loose", id=2, lk="fling", who="B", second=True, tl=tp + 0.6, xl=bx + 150, spin=2,
      land_ang=165)
    E(tp + 0.6, "swordland", v=1.0)
    BK(tp + 0.01, "t_hurt", bx - 20, "snap", nosw=1, nosw2=1)
    tk = tp + 0.30
    AK(tk - 0.08, "k_ready", xa - 24, "back", T=-6)
    xk = bx - 4 - 104                    # sickle point at his throat
    AK(tk, "k_point", xk, "snap")
    BK(tk + 0.02, "t_lost", bx - 4, "snap")
    E(tk, "kill", song=True)
    stop(tk, 0.18)
    # 18. hold
    end = tk + 3.6
    AK(tk + 1.2, "k_point", xk - 1, "io", T=29)
    AK(end, "k_point", xk - 1, T=30)
    BK(end, "t_lost", bx - 4, H=-40)
    E(tk + 0.7, "winner", name="CHAIN SICKLE WINS", color=ORANGE)
    return dict(fighters=[("B", B, TWIN), ("A", A, KUSARI)], events=ev, end=end,
                title=(("CHAIN SICKLE", ORANGE), ("TWIN SWORDS", RED)),
                hp=[("A", "KUSARI", ORANGE), ("B", "TWIN", RED)],
                springy=True, fluid=True, drawn=drawn, theme="meadow")
