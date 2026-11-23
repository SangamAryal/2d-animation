"""Fight 09: "KATANA vs WAR AXE" on a cliff edge (the terrain fight).

Same meadow look as fight 08, but the ground ends at a cliff on the right,
and the scene itself takes part in the fight (terrain.py):

  0-4 s    AXE (rust red, horned helm) stands on a boulder over the drop,
           looking at the valley. KATANA (navy, straw hat) walks in. Axe turns,
           jumps down; Katana draws.
  4-9 s    the axe is heavy: an overhead buries itself in the ground, Katana's
           cuts are blocked on the haft, a kick sends him back to the old pine.
           A sweep he ducks chops the pine through, and it falls on both of them.
  9-13 s   Katana runs up the fallen trunk, leaps over Axe (clash in the air)
           and lands on top of the boulder: high ground. He cuts Axe's shoulder.
  13-17 s  Axe smashes the boulder out from under him; rocks fly, Katana is
           thrown to the very edge and nearly goes over. Axe charges to push
           him off, Katana slides under, and now Axe teeters on the edge.
  17-24 s  Katana takes over: a four-cut combo on the haft, Axe's kick, one
           last overhead that cracks the ground near the edge. Katana's rising
           cut goes through him: freeze-frame. The cracked ledge breaks and
           Axe falls with it into the valley.
"""
from rig import P, Track, pose
import choreo_ambush  # noqa: F401  (h_* hero poses, br_* brute poses, sp_/t_ poses)

NAVY = "#1f2d4d"
RUST = "#a8432a"
EDGE, TREE, BOULDER = 560, -380, 200
ROCK_TOP = 60          # standing height on the boulder
LOG_TOP = 48           # standing height on the fallen trunk

KATANA = dict(name="KATANA", body=NAVY, back="#5a6c93", band="#d8323c", hat="#d9b26a",
              scabbard=True, scab="#4a2626", steel="#eef2f6", ghost="#5a6c93",
              trail="#e6ecff", limb=8.5, size=1.0, blade=66)
AXE = dict(name="AXE", body=RUST, back="#d07a5a", horns="#e8dcc0", sword="axe",
           blade=124, butt=10, head_len=34, head_w=34, wood="#6e4a2a", steel="#d7dce1",
           ghost="#d07a5a", trail="#ffe6da", limb=10.5, torso=1.3, size=1.16,
           springs={"sw": (55, 0.6)})

# ---------------------------------------------------------------- extra poses
pose("ax_teeter1", T=-30, H=-20, uaf=50, faf=20, sw=30, grip=0, uab=300, fab=330,
     thf=166, shf=182, thb=200, shb=190)
pose("ax_teeter2", "ax_teeter1", T=-18, uaf=130, faf=80, uab=240, fab=250, H=-6)
pose("ax_plant", T=26, H=12, uaf=150, faf=150, sw=168, grip=1,
     thf=130, shf=182, thb=222, shb=210)
pose("ax_look", "shoulder", T=2, H=-8)
pose("ax_crouch", "crouch", sw=-130, uaf=165, faf=25, grip=0)
pose("ax_air", "jump_tuck", sw=-130, uaf=165, faf=25, grip=0)
pose("ax_land", "crouch", sw=60, grip=1)
pose("ax_overhead_hi", "high_wind", T=-18, uaf=-5, faf=-30, sw=-160)
pose("ax_stuck", "slam", T=56, H=40, sw=118)
pose("ax_roar", T=-16, H=-26, uaf=120, faf=40, sw=10, grip=0, uab=250, fab=230,
     thf=140, shf=182, thb=220, shb=200)
pose("ax_shoulder_charge", "run1", uaf=165, faf=25, sw=-130, grip=0, T=34)
pose("ax_hurt", "stagger", sw=150, grip=0)
pose("ax_fall", T=-60, H=-50, uaf=40, faf=0, sw=20, grip=0, uab=320, fab=340,
     thf=130, shf=160, thb=220, shb=250)
pose("k_teeter1", T=-30, H=-20, uaf=50, faf=20, sw=40, grip=0, uab=300, fab=330,
     thf=166, shf=182, thb=200, shb=190)
