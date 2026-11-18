"""Fight 07: "SCYTHE vs KATANA".

REAPER (violet, deep hood with glowing eyes, tattered cloak strips, a long
scythe) is patient and has reach. SAMURAI (black, red headband, katana) is
fast. The samurai keeps getting inside the reach and draws blood twice, so he
goes for his finishing quick-draw. The reaper plants the scythe and vaults
clean over the draw, lands behind him, and reaps the head from behind on the
song's drop.

First fight on the fluid motion layer (fluid=True): hips travel on springs
(arcs, overshoot and settle), feet plant and take real steps, the upper body
squashes and stretches, and fast limbs/weapons get smear frames. Keys still
use the 4-beat recipe: anticipation ("back"), strike ("snap"), follow-through,
recovery.
"""
from rig import Track, pose
import choreo_knight  # noqa: F401  (shared poses: sw_chiburi etc.)

SAMURAI = dict(choreo_knight.SAMURAI)
REAPER = dict(name="REAPER", body="#3d2466", back="#7a5aa8", hood="#24143d",
              band="#24143d", eyes="#d7b8ff", sword="scythe", blade=70, butt=84,
              grip_off=-36, wood="#2b1d33", wrap="#9b7bd0", steel="#e9ecf2",
              edge="#b48cff", ghost="#7a5aa8", trail="#ece0ff", limb=8.5,
              size=1.06, blade_len=66, blade_ang=112, springs={"sw": (56, 0.6)})
RED = "#e0303a"
VIOLET = "#7a4fc4"

# ---------------------------------------------------------------- reaper poses
pose("r_idle", T=4, H=2, uaf=150, faf=40, uab=170, fab=120, sw=8, grip=1,
     thf=160, shf=182, thb=200, shb=188)
pose("r_guard", T=12, H=6, uaf=140, faf=70, sw=48, grip=1,
     thf=142, shf=182, thb=218, shb=200)
pose("r_walk1", "r_guard", thf=160, shf=186, thb=200, shb=214)
pose("r_walk2", "r_guard", thf=198, shf=188, thb=162, shb=176)
pose("r_drag1", T=10, H=8, uaf=200, faf=205, uab=190, fab=180, sw=-118, grip=0,
     thf=160, shf=186, thb=200, shb=214)
pose("r_drag2", "r_drag1", thf=198, shf=188, thb=162, shb=176)
pose("r_low_wind", T=-14, H=-4, uaf=235, faf=250, sw=-105, grip=1,
     thf=152, shf=182, thb=214, shb=198, sq=-0.1)
pose("r_low_sweep", T=34, H=20, uaf=105, faf=110, sw=118, grip=1,
     thf=106, shf=170, thb=246, shb=258, sq=0.08)
pose("r_high_wind", T=-14, H=-10, uaf=12, faf=-15, sw=-40, grip=1,
     thf=148, shf=182, thb=212, shb=196, sq=0.06)
pose("r_reap", T=40, H=30, uaf=125, faf=140, sw=150, grip=1,
     thf=108, shf=176, thb=244, shb=246, sq=-0.06)
pose("r_side_wind", T=-12, H=0, uaf=230, faf=-20, sw=-80, grip=1,
     thf=150, shf=182, thb=212, shb=196, sq=-0.06)
pose("r_side", T=26, H=14, uaf=95, faf=88, sw=92, grip=1,
     thf=122, shf=178, thb=236, shb=220, sq=0.06)
pose("r_block", T=-6, H=-4, uaf=118, faf=25, sw=12, grip=1,
     thf=150, shf=182, thb=214, shb=198)
pose("r_butt", T=26, H=14, uaf=100, faf=96, sw=-88, grip=1,
     thf=114, shf=172, thb=242, shb=256)
pose("r_twirl", T=2, H=-4, uaf=20, faf=5, uab=200, fab=180, sw=0, grip=0,
     thf=150, shf=182, thb=210, shb=196)
