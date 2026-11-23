"""Fight 09: "KATANA vs WAR AXE" on a cliff edge (the terrain fight).

Same meadow look as fight 08, but the ground ends at a cliff on the right,
and the scene itself takes part in the fight (terrain.py):

  0-4 s    AXE (rust red, horned helm) stands on a boulder over the drop.
           KATANA (navy, straw hat) walks in. Axe jumps down; Katana draws.
  4-9 s    the axe out-reaches him: an overhead buries itself where he stood,
           a rising rip blocked on the axe head, a chop blocked high, then a
           low mow at his legs by the old pine: he hops it and the axe bites
           the trunk at that height. The pine falls between them.
  9-13 s   Katana runs up the trunk, parries a rising swing in the air, flips
           onto the boulder. A blocked overhead leaves Axe open: Katana jumps
           down, cuts his shoulder and jumps straight back up.
  13-17 s  Axe mows the boulder apart; Katana leaps clear to the very edge.
           Axe charges and mows at his legs; Katana vaults him with a flip and
           Axe is carried to the brink.
  17-24 s  four cuts met out between them on the axe head, a kick, a last
           overhead that sticks in the ground; Katana's cut goes through him
           (freeze-frame) and the ledge breaks under him.

Spacing rule: the axe always strikes from near full reach, blades meet out
between the two men, the katana only reaches flesh after closing in.
Check with  python3 fights/audit.py --fight cliff  (flags clashes near hands,
blades through bodies, weapons crossing outside clashes, bodies overlapping).
"""
from rig import P, Track, pose
import choreo_ambush  # noqa: F401  (h_* hero poses, br_* brute poses, sp_/t_ poses)

NAVY = "#1f2d4d"
RUST = "#a8432a"
EDGE, TREE, BOULDER = 420, -380, 200
ROCK_TOP = 60          # standing height on the boulder
LOG_TOP = 67           # standing height on the fallen trunk (cut height 59 + 8)

KATANA = dict(name="KATANA", body=NAVY, back="#5a6c93", band="#d8323c", hat="#d9b26a",
              scabbard=True, scab="#4a2626", steel="#eef2f6", ghost="#5a6c93",
              trail="#e6ecff", limb=8.5, size=1.0, blade=66)
AXE = dict(name="AXE", body=RUST, back="#d07a5a", horns="#e8dcc0", sword="axe",
           blade=124, butt=10, head_len=34, head_w=34, wood="#6e4a2a", steel="#d7dce1",
           ghost="#d07a5a", trail="#ffe6da", limb=10.5, torso=1.3, size=1.16)

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
# low sweep at the legs: the head travels a hand's width above the ground
pose("ax_low_wind", "sweep_wind", T=10, H=10, uaf=230, faf=250, sw=-95,
     thf=120, shf=178, thb=230, shb=214)
pose("ax_low_sweep", "sweep", T=42, H=30, uaf=130, faf=118, sw=96,
     thf=108, shf=170, thb=248, shb=245)
# the haft held out in front, angled up: blocks land on its upper half
# underhand mow: from low behind, through the bottom, out low in front (in a
# side view a horizontal swing that stays near the ground)
pose("ax_mow_wind", "sweep_wind", T=0, H=6, uaf=230, faf=220, sw=-120,
     thf=140, shf=178, thb=222, shb=210)
pose("ax_mow_mid", "sweep", T=20, H=10, uaf=40, faf=20, sw=178,
     thf=125, shf=175, thb=230, shb=214)
pose("ax_mow_mid2", "sweep", T=24, H=10, uaf=70, faf=40, sw=150,
     thf=125, shf=175, thb=230, shb=214)
pose("ax_block_diag", "block_mid", T=-4, uaf=120, faf=60, sw=38)
pose("ax_block_diag2", "block_mid", T=-8, uaf=100, faf=40, sw=55)
# katana: a high horizontal cut (at the haft above the hands)
# the axe at rest: held up and back across the body, head high, so at fighting
# distance it does not poke into the other man
pose("ax_guard", "guard", T=8, uaf=170, faf=135, sw=30)
AX_REST = dict(uaf=170, faf=135, sw=30)
pose("k_side_hi", "side_cut", uaf=70, faf=60, sw=78, T=14)
pose("k_side_hi_wind", "side_wind", uaf=200, faf=-50, sw=-80)
pose("k_dive", T=70, H=50, uaf=170, faf=170, uab=200, fab=190, sw=110, grip=0,
     thf=150, shf=200, thb=250, shb=270)