pose("k_teeter2", "k_teeter1", T=-14, uaf=140, faf=90, uab=230, fab=250, H=-4)
pose("k_run1", "run1_g", T=26)
pose("k_run2", "run2_g", T=26)
pose("k_look_down", "stand_sheathed", T=30, H=50)


def build(drawn=True):
    ids = ["B", "A"]
    T = {"A": Track(facing=1), "B": Track(facing=1)}
    X, ROT = {}, {"A": 0.0, "B": 0.0}
    ST = {"A": [], "B": []}
    ev = []

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

    def A(t, name, x=None, e="io", **kw):
        K("A", t, name, x, e, **kw)

    def B(t, name, x=None, e="io", **kw):
        K("B", t, name, x, e, **kw)

    def face(w, t, f):
        T[w].face(t, f)

    def stop(t, d):
        E(t, "hitstop", dur=d)

    ST["A"].append((0.0, 3.55, dict(sheath=1)))

    # =========================================================== 0-4 opening
    B(0.0, "ax_look", BOULDER, air=ROCK_TOP)
    B(1.2, "ax_look", BOULDER + 2, air=ROCK_TOP, T=6)
    E(0.7, "pebbles", x=EDGE, n=5, v=0.6)
    ax = -640
    A(0.0, "h_walk1", ax)
    for i in range(7):
        tt = 0.36 * (i + 1)
        ax += 50
        A(tt, "h_walk2" if i % 2 == 0 else "h_walk1", ax)
        E(tt, "step", who="A", v=0.35)
    A(2.75, "h_hand", ax + 6)
    ax += 6                                     # -284
    face("B", 1.75, -1)
    B(1.85, "ax_look", BOULDER, air=ROCK_TOP)
    B(2.35, "ax_crouch", BOULDER - 6, "back", air=ROCK_TOP, sq=-0.14)
    B(2.62, "ax_air", BOULDER - 70, "out", air=ROCK_TOP + 70)
    B(2.86, "ax_land", BOULDER - 110, "in", air=0, sq=-0.2)
    E(2.86, "ground", x=BOULDER - 110, v=1.0)
    E(2.86, "dust", x=BOULDER - 110, v=1.0)
    E(2.86, "thud", v=0.8)
    bx = BOULDER - 110                           # 90
    B(3.25, "guard", bx, "out")
    A(3.10, "iai", ax, "io")
    A(3.40, "iai_deep", ax - 4, "out")
    A(3.60, "guard", ax - 4, "snap")
    E(3.55, "draw", v=1.0)
    ax -= 4                                      # -288
    E(3.62, "banner", text="FIGHT!")
    E(3.62, "fight")
    E(0.05, "drum", v=0.7)
    E(0.0, "frame", ids=["B", EDGE + 120, BOULDER - 200])   # opening: him over the drop
    E(1.5, "frame", ids=["A", "B", EDGE + 120])
    E(3.9, "frame", ids=["A", "B"])
    E(14.6, "frame", ids=["A", "B", EDGE + 60])

    # =========================================================== 4-9 the axe is heavy
    # beat 1: two heavy steps, overhead that buries itself in the ground
    for i in range(2):
        tt = 3.80 + 0.26 * i
        bx -= 40
        B(tt, "walk2" if i % 2 == 0 else "walk1", bx)
        E(tt, "step", who="B", v=0.9)
    t = 4.55
    B(t - 0.28, "ax_overhead_hi", bx - 10, "back")
    B(t, "ax_stuck", bx - 50, "snap")
    bx -= 50                                     # -40
    E(t, "slam", by="B", v=1.2)
    stop(t, 0.07)
    A(t - 0.20, "guard", ax, "io")
    A(t - 0.10, "crouch", ax - 6, "back")
    A(t + 0.06, "jump_tuck", ax - 50, "out", air=28)
    A(t + 0.22, "guard", ax - 66, "in", sq=-0.1)
    E(t + 0.22, "ground", x=ax - 66, v=0.4)
    ax -= 66                                     # -354
    # he tugs at the stuck axe
    B(t + 0.25, "ax_stuck", bx - 4, "io", T=48)
    B(t + 0.45, "ax_stuck", bx - 8, "io", T=60, sw=122)
    B(t + 0.62, "ax_stuck", bx - 2, "io", T=44, sw=116)
    # beat 2: Katana rushes in; Axe rips it free just in time, block on the haft
    c1 = t + 0.88
    E(c1 - 0.24, "zip", v=0.9)
    A(c1 - 0.22, "guard", ax + 8, "back", sq=-0.14, T=24)
    A(c1 - 0.08, "side_wind", bx - 175, "out")
    A(c1, "side_cut", bx - 150, "snap")
    ax = bx - 150                                # -190
    B(c1 - 0.10, "ax_stuck", bx, "io", T=30, sw=90)
    B(c1 - 0.01, "block_mid", bx + 6, "snap")
    E(c1, "clash", v=1.2, big=True)
    stop(c1, 0.08)
    c2 = c1 + 0.34
    A(c2 - 0.12, "rise_wind", ax + 6, "back")
    A(c2, "rise_cut", ax + 20, "snap")
    ax += 20
    B(c2 - 0.08, "guard", bx + 8, "io")
    B(c2 - 0.01, "block_high", bx + 10, "snap")
    E(c2, "clash", v=1.0)
    stop(c2, 0.06)
    bx += 10                                     # -30
    # beat 3: boot to the chest, back toward the pine
    k = c2 + 0.36
    B(k - 0.12, "kick_wind", bx, "back")
    B(k, "kick", bx + 10, "snap")
    E(k, "hit", by="B", on="A", v=1.3, part="ftf")
    stop(k, 0.08)
    A(k + 0.02, "recoil", ax - 30, "snap")
    A(k + 0.36, "stagger", ax - 150, "out")
    E(k + 0.36, "skid", x=ax - 150, v=1.0)
    ax -= 150                                    # -320
    A(k + 0.60, "guard", ax - 4, "io")
    ax -= 4
    B(k + 0.30, "guard", bx + 10, "out")
    bx += 10                                     # -20
    # beat 4: a diagonal chop he blocks, the weight crushes him down
    t = k + 1.00                                 # ~6.8
    B(t - 0.42, "walk1", bx - 40)
    E(t - 0.42, "step", who="B", v=0.9)
    B(t - 0.22, "heavy_wind", bx - 50, "back")
    B(t, "slam", bx - 90, "snap", T=30, sw=110)
    bx -= 90                                     # -110
    A(t - 0.10, "guard", ax, "io")
    A(t - 0.01, "block_high", ax + 4, "snap")
    E(t, "clash", v=1.3, big=True)
    stop(t, 0.10)
    A(t + 0.14, "brace", ax - 6, "snap", sq=-0.14)
    E(t + 0.14, "skid", x=ax - 6, v=0.8)
    ax -= 6                                      # -330
    B(t + 0.14, "slam", bx, "io", T=38, sw=104)
    # beat 5: a sweep at his head; he ducks; the axe goes through the pine
    s = t + 0.80
    B(t + 0.40, "guard", bx + 20, "out")
    B(s - 0.24, "sweep_wind", bx + 10, "back")
    B(s, "sweep", bx - 10, "snap", T=30)
    bx -= 10                                     # -120
    A(s - 0.20, "guard", ax, "io")
    A(s - 0.07, "h_duck", ax - 4, "snap")
    E(s + 0.03, "treecut", dir=1, h=40, dur=0.95)
    stop(s + 0.03, 0.08)
    E(s + 0.03, "dust", x=TREE, v=0.6)
    T_TREE = s + 0.03
    # the pine comes down on both of them
    A(s + 0.30, "h_duck", ax - 6, "io", H=10, T=40)            # looks up
    A(s + 0.42, "crouch", ax - 10, "back")
    A(s + 0.72, "tumble", ax - 130, "out", rot=-200, air=46)
    A(s + 0.98, "crouch", ax - 200, "in", rot=-360, sq=-0.1)
    ROT["A"] -= 360
    E(s + 0.98, "ground", x=ax - 200, v=0.6)
    ax -= 200                                    # -530
    face("B", s + 0.30, -1)
    B(s + 0.30, "sweep", bx, "io", T=10, H=-20)
    B(s + 0.50, "crouch", bx + 10, "back", sw=60, grip=1)
    B(s + 0.80, "jump_tuck", bx + 110, "out", air=40, sw=60, uaf=150, faf=95)
    B(s + 1.02, "ax_land", bx + 160, "in", air=0, sq=-0.12)
    E(s + 1.02, "ground", x=bx + 160, v=0.6)
    bx += 160                                    # 40
    tl = T_TREE + 0.95
    E(tl, "treefall", v=1.0)
    E(tl, "dust", x=TREE + 140, v=1.4)
    E(tl, "dust", x=TREE + 250, v=1.2)
    stop(tl, 0.05)
    A(tl + 0.30, "guard", ax, "io")
    B(tl + 0.30, "guard", bx, "io")

    # =========================================================== 9-13 the trunk, the boulder
    t0 = tl + 0.70                               # ~9.0
    A(t0, "guard", ax, "back", sq=-0.12, T=22)
    E(t0 + 0.05, "zip", v=0.7)
    A(t0 + 0.16, "k_run1", ax + 70)
    E(t0 + 0.16, "step", who="A", v=0.5)
    A(t0 + 0.30, "crouch", TREE - 20, "out", sq=-0.1)
    A(t0 + 0.46, "k_run2", TREE + 40, "out", air=LOG_TOP)
    E(t0 + 0.46, "step", who="A", v=0.6)
    A(t0 + 0.60, "k_run1", TREE + 130, "lin", air=LOG_TOP)
    E(t0 + 0.60, "step", who="A", v=0.6)
    A(t0 + 0.74, "crouch", TREE + 200, "lin", air=LOG_TOP, sq=-0.14)
    # the leap over him, clash in the air
    lp = t0 + 0.98
    A(lp - 0.08, "jump_tuck", bx - 90, "out", air=150)
    A(lp, "high_cut", bx - 10, "snap", air=180)
    B(lp - 0.24, "guard", bx, "io")
    B(lp - 0.10, "rise_wind", bx - 4, "back")
    B(lp, "rise_cut", bx + 4, "snap")
    E(lp, "clash", v=1.3, big=True)
    stop(lp, 0.10)
    E(lp - 0.10, "slowmo", a0=lp - 0.10, a1=lp + 0.14, rate=0.35)
    A(lp + 0.16, "jump_tuck", bx + 80, "out", air=150, rot=180)
    face("A", lp + 0.22, -1)
    A(lp + 0.36, "crouch", BOULDER + 10, "in", air=ROCK_TOP, rot=360, sq=-0.16)
    ROT["A"] += 360
    E(lp + 0.36, "ground", x=BOULDER + 10, v=0.5)
    E(lp + 0.36, "pebbles", x=BOULDER + 40, n=3, v=0.4)
    ax = BOULDER + 10
    A(lp + 0.70, "guard", ax, "out", air=ROCK_TOP)
    face("B", lp + 0.30, 1)
    B(lp + 0.40, "guard", bx + 6, "out")
    bx += 6                                      # ~46
    # beat 6: from below, Axe swings at his legs; he hops it; blocks the overhead
    h1 = lp + 1.10
    B(h1 - 0.30, "walk1", bx + 30)
    E(h1 - 0.30, "step", who="B", v=0.8)
    B(h1 - 0.16, "sweep_wind", bx + 30, "back", T=20)
    B(h1, "sweep", bx + 40, "snap", T=40, sw=125, uaf=120, faf=110)
    bx += 40                                     # 86
    A(h1 - 0.10, "crouch", ax, "back", air=ROCK_TOP)
    A(h1 + 0.02, "jump_tuck", ax, "out", air=ROCK_TOP + 46)
    A(h1 + 0.20, "guard", ax, "in", air=ROCK_TOP, sq=-0.1)
    h2 = h1 + 0.55
    B(h2 - 0.22, "ax_overhead_hi", bx, "back")
    B(h2, "high_cut", bx + 10, "snap", T=10, sw=60)
    A(h2 - 0.08, "guard", ax, "io", air=ROCK_TOP)
    A(h2 - 0.01, "block_mid", ax, "snap", air=ROCK_TOP, T=10)
    E(h2, "clash", v=1.1)
    stop(h2, 0.07)
    # beat 7: high ground: a cut down into his shoulder
    h3 = h2 + 0.36
    A(h3 - 0.14, "high_wind", ax, "back", air=ROCK_TOP)
    A(h3, "land_cut", ax - 20, "snap", air=ROCK_TOP - 8)
    E(h3, "hit", by="A", on="B", v=1.3, big=True, limb=("neck", "sho", 0.9), blood=16)
    stop(h3, 0.10)
    B(h3 + 0.02, "ax_hurt", bx - 30, "snap")
    B(h3 + 0.36, "ax_hurt", bx - 70, "out")
    E(h3 + 0.36, "skid", x=bx - 70, v=0.8)
    bx -= 70                                     # 16
    A(h3 + 0.40, "guard", ax, "out", air=ROCK_TOP)
    # he looks at the cut, roars
    B(h3 + 0.90, "ax_roar", bx, "out")
    E(h3 + 0.90, "roar", v=1.0)
    E(h3 + 0.90, "radial", v=0.6)
    B(h3 + 1.40, "guard", bx + 4, "io")
    bx += 4

    # =========================================================== 13-17 the boulder breaks, the edge
    r0 = h3 + 1.70                               # ~13.3
    for i in range(2):
        tt = r0 + 0.22 * i
        bx += 44
        B(tt, "walk2" if i % 2 == 0 else "walk1", bx)
        E(tt, "step", who="B", v=1.0)
    rs = r0 + 0.68
    B(rs - 0.26, "sweep_wind", bx + 10, "back", T=26)
    B(rs, "sweep", bx + 30, "snap", T=46, thf=110, thb=248, shb=255, sw=100)
    bx += 30                                     # 134
    E(rs, "rocksmash", dir=1, v=1.0)
    E(rs, "hit", by="B", on="A", v=1.3, big=True, part="hilt0", nosolve=True,
      contact=(BOULDER + 10, ROCK_TOP + 90))
    stop(rs, 0.10)
    E(rs - 0.08, "slowmo", a0=rs - 0.08, a1=rs + 0.16, rate=0.35)
    A(rs - 0.10, "guard", ax, "io", air=ROCK_TOP)
    A(rs + 0.02, "recoil", ax + 20, "snap", air=ROCK_TOP + 10)
    A(rs + 0.34, "tumble", ax + 150, "out", air=60, rot=-160)
    A(rs + 0.62, "h_lie", EDGE - 120, "in", rot=-360)
    E(rs + 0.62, "thud", v=1.0)
    E(rs + 0.62, "dust", x=EDGE - 120, v=0.9)
    A(rs + 0.95, "h_lie", EDGE - 60, "out", rot=-360)
    E(rs + 0.95, "skid", x=EDGE - 60, v=1.0)
    E(rs + 0.95, "pebbles", x=EDGE, n=7, v=1.0)
    ROT["A"] -= 360
    ax = EDGE - 60                               # 500
    # up on his knees, then on his feet with his heels over the drop
    A(rs + 1.30, "h_getup", ax - 4, "io")
    A(rs + 1.62, "k_teeter1", ax + 12, "out")
    E(rs + 1.62, "pebbles", x=EDGE, n=4, v=0.8)
    A(rs + 1.86, "k_teeter2", ax + 14, "io")
    A(rs + 2.10, "k_teeter1", ax + 10, "io")
    A(rs + 2.36, "guard", ax - 10, "out", T=20)
    ax -= 10                                     # 490
    E(rs + 1.70, "heart", v=0.9)
    B(rs + 0.40, "sweep", bx, "io", T=30)
    B(rs + 1.10, "guard", bx, "io")
    # beat 8: Axe charges to drive him off the edge; he slides under
    ch = rs + 2.60                               # ~16.5
    B(ch - 0.24, "guard", bx - 6, "back", sq=-0.14, T=24)
    for i in range(3):
        tt = ch + 0.16 * (i + 1)
        bx += 70
        B(tt, "run2_g" if i % 2 == 0 else "run1_g", bx)
        E(tt, "step", who="B", v=1.0)
    bx += 0                                      # 344
    ct = ch + 0.64
    B(ct - 0.10, "ax_overhead_hi", bx + 40, "out")
    B(ct + 0.08, "slam", bx + 110, "snap", T=40)
    bx += 110                                    # 454
    E(ct + 0.08, "ground", x=bx + 70, v=0.9)
    E(ct + 0.08, "dust", x=bx + 60, v=0.8)
    A(ct - 0.16, "guard", ax, "io")
    A(ct - 0.04, "h_duck", ax - 10, "snap")
    A(ct + 0.14, "slide", ax - 150, "out", sw=200, uaf=200, faf=200, grip=0)
    E(ct + 0.06, "zip", v=0.9)
    E(ct + 0.14, "dust", x=ax - 150, v=0.9)
    A(ct + 0.40, "crouch", ax - 220, "in")
    ax -= 220                                    # 270
    face("A", ct + 0.30, 1)
    A(ct + 0.70, "guard", ax, "out")
    # now Axe is the one teetering
    B(ct + 0.30, "ax_teeter1", bx + 20, "out", sw=150)
    E(ct + 0.30, "pebbles", x=EDGE, n=8, v=1.0)
    B(ct + 0.56, "ax_teeter2", bx + 24, "io", sw=200)
    B(ct + 0.82, "ax_teeter1", bx + 20, "io", sw=150)
    B(ct + 1.10, "ax_plant", bx + 6, "out")
    E(ct + 1.10, "thud", v=0.6)
    face("B", ct + 1.20, -1)
    B(ct + 1.40, "guard", bx - 10, "io")
    bx -= 10                                     # 444

    # =========================================================== 17-24 Katana takes over
    f0 = ct + 1.80                               # ~19.0
    E(f0 - 0.24, "zip", v=1.0)
    A(f0 - 0.26, "guard", ax, "back", sq=-0.14, T=22)
    combo = (("side_wind", "side_cut", "block_mid"), ("rise_wind", "rise_cut", "block_high"),
             ("high_wind", "high_cut", "block_high"), ("side_wind", "side_cut", "block_mid"))
    for i, (wd, st_, blk) in enumerate(combo):
        ti = f0 + 0.30 * i
        A(ti - 0.12, wd, bx - 168 + 6 * i, "back")
        A(ti, st_, bx - 150 + 6 * i, "snap")
        B(ti - 0.08, "guard", bx + 4, "io")
        B(ti - 0.01, blk, bx + 8, "snap")
        bx += 8
        E(ti, "clash", v=1.0 + 0.08 * i, big=(i == 3))
        stop(ti, 0.06)
        if i == 3:
            E(ti, "pebbles", x=EDGE, n=5, v=0.8)
    ax = bx - 150 + 18                           # ~ 326
    bx = min(bx, EDGE - 70)                      # 476
    # beat 9: Axe kicks him off, one last overhead: the ground cracks
    k = f0 + 1.30
    B(k - 0.12, "kick_wind", bx, "back")
    B(k, "kick", bx - 30, "snap")
    E(k, "hit", by="B", on="A", v=1.2, part="ftf")
    stop(k, 0.07)
    bx -= 30                                     # 446
    A(k + 0.02, "recoil", ax - 30, "snap")
    A(k + 0.34, "stagger", ax - 120, "out")
    E(k + 0.34, "skid", x=ax - 120, v=0.9)
    ax -= 120                                    # ~206
    A(k + 0.60, "guard", ax, "io")
    o = k + 1.20
    B(k + 0.40, "guard", bx, "out")
    B(o - 0.40, "walk1", bx - 30)
    E(o - 0.40, "step", who="B", v=1.0)
    B(o - 0.26, "ax_overhead_hi", bx - 40, "back", T=-24)
    B(o, "ax_stuck", bx - 70, "snap")
    bx -= 70                                     # 376
    E(o, "slam", by="B", v=1.5, big=True)
    E(o, "pebbles", x=EDGE, n=10, v=1.0)
    stop(o, 0.10)
    A(o - 0.14, "guard", ax, "io")
    A(o - 0.04, "crouch", ax - 10, "back")
    A(o + 0.10, "jump_tuck", ax - 60, "out", air=26)
    A(o + 0.26, "guard", ax - 76, "in", sq=-0.1)
    E(o + 0.26, "ground", x=ax - 76, v=0.4)
    ax -= 76                                     # 130
    B(o + 0.30, "ax_stuck", bx, "io", T=50)
    B(o + 0.55, "ax_stuck", bx + 2, "io", T=62, sw=124)
    # the rising cut, straight through him while the axe is stuck
    tk = o + 0.90
    A(tk - 0.30, "guard", ax, "back", sq=-0.18, T=26)
    E(tk - 0.30, "zip", v=1.1)
    E(tk - 0.20, "slowmo", a0=tk - 0.20, a1=tk + 0.04, rate=0.3)
    A(tk - 0.08, "rise_wind", bx - 120, "lin")
    A(tk, "rise_cut", bx - 70, "snap")
    E(tk - 0.02, "iai")
    B(tk - 0.06, "ax_stuck", bx, "io", T=40, H=-10)
    B(tk + 0.04, "ax_hurt", bx + 10, "snap", air=6)
    E(tk, "hit", by="A", on="B", v=1.4, big=True, blood=26, dmg=0)
    E(tk + 0.01, "kill", song=True)
    E(4.0, "song", name="song_murder_in_my_mind", drop=17.03, drop_at=tk, duck_at=tk - 1.2,
      pre=0.34, duck=0.12, post=0.95)
    stop(tk, 0.06)
    ax = bx - 70
    fz = tk + 0.14
    A(fz, "rise_cut", ax + 4, "out", T=-14)
    B(fz, "ax_hurt", bx + 14)
    E(fz, "freezeframe", dur=1.2, zoom=0.18, x=(ax + bx) / 2)
    E(fz + 0.04, "dmg", who="B", by="A", amt=0, big=True)
    # the frame lets go: he staggers back, the cracked ledge breaks under him
    B(fz + 0.40, "ax_hurt", bx + 50, "out", sw=170)
    B(fz + 0.75, "ax_teeter1", bx + 80, "io", sw=150)
    bx += 80                                     # 456
    E(fz + 0.55, "pebbles", x=EDGE, n=8, v=1.0)
    E(fz + 0.60, "heart", v=1.0)
    lt = fz + 0.95
    E(lt, "ledge", x0=360)
    E(lt, "dust", x=380, v=1.4)
    stop(lt, 0.05)
    B(lt + 0.30, "ax_fall", bx + 30, "in", dy=-140, rot=-30)
    B(lt + 0.80, "ax_fall", bx + 70, "in", dy=-620, rot=-80)
    B(lt + 1.40, "ax_fall", bx + 100, "in", dy=-1600, rot=-160)
    A(fz + 0.40, "rise_cut", ax, "io", T=-6)
    A(lt + 0.20, "guard", ax - 30, "out")
    E(lt + 0.20, "skid", x=ax - 30, v=0.5)
    ax -= 30
    A(lt + 1.40, "guard", ax + 60, "io")
    A(lt + 2.00, "sw_chiburi", ax + 60, "snap")
    E(lt + 2.00, "swoosh", v=0.8)
    A(lt + 2.60, "sheathing", ax + 60, "io")
    A(lt + 3.00, "stand_sheathed", ax + 60, "snap", sheath=1)
    E(lt + 3.00, "sheathe", v=1.0, final=True)
    E(lt + 1.6, "winner", name="KATANA WINS", color="#d8323c")
    E(lt + 0.5, "frame", ids=["A", EDGE - 120])
    end = lt + 4.2
    A(end, "stand_sheathed", ax + 60, sheath=1, T=6)
    for w in ids:
        T[w].key(end, T[w].keys[-1][1], T[w].keys[-1][2])
    title = (("KATANA", NAVY), ("WAR AXE", RUST))
    return dict(fighters=[("B", T["B"], AXE), ("A", T["A"], KATANA)],
                events=ev, end=end, title=title,
                terrain=dict(edge=EDGE, tree=TREE, boulder=BOULDER),
                springy=True, fluid=True, drawn=drawn, theme="meadow", red_hits=True)
