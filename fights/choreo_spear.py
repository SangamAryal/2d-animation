"""Fight 05: "SWORD vs SPEAR" (reach vs speed).

SWORD (black, red headband, katana) is fast but short-ranged. SPEAR (teal,
gold headband, long spear with a red tassel) controls the distance with pokes, sweeps and butt strikes. SWORD learns
to get inside the reach: deflects a thrust, grinds his blade up the shaft, and
ends it with a quick-draw that cuts the spear (and its owner) in half.

Every attack is keyed in four beats: anticipation (pull back, ease "back"),
strike ("snap"), follow-through (overshoot), recovery. Secondary motion
(head bob, loose arm, weapon overshoot, flinches) comes from motion.py
because this fight sets springy=True.
"""
from rig import Track, pose

SWORD = dict(name="SWORD", body="#16161b", back="#44444f", band="#e0303a",
             scabbard=True, scab="#5a2a2a", steel="#eef3f7", ghost="#e0303a",
             trail="#ffe3e3", blade=82, limb=8.5)
SPEAR = dict(name="SPEAR", body="#14708a", back="#5aa3b8", band="#f2b821",
             sword="spear", blade=112, butt=88, grip_off=-36, head_len=28,
             cut=30, wood="#8a5a33", tassel="#d42a2a", steel="#eef3f7",
             ghost="#5aa3b8", trail="#dff6ff", limb=8.5,
             springs={"sw": (62, 0.62)})

# ---------------------------------------------------------------- spear poses
pose("sp_rest", T=2, H=0, uaf=168, faf=150, sw=8, grip=0, uab=190, fab=176,
     thf=165, shf=180, thb=195, shb=184)
pose("sp_guard", T=10, H=6, uaf=140, faf=88, sw=84, grip=1,
     thf=140, shf=182, thb=220, shb=202)
pose("sp_guard_lo", "sp_guard", T=18, sw=96, thf=128, thb=228, shb=210)
pose("sp_step1", "sp_guard", thf=160, shf=186, thb=200, shb=212)
pose("sp_step2", "sp_guard", thf=196, shf=186, thb=160, shb=178)
pose("sp_wind", T=-10, H=-4, uaf=205, faf=112, sw=90, grip=1,
     thf=152, shf=182, thb=210, shb=196)
pose("sp_thrust", T=34, H=24, uaf=96, faf=92, sw=90, grip=1,
     thf=106, shf=168, thb=246, shb=262)
pose("sp_thrust_hi", "sp_thrust", sw=72, uaf=82, faf=74, T=26)
pose("sp_thrust_lo", "sp_thrust", sw=112, uaf=118, faf=114, T=42)
pose("sp_sweep_wind", T=-14, H=-6, uaf=30, faf=-10, sw=-70, grip=1,
     thf=150, shf=182, thb=212, shb=196)
pose("sp_sweep", T=30, H=18, uaf=128, faf=132, sw=118, grip=1,
     thf=118, shf=176, thb=236, shb=222)
pose("sp_slam_wind", T=-16, H=-10, uaf=8, faf=-12, sw=-40, grip=1,
     thf=150, shf=182, thb=208, shb=194)
pose("sp_slam", T=48, H=36, uaf=118, faf=112, sw=112, grip=1,
     thf=108, shf=176, thb=246, shb=246)
pose("sp_block", T=-6, H=-2, uaf=118, faf=30, sw=12, grip=1,
     thf=150, shf=182, thb=214, shb=198)
pose("sp_butt_wind", T=-4, H=0, uaf=200, faf=130, sw=-100, grip=1,
     thf=148, shf=182, thb=212, shb=198)
pose("sp_butt", T=28, H=18, uaf=98, faf=96, sw=-96, grip=1,
     thf=112, shf=172, thb=242, shb=258)
pose("sp_knocked", T=-20, H=-18, uaf=60, faf=10, sw=-10, grip=1,
     thf=158, shf=184, thb=210, shb=196)
pose("sp_twirl", T=4, H=2, uaf=105, faf=70, sw=0, grip=0, uab=200, fab=178,
     thf=150, shf=182, thb=210, shb=196)
pose("sp_plant", T=-4, H=-8, uaf=150, faf=150, sw=0, grip=0, uab=205, fab=190,
     thf=158, shf=182, thb=204, shb=190)
