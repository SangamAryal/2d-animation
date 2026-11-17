"""Fight 06: "SAMURAI vs KNIGHT" (speed vs armour).

SAMURAI (black, red headband, topknot, katana) is fast. KNIGHT (big, slate
plate, great helm with a blue plume, longsword and kite shield) is slow but
every cut lands on steel. The samurai's flurry dies on the shield, his cuts
skid off the armour, then he splits the shield with a jumping cut, opens the
armpit gap, and ends it by flipping over the knight's final overhead slam
with a mid-air draw. He lands with his back turned; the head comes off when
the sword clicks home.

Same 4-beat keying as the spear fight (anticipation, strike, follow-through,
recovery); secondary motion comes from motion.py because springy=True.
"""
from rig import P, Track, pose

SAMURAI = dict(name="SAMURAI", body="#16161b", back="#44444f", band="#e0303a",
               topknot=True, scabbard=True, scab="#5a2a2a", steel="#eef3f7",
               ghost="#e0303a", trail="#ffe3e3", blade=82, limb=8.5)
KNIGHT = dict(name="KNIGHT", body="#2a3850", back="#6a7d9c", helm="#c8cfd8",
              plume="#2a5bc4", shield="#2a5bc4", rim="#e3b341",
              sword="longsword", blade=94, steel="#eef3f7", ghost="#6a7d9c",
              trail="#e3ecff", size=1.12, limb=10.5, torso=1.25, grip_off=10.0)
BLUE = "#2a5bc4"
RED = "#e0303a"

# ---------------------------------------------------------------- knight poses
# grip=0 everywhere: the back hand holds the shield, not the sword
pose("k_rest", T=2, H=0, uaf=160, faf=120, sw=60, grip=0, uab=140, fab=60,
     thf=165, shf=180, thb=195, shb=184)
pose("k_guard", T=6, H=4, uaf=150, faf=82, sw=38, grip=0, uab=125, fab=45,
     thf=148, shf=182, thb=214, shb=198)
pose("k_walk1", "k_guard", thf=160, shf=186, thb=200, shb=214)
pose("k_walk2", "k_guard", thf=198, shf=188, thb=162, shb=176)
pose("k_brace", T=12, H=6, uaf=165, faf=110, sw=50, grip=0, uab=110, fab=35,
     thf=130, shf=180, thb=228, shb=208)
pose("k_shield_up", T=0, H=-2, uaf=165, faf=110, sw=40, grip=0, uab=95, fab=8,
     thf=145, shf=182, thb=218, shb=200)
pose("k_bash_wind", T=-10, H=-4, uaf=175, faf=130, sw=60, grip=0, uab=185, fab=95,
     thf=150, shf=182, thb=212, shb=196)
pose("k_bash", T=32, H=22, uaf=175, faf=140, sw=80, grip=0, uab=82, fab=72,
     thf=108, shf=172, thb=244, shb=256)
pose("k_over_wind", T=-12, H=-6, uaf=15, faf=-25, sw=-125, grip=0, uab=130, fab=60,
     thf=148, shf=182, thb=212, shb=196)
pose("k_over", T=46, H=36, uaf=120, faf=140, sw=158, grip=0, uab=150, fab=90,
     thf=108, shf=176, thb=246, shb=246)
pose("k_side_wind", T=-10, H=0, uaf=228, faf=-30, sw=-95, grip=0, uab=120, fab=50,
     thf=150, shf=180, thb=212, shb=196)
pose("k_side", T=22, H=15, uaf=100, faf=95, sw=95, grip=0, uab=150, fab=90,
     thf=125, shf=178, thb=235, shb=218)
pose("k_rise_wind", T=24, H=18, uaf=195, faf=225, sw=228, grip=0, uab=120, fab=60,
     thf=130, shf=178, thb=230, shb=212)