pose("r_plant", T=-2, H=-6, uaf=150, faf=150, sw=0, grip=0, uab=200, fab=185,
     thf=158, shf=182, thb=204, shb=190)
pose("r_hurt", T=-22, H=-24, uaf=170, faf=110, sw=40, grip=1, uab=220, fab=240,
     thf=158, shf=178, thb=214, shb=198, sq=-0.08)
pose("r_crouch", T=30, H=18, uaf=150, faf=80, sw=60, grip=1,
     thf=108, shf=205, thb=218, shb=262, sq=-0.14)
pose("r_vault", T=0, H=0, uaf=175, faf=175, uab=175, fab=175, sw=180, grip=1,
     thf=150, shf=210, thb=160, shb=230)
pose("r_reach", T=8, H=2, uaf=75, faf=55, sw=58, grip=1,
     thf=145, shf=182, thb=214, shb=198, sq=0.08)
pose("r_pull", T=-18, H=-10, uaf=150, faf=60, sw=96, grip=1,
     thf=165, shf=182, thb=226, shb=206, sq=-0.12)
pose("r_victory", T=-4, H=-8, uaf=165, faf=150, sw=2, grip=0, uab=205, fab=190,
     thf=162, shf=182, thb=200, shb=188)

# samurai extras
pose("s_slide", T=60, H=46, uaf=95, faf=88, uab=230, fab=250, sw=88, grip=0,
     thf=88, shf=95, thb=240, shb=265, sq=0.1)


T0, D = 11.28, 2.0     # round 3 is inserted here; everything after slides D later


def _shift(A, B, ev, t0, d):
    for tr in (A, B):
        tr.keys = [(t + d if t >= t0 else t, p, x, e) for t, p, x, e in tr.keys]
        tr.facing_keys = [(t + d if t >= t0 else t, f) for t, f in tr.facing_keys]
    for j, (t, k, kw) in enumerate(ev):
        for q in ("a0", "a1", "duck_at", "stop_at"):
            if q in kw and kw[q] >= t0:
                kw[q] += d
        ev[j] = (t + d if t >= t0 else t, k, kw)


def _round3(A, B, E, stop, rots, T0):
    """Inserted exchange: buzzsaw spin, a reap that bites the ground, the
    samurai's chest cut, and the reaper ripping the blade free."""
    ra, rb = rots
    T = lambda u: T0 + u

    def AK(t, name, x, e="io", **kw):
        kw["rot"] = ra + kw.get("rot", 0)
        A.key(T(t), name, x, e, **kw)

    def BK(t, name, x, e="io", **kw):
        kw["rot"] = rb + kw.get("rot", 0)
        B.key(T(t), name, x, e, **kw)
    ax, bx = 380, 570
    # buzzsaw: the reaper walks in spinning the scythe in front of him
    BK(0.05, "r_guard", bx)
    BK(0.20, "r_twirl", bx - 10, "back", sw=60, uaf=95, faf=90)
    BK(0.75, "r_twirl", bx - 90, "lin", sw=60 + 1080, uaf=95, faf=90)
    E(T(0.20), "twirl", dur=0.55, scythe=True)
    for i, u in enumerate((0.35, 0.55)):
        E(T(u), "step", who="B", v=0.6)
    AK(0.10, "guard", ax)
    AK(0.40, "guard", ax - 25, "out")
    AK(0.62, "guard_low", ax - 45)
    AK(0.78, "parry", ax - 50, "snap")
    E(T(0.78), "clash", v=1.0, big=True)
    stop(T(0.78), 0.10)
    BK(0.80, "r_side", bx - 96, "snap", sw=150)
    AK(0.95, "guard", ax - 60, "out")
    bx -= 96          # 474
    # big overhead reap: samurai steps back, the blade bites into the ground
    BK(1.00, "r_high_wind", bx + 6, "back")
    BK(1.14, "r_high_wind", bx + 4, "lin", T=-22)
    BK(1.26, "r_reap", bx - 50, "snap", sw=162)
    AK(1.10, "guard_low", ax - 70)
    AK(1.24, "stagger", ax - 100, "snap")
    E(T(1.26), "ground", x=bx - 175, v=1.0)
    E(T(1.26), "stomp", x=bx - 175, v=0.8)
    stop(T(1.26), 0.07)
    BK(1.40, "r_reap", bx - 52, sw=164, T=46)       # stuck
    # samurai darts in and cuts across the chest
    AK(1.34, "crouch", ax - 96, sq=-0.15)
    AK(1.44, "side_wind", bx - 120, "out")
    E(T(1.36), "zip", v=0.9)
    AK(1.52, "side_cut", bx - 104, "snap")
    E(T(1.52), "hit", by="A", on="B", v=1.1, big=True, dmg=14)
    stop(T(1.52), 0.12)
    BK(1.53, "r_hurt", bx - 40, "snap", sw=150)
    # the reaper rips the blade out of the ground in a rising cut
    BK(1.70, "r_low_wind", bx - 30, "back", sw=-140, T=20)
    BK(1.82, "r_high_wind", bx - 10, "snap", sw=-10)
    AK(1.62, "side_cut", bx - 108)
    AK(1.76, "block_high", bx - 120, "snap")
    E(T(1.82), "clash", v=1.1, big=True)
    stop(T(1.82), 0.10)
    AK(1.84, "recoil", bx - 130, "snap")
    AK(1.98, "stagger", ax - 10, "out")
    E(T(1.98), "skid", x=ax - 10, v=1.0)
    # both reset to range: the reaper backs off, the samurai straightens
    BK(1.96, "r_guard", bx + 40, "out")
    E(T(1.96), "step", who="B", v=0.6)