pose("sp_run1", T=26, H=14, uaf=145, faf=95, sw=92, grip=1,
     thf=110, shf=170, thb=228, shb=282)
pose("sp_run2", "sp_run1", thf=212, shf=272, thb=126, shb=180)
pose("sp_hurt", T=-20, H=-26, uaf=170, faf=120, sw=60, grip=0, uab=225, fab=245,
     thf=158, shf=178, thb=214, shb=198)
# sword extras
pose("sw_chiburi", T=10, H=8, uaf=150, faf=165, uab=200, fab=185, sw=200, grip=0,
     thf=150, shf=182, thb=212, shb=196)
pose("duck_cut", "iai_cut", T=58, H=48, dy=-10)


def build():
    A = Track(facing=1)    # SWORD, starts left
    B = Track(facing=-1)   # SPEAR, starts right
    ev = []

    def E(t, kind, **kw):
        ev.append((t, kind, kw))

    def stop(t, d):
        E(t, "hitstop", dur=d)

    # ======================================================= intro (0 - 3.0)
    A.key(0.0, "swalk1", -470)
    t, x = 0.0, -470
    for i in range(4):
        t += 0.30
        x += 40
        A.key(t, "swalk2" if i % 2 == 0 else "swalk1", x)
        E(t, "step", who="A", v=0.5)
    A.key(1.35, "stand_sheathed", -320)
    B.key(0.0, "sp_rest", 330)
    B.key(0.45, "sp_twirl", 330, "back")
    # one-handed twirl: three spins over the head, accelerating
    B.key(1.25, "sp_twirl", 325, "in", sw=-1080 + 0, T=6)
    E(0.5, "twirl", who="B", dur=0.75)
    B.key(1.45, "sp_plant", 320, "snap", sw=-1080 - 8)
    E(1.45, "stomp", x=280, v=1.0)
    E(1.45, "plant")
    B.key(1.9, "sp_plant", 320, sw=-1088, dy=-1)
    B.key(2.25, "sp_guard", 250, "back", sw=-1080 + 84)
    E(2.25, "step", who="B", v=0.7)
    # SWORD draws
    A.key(1.60, "iai", -310)
    A.key(1.95, "iai_deep", -312)
    A.key(2.10, "iai_cut", -300, "snap", sheath=0, T=20, H=12)
    E(2.07, "draw")
    A.key(2.40, "guard", -280, "out")
    E(0.05, "drum", v=1.0)
    E(1.45, "drum", v=0.8)
    E(2.45, "banner", text="FIGHT!")
    E(2.45, "fight")
    E(2.45, "bed", stop_at=11.6, gain=0.32)

    # spear angle is now 84 - 1080 internally: keep it continuous
    S0 = -1080

    def BK(t, name, x, e="io", **kw):
        from rig import P
        sw = kw.pop("sw", P[name]["sw"])
        B.key(t, name, x, e, sw=sw + S0, **kw)

    # ======================================================= round 1: reach
    # (2.6 - 6.4) three pokes, a low sweep, a butt strike
    ax, bx = -230, 150
    A.key(2.75, "guard", ax)
    A.key(2.95, "walk1", ax + 30)
    A.key(3.10, "guard", ax + 55)
    ax += 55            # -175
    E(2.95, "step", who="A", v=0.6)
    BK(2.75, "sp_guard", bx + 20)
    BK(2.95, "sp_guard_lo", bx)
    # poke 1 (parried)
    BK(3.16, "sp_wind", bx + 18, "back")
    BK(3.26, "sp_thrust", bx - 70, "snap")
    E(3.24, "thrust", v=0.9)
    A.key(3.20, "guard", ax)
    A.key(3.26, "parry", ax - 6, "snap")
    E(3.27, "clash", v=0.8)
    stop(3.27, 0.05)
    BK(3.42, "sp_guard", bx - 10, "out")
    A.key(3.45, "guard", ax - 10)
    # poke 2 (high, blocked)
    BK(3.55, "sp_wind", bx + 5, "back")
    BK(3.64, "sp_thrust_hi", bx - 75, "snap")
    E(3.62, "thrust", v=0.9)
    A.key(3.60, "block_high", ax - 10, "snap")
    E(3.65, "clash", v=0.8)
    stop(3.65, 0.05)
    BK(3.80, "sp_guard", bx - 15, "out")
    A.key(3.82, "guard", ax - 15)
    # poke 3: feint high, go low. SWORD bites on the feint and gets stabbed in the leg
    BK(3.90, "sp_wind", bx, "back", sw=80)
    BK(3.97, "sp_wind", bx - 5, "io", sw=78, T=-4)       # the feint twitch
    A.key(3.98, "block_high", ax - 15, "snap")
    BK(4.07, "sp_thrust_lo", bx - 82, "snap")
    E(4.05, "thrust", v=1.0)
    E(4.08, "hit", by="B", on="A", v=0.9, dmg=8)
    stop(4.08, 0.07)
    A.key(4.09, "stagger", ax - 22, "snap", grip=1, sw=60)
    A.key(4.30, "guard_low", ax - 40, "out")
    BK(4.28, "sp_guard", bx - 10, "out")
    # SWORD rushes in; SPEAR sweeps low, SWORD jumps it
    A.key(4.42, "crouch", ax - 40)
    A.key(4.55, "run1_g", ax + 40, "lin")
    E(4.50, "zip", v=0.7)
    BK(4.40, "sp_sweep_wind", bx, "back")
    BK(4.62, "sp_sweep", bx - 20, "snap")
    E(4.62, "gust", x=bx - 140, v=1.0)
    A.key(4.60, "crouch", ax + 60, "out")
    A.key(4.72, "jump_tuck", ax + 120, "out", air=95)
    A.key(4.86, "high_wind", ax + 165, "lin", air=40)
    A.key(4.96, "high_cut", ax + 175, "snap")      # lands with an overhead cut
    E(4.96, "ground", x=ax + 175, v=0.6)
    BK(4.78, "sp_guard", bx + 10, "out")
    BK(4.90, "sp_block", bx + 10, "snap")
    E(4.96, "clash", v=1.0, big=True)
    stop(4.96, 0.11)
    A.key(5.08, "high_cut", ax + 170, dy=-3)
    # butt strike to the chest: SWORD flies back
    BK(5.06, "sp_butt_wind", bx + 18, "back")
    BK(5.18, "sp_butt", bx - 35, "snap")
    E(5.19, "hit", by="B", on="A", v=1.0, big=True, dmg=12, part="hilt0")
    stop(5.19, 0.12)
    A.key(5.20, "recoil", ax + 165, "lin", air=10)
    A.key(5.45, "recoil", ax - 10, "out", air=26)
    A.key(5.68, "stagger", ax - 110, "out")
    E(5.68, "skid", x=ax - 110, v=1.2)
    A.key(5.95, "guard_low", ax - 120)
    ax -= 120    # -295
    # SPEAR shows off
    BK(5.45, "sp_guard", bx - 20)
    B.key(5.75, "sp_twirl", bx - 10, "back", sw=-1080 - 96)
    B.key(6.30, "sp_twirl", bx - 5, "in", sw=-1080 - 96 - 720)
    E(5.78, "twirl", who="B", dur=0.52)
    S0 = -1080 - 720 - 180
    BK(6.50, "sp_guard", bx, "snap")
    E(6.50, "stomp", x=bx, v=0.7)

    # ======================================================= round 2: speed
    # (6.6 - 8.6) deflect the thrust, get inside, three cuts
    A.key(6.55, "guard_low", ax, T=24)
    A.key(6.70, "crouch", ax)
    A.key(6.80, "dash", ax + 160, "lin")
    E(6.71, "zip", v=1.0)
    E(6.71, "dust", x=ax, v=0.8)
    BK(6.68, "sp_wind", bx + 10, "back")
    BK(6.82, "sp_thrust", bx - 60, "snap")
    E(6.80, "thrust", v=1.0)
    A.key(6.86, "rise_cut", ax + 205, "snap")        # knocks the spear up
    E(6.86, "clash", v=1.0, big=True)
    stop(6.86, 0.10)
    BK(6.98, "sp_knocked", bx - 35, "out")
    ax2 = bx - 105
    A.key(6.96, "side_wind", ax2 - 10, "out")
    A.key(7.04, "side_cut", ax2 + 5, "snap")
    E(7.04, "hit", by="A", on="B", v=0.9, dmg=10)
    stop(7.04, 0.06)
    BK(7.10, "sp_knocked", bx - 25, "out", T=-26)
    A.key(7.14, "rise_wind", ax2 + 5, "out")
    A.key(7.22, "rise_cut", ax2 + 15, "snap")
    E(7.22, "hit", by="A", on="B", v=0.9, dmg=8)
    stop(7.22, 0.06)
    BK(7.28, "sp_hurt", bx - 15, "out")
    A.key(7.34, "high_wind", ax2 + 10, "back")
    A.key(7.46, "high_cut", ax2 + 35, "snap")
    E(7.46, "hit", by="A", on="B", v=1.0, big=True, dmg=12)
    stop(7.46, 0.13)
    BK(7.47, "sp_hurt", bx - 10, "lin")
    BK(7.72, "sp_hurt", bx + 110, "out", air=18)
    BK(7.98, "sp_guard_lo", bx + 160, "out")
    E(7.98, "skid", x=bx + 160, v=1.0)
    bx += 160    # 310
    A.key(7.75, "high_cut", ax2 + 35, dy=-2)
    A.key(8.10, "guard", ax2 - 20)
    ax = ax2 - 20    # 25

    # ======================================================= round 3: escalation
    # (8.4 - 11.4) overhead slam, the long thrust, blade grinds up the shaft
    BK(8.40, "sp_guard_lo", bx - 30)
    BK(8.62, "sp_slam_wind", bx - 60, "back")
    BK(8.74, "sp_slam_wind", bx - 64, "lin", T=-20)     # a held beat at the top
    BK(8.86, "sp_slam", bx - 110, "snap")
    E(8.87, "slam", by="B", v=1.0)
    stop(8.87, 0.12)
    A.key(8.55, "guard", ax)
    A.key(8.70, "crouch", ax)
    A.key(8.84, "jump_tuck", ax - 70, "out", air=110, rot=-200, T=20)
    A.key(9.02, "jump_tuck", ax - 150, "in", air=5, rot=-360, T=20)
    A.key(9.08, "guard_low", ax - 160, "snap", rot=0)
    E(9.06, "skid", x=ax - 160, v=0.8)
    ax -= 160    # -135
    bx -= 110    # 200
    BK(9.10, "sp_slam", bx, dy=-3)
    # the long thrust
    BK(9.22, "sp_wind", bx + 15, "back")
    BK(9.36, "sp_thrust", bx - 90, "snap")
    E(9.34, "thrust", v=1.1)
    A.key(9.30, "guard_low", ax)
    A.key(9.37, "parry", ax - 4, "snap")
    E(9.37, "clash", v=1.0)
    stop(9.37, 0.05)
    # blade rides up the shaft toward his hands (slow motion)
    bxs = bx - 90
    A.key(9.42, "block_mid", ax + 10, "out", sw=62)
    A.key(9.85, "block_mid", bxs - 70, "lin", sw=70, T=8)
    E(9.40, "scrape", dur=0.45)
    E(9.40, "slowmo", a0=9.40, a1=9.86, rate=0.35)
    BK(9.85, "sp_thrust", bxs + 10, "lin", T=24)
    A.key(9.94, "side_cut", bxs - 50, "snap")
    E(9.94, "hit", by="A", on="B", v=1.0, dmg=10)
    stop(9.94, 0.08)
    BK(9.98, "sp_hurt", bxs + 30, "out")
    # ...but SPEAR spins the butt into his face
    BK(10.08, "sp_butt_wind", bxs + 40, "back")
    BK(10.20, "sp_butt", bxs - 5, "snap")
    E(10.21, "hit", by="B", on="A", v=1.1, big=True, dmg=14, part="hilt0")
    stop(10.21, 0.14)
    A.key(10.05, "side_cut", bxs - 52)
    A.key(10.22, "tumble", bxs - 70, "snap", air=30, rot=-30)
    A.key(10.52, "tumble", bxs - 260, "lin", air=90, rot=-330)
    A.key(10.74, "fallen", bxs - 350, "in", rot=-360)
    E(10.74, "thud", v=1.0)
    E(10.74, "skid", x=bxs - 350, v=1.2)
    A.key(11.00, "fallen", bxs - 380, "out", rot=-360)
    A.key(11.40, "kneel", bxs - 380, rot=-360)
    A.key(11.75, "guard_low", bxs - 380, rot=-360)
    ax = bxs - 380   # about -270
    BK(10.40, "sp_butt", bxs - 8)
    BK(10.70, "sp_guard", bxs + 20)

    # ======================================================= climax
    # SWORD sheathes. Heartbeats. SPEAR charges, SWORD ducks the thrust and draws.
    bx = bxs + 20    # 130
    A.key(12.00, "sheathing", ax, rot=-360)
    A.key(12.25, "iai", ax - 4, "snap", sheath=1, rot=-360)
    E(12.25, "sheathe")
    A.key(12.70, "iai_deep", ax - 6, rot=-360)
    E(12.05, "heart", v=0.9)
    E(12.65, "heart", v=1.0)
    BK(11.80, "sp_guard_lo", bx + 30)
    BK(12.50, "sp_guard_lo", bx + 30, dy=-3)
    # charge
    BK(12.80, "sp_guard_lo", bx + 30, T=26)
    t, x, i = 12.80, bx + 30, 0
    while x > ax + 230:
        t += 0.12
        x -= 58
        BK(t, "sp_run2" if i % 2 == 0 else "sp_run1", x, "lin")
        E(t, "step", who="B", v=0.9)
        i += 1
    t_th = t + 0.10
    BK(t_th - 0.04, "sp_wind", x - 10, "lin")
    BK(t_th + 0.06, "sp_thrust_hi", x - 70, "snap")
    E(t_th + 0.02, "thrust", v=1.2)
    # SWORD ducks under the tip and draws through him
    A.key(t_th - 0.12, "iai_deep", ax - 6, rot=-360)
    A.key(t_th - 0.02, "iai_deep", ax - 2, "snap", rot=-360, T=64, H=52, dy=-30)
    t_cut = t_th + 0.10
    A.key(t_cut - 0.02, "iai_deep", ax, rot=-360, T=64, H=52, dy=-30)
    xe = x + 170
    A.key(t_cut + 0.05, "iai_cut", xe, "snap", sheath=0, rot=-360)
    E(t_cut, "iai", x0=ax, x1=xe)
    E(t_cut, "slowmo", a0=t_th - 0.30, a1=t_cut - 0.01, rate=0.2)
    stop(t_cut + 0.05, 0.05)
    BK(t_cut + 0.10, "sp_thrust_hi", x - 74)
    # silence, then everything falls apart
    t_brk = t_cut + 1.15
    A.key(t_brk, "iai_hold", xe, rot=-360)
    BK(t_brk, "sp_thrust_hi", x - 76, dy=-2)
    E(t_brk, "break", who="B")
    E(t_brk, "decap", who="B", by="A")
    E(t_brk + 0.01, "dmg", who="B", by="A", amt=100, big=True)
    E(t_brk + 0.01, "kill")
    B.key(t_brk + 0.01, "sp_hurt", x - 70, "snap", broken=1, headless=1, sw=60)
    B.key(t_brk + 0.45, "kneel", x - 64, "in", broken=1, headless=1, sw=150)
    E(t_brk + 0.45, "thud", v=0.7)
    B.key(t_brk + 1.05, "fallen", x - 40, "in", broken=1, headless=1, sw=100)
    E(t_brk + 1.05, "thud", v=1.0)
    E(t_brk + 1.05, "dust", x=x - 80, v=1.0)
    # chiburi (flick the blood off) and sheathe
    A.key(t_brk + 0.9, "iai_hold", xe + 2, rot=-360)
    A.key(t_brk + 1.15, "sw_chiburi", xe + 4, "snap", rot=-360)
    E(t_brk + 1.15, "swoosh", v=0.8)
    A.key(t_brk + 1.55, "sheathing", xe + 4, rot=-360)
    A.key(t_brk + 1.85, "stand_sheathed", xe + 6, "snap", rot=-360)
    E(t_brk + 1.85, "sheathe", final=True)
    E(t_brk + 0.6, "winner", name="SWORD WINS", color="#e0303a")
    end = t_brk + 6.9
    A.key(end, "stand_sheathed", xe + 6, rot=-360)
    B.key(end, "fallen", x - 40, broken=1, headless=1, sw=100)
    return dict(fighters=[("B", B, SPEAR), ("A", A, SWORD)], events=ev, end=end,
                title=(("SWORD", "#e0303a"), ("SPEAR", SPEAR["body"])),
                hp=[("A", "SWORD", "#e0303a"), ("B", "SPEAR", SPEAR["body"])],
                springy=True)