def build(drawn=True):
    ids = ["B", "A"]
    T = {"A": Track(facing=1), "B": Track(facing=1)}
    X, ROT = {}, {"A": 0.0, "B": 0.0}
    SWOFF = {"A": 0.0, "B": 0.0}   # full turns of the weapon (an underhand mow
                                    # goes round through the bottom)
    ST = {"A": [], "B": []}
    ev = []

    def E(t, kind, **kw):
        ev.append((t, kind, kw))

    def K(w, t, name, x=None, e="io", **kw):
        if x is None:
            x = X[w]
        X[w] = x
        kw["rot"] = ROT[w] + kw.get("rot", 0)
        if SWOFF[w]:
            kw["sw"] = kw.get("sw", P[name]["sw"]) + SWOFF[w]
        for a, b, d in ST[w]:
            if a <= t < b:
                for k, v in d.items():
                    kw.setdefault(k, v)
        T[w].key(t, name, x, e, **kw)

    def A(t, name, x=None, e="io", **kw):
        K("A", t, name, x, e, **kw)

    def B(t, name, x=None, e="io", **kw):
        if name in ("guard", "walk1", "walk2", "run1_g", "run2_g"):
            for k_, v_ in AX_REST.items():
                kw.setdefault(k_, v_)
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
    ax = -500
    A(0.0, "h_walk1", ax)
    for i in range(7):
        tt = 0.36 * (i + 1)
        ax += 30
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
    E(1.5, "frame", ids=["A", "B"])
    E(3.9, "frame", ids=["A", "B"])

    # Spacing rule (from how long-axe vs sword fights actually go): the axe
    # strikes from near its full reach (hips ~215-235 apart), so blades meet out
    # between the two men, on the axe's upper haft / head and the katana's mid
    # blade. The katana only reaches flesh after closing in (hips <= 130), and
    # gets straight back out of the axe's range.
    # =========================================================== 4-9 the axe is heavy
    # beat 1: two heavy steps, an overhead from full reach; he hops back and it
    # buries itself in the ground where he stood
    for i in range(2):
        tt = 3.80 + 0.26 * i
        bx -= 40
        B(tt, "walk2" if i % 2 == 0 else "walk1", bx)
        E(tt, "step", who="B", v=0.9)
    t = 4.55                                     # bx 10
    B(t - 0.30, "ax_overhead_hi", bx - 10, "back")
    B(t, "ax_stuck", bx - 40, "snap")
    bx -= 40                                     # -30: head lands at ~-255
    E(t, "slam", by="B", v=1.2)
    stop(t, 0.07)
    A(t - 0.50, "guard", ax, "io")
    A(t - 0.38, "crouch", ax - 4, "back")
    A(t - 0.22, "jump_tuck", ax - 50, "out", air=34)
    A(t - 0.02, "guard", ax - 70, "in", sq=-0.1)
    E(t - 0.02, "ground", x=ax - 70, v=0.4)
    ax -= 70                                     # -358
    B(t + 0.25, "ax_stuck", bx - 4, "io", T=48)
    B(t + 0.45, "ax_stuck", bx - 8, "io", T=60, sw=122)
    B(t + 0.62, "ax_stuck", bx - 2, "io", T=44, sw=116)
    # beat 2: Katana rushes in while it is stuck; Axe rips it out in a rising
    # arc and Katana has to block it on the upper haft, it throws him back
    c1 = t + 0.92
    E(c1 - 0.34, "zip", v=0.9)
    A(c1 - 0.32, "guard", ax, "back", sq=-0.14, T=24)
    A(c1 - 0.15, "k_run1", ax + 44)
    E(c1 - 0.15, "step", who="A", v=0.5)
    xa = bx - 266
    A(c1 - 0.02, "block_mid", xa, "snap", sw=24)
    B(c1 - 0.40, "ax_stuck", bx, "io", T=50, sw=122)
    B(c1 - 0.22, "sweep_wind", bx + 4, "back")
    B(c1, "sweep", bx, "snap", sw=48)
    E(c1, "clash", v=1.3, big=True)
    stop(c1, 0.09)
    A(c1 + 0.06, "block_mid", xa - 12, "snap", T=-14)
    A(c1 + 0.34, "brace", xa - 62, "out")
    E(c1 + 0.34, "skid", x=xa - 62, v=0.9)
    ax = xa - 62                                 # -342
    B(c1 + 0.16, "rise_cut", bx + 4, "out", T=-2)
    B(c1 + 0.50, "guard", bx, "io")
    A(c1 + 0.60, "guard", ax, "io")
    # beat 3: a diagonal chop from full reach; he blocks it high and the weight
    # crushes him down
    t3 = c1 + 1.05
    xb = ax + 2 + 226
    B(t3 - 0.55, "walk1", (bx + xb) / 2)
    E(t3 - 0.55, "step", who="B", v=0.9)
    B(t3 - 0.30, "heavy_wind", xb + 10, "back")
    B(t3, "high_cut", xb, "snap", sw=20)
    bx = xb                                      # -114
    A(t3 - 0.12, "guard", ax, "io")
    A(t3 - 0.01, "block_high", ax + 2, "snap", sw=76)
    E(t3, "clash", v=1.3, big=True)
    stop(t3, 0.10)
    A(t3 + 0.14, "brace", ax - 6, "snap", sq=-0.14)
    E(t3 + 0.14, "skid", x=ax - 6, v=0.8)
    ax -= 6                                      # -346
    B(t3 + 0.14, "high_cut", bx, "io", T=34, sw=26)
    B(t3 + 0.36, "high_cut", bx + 16, "out", T=10, sw=20)
    # beat 4: his back is at the pine. A low sweep at his legs: he hops it and
    # the axe bites into the trunk behind him, at the height it was swung
    s = t3 + 1.10
    bx = TREE + 242                              # -138: head reaches the trunk
    B(t3 + 0.50, "guard", bx + 14, "out")
    B(s - 0.34, "ax_mow_wind", bx + 10, "back")
    B(s - 0.13, "ax_mow_mid", bx + 6, "in", sw=-182)
    B(s - 0.06, "ax_mow_mid2", bx + 3, "lin", sw=-210)
    SWOFF["B"] -= 360
    B(s, "ax_low_sweep", bx, "out")
    A(t3 + 0.55, "guard", ax, "io")
    A(s - 0.30, "guard", ax, "io")
    A(s - 0.20, "crouch", ax, "back", sq=-0.14)
    A(s - 0.07, "jump_tuck", ax - 2, "out", air=66)
    A(s + 0.08, "jump_tuck", ax - 4, "io", air=56)
    A(s + 0.24, "crouch", ax - 8, "in", sq=-0.12)
    E(s + 0.24, "ground", x=ax - 8, v=0.4)
    E(s, "treecut", by="B", dir=1, dur=0.95)
    stop(s, 0.08)
    E(s, "dust", x=TREE, v=0.6)
    # the pine comes down on both of them: he rolls back over the stump,
    # Axe jumps clear the other way
    A(s + 0.46, "tumble", ax - 90, "out", rot=-180, air=58)
    A(s + 0.72, "crouch", ax - 180, "in", rot=-360, sq=-0.1)
    ROT["A"] -= 360
    E(s + 0.72, "ground", x=ax - 180, v=0.6)
    ax -= 180                                    # -512
    B(s + 0.12, "ax_low_sweep", bx + 50, "out")
    B(s + 0.30, "guard", bx + 56, "out", H=-24)
    B(s + 0.42, "crouch", bx + 10, "back", sw=60, grip=1)
    B(s + 0.72, "jump_tuck", bx + 110, "out", air=40, sw=60, uaf=150, faf=95)
    B(s + 0.94, "ax_land", bx + 170, "in", air=0, sq=-0.12)
    E(s + 0.94, "ground", x=bx + 170, v=0.6)
    bx += 170                                    # 32
    tl = s + 0.95
    E(tl, "treefall", v=1.0)
    E(tl, "dust", x=TREE + 140, v=1.4)
    E(tl, "dust", x=TREE + 230, v=1.2)
    stop(tl, 0.05)
    A(tl + 0.30, "guard", ax, "io")
    B(tl + 0.30, "guard", bx, "io")

    # =========================================================== 9-13 the trunk, the boulder
    t0 = tl + 0.70
    A(t0, "guard", ax, "back", sq=-0.12, T=22)
    E(t0 + 0.05, "zip", v=0.7)
    A(t0 + 0.16, "k_run1", ax + 70)
    E(t0 + 0.16, "step", who="A", v=0.5)
    A(t0 + 0.30, "crouch", TREE - 20, "out", sq=-0.1)
    A(t0 + 0.46, "k_run2", TREE + 50, "out", air=LOG_TOP)
    E(t0 + 0.46, "step", who="A", v=0.6)
    A(t0 + 0.60, "k_run1", TREE + 140, "lin", air=LOG_TOP)
    E(t0 + 0.60, "step", who="A", v=0.6)
    A(t0 + 0.74, "crouch", TREE + 215, "lin", air=LOG_TOP, sq=-0.14)
    # the leap over him: Axe swings up at him in the air, Katana parries it
    # high and flips over onto the boulder
    lp = t0 + 0.98
    A(lp - 0.12, "jump_tuck", bx - 182, "out", air=110)
    A(lp, "block_high", bx - 152, "snap", air=130, sw=72)
    B(lp - 0.62, "rise_wind", bx - 4, "io", sw=-130)
    B(lp - 0.24, "rise_wind", bx - 4, "io", sw=-126, T=28)
    B(lp - 0.12, "rise_wind", bx - 4, "io", sw=-120, T=30)
    B(lp, "rise_cut", bx, "snap", sw=4)
    E(lp, "clash", v=1.3, big=True)
    stop(lp, 0.08)
    B(lp + 0.12, "crouch", bx, "out", sw=150, uaf=170, faf=150)
    A(lp + 0.14, "jump_tuck", bx - 30, "out", air=200, rot=170)
    face("A", lp + 0.22, -1)
    A(lp + 0.30, "jump_tuck", bx + 90, "lin", air=160, rot=300)
    A(lp + 0.44, "crouch", BOULDER + 10, "in", air=ROCK_TOP, rot=360, sq=-0.16)
    ROT["A"] += 360
    E(lp + 0.44, "ground", x=BOULDER + 10, v=0.5)
    E(lp + 0.44, "pebbles", x=BOULDER + 40, n=3, v=0.4)
    ax = BOULDER + 10                            # 210
    A(lp + 0.76, "guard", ax, "out", air=ROCK_TOP, sw=-8)
    face("B", lp + 0.34, 1)
    B(lp + 0.55, "ax_look", -50, "out", T=10, H=4)    # axe on the shoulder: sizing him up
    bx = -50                                     # out of his reach
    # beat 5: Axe backs off to full reach and brings an overhead down on him;
    # blocked high, it glances off and bites into the rock
    h2 = lp + 1.25
    B(h2 - 0.62, "walk1", bx + 6, uaf=170, faf=135, sw=30)
    E(h2 - 0.62, "step", who="B", v=0.7)
    B(h2 - 0.45, "guard", bx + 2, "io")
    B(h2 - 0.26, "ax_overhead_hi", bx - 2, "back")
    B(h2, "high_cut", -10, "snap", sw=12)
    bx = -10
    A(h2 - 0.30, "guard", ax, "io", air=ROCK_TOP, sw=-8)
    A(h2 - 0.10, "guard", ax, "io", air=ROCK_TOP, sw=40)
    A(h2 - 0.01, "block_high", ax + 2, "snap", air=ROCK_TOP, sw=96)
    E(h2, "clash", v=1.1, big=True)
    stop(h2, 0.08)
    B(h2 + 0.16, "recoil", bx - 16, "out", sw=-40)
    # beat 6: the block throws the heavy axe back and leaves him open: he jumps
    # down onto him, a cut into the shoulder, and straight back up out of reach
    h3 = h2 + 0.40
    A(h3 - 0.22, "crouch", ax, "back", air=ROCK_TOP, sq=-0.12)
    A(h3 - 0.09, "high_wind", ax - 60, "out", air=ROCK_TOP + 40)
    A(h3, "land_cut", bx + 92, "snap", air=14)
    E(h3, "hit", by="A", on="B", v=1.3, big=True, limb=("neck", "sho", 0.9), blood=16)
    stop(h3, 0.10)
    xa = bx + 100
    A(h3 + 0.10, "crouch", xa, "in", air=0, sq=-0.12)
    E(h3 + 0.10, "ground", x=xa, v=0.4)
    B(h3 + 0.02, "ax_hurt", bx - 30, "snap")
    bx -= 16
    B(h3 + 0.36, "ax_hurt", bx - 70, "out")
    E(h3 + 0.36, "skid", x=bx - 70, v=0.8)
    bx -= 70                                     # -80
    A(h3 + 0.20, "crouch", xa + 6, "back", sq=-0.14)
    A(h3 + 0.40, "jump_tuck", xa + 60, "out", air=110)
    A(h3 + 0.60, "crouch", BOULDER + 5, "in", air=ROCK_TOP, sq=-0.14)
    E(h3 + 0.60, "pebbles", x=BOULDER + 40, n=3, v=0.4)
    ax = BOULDER + 5
    A(h3 + 1.00, "guard", ax, "out", air=ROCK_TOP)
    B(h3 + 0.90, "ax_roar", bx, "out")
    E(h3 + 0.90, "roar", v=1.0)
    E(h3 + 0.90, "radial", v=0.6)
    B(h3 + 1.40, "guard", bx - 2, "io")
    bx -= 2

    # =========================================================== 13-17 the boulder breaks, the edge
    # beat 7: he smashes the rock itself; Katana sees the wind-up and leaps
    # clear, back toward the drop, and lands with his heels over it
    rs = h3 + 1.95
    B(rs - 0.62, "guard", bx - 2, "io")
    B(rs - 0.46, "ax_mow_wind", bx + 4, "back", T=4)
    B(rs - 0.13, "ax_mow_mid", bx + 2, "in", sw=-182)
    B(rs - 0.06, "ax_mow_mid2", bx, "lin", sw=-210)
    SWOFF["B"] -= 360
    B(rs, "ax_low_sweep", bx - 4, "out", sw=101)
    bx -= 4                                      # -86: head on the rock face
    E(rs, "rocksmash", by="B", dir=1, v=1.0)
    stop(rs, 0.12)
    A(rs - 0.36, "guard", ax, "io", air=ROCK_TOP)
    A(rs - 0.22, "crouch", ax, "back", air=ROCK_TOP, sq=-0.16)
    A(rs - 0.08, "jump_tuck", ax + 50, "out", air=ROCK_TOP + 70)
    A(rs + 0.12, "jump_tuck", ax + 110, "io", air=ROCK_TOP + 40)
    A(rs + 0.30, "crouch", EDGE - 84, "in", air=0, sq=-0.18)
    E(rs + 0.30, "ground", x=EDGE - 84, v=0.8)
    E(rs + 0.30, "thud", v=0.7)
    A(rs + 0.50, "crouch", EDGE - 50, "out", T=36)
    E(rs + 0.46, "skid", x=EDGE - 50, v=1.0)
    E(rs + 0.50, "pebbles", x=EDGE, n=7, v=1.0)
    ax = EDGE - 50                               # 370: heels over the drop
    A(rs + 0.68, "k_teeter1", ax + 4, "out")
    E(rs + 0.70, "pebbles", x=EDGE, n=4, v=0.8)
    A(rs + 0.86, "k_teeter2", ax + 6, "io")
    A(rs + 1.04, "k_teeter1", ax + 4, "io")
    A(rs + 1.22, "guard", ax - 10, "out", T=20)
    ax -= 10                                     # 360
    E(rs + 0.80, "heart", v=0.9)
    B(rs + 0.34, "ax_low_sweep", bx + 8, "io", T=24)
    B(rs + 0.90, "guard", bx, "io")
    # beat 8: Axe charges to drive him over and mows low at his legs; Katana
    # vaults over him with a flip, the axe passes under, and the charge carries
    # Axe to the brink
    ch = rs + 1.40
    B(ch - 0.24, "guard", bx - 6, "back", sq=-0.14, T=24)
    for i in range(4):
        tt = ch + 0.15 * (i + 1)
        bx += 62
        B(tt, "run2_g" if i % 2 == 0 else "run1_g", bx)
        E(tt, "step", who="B", v=1.0)
    ct = ch + 0.80                               # bx 162
    B(ct - 0.20, "ax_mow_wind", bx + 14, "back")
    B(ct - 0.08, "ax_mow_mid", bx + 26, "in", sw=-182)
    B(ct - 0.03, "ax_mow_mid2", bx + 32, "lin", sw=-210)
    SWOFF["B"] -= 360
    B(ct + 0.04, "ax_low_sweep", bx + 44, "out")
    bx += 44                                     # 206
    E(ct + 0.04, "swoosh", v=1.0)
    E(ct - 0.20, "pass", dur=0.62)
    A(ct - 0.40, "guard", ax, "io")
    A(ct - 0.20, "crouch", ax - 4, "back", sq=-0.16)
    E(ct - 0.16, "zip", v=0.9)
    A(ct - 0.06, "jump_tuck", ax - 50, "out", air=110)
    A(ct + 0.10, "jump_tuck", ax - 150, "lin", air=200, rot=160)
    A(ct + 0.26, "jump_tuck", ax - 250, "lin", air=150, rot=300)
    A(ct + 0.40, "crouch", ax - 300, "in", rot=360, sq=-0.14)
    ROT["A"] += 360
    E(ct + 0.40, "ground", x=ax - 300, v=0.6)
    ax -= 300                                    # 60
    face("A", ct + 0.30, 1)
    A(ct + 0.70, "guard", ax, "out")
    B(ct + 0.20, "ax_low_sweep", bx + 70, "io", T=30)
    xt = EDGE - 30
    B(ct + 0.42, "ax_teeter1", xt, "out", sw=60)
    E(ct + 0.42, "pebbles", x=EDGE, n=8, v=1.0)
    B(ct + 0.66, "ax_teeter2", xt + 4, "io", sw=20)
    B(ct + 0.90, "ax_teeter1", xt, "io", sw=60)
    B(ct + 1.14, "ax_plant", xt - 14, "out")
    E(ct + 1.14, "thud", v=0.6)
    face("B", ct + 1.22, -1)
    B(ct + 1.42, "guard", xt - 20, "io")
    bx = xt - 20                                 # 370

    # =========================================================== 17-24 Katana takes over
    # beat 9: four cuts; every one is met out in front on the upper haft
    f0 = ct + 1.90
    E(f0 - 0.30, "zip", v=1.0)
    A(f0 - 0.46, "guard", ax, "back", sq=-0.14, T=22)
    A(f0 - 0.30, "k_run1", ax + 40)
    combo = (("k_side_hi_wind", "k_side_hi", 44, "ax_block_diag"),
             ("rise_wind", "rise_cut", 20, "ax_block_diag2"),
             ("k_side_hi_wind", "k_side_hi", 44, "ax_block_diag"),
             ("rise_wind", "rise_cut", 20, "ax_block_diag2"))
    for i, (wd, st_, swa, blk) in enumerate(combo):
        ti = f0 + 0.32 * i
        xa = bx - 212 + 6 * i
        A(ti - 0.13, wd, xa - 10, "back")
        A(ti, st_, xa, "snap", sw=swa)
        B(ti - 0.10, "guard", bx, "io")
        B(ti - 0.01, blk, bx + 4, "snap", sw=64)
        E(ti, "clash", v=1.0 + 0.08 * i, big=(i == 3))
        stop(ti, 0.06)
        if i == 3:
            E(ti, "pebbles", x=EDGE, n=5, v=0.8)
    ax = bx - 212 + 18                           # 282
    # beat 10: Axe lunges in with a kick that throws him off
    k = f0 + 1.40
    B(k - 0.30, "guard", bx, "io")
    B(k - 0.16, "kick_wind", bx - 30, "back", sw=-10)
    B(k, "kick", bx - 80, "snap", sw=-20)
    E(k, "hit", by="B", on="A", v=1.2, part="ftf")
    stop(k, 0.07)
    bx -= 80                                     # 396
    A(k - 0.20, "guard", ax, "io")
    A(k + 0.02, "recoil", ax - 30, "snap")
    A(k + 0.34, "stagger", ax - 110, "out")
    E(k + 0.34, "skid", x=ax - 110, v=0.9)
    ax -= 110                                    # 174
    A(k + 0.60, "guard", ax, "io")
    B(k + 0.40, "guard", bx, "out")
    # beat 11: one last overhead from full reach; he hops back, it sticks
    o = k + 1.20
    B(o - 0.40, "walk1", bx - 6)
    E(o - 0.40, "step", who="B", v=1.0)
    B(o - 0.26, "ax_overhead_hi", bx - 10, "back", T=-24)
    B(o, "ax_stuck", bx - 30, "snap")
    bx -= 30                                     # 366
    E(o, "slam", by="B", v=1.5, big=True)
    E(o, "pebbles", x=EDGE, n=10, v=1.0)
    stop(o, 0.10)
    A(o - 0.58, "guard", ax, "io")
    A(o - 0.46, "crouch", ax - 4, "back")
    A(o - 0.30, "jump_tuck", ax - 50, "out", air=34)
    A(o - 0.10, "guard", ax - 80, "in", sq=-0.1)
    E(o - 0.10, "ground", x=ax - 80, v=0.4)
    ax -= 80
    B(o + 0.30, "ax_stuck", bx, "io", T=50)
    B(o + 0.55, "ax_stuck", bx + 2, "io", T=62, sw=124)
    # the kill: he closes in while the axe is stuck, a cut through the body
    tk = o + 0.92
    A(tk - 0.34, "guard", ax, "back", sq=-0.18, T=26)
    E(tk - 0.30, "zip", v=1.1)
    E(tk - 0.20, "slowmo", a0=tk - 0.20, a1=tk + 0.04, rate=0.3)
    A(tk - 0.18, "k_run1", ax + 60, air=8)
    A(tk - 0.08, "side_wind", bx - 150, "lin")
    A(tk, "side_cut", bx - 125, "snap")
    E(tk - 0.02, "iai")
    B(tk - 0.06, "ax_stuck", bx, "io", T=40, H=-10)
    B(tk + 0.04, "ax_hurt", bx + 10, "snap", air=6)
    E(tk, "hit", by="A", on="B", v=1.4, big=True, blood=26, dmg=0, limb=("hip", "neck", 0.6))
    E(tk + 0.01, "kill", song=True)
    E(4.0, "song", name="song_murder_in_my_mind", drop=17.03, drop_at=tk, duck_at=tk - 1.2,
      pre=0.34, duck=0.12, post=0.95)
    stop(tk, 0.06)
    ax = bx - 125
    fz = tk + 0.14
    A(fz, "side_cut", ax + 4, "out", T=-10)
    B(fz, "ax_hurt", bx + 14)
    E(fz, "freezeframe", dur=1.2, zoom=0.18, x=(ax + bx) / 2)
    E(fz + 0.04, "dmg", who="B", by="A", amt=0, big=True)
    # the frame lets go: he staggers back, the cracked ledge breaks under him
    B(fz + 0.40, "ax_hurt", bx + 60, "out", sw=170)
    B(fz + 0.75, "ax_teeter1", bx + 110, "io", sw=150)
    bx += 110                                    # near the edge
    E(fz + 0.55, "pebbles", x=EDGE, n=8, v=1.0)
    E(fz + 0.60, "heart", v=1.0)
    lt = fz + 0.95
    E(lt, "ledge", x0=EDGE - 160)
    E(lt, "dust", x=EDGE - 140, v=1.4)
    stop(lt, 0.05)
    B(lt + 0.30, "ax_fall", bx + 30, "in", dy=-140, rot=-30)
    B(lt + 0.80, "ax_fall", bx + 70, "in", dy=-620, rot=-80)
    B(lt + 1.40, "ax_fall", bx + 100, "in", dy=-1600, rot=-160)
    A(fz + 0.40, "side_cut", ax, "io", T=-6)
    A(lt + 0.20, "guard", ax - 30, "out")
    E(lt + 0.20, "skid", x=ax - 30, v=0.5)
    ax -= 30
    A(lt + 1.40, "guard", ax + 40, "io")
    A(lt + 2.00, "sw_chiburi", ax + 40, "snap")
    E(lt + 2.00, "swoosh", v=0.8)
    A(lt + 2.60, "sheathing", ax + 40, "io")
    A(lt + 3.00, "stand_sheathed", ax + 40, "snap", sheath=1)
    E(lt + 3.00, "sheathe", v=1.0, final=True)
    E(lt + 1.6, "winner", name="KATANA WINS", color="#d8323c")
    E(lt + 0.5, "frame", ids=["A", EDGE - 120])
    end = lt + 4.2
    A(end, "stand_sheathed", ax + 40, sheath=1, T=6)
    for w in ids:
        T[w].key(end, T[w].keys[-1][1], T[w].keys[-1][2])

    title = (("KATANA", NAVY), ("WAR AXE", RUST))
    return dict(fighters=[("B", T["B"], AXE), ("A", T["A"], KATANA)],
                events=ev, end=end, title=title,
                terrain=dict(edge=EDGE, tree=TREE, boulder=BOULDER),
                springy=True, fluid=True, drawn=drawn, theme="meadow", red_hits=True,
                clear_hands=36)