pose("k_rise", T=-8, H=-6, uaf=40, faf=40, sw=20, grip=0, uab=140, fab=80,
     thf=150, shf=180, thb=205, shb=192)
pose("k_press", T=26, H=18, uaf=55, faf=48, sw=122, grip=0, uab=150, fab=90,
     thf=112, shf=176, thb=244, shb=244)
pose("k_bang_up", T=-4, H=-6, uaf=30, faf=10, sw=-10, grip=0, uab=118, fab=40,
     thf=152, shf=182, thb=208, shb=194)
pose("k_bang", T=4, H=2, uaf=128, faf=165, sw=200, grip=0, uab=118, fab=40,
     thf=152, shf=182, thb=208, shb=194)
# two-handed, after the shield is gone
pose("k_charge1", "heavy_wind", T=8, thf=110, shf=170, thb=228, shb=280)
pose("k_charge2", "heavy_wind", T=8, thf=212, shf=272, thb=126, shb=180)
pose("k_slam", "slam", T=52, H=44, sw=112)


def build(knight_wins=False, armoured=False):
    knight = dict(KNIGHT, body="#a9b3c1", back="#727e8d", plate=True, tabard=BLUE,
                  limb=9.5) if armoured else KNIGHT
    A = Track(facing=1)    # SAMURAI, starts left
    B = Track(facing=-1)   # KNIGHT, starts right
    ev = []
    R = [0]                # samurai's accumulated flip rotation (keeps rot continuous)
    NS = [0]               # knight has lost the shield

    # v3 (knight wins) is longer: an extra exchange is inserted at T0 and
    # everything keyed after it slides D seconds later.
    LONG = knight_wins
    T0, D = 7.95, 3.2
    RAW = [False]

    def S(t):
        return t + D if (LONG and t >= T0 and not RAW[0]) else t

    def E(t, kind, **kw):
        for k in ("a0", "a1", "stop_at", "duck_at"):
            if k in kw:
                kw[k] = S(kw[k])
        ev.append((S(t), kind, kw))

    _af, _bf = A.face, B.face
    A.face = lambda t, f: _af(S(t), f)
    B.face = lambda t, f: _bf(S(t), f)

    def stop(t, d):
        E(t, "hitstop", dur=d)

    def AK(t, name, x, e="io", **kw):
        kw["rot"] = R[0] + kw.get("rot", 0)
        A.key(S(t), name, x, e, **kw)

    def BK(t, name, x, e="io", **kw):
        if NS[0]:
            kw.setdefault("noshield", 1)
        B.key(S(t), name, x, e, **kw)

    # ======================================================= intro (0 - 2.6)
    A.key(0.0, "swalk1", -470)
    t, x = 0.0, -470
    for i in range(4):
        t += 0.30
        x += 40
        A.key(t, "swalk2" if i % 2 == 0 else "swalk1", x)
        E(t, "step", who="A", v=0.5)
    A.key(1.35, "stand_sheathed", -320)
    # knight marches in: heavy armoured steps
    BK(0.0, "k_walk1", 470)
    t, x = 0.0, 470
    for i in range(3):
        t += 0.36
        x -= 40
        BK(t, "k_walk2" if i % 2 == 0 else "k_walk1", x)
        E(t, "step", who="B", v=0.9, armor=True)
    BK(1.18, "k_guard", 350)
    E(1.18, "stomp", x=350, v=0.8)
    # bangs the sword on the shield twice
    BK(1.40, "k_bang_up", 350, "back")
    BK(1.52, "k_bang", 348, "snap")
    E(1.52, "shieldbang", v=0.8)
    E(1.52, "flinch", who="B", v=0.4)
    BK(1.68, "k_bang_up", 350, "back")
    BK(1.80, "k_bang", 348, "snap")
    E(1.80, "shieldbang", v=1.0)
    E(1.80, "flinch", who="B", v=0.5)
    BK(2.20, "k_guard", 300, "out")
    E(2.20, "step", who="B", v=0.8, armor=True)
    # samurai draws
    A.key(1.60, "iai", -310)
    A.key(1.95, "iai_deep", -312)
    A.key(2.10, "iai_cut", -300, "snap", sheath=0, T=20, H=12)
    E(2.07, "draw")
    A.key(2.40, "guard", -280, "out")
    E(0.05, "drum", v=1.0)
    E(1.18, "drum", v=0.8)
    E(2.45, "banner", text="FIGHT!")
    E(2.45, "fight")
    if LONG:
        # Kordhell "Murder In My Mind": its drop (17.03 s) lands on the kill
        E(2.45, "song", name="song_murder_in_my_mind", drop=17.03, duck_at=11.25,
          pre=0.34, duck=0.12, post=0.9)
    else:
        E(2.45, "bed", stop_at=11.2, gain=0.32)

    # ======================================================= round 1: the shield
    # (2.6 - 5.4) a four-cut flurry dies on the shield, shield bash, overhead slam
    bx = 240
    BK(2.70, "k_brace", bx)
    AK(2.68, "crouch", -280)
    AK(2.84, "dash", 50, "lin")
    E(2.70, "zip", v=1.0)
    E(2.70, "dust", x=-280, v=0.8)
    # 1: side cut
    AK(2.92, "side_wind", 70, "out")
    AK(3.00, "side_cut", 82, "snap")
    E(3.00, "shieldhit", by="A", on="B", v=0.9)
    stop(3.00, 0.05)
    BK(3.02, "k_brace", bx + 6, "snap")
    # 2: rising cut
    AK(3.08, "rise_wind", 78, "out")
    AK(3.16, "rise_cut", 88, "snap")
    E(3.16, "shieldhit", by="A", on="B", v=0.9)
    stop(3.16, 0.05)
    BK(3.12, "k_shield_up", bx + 6)
    BK(3.18, "k_shield_up", bx + 12, "snap")
    # 3: overhead
    AK(3.24, "high_wind", 84, "back")
    AK(3.34, "high_cut", 96, "snap")
    E(3.34, "shieldhit", by="A", on="B", v=1.0)
    stop(3.34, 0.06)
    BK(3.36, "k_shield_up", bx + 16, "snap", T=-4)
    # 4: side cut again
    AK(3.42, "side_wind", 90, "out")
    AK(3.50, "side_cut", 100, "snap")
    E(3.50, "shieldhit", by="A", on="B", v=1.0)
    stop(3.50, 0.05)
    BK(3.46, "k_brace", bx + 14)
    BK(3.52, "k_brace", bx + 18, "snap")
    # shield bash: samurai flies back
    BK(3.60, "k_bash_wind", bx + 30, "back")
    BK(3.72, "k_bash", bx - 70, "snap")
    E(3.72, "hit", by="B", on="A", v=1.1, big=True, dmg=10, part="hab")
    stop(3.72, 0.12)
    AK(3.62, "side_cut", 100)
    AK(3.73, "recoil", 95, "snap")
    AK(3.98, "recoil", -60, "out", air=30)
    AK(4.20, "stagger", -170, "out")
    E(4.20, "skid", x=-170, v=1.2)
    AK(4.45, "guard_low", -185)
    ax = -185
    bx -= 70    # 170
    # knight walks in and brings the overhead down
    BK(3.95, "k_guard", bx)
    BK(4.15, "k_walk1", bx - 35)
    E(4.15, "step", who="B", v=0.8, armor=True)
    BK(4.35, "k_walk2", bx - 70)
    E(4.35, "step", who="B", v=0.8, armor=True)
    bx -= 70    # 100
    BK(4.50, "k_over_wind", bx - 5, "back")
    BK(4.64, "k_over_wind", bx - 8, "lin", T=-18)     # held beat at the top
    BK(4.80, "k_over", bx - 40, "snap")
    E(4.81, "slam", by="B", v=1.1)
    stop(4.81, 0.12)
    # samurai back-flips out of it
    AK(4.62, "crouch", ax)
    AK(4.76, "jump_tuck", ax - 80, "out", air=105, rot=-200, T=20)
    AK(4.96, "jump_tuck", ax - 150, "in", air=5, rot=-360, T=20)
    AK(5.02, "guard_low", ax - 160, "snap", rot=-360)
    E(5.00, "skid", x=ax - 160, v=0.8)
    R[0] -= 360
    ax -= 160    # -345
    bx -= 40     # 60
    BK(5.10, "k_over", bx, dy=-3)
    BK(5.45, "k_guard", bx + 20, "out")

    # ======================================================= round 2: the armour
    # (5.4 - 8.0) cuts skid off the plate, knight sweeps, backhand sends him flying
    AK(5.40, "crouch", ax)
    AK(5.54, "dash", bx - 135, "lin")
    E(5.42, "zip", v=1.0)
    E(5.42, "dust", x=ax, v=0.8)
    ax = bx - 135    # -75
    AK(5.62, "side_wind", ax + 10, "out")
    AK(5.70, "side_cut", ax + 25, "snap")
    E(5.70, "armor", by="A", on="B", v=1.0, dmg=2)
    stop(5.70, 0.07)
    BK(5.72, "k_guard", bx + 26, "snap", T=-6)
    AK(5.80, "rise_wind", ax + 22, "out")
    AK(5.88, "rise_cut", ax + 32, "snap")
    E(5.88, "armor", by="A", on="B", v=1.0, dmg=2)
    stop(5.88, 0.07)
    BK(5.90, "k_guard", bx + 30, "snap", T=-10, H=-8)
    # knight's flat sweep: samurai ducks under it
    BK(6.00, "k_side_wind", bx + 34, "back")
    BK(6.14, "k_side", bx + 6, "snap")
    E(6.14, "gust", x=ax + 20, v=1.0)
    AK(5.98, "rise_cut", ax + 30)
    AK(6.08, "crouch", ax + 20, "snap", T=48, H=40, sw=20)
    # ...and the rising backhand catches him on the way up
    BK(6.26, "k_rise_wind", bx + 14, "back")
    BK(6.38, "k_rise", bx - 6, "snap")
    AK(6.28, "crouch", ax + 18, T=40, H=30)
    AK(6.36, "guard", ax + 18)
    E(6.38, "hit", by="B", on="A", v=1.1, big=True, dmg=14)
    stop(6.38, 0.13)
    AK(6.39, "tumble", ax + 5, "snap", air=40, rot=-30)
    AK(6.68, "tumble", ax - 190, "lin", air=110, rot=-330)
    AK(6.90, "fallen", ax - 280, "in", rot=-360)
    E(6.90, "thud", v=1.0)
    E(6.90, "skid", x=ax - 280, v=1.2)
    AK(7.12, "fallen", ax - 300, "out", rot=-360)
    AK(7.55, "kneel", ax - 300, rot=-360)
    AK(7.85, "guard_low", ax - 300, rot=-360)
    R[0] -= 360
    ax -= 300    # -350
    # knight bangs the shield again and walks in
    BK(6.60, "k_guard", bx + 10, "out")
    BK(6.95, "k_bang_up", bx + 10, "back")
    BK(7.07, "k_bang", bx + 8, "snap")
    E(7.07, "shieldbang", v=1.0)
    E(7.07, "flinch", who="B", v=0.5)
    BK(7.30, "k_guard", bx + 5)
    BK(7.52, "k_walk1", bx - 30)
    E(7.52, "step", who="B", v=0.8, armor=True)
    BK(7.74, "k_walk2", bx - 65)
    E(7.74, "step", who="B", v=0.8, armor=True)
    BK(7.95, "k_shield_up", bx - 90)
    bx -= 90    # -30
    if LONG:
        _extra_exchange(AK, BK, E, stop, RAW, T0, ax, bx)

    # ======================================================= round 3: break the shield
    # (8.0 - 11.0) jumping cut splits the shield, two parries, kick, armpit cut
    AK(7.95, "guard_low", ax)
    AK(8.08, "crouch", ax)
    AK(8.22, "dash", bx - 200, "lin")
    E(8.10, "zip", v=1.0)
    E(8.10, "dust", x=ax, v=0.9)
    AK(8.30, "crouch", bx - 180, "out")
    AK(8.44, "jump_tuck", bx - 150, "out", air=125)
    AK(8.56, "high_wind", bx - 128, "lin", air=60)
    AK(8.66, "high_cut", bx - 118, "snap")
    E(8.66, "ground", x=bx - 118, v=0.6)
    BK(8.50, "k_shield_up", bx)
    BK(8.65, "k_shield_up", bx + 2, T=-4)
    E(8.66, "shieldbreak", by="A", on="B", v=1.2, big=True)
    stop(8.66, 0.16)
    NS[0] = 1
    BK(8.67, "stagger", bx + 20, "snap")
    BK(8.95, "stagger", bx + 70, "out")
    E(8.95, "skid", x=bx + 70, v=0.9)
    bx += 70    # 40
    AK(8.80, "high_cut", bx - 190, dy=-2)
    AK(9.05, "guard", bx - 200)
    ax = bx - 200    # -160
    # two-handed now, and angry
    BK(9.10, "guard", bx)
    E(9.12, "roar", v=0.8)
    BK(9.24, "side_wind", bx + 10, "back")
    BK(9.37, "side_cut", bx - 30, "snap")
    AK(9.28, "guard", ax + 10)
    AK(9.37, "parry", ax + 4, "snap")
    E(9.37, "clash", v=1.0, big=True)
    stop(9.37, 0.10)
    AK(9.50, "guard_low", ax - 20, "out")
    BK(9.50, "high_wind", bx - 25, "back")
    BK(9.62, "high_cut", bx - 45, "snap")
    AK(9.57, "block_high", ax - 20, "snap")
    E(9.62, "clash", v=1.0)
    stop(9.62, 0.07)
    BK(9.74, "kick_wind", bx - 40, "back")
    BK(9.84, "kick", bx - 60, "snap")
    E(9.84, "hit", by="B", on="A", v=1.0, dmg=8, part="ftf")
    stop(9.84, 0.09)
    AK(9.70, "block_high", ax - 22)
    AK(9.85, "recoil", ax - 30, "snap")
    AK(10.08, "stagger", ax - 110, "out")
    E(10.08, "skid", x=ax - 110, v=1.0)
    ax -= 110    # -270
    bx -= 60     # -20
    # counter: under the raised arms, into the armpit gap
    BK(10.00, "guard", bx)
    BK(10.22, "high_wind", bx + 5, "back")
    AK(10.18, "crouch", ax)
    AK(10.30, "dash", bx - 120, "lin")
    E(10.20, "zip", v=1.0)
    AK(10.36, "rise_wind", bx - 110, "out")
    AK(10.44, "rise_cut", bx - 98, "snap")
    E(10.44, "hit", by="A", on="B", v=1.1, big=True, dmg=15)
    stop(10.44, 0.13)
    BK(10.45, "stagger", bx + 10, "snap")
    BK(10.75, "stagger", bx + 80, "out")
    E(10.75, "skid", x=bx + 80, v=0.9)
    bx += 80    # 60
    AK(10.62, "rise_cut", bx - 175)
    AK(10.85, "guard", bx - 230, "out")
    AK(11.10, "guard", bx - 270)
    ax = bx - 270    # -210

    # ======================================================= climax
    # samurai sheathes; knight raises the sword two-handed and charges
    AK(11.30, "sheathing", ax)
    AK(11.55, "iai", ax - 4, "snap", sheath=1)
    E(11.55, "sheathe")
    AK(11.95, "iai_deep", ax - 6)
    E(11.35, "heart", v=0.9)
    E(11.95, "heart", v=1.0)
    BK(11.20, "guard", bx + 30)
    BK(11.50, "heavy_wind", bx + 40, "back")
    E(11.52, "roar", v=1.0)
    BK(11.95, "heavy_wind", bx + 40, T=-20)
    t, x, i = 12.05, bx + 40, 0
    while x > ax + 230:
        t += 0.13
        x -= 56
        BK(t, "k_charge2" if i % 2 == 0 else "k_charge1", x, "lin")
        E(t, "step", who="B", v=1.0, armor=True)
        i += 1
    t_s = t + 0.14          # the slam lands
    BK(t_s - 0.07, "heavy_wind", x - 15, "lin", T=-8)
    BK(t_s, "k_slam", x - 50, "snap")
    E(t_s, "slam", by="B", v=1.2)
    stop(t_s, 0.10)
    kx = x - 50
    # samurai leaps a front flip over him, drawing at the top
    AK(t_s - 0.14, "iai_deep", ax - 6, T=50, H=40, dy=-14)
    AK(t_s - 0.04, "jump_tuck", ax + 90, "out", air=150, rot=80, sheath=1, T=30)
    t_c = t_s + 0.08
    AK(t_c - 0.01, "jump_tuck", kx - 10, "lin", air=165, rot=160, sheath=1, T=30)
    AK(t_c + 0.03, "iai_cut", kx + 15, "snap", air=165, rot=200, sheath=0)
    if knight_wins:
        # the draw rings off the great helm instead of the neck
        E(t_c + 0.01, "armor", by="A", on="B", v=1.2, dmg=3)
    E(t_c, "iai", x0=ax, x1=kx + 150)
    E(t_c, "slowmo", a0=t_s - 0.10, a1=t_c - 0.01, rate=0.22)
    AK(t_c + 0.20, "iai_cut", kx + 110, "lin", air=90, rot=310)
    xl = kx + 165
    AK(t_c + 0.30, "iai_cut", xl, "snap", rot=360)
    E(t_c + 0.30, "ground", x=xl, v=0.7)
    R[0] += 360
    BK(t_c + 0.30, "k_slam", kx, dy=-2)
    if knight_wins:
        d = _knight_ending(A, B, E, AK, BK, stop, t_c, xl, kx, ev, knight)
        d["end"] = S(d["end"])
        return d
    # silence, then the sword goes home and the head comes off
    t_brk = t_c + 1.45
    AK(t_c + 0.75, "iai_hold", xl + 2)
    AK(t_c + 1.00, "sw_chiburi", xl + 4, "snap")
    E(t_c + 1.00, "swoosh", v=0.8)
    AK(t_brk - 0.30, "sheathing", xl + 4)
    AK(t_brk, "stand_sheathed", xl + 6, "snap")
    E(t_brk, "sheathe", final=True)
    E(t_brk + 0.02, "decap", who="B", by="A")
    E(t_brk + 0.03, "dmg", who="B", by="A", amt=100, big=True)
    E(t_brk + 0.03, "kill")
    BK(t_brk + 0.03, "k_slam", kx, "snap", headless=1, dy=-2)
    BK(t_brk + 0.55, "kneel", kx + 4, "in", headless=1, sw=150, grip=0)
    E(t_brk + 0.55, "thud", v=0.8)
    BK(t_brk + 1.15, "fallen", kx + 20, "in", headless=1, sw=100)
    E(t_brk + 1.15, "thud", v=1.0)
    E(t_brk + 1.15, "dust", x=kx - 30, v=1.0)
    E(t_brk + 0.6, "winner", name="SAMURAI WINS", color=RED)
    end = t_brk + 4.2
    AK(end, "stand_sheathed", xl + 6)
    BK(end, "fallen", kx + 20, headless=1, sw=100)
    return dict(fighters=[("B", B, knight), ("A", A, SAMURAI)], events=ev, end=end,
                title=(("SAMURAI", RED), ("KNIGHT", BLUE)),
                hp=[("A", "SAMURAI", RED), ("B", "KNIGHT", BLUE)],
                springy=True)