def build(drawn=True):
    """drawn=False rebuilds the original v1 keys (render.py --classic)."""
    A = Track(facing=1)    # SAMURAI, starts left
    B = Track(facing=-1)   # REAPER, starts right
    ev = []
    RA, RB = [0], [0]      # accumulated flip rotations

    def E(t, kind, **kw):
        ev.append((t, kind, kw))

    def stop(t, d):
        E(t, "hitstop", dur=d)

    def AK(t, name, x, e="io", **kw):
        kw["rot"] = RA[0] + kw.get("rot", 0)
        A.key(t, name, x, e, **kw)

    def BK(t, name, x, e="io", **kw):
        kw["rot"] = RB[0] + kw.get("rot", 0)
        B.key(t, name, x, e, **kw)

    # ======================================================= intro (0 - 2.6)
    # reaper drifts in dragging the scythe; samurai walks in sheathed
    BK(0.0, "r_drag1", 470)
    t, x = 0.0, 470
    for i in range(3):
        t += 0.42
        x -= 38
        BK(t, "r_drag2" if i % 2 == 0 else "r_drag1", x)
        E(t, "step", who="B", v=0.6)
    AK(0.0, "swalk1", -470)
    t, x = 0.0, -470
    for i in range(4):
        t += 0.30
        x += 38
        AK(t, "swalk2" if i % 2 == 0 else "swalk1", x)
        E(t, "step", who="A", v=0.5)
    AK(1.35, "stand_sheathed", -318)
    # twirl overhead, then the butt slams down
    bx = 340
    BK(1.40, "r_twirl", bx, "back", sw=-90)
    BK(1.95, "r_twirl", bx, "lin", sw=630)
    E(1.40, "twirl", dur=0.55, scythe=True)
    BK(2.10, "r_plant", bx - 4, "snap", sw=720 - 720)
    E(2.10, "plant")
    E(2.10, "stomp", x=bx - 4, v=0.6)
    BK(2.45, "r_guard", bx - 10, "out")
    # samurai draws
    AK(1.60, "iai", -310)
    AK(1.95, "iai_deep", -312)
    AK(2.10, "iai_cut", -300, "snap", sheath=0, T=20, H=12)
    E(2.07, "draw")
    AK(2.40, "guard", -280, "out")
    E(0.05, "drum", v=1.0)
    E(2.45, "banner", text="FIGHT!")
    E(2.45, "fight")
    # Dxrk "RAVE": its drop (16.07 s) lands on the kill
    E(2.45, "song", name="song_rave", drop=16.07, duck_at=13.0,
      pre=0.36, duck=0.14, post=0.95)

    # ======================================================= round 1 (2.6 - 6.2)
    ax, bx = -280, 330
    # samurai rushes in; the reaper answers with a low sweep, samurai flips over it
    AK(2.62, "crouch", ax, sq=-0.15)
    AK(2.80, "dash", bx - 190, "lin")
    E(2.64, "zip", v=1.0)
    E(2.64, "dust", x=ax, v=0.8)
    BK(2.66, "r_low_wind", bx + 6, "back")
    BK(2.90, "r_low_sweep", bx - 30, "snap")
    E(2.90, "gust", x=bx - 150, v=1.0)
    AK(2.84, "crouch", bx - 185, "out", sq=-0.12)
    AK(2.98, "jump_tuck", bx - 150, "out", air=85, rot=180, T=20)
    AK(3.12, "high_wind", bx - 115, "lin", air=70, rot=360)
    RA[0] += 360
    AK(3.22, "high_cut", bx - 100, "snap")
    E(3.22, "ground", x=bx - 100, v=0.5)
    # the reaper gets the snath up in time
    BK(3.08, "r_low_sweep", bx - 32)
    BK(3.18, "r_block", bx - 10, "snap")
    E(3.22, "clash", v=1.1, big=True)
    stop(3.22, 0.12)
    BK(3.26, "r_block", bx - 4, "snap", T=-12)
    # butt to the gut pushes him off
    BK(3.40, "r_side_wind", bx + 4, "back", sw=-110)
    BK(3.52, "r_butt", bx - 22, "snap")
    AK(3.40, "high_cut", bx - 104)
    E(3.52, "hit", by="B", on="A", v=1.0, dmg=8, part="hilt0")
    stop(3.52, 0.09)
    if drawn:
        # the butt drives him back off the snath instead of passing through him,
        # and the reaper pulls the staff back in (follow-through, then recover)
        AK(3.53, "recoil", bx - 150, "snap")
        AK(3.80, "stagger", bx - 230, "out")
        BK(3.57, "r_butt", bx - 24, "out", T=20, uaf=110, faf=104)
        BK(3.66, "r_guard", bx - 6, "io")
    else:
        AK(3.53, "recoil", bx - 110, "snap")
        AK(3.80, "stagger", bx - 230, "out")
    E(3.80, "skid", x=bx - 230, v=1.0)
    ax = bx - 230    # 100
    bx -= 40         # 290
    # overhead reap, samurai parries and slides out
    BK(3.75, "r_high_wind", bx, "back")
    BK(3.92, "r_high_wind", bx - 4, "lin", T=-20)
    BK(4.04, "r_reap", bx - 60, "snap")
    AK(3.95, "guard", ax + 20)
    AK(4.04, "parry", ax + 14, "snap")
    E(4.04, "clash", v=1.0)
    stop(4.04, 0.08)
    E(4.04, "ground", x=bx - 150, v=0.6)
    AK(4.20, "guard_low", ax - 10, "out")
    BK(4.30, "r_reap", bx - 62)
    BK(4.50, "r_guard", bx - 50, "out")
    bx -= 50         # 240
    # three-cut flurry: two into the snath, the third runs through him
    AK(4.46, "side_wind", ax + 30, "back")
    AK(4.55, "side_cut", bx - 115, "snap")
    BK(4.52, "r_block", bx + 2, "snap")
    E(4.55, "clash", v=0.9)
    stop(4.55, 0.05)
    AK(4.63, "rise_wind", bx - 112, "out")
    AK(4.71, "rise_cut", bx - 104, "snap")
    BK(4.70, "r_block", bx + 6, "snap", sw=-10, T=-10)
    E(4.71, "clash", v=0.9)
    stop(4.71, 0.05)
    AK(4.80, "crouch", bx - 110, "out", sq=-0.14)
    AK(4.92, "iai_cut", bx + 150, "snap", sheath=0)
    E(4.82, "zip", v=1.0)
    E(4.90, "hit", by="A", on="B", v=1.1, big=True, dmg=16)
    stop(4.92, 0.13)
    BK(4.93, "r_hurt", bx + 10, "snap")
    BK(5.20, "r_hurt", bx + 4, "out", T=-12, H=-14)
    AK(5.20, "iai_hold", bx + 165, "out")
    A.face(5.36, -1)
    AK(5.36, "guard", bx + 170, "snap")
    ax = bx + 170    # 410
    # reaper wheels round with a backhand sweep; samurai ducks it
    B.face(5.30, 1)
    BK(5.30, "r_side_wind", bx + 6, "snap")
    BK(5.46, "r_side", bx + 40, "snap")
    E(5.46, "gust", x=bx + 120, v=1.0)
    AK(5.40, "crouch", ax + 6, "snap", T=52, H=42, sw=20, sq=-0.16)
    AK(5.62, "guard_low", ax + 30, "out")
    # reaper backs off and twirls the scythe
    BK(5.62, "r_guard", bx + 20, "out")
    BK(5.80, "r_twirl", bx - 10, "back", sw=0)
    BK(6.30, "r_twirl", bx - 30, "lin", sw=720)
    E(5.80, "twirl", dur=0.5, scythe=True)
    BK(6.42, "r_guard", bx - 40, "snap", sw=48 + 720 - 720)
    bx -= 40         # 200
    AK(6.00, "guard", ax + 20)

    # ======================================================= round 2 (6.4 - 10.2)
    # reaper presses forward: diagonal, low reap, rising reap that connects
    BK(6.55, "r_walk1", bx + 30)
    E(6.55, "step", who="B", v=0.6)
    BK(6.70, "r_high_wind", bx + 55, "back")
    BK(6.84, "r_reap", bx + 110, "snap")
    AK(6.78, "block_high", ax + 15, "snap")
    E(6.84, "clash", v=1.0, big=True)
    stop(6.84, 0.10)
    AK(6.90, "block_high", ax + 26, "snap", T=-12)
    bx += 110        # 310
    BK(7.00, "r_low_wind", bx, "back")
    BK(7.14, "r_low_sweep", bx + 50, "snap")
    E(7.14, "gust", x=bx + 150, v=1.0)
    AK(7.02, "crouch", ax + 26, "snap", sq=-0.14)
    AK(7.12, "jump_tuck", ax + 70, "out", air=95, rot=-180)
    AK(7.30, "crouch", ax + 110, "in", rot=-360)
    RA[0] -= 360
    ax += 110        # 520
    bx += 50         # 360
    # the rising reap catches him on the landing
    BK(7.30, "r_low_sweep", bx + 4)
    BK(7.38, "r_low_wind", bx - 4, "back", sw=-150, T=10)
    BK(7.50, "r_high_wind", bx + 40, "snap", sw=-20)
    E(7.50, "hit", by="B", on="A", v=1.2, big=True, dmg=18, part="blade_end")
    stop(7.50, 0.14)
    AK(7.40, "guard", ax)
    AK(7.51, "tumble", ax + 10, "snap", air=40, rot=-30)
    AK(7.80, "tumble", ax + 160, "lin", air=120, rot=-330)
    AK(8.02, "fallen", ax + 230, "in", rot=-360)
    E(8.02, "thud", v=1.0)
    E(8.02, "skid", x=ax + 230, v=1.2)
    AK(8.22, "fallen", ax + 250, "out", rot=-360)
    RA[0] -= 360
    ax += 250        # 770 -> reset ranges below
    AK(8.60, "kneel", ax, rot=0)
    AK(8.90, "guard_low", ax)
    # reaper walks after him
    BK(7.80, "r_guard", bx + 50, "out")
    for i, tt in enumerate((8.10, 8.40, 8.70)):
        BK(tt, "r_walk2" if i % 2 == 0 else "r_walk1", bx + 90 + 45 * i)
        E(tt, "step", who="B", v=0.6)
    bx += 180        # 540
    BK(8.95, "r_guard", bx)
    # samurai slides under the reach and opens his leg, ends up behind him again
    AK(9.02, "crouch", ax, sq=-0.15)
    AK(9.16, "s_slide", bx + 30, "out", sheath=0)
    E(9.04, "zip", v=1.0)
    E(9.04, "dust", x=ax, v=1.0)
    BK(9.04, "r_low_wind", bx + 4, "back")
    BK(9.16, "r_low_sweep", bx - 40, "snap")
    E(9.16, "gust", x=bx - 120, v=0.8)
    E(9.17, "hit", by="A", on="B", v=1.0, big=True, dmg=12, part="tip")
    stop(9.17, 0.11)
    AK(9.34, "s_slide", bx - 120, "out")
    E(9.34, "skid", x=bx - 120, v=1.1)
    AK(9.52, "guard_low", bx - 150, "out")
    A.face(9.52, 1)
    AK(9.62, "guard", bx - 150, "snap")
    ax = bx - 150    # 390
    BK(9.18, "r_hurt", bx - 36, "snap", T=-8)
    BK(9.42, "r_hurt", bx - 30, "out")
    B.face(9.55, -1)
    BK(9.55, "r_guard", bx - 30, "snap")
    bx -= 30         # 510
    # blade lock: the scythe hooks the katana, grinding in slow motion
    BK(9.70, "r_side_wind", bx + 6, "back")
    BK(9.86, "r_side", bx + 14, "snap")
    AK(9.80, "block_mid", ax + 10, "snap")
    E(9.86, "clash", v=1.1, big=True)
    stop(9.86, 0.10)
    E(9.92, "scrape", dur=0.65)
    E(9.92, "slowmo", a0=9.92, a1=10.57, rate=0.45)
    AK(9.92, "block_mid", ax + 8)
    AK(10.57, "block_mid", ax - 6, "lin", T=-16, dy=-6)
    BK(9.92, "r_side", bx + 12)
    BK(10.57, "r_side", bx + 2, "lin", T=34, sw=104)
    # kick breaks it
    AK(10.64, "kick_wind", ax - 4, "back")
    AK(10.74, "kick", ax + 10, "snap")
    E(10.74, "hit", by="A", on="B", v=1.0, dmg=8, part="ftf")
    stop(10.74, 0.09)
    BK(10.75, "r_hurt", bx + 4, "snap")
    BK(11.05, "r_hurt", bx + 60, "out")
    E(11.05, "skid", x=bx + 60, v=1.0)
    BK(11.35, "r_guard", bx + 70, "out")
    bx += 70         # 580
    AK(10.95, "guard", ax - 10, "out")
    ax -= 10         # 380

    rot_snap = (RA[0], RB[0])

    # ======================================================= climax
    # samurai sheathes for the quick-draw; the reaper waits, scythe high
    AK(11.30, "sheathing", ax)
    AK(11.55, "iai", ax - 4, "snap", sheath=1)
    E(11.55, "sheathe")
    AK(12.10, "iai_deep", ax - 8, sq=-0.12)
    E(11.60, "heart", v=0.9)
    E(12.20, "heart", v=1.0)
    BK(11.70, "r_idle", bx)
    BK(12.30, "r_idle", bx + 2, T=-2)
    E(12.60, "heart", v=1.1)
    # the draw-dash
    t_go = 12.85
    AK(t_go - 0.08, "iai_deep", ax - 12, T=50, H=40, dy=-12, sq=-0.18)
    AK(t_go + 0.10, "dash", ax + 150, "lin", sheath=1, sq=0.14)
    E(t_go, "zip", v=1.2)
    E(t_go, "dust", x=ax, v=1.2)
    # reaper plants the butt and vaults over the cut
    BK(t_go - 0.02, "r_crouch", bx - 6, "snap")
    E(t_go + 0.02, "plant")
    t_c = t_go + 0.18                  # the katana sweeps under him
    BK(t_go + 0.08, "r_vault", bx - 14, "out", air=90, rot=70, sw=180 - 70)
    BK(t_c, "r_vault", ax + 225, "lin", air=165, rot=180, sw=0)
    AK(t_c - 0.02, "dash", ax + 230, sheath=1)
    xs = ax + 330                      # where the samurai's draw ends
    AK(t_c + 0.04, "iai_cut", xs, "snap", sheath=0)
    E(t_c + 0.02, "swoosh", v=1.0)
    E(t_c + 0.02, "gust", x=xs - 20, v=1.0)
    E(t_c, "slowmo", a0=t_go + 0.06, a1=t_c + 0.10, rate=0.18)
    xr = ax + 110                      # reaper lands behind him
    BK(t_c + 0.20, "r_vault", xr + 40, "lin", air=95, rot=290, sw=-110)
    BK(t_c + 0.32, "r_crouch", xr, "in", rot=360, sw=60)
    E(t_c + 0.32, "ground", x=xr, v=0.8)
    RB[0] += 360
    # samurai holds the finish, thinking it landed
    AK(t_c + 0.45, "iai_hold", xs + 6, "out")
    # the reaper turns and hooks the blade round his neck from behind
    xr2 = xs - 92
    B.face(t_c + 0.48, 1)
    BK(t_c + 0.48, "r_guard", xr + 6, "snap")
    t_k = t_c + 1.05
    BK(t_k - 0.30, "r_high_wind", xr + 4, "back")
    BK(t_k - 0.12, "r_reach", xr2, "snap")
    E(t_k - 0.30, "heart", v=1.2)
    A.face(t_k - 0.10, -1)
    AK(t_k - 0.16, "iai_hold", xs + 6, H=-10)
    AK(t_k - 0.06, "guard", xs + 4, "snap")
    BK(t_k, "r_pull", xr2 - 30, "snap")
    E(t_k - 0.01, "slowmo", a0=t_k - 0.12, a1=t_k - 0.01, rate=0.3)
    E(t_k, "decap", who="A", by="B")
    E(t_k + 0.01, "dmg", who="A", by="B", amt=100, big=True)
    E(t_k, "kill", song=True)
    stop(t_k, 0.16)
    AK(t_k + 0.01, "guard", xs + 4, "snap", headless=1)
    AK(t_k + 0.50, "kneel", xs + 2, "in", headless=1, grip=0, sw=150)
    E(t_k + 0.50, "thud", v=0.8)
    AK(t_k + 1.10, "fallen", xs - 20, "in", headless=1)
    E(t_k + 1.10, "thud", v=1.0)
    E(t_k + 1.10, "dust", x=xs - 40, v=1.0)
    # the reaper straightens, twirls once and plants the scythe
    BK(t_k + 0.45, "r_pull", xr2 - 34, "out")
    BK(t_k + 1.00, "r_twirl", xr2 - 34, "back", sw=-90)
    BK(t_k + 1.45, "r_twirl", xr2 - 34, "lin", sw=630)
    E(t_k + 1.00, "twirl", dur=0.45, scythe=True)
    BK(t_k + 1.60, "r_victory", xr2 - 34, "snap", sw=2)
    E(t_k + 1.60, "plant")
    E(t_k + 1.60, "stomp", x=xr2 - 34, v=0.6)
    E(t_k + 0.6, "winner", name="REAPER WINS", color=VIOLET)
    end = t_k + 4.4 + D
    _shift(A, B, ev, T0, D)
    _round3(A, B, E, stop, rot_snap, T0)
    AK(end, "fallen", xs - 20, headless=1)
    BK(end, "r_victory", xr2 - 34)
    return dict(fighters=[("B", B, REAPER), ("A", A, SAMURAI)], events=ev, end=end,
                title=(("SCYTHE", VIOLET), ("KATANA", RED)),
                hp=[("B", "REAPER", VIOLET), ("A", "SAMURAI", RED)],
                springy=True, fluid=True, drawn=drawn)