def _extra_exchange(AK, BK, E, stop, RAW, T0, ax, bx):
    """Inserted exchange (v3): shield, a low cut that sparks off the greaves,
    a blade lock that grinds in slow motion, and a shield bash out of it."""
    RAW[0] = True
    T = lambda u: T0 + u
    cx = bx - 150                     # where the samurai fights from
    AK(T(0.05), "guard_low", ax)
    AK(T(0.16), "crouch", ax)
    AK(T(0.30), "dash", cx, "lin")
    E(T(0.17), "zip", v=1.0)
    E(T(0.17), "dust", x=ax, v=0.8)
    BK(T(0.05), "k_guard", bx)
    BK(T(0.22), "k_brace", bx)
    # cut into the shield
    AK(T(0.36), "side_wind", cx + 10, "out")
    AK(T(0.44), "side_cut", cx + 22, "snap")
    E(T(0.44), "shieldhit", by="A", on="B", v=1.0)
    stop(T(0.44), 0.05)
    BK(T(0.46), "k_brace", bx + 6, "snap")
    # drops low and cuts the leg: sparks off the greave
    AK(T(0.52), "crouch", cx + 25, "snap", T=50, H=40, sw=-40)
    AK(T(0.60), "sweep", cx + 40, "snap")
    E(T(0.60), "armor", by="A", on="B", v=1.0, dmg=2)
    stop(T(0.60), 0.07)
    BK(T(0.62), "k_guard", bx + 10, "snap", T=-8, H=-6)
    # knight's rising cut, samurai leans out of it
    BK(T(0.70), "k_rise_wind", bx + 8, "back")
    BK(T(0.82), "k_rise", bx - 10, "snap")
    AK(T(0.72), "crouch", cx + 30)
    AK(T(0.86), "stagger", cx - 50, "out")
    E(T(0.82), "gust", x=cx + 20, v=0.9)
    # overhead into a blade lock
    BK(T(1.00), "k_over_wind", bx - 5, "back")
    BK(T(1.16), "k_press", bx - 40, "snap")
    AK(T(1.10), "block_high", cx - 40, "snap")
    E(T(1.16), "clash", v=1.1, big=True)
    stop(T(1.16), 0.10)
    E(T(1.22), "scrape", dur=0.75)
    E(T(1.22), "slowmo", a0=T(1.22), a1=T(1.95), rate=0.4)
    AK(T(1.22), "block_high", cx - 42)
    AK(T(1.95), "block_high", cx - 50, "lin", T=14, H=14, dy=-12)    # pushed down
    BK(T(1.22), "k_press", bx - 42)
    BK(T(1.95), "k_press", bx - 52, "lin", T=34, H=26, sw=128, uaf=62)
    # shield bash breaks the lock
    BK(T(2.05), "k_bash_wind", bx - 40, "back")
    BK(T(2.17), "k_bash", bx - 110, "snap")
    E(T(2.17), "hit", by="B", on="A", v=1.1, big=True, dmg=6, part="hab")
    stop(T(2.17), 0.12)
    AK(T(2.06), "block_high", cx - 50, dy=-12)
    AK(T(2.18), "recoil", cx - 55, "snap")
    AK(T(2.45), "recoil", cx - 150, "out", air=28)
    AK(T(2.70), "stagger", ax + 10, "out")
    E(T(2.70), "skid", x=ax + 10, v=1.1)
    AK(T(3.05), "guard_low", ax)
    BK(T(2.55), "k_guard", bx - 90)
    BK(T(2.85), "k_walk1", bx - 50)
    E(T(2.85), "step", who="B", v=0.8, armor=True)
    BK(T(3.10), "k_walk2", bx - 15)
    E(T(3.10), "step", who="B", v=0.8, armor=True)
    RAW[0] = False


def _knight_ending(A, B, E, AK, BK, stop, t_c, xl, kx, ev, knight):
    """The samurai sheathes thinking it is over. Nothing falls. The knight
    straightens up, turns, and takes his head while his back is turned."""
    t_sh = t_c + 1.45
    AK(t_c + 0.75, "iai_hold", xl + 2)
    AK(t_c + 1.00, "sw_chiburi", xl + 4, "snap")
    E(t_c + 1.00, "swoosh", v=0.8)
    AK(t_sh - 0.30, "sheathing", xl + 4)
    AK(t_sh, "stand_sheathed", xl + 6, "snap")
    E(t_sh, "sheathe", final=True)
    # ...silence. the knight is still standing
    E(t_sh + 0.45, "heart", v=1.0)
    BK(t_sh + 0.30, "k_slam", kx, dy=-2)
    BK(t_sh + 0.70, "guard", kx + 10, "out")
    E(t_sh + 0.70, "step", who="B", v=0.9, armor=True)
    B.face(t_sh + 0.82, 1)
    BK(t_sh + 0.82, "guard", kx + 12, "snap")
    E(t_sh + 0.82, "stomp", x=kx + 12, v=0.7)
    E(t_sh + 1.05, "heart", v=1.1)
    # samurai hears the armour and starts to turn: too late
    A.face(t_sh + 1.20, -1)
    AK(t_sh + 1.12, "stand_sheathed", xl + 6, H=-10)
    AK(t_sh + 1.20, "iai", xl + 4, "snap")
    BK(t_sh + 1.00, "side_wind", kx + 40, "back")
    t_k = t_sh + 1.24
    BK(t_k, "side_cut", xl - 125, "snap")
    E(t_k - 0.02, "slowmo", a0=t_k - 0.16, a1=t_k - 0.01, rate=0.3)
    E(t_k, "decap", who="A", by="B")
    E(t_k + 0.01, "dmg", who="A", by="B", amt=100, big=True)
    E(t_k + 0.01, "kill", song=True)
    stop(t_k, 0.10)
    AK(t_k + 0.01, "iai", xl + 4, "snap", headless=1)
    AK(t_k + 0.50, "kneel", xl + 10, "in", headless=1, sheath=1)
    E(t_k + 0.50, "thud", v=0.8)
    AK(t_k + 1.10, "fallen", xl + 30, "in", headless=1, sheath=1)
    E(t_k + 1.10, "thud", v=1.0)
    E(t_k + 1.10, "dust", x=xl + 60, v=1.0)
    BK(t_k + 0.40, "side_cut", xl - 128)
    BK(t_k + 1.00, "guard", xl - 140)
    BK(t_k + 1.60, "high_wind", xl - 140, "back", T=-14, H=-16)   # raises the sword
    E(t_k + 1.60, "roar", v=0.9)
    E(t_k + 0.6, "winner", name="KNIGHT WINS", color=BLUE)
    end = t_k + 4.2
    AK(end, "fallen", xl + 30, headless=1, sheath=1)
    BK(end, "high_wind", xl - 140, T=-14, H=-16)
    return dict(fighters=[("B", B, knight), ("A", A, SAMURAI)], events=ev, end=end,
                title=(("SAMURAI", RED), ("KNIGHT", BLUE)),
                hp=[("A", "SAMURAI", RED), ("B", "KNIGHT", BLUE)],
                springy=True)


pose("sw_chiburi", T=10, H=8, uaf=150, faf=165, uab=200, fab=185, sw=200, grip=0,
     thf=150, shf=182, thb=212, shb=196) if "sw_chiburi" not in P else None
