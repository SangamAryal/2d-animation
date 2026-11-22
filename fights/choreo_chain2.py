"""Fight 08 v2: "CHAIN SICKLE vs TWIN SWORDS", the long cut (~44 s).

Sangam's second brief (2026-11-22): no health bars, 40-45 s, every action on
its own beat, and this time TWIN SWORDS wins.

  0-7 s    opening: range is set, fast dodges, first collision of weapons
  7-15 s   Chain Sickle takes over: disarms one sword, cuts Twin's shoulder,
           gets cocky, nearly finishes him on his knees
  15-23 s  comeback: Twin throws his last sword as a distraction, kicks,
           catches it, cuts, gets his first sword back off the ground, cuts again
  23-32 s  the twist: Twin offers his sword to the chain on purpose, lets go
           as Kusari heaves, rides that pull in and cuts the sickle out of his
           hand; both are hurt now
  32-40 s  last exchange: Kusari swings the loose sickle on its chain, his
           last great throw
  40-45 s  Twin slides under it and cuts through him: freeze-frame, the end

Same characters, rig and kit as choreo_chain (fight 08 v1).
"""
from rig import P, Track, pose
from choreo_chain import KUSARI, TWIN, ORANGE, RED  # noqa: F401  (also registers v1 poses)

# ---------------------------------------------------------------- new twin poses
L_READY = dict(thf=140, shf=180, thb=218, shb=200)
L_WIDE = dict(thf=128, shf=178, thb=232, shb=214)
pose("t_xblock", T=4, H=0, uaf=70, faf=28, sw=28, uab=78, fab=30, sw2=-28, **L_WIDE)
pose("t_block2_hi", T=-4, H=-4, uaf=150, faf=95, sw=70, uab=40, fab=8, sw2=95, **L_READY)
pose("t_clutch", T=14, H=10, uaf=186, faf=178, sw=175, uab=140, fab=18, sw2=-20,
     thf=150, shf=184, thb=212, shb=200)
pose("t_clutch_lo", "t_clutch", T=26, H=20, thf=122, shf=196, thb=228, shb=244)
pose("t_kneel", T=24, H=14, uaf=180, faf=170, sw=170, uab=120, fab=70, sw2=60,
     thf=95, shf=185, thb=150, shb=265)
pose("t_kneel_block", T=10, H=-6, uaf=185, faf=175, sw=170, uab=35, fab=-5, sw2=92,
     thf=95, shf=185, thb=150, shb=265)
pose("t_shove", T=30, H=18, uaf=190, faf=175, sw=170, uab=70, fab=55, sw2=40, **L_WIDE)
pose("t_slide", T=-26, H=-10, uaf=200, faf=185, sw=150, uab=228, fab=250, sw2=250,
     thf=96, shf=96, thb=200, shb=262, sq=-0.1)
pose("t_reach_dn", T=62, H=40, uaf=178, faf=178, sw=180, uab=230, fab=250, sw2=240,
     thf=100, shf=196, thb=220, shb=262)
pose("t_bait", T=-6, H=-12, uaf=18, faf=8, sw=6, uab=150, fab=95, sw2=95, **L_READY)
pose("t_bait_walk1", "t_bait", thf=160, shf=186, thb=200, shb=214)
pose("t_bait_walk2", "t_bait", thf=198, shf=188, thb=162, shb=176)
pose("t_release", T=8, H=-6, uaf=70, faf=80, sw=60, uab=200, fab=210, sw2=230, **L_WIDE)
pose("t_rush", T=48, H=34, uaf=230, faf=250, sw=250, uab=200, fab=225, sw2=245,
     thf=110, shf=160, thb=250, shb=268)
pose("t_hand_wind", T=-6, H=-4, uaf=200, faf=190, sw=180, uab=-20, fab=-60, sw2=-100, **L_WIDE)
pose("t_hand_cut", T=34, H=22, uaf=210, faf=215, sw=200, uab=110, fab=128, sw2=150,
     thf=106, shf=170, thb=248, shb=240)
pose("t_knee", T=-12, H=-6, uaf=150, faf=95, sw=60, uab=200, fab=170, sw2=200,
     thf=40, shf=150, thb=192, shb=184)
pose("t_pass", T=44, H=30, uaf=205, faf=230, sw=230, uab=95, fab=98, sw2=100,
     thf=104, shf=172, thb=250, shb=262)
pose("t_pass_hold", "t_pass", T=36, H=22, uab=118, fab=125, sw2=135)
pose("t_flick", T=8, H=4, uaf=200, faf=215, sw=220, uab=150, fab=170, sw2=210, **L_READY)
pose("t_stand_win", T=4, H=-4, uaf=190, faf=205, sw=215, uab=170, fab=190, sw2=200,
     thf=160, shf=182, thb=200, shb=188)
pose("t_breathe", T=20, H=12, uaf=150, faf=90, sw=55, uab=175, fab=120, sw2=110,
     thf=128, shf=190, thb=226, shb=226)
pose("t_kick_wind", T=-10, H=-4, uaf=140, faf=60, sw=50, uab=200, fab=170, sw2=200,
     thf=60, shf=200, thb=185, shb=182)
pose("t_kick", T=-30, H=-14, uaf=160, faf=90, sw=60, uab=210, fab=190, sw2=200,
     thf=88, shf=92, thb=190, shb=184)
pose("t_elbow", T=30, H=16, uaf=80, faf=-40, sw=60, uab=210, fab=200, sw2=220, **L_WIDE)
pose("t_catch_hi", T=-8, H=-14, uaf=170, faf=110, sw=60, uab=20, fab=-5, sw2=10, **L_READY)

# ---------------------------------------------------------------- new kusari poses
pose("k_chop_wind", T=-12, H=-10, uaf=8, faf=-25, sw=-70, uab=170, fab=140, reel=58,
     thf=145, shf=182, thb=214, shb=198)
pose("k_chop", T=34, H=22, uaf=118, faf=128, sw=140, uab=205, fab=220, reel=58,
     thf=108, shf=172, thb=246, shb=236)
pose("k_cut_wind", T=-4, H=-2, uaf=235, faf=-30, sw=-80, uab=150, fab=110, reel=58,
     thf=140, shf=182, thb=216, shb=198)
pose("k_cut", T=26, H=16, uaf=92, faf=92, sw=95, uab=205, fab=228, reel=58,
     thf=112, shf=172, thb=244, shb=232)
pose("k_taunt", T=-4, H=-12, uaf=160, faf=110, sw=60, uab=110, fab=60, reel=60,
     thf=160, shf=182, thb=202, shb=188)
pose("k_stroll1", "k_taunt", thf=160, shf=186, thb=200, shb=214)
pose("k_stroll2", "k_taunt", thf=198, shf=188, thb=162, shb=176)
pose("k_double", T=46, H=36, uaf=150, faf=60, sw=40, uab=160, fab=60, reel=58,
     thf=150, shf=186, thb=212, shb=204, sq=-0.06)
pose("k_head_back", T=-30, H=-40, uaf=190, faf=200, sw=160, uab=215, fab=230, reel=58,
     thf=152, shf=180, thb=222, shb=204)
pose("k_stagger", T=-16, H=-14, uaf=200, faf=215, sw=170, uab=220, fab=235, reel=58,
     thf=156, shf=180, thb=208, shb=196)
pose("k_whirl", T=6, H=0, uaf=150, faf=60, sw=30, uab=110, fab=80, reel=58,
     thf=136, shf=182, thb=222, shb=204)
pose("k_hurt_side", T=22, H=14, uaf=150, faf=20, sw=-10, uab=160, fab=110, reel=58,
     thf=132, shf=192, thb=222, shb=226)
pose("k_heave", T=-34, H=-20, uaf=150, faf=70, sw=40, uab=250, fab=262, reel=58,
     thf=118, shf=176, thb=238, shb=214, sq=-0.06)
pose("k_flail", T=-42, H=-30, uaf=40, faf=10, sw=-20, uab=280, fab=300, reel=58,
     thf=170, shf=176, thb=232, shb=208)
pose("k_hurt_hand", T=18, H=10, uaf=170, faf=50, sw=40, uab=150, fab=60, reel=40,
     thf=146, shf=184, thb=216, shb=202)
pose("k_whirl_hi", T=-8, H=-10, uaf=170, faf=50, sw=40, uab=-6, fab=4, reel=40,
     thf=140, shf=182, thb=222, shb=204)
pose("k_hurl", T=30, H=18, uaf=200, faf=60, sw=40, uab=84, fab=88, reel=40,
     thf=104, shf=170, thb=250, shb=246)
pose("k_cut_thru", T=-6, H=-22, uaf=190, faf=70, sw=40, uab=60, fab=70, reel=40,
     thf=146, shf=182, thb=216, shb=200, sq=-0.04)


def build(drawn=True):
    A = Track(facing=1)    # KUSARI, left
    B = Track(facing=-1)   # TWIN, right
    ev = []
    RA, RB = [0], [0]

    def E(t, kind, **kw):
        ev.append((t, kind, kw))

    def stop(t, d):
        E(t, "hitstop", dur=d)

    # state windows: pose keys that hold over a stretch of the story
    SA, SB = [], []     # (t0, t1, dict)

    def AK(t, name, x, e="io", **kw):
        kw["rot"] = RA[0] + kw.get("rot", 0)
        for a, b, d in SA:
            if a <= t < b:
                for k, v in d.items():
                    kw.setdefault(k, v)
        A.key(t, name, x, e, **kw)

    OB = []    # (t0, dsw, dsw2): whole turns added after a twirl, so nothing unwinds

    def BK(t, name, x, e="io", **kw):
        kw["rot"] = RB[0] + kw.get("rot", 0)
        base = P[name] if isinstance(name, str) else name
        for t0, d1, d2 in OB:
            if t >= t0:
                kw["sw"] = kw.get("sw", base["sw"]) + d1
                kw["sw2"] = kw.get("sw2", base["sw2"]) + d2
        for a, b, d in SB:
            if a <= t < b:
                for k, v in d.items():
                    kw.setdefault(k, v)
        B.key(t, name, x, e, **kw)

    # who holds what (times fixed up front so every key gets them)
    T_DISARM1 = 10.30     # chain rips Twin's front sword away
    T_THROW2 = 15.95      # Twin throws his last sword...
    T_CATCH2 = 16.80      # ...and catches it again
    T_PICK1 = 19.55       # Twin pulls his first sword out of the ground
    T_RELEASE = 25.30     # Twin lets the chain have his front sword
    T_SICKLE = 25.86      # Twin's cut takes the sickle out of Kusari's hand
    SB.append((T_DISARM1, T_PICK1, dict(nosw=1)))
    SB.append((T_THROW2 + 0.01, T_CATCH2, dict(nosw2=1)))
    SB.append((T_RELEASE, 99, dict(nosw=1)))
    SA.append((T_SICKLE, 99, dict(nosw=1)))

    # =========================================================== 0-2 intro
    ax, bx = -200, 430
    AK(0.0, "k_idle", ax)
    AK(0.9, "k_idle", ax, T=6, uab=150, fab=120)
    E(0.55, "chain", mode="spin", dur=1.25, r=34, turns=1.4, plane="side", c=(18, -6))
    E(0.55, "chainspin", dur=1.2, v=0.5)
    AK(1.55, "k_ready", ax + 4)
    BK(0.0, "t_walk1", bx)
    for i in range(5):
        tt = 0.28 * (i + 1)
        bx -= 40
        BK(tt, "t_walk2" if i % 2 == 0 else "t_walk1", bx, sw=55 + 360 * min(i, 2),
           sw2=100 - 360 * min(max(0, i - 2), 2))
        E(tt, "step", who="B", v=0.5)
    E(0.30, "twirl", dur=0.5)
    E(0.86, "twirl", dur=0.5)
    BK(1.62, "t_ready", bx - 6, sw=55 + 720, sw2=100 - 720)
    OB.append((1.62 + 1e-4, 720, -720))
    bx -= 6           # 224
    E(0.05, "drum", v=1.0)
    E(1.75, "banner", text="FIGHT!")
    E(1.75, "fight")
    # Mr.Kitty "After Dark": the drop hits on the twist (the sickle cut out of his hand)
    E(1.75, "song", name="song_after_dark", drop=30.85, drop_at=T_SICKLE, duck_at=24.4,
      pre=0.34, duck=0.12, post=0.95)

    # =========================================================== 2-3 measuring range
    E(1.80, "chain", mode="spin", dur=1.25, r=36, turns=1.6, plane="side", c=(16, -6))
    E(1.80, "chainspin", dur=1.2, v=0.45)
    AK(2.20, "k_walk1", ax + 14)
    E(2.20, "step", who="A", v=0.4)
    AK(2.55, "k_walk2", ax + 26)
    E(2.55, "step", who="A", v=0.4)
    ax += 26          # -174
    AK(2.85, "k_ready", ax)
    BK(2.10, "t_walk1", bx - 14)
    E(2.10, "step", who="B", v=0.4)
    BK(2.45, "t_walk2", bx - 26)
    E(2.45, "step", who="B", v=0.4)
    BK(2.80, "t_ready", bx - 30, T=16)
    bx -= 30          # 194

    # =========================================================== beat 1: weight at the head, he leans back
    t = 3.10
    AK(t - 0.12, "k_ready", ax - 4, "back", T=-10, uab=210, fab=200)
    AK(t + 0.08, "k_sling", ax + 20, "snap")
    E(t - 0.02, "chain", mode="path", dur=0.26, ease="out",
      pts=[(ax + 130, 150), ("Jf", "B", "head", 30, 2), (bx + 60, 120)])
    E(t - 0.02, "chainthrow", v=0.8)
    BK(t + 0.04, "t_ready", bx + 4, "back")
    BK(t + 0.15, "t_lean_back", bx + 36, "snap")
    E(t + 0.30, "chain", mode="free")
    BK(t + 0.45, "t_ready", bx + 50, "out")
    AK(t + 0.40, "k_ready", ax + 14, "io", uab=210, fab=200)

    # =========================================================== beat 2: low swing, he hops it
    t = 3.80
    AK(t, "k_sling", ax + 30, "snap", uab=110, fab=120, T=30)
    E(t - 0.10, "chain", mode="path", dur=0.27, ease="out",
      pts=[(ax + 80, 46), ("Jf", "B", "knf", 26, -6), (bx + 160, 36)], lead=0.1)
    E(t - 0.10, "chainthrow", v=0.7)
    BK(t - 0.02, "t_ready", bx + 54, "back", sq=-0.12)
    BK(t + 0.12, "t_tuck", bx + 86, "out", air=50)
    BK(t + 0.30, "t_ready", bx + 100, "in", sq=-0.1)
    E(t + 0.30, "ground", x=bx + 100, v=0.4)
    E(t + 0.22, "chain", mode="free")
    bx += 100        # 294
    ax += 30         # -144
    AK(t + 0.35, "k_ready", ax, "out")
    E(t + 0.40, "chain", mode="spin", dur=0.6, r=34, turns=1.2, plane="side", c=(16, -6))

    # =========================================================== beat 3: he dashes in, front slash, Kusari sways
    t = 4.55
    BK(t - 0.14, "t_ready", bx + 8, "back", sq=-0.16, T=24)
    BK(t + 0.14, "t_dash", ax + 215, "lin")
    E(t, "zip", v=1.0)
    E(t, "dust", x=bx, v=0.9)
    BK(t + 0.22, "t_h1_wind", ax + 192, "out")
    BK(t + 0.31, "t_h1", ax + 160, "snap")
    AK(t + 0.18, "k_ready", ax - 6, "out")
    AK(t + 0.29, "k_sway", ax - 26, "snap")
    # =========================================================== beat 4: back-hand slash, the first collision
    s = t + 0.55
    BK(s - 0.12, "t_h2_wind", ax + 150, "out")
    BK(s, "t_h2", ax + 128, "snap")
    AK(s - 0.12, "k_ready", ax - 20, "out")
    AK(s - 0.02, "k_block_lo", ax - 24, "snap", sw=150)
    E(s, "clash", v=1.2, big=True, blade=2)
    stop(s, 0.10)
    E(s - 0.04, "slowmo", a0=s - 0.04, a1=s + 0.14, rate=0.4)
    # they shove off each other
    AK(s + 0.14, "k_block_lo", ax - 34, "snap", T=4)
    AK(s + 0.40, "k_hop", ax - 80, "out", air=16)
    AK(s + 0.58, "k_ready", ax - 96, "in", sq=-0.1)
    E(s + 0.58, "ground", x=ax - 96, v=0.4)
    ax -= 96         # -240
    BK(s + 0.16, "t_h2", ax + 280, "snap", T=10)
    BK(s + 0.50, "t_ready", ax + 320, "out")
    E(s + 0.50, "skid", x=ax + 320, v=0.6)
    bx = ax + 320    # 60

    # =========================================================== 6-7 overhead spin (calm, in control)
    t = 6.00
    AK(t + 0.05, "k_spin_over", ax + 4, "out")
    E(t + 0.02, "chain", mode="spin", dur=1.0, r=74, turns=2.8, plane="over", c=(-4, 14))
    E(t + 0.02, "chainspin", dur=1.0, v=1.0)
    AK(t + 0.55, "k_spin_over", ax + 10, T=-8)
    BK(t + 0.30, "t_walk1", bx - 12)
    E(t + 0.30, "step", who="B", v=0.4)
    BK(t + 0.62, "t_ready", bx - 22, T=16)
    bx -= 22         # 38

    # =========================================================== beat 5: weight smashes into his crossed swords
    t = 7.10
    AK(t - 0.06, "k_spin_over", ax + 12, "back", T=-14)
    AK(t + 0.10, "k_sling", ax + 36, "snap")
    E(t, "chain", mode="path", dur=0.20, ease="out",
      pts=[(ax + 150, 140), ("M", "B", "guard", "tip", 0.42)])
    E(t, "chainthrow", v=0.9)
    BK(t + 0.02, "t_ready", bx + 2, "back")
    BK(t + 0.14, "t_xblock", bx + 4, "snap")
    E(t + 0.20, "clash", v=1.1, nosolve=True, at_weight=True)
    stop(t + 0.20, 0.08)
    E(t + 0.20, "chain", mode="free")
    BK(t + 0.30, "t_xblock", bx + 44, "snap", T=-12)
    E(t + 0.30, "skid", x=bx + 44, v=0.8)
    BK(t + 0.62, "t_ready", bx + 52, "out")
    bx += 52         # 90
    AK(t + 0.50, "k_ready", ax + 40, "out")
    ax += 40         # -200

    # =========================================================== beat 6: Kusari presses, high sickle cut, blocked
    t = 8.00
    AK(t - 0.30, "k_walk1", ax + 30)
    E(t - 0.30, "step", who="A", v=0.5)
    AK(t - 0.14, "k_chop_wind", ax + 62, "out")
    AK(t, "k_chop", ax + 92, "snap")
    BK(t - 0.10, "t_ready", bx - 4, "io")
    BK(t - 0.02, "t_block2_hi", bx - 6, "snap")
    E(t, "clash", v=1.0, blade=2)
    stop(t, 0.07)
    ax += 92         # -108
    # =========================================================== beat 7: front kick to the chest
    k = t + 0.32
    AK(k - 0.12, "kick_wind", ax + 6, "back", uaf=140, faf=60, sw=30, uab=200, fab=170)
    AK(k, "kick", ax + 44, "snap", uaf=150, faf=70, sw=40, uab=210, fab=180)
    E(k, "hit", by="A", on="B", v=1.0, dmg=8, part="ftf")
    stop(k, 0.08)
    BK(k - 0.10, "t_block2_hi", bx - 4, "io")
    BK(k + 0.02, "t_hurt", bx + 40, "snap")
    BK(k + 0.26, "t_hurt", bx + 100, "out", T=-14)
    E(k + 0.26, "skid", x=bx + 100, v=0.9)
    AK(k + 0.28, "k_ready", ax + 40, "out")
    ax += 40         # -68
    bx += 100        # 190

    # =========================================================== beat 8: Twin's angry counter, two cuts
    t = 9.05
    BK(t - 0.14, "t_ready", bx + 6, "back", sq=-0.14, T=24)
    BK(t + 0.06, "t_high1_wind", ax + 190, "out")
    E(t - 0.08, "zip", v=0.8)
    c1 = t + 0.16
    BK(c1, "t_high1", ax + 168, "snap")
    AK(c1 - 0.05, "k_taut_v", ax - 6, "snap")
    E(c1, "clash", v=1.0, blade=1, chain=True)
    stop(c1, 0.07)
    c2 = c1 + 0.22
    BK(c2 - 0.10, "t_rise2_wind", ax + 150, "out")
    BK(c2, "t_rise2", ax + 160, "snap")
    AK(c2 - 0.04, "k_slip", ax - 30, "snap")       # sways out of the rising cut
    bx = ax + 160
    # =========================================================== beat 9: chain wraps the front sword, rips it away
    tw = 10.05
    AK(c2 + 0.16, "k_ready", ax - 20, "out", uab=220, fab=210)
    AK(tw - 0.14, "k_sling", ax - 4, "snap", reel=90)
    E(c2 + 0.10, "chain", mode="spin", dur=0.22, r=46, turns=1.6, plane="side", c=(0, 10))
    E(tw - 0.12, "chain", mode="path", dur=0.12, ease="out", pts=[("J", "B", "hilt0", 0, 22)])
    E(tw, "chain", mode="attach", dur=T_DISARM1 - tw, to=("B", "hilt0", "guard", 0.45), blend=0.03)
    E(tw, "chainwrap", v=1.0)
    E(tw, "hit", by="A", on="B", v=0.6, dmg=0, part="chain", nosolve=True, at_weight=True)
    stop(tw, 0.07)
    BK(c2 + 0.18, "t_rise2", ax + 164, "out")
    BK(tw + 0.02, "t_ready", bx + 6, "snap", T=-6, uaf=170, faf=110, sw=60)
    AK(T_DISARM1 - 0.08, "k_sling", ax - 8, "out")
    AK(T_DISARM1 + 0.06, "k_yank", ax - 34, "snap")
    E(T_DISARM1, "chainyank", v=1.2)
    XL1 = ax - 360    # where his first sword sticks in the ground: -298
    E(T_DISARM1, "loose", id=1, lk="fling", who="B", second=False, tl=T_DISARM1 + 0.62,
      xl=XL1, spin=-2, land_ang=200, tp=T_PICK1)
    E(T_DISARM1, "chain", mode="loose", sword=1, dur=0.12)
    E(T_DISARM1 + 0.62, "swordland", v=1.0)
    BK(T_DISARM1, "t_hurt", bx + 20, "snap", T=6)
    E(T_DISARM1 + 0.12, "chain", mode="free")
    ax -= 34         # -102
    bx += 20         # 84

    # =========================================================== beat 10: two sickle cuts; the second opens his shoulder
    t = 10.85
    BK(t - 0.30, "t_ready", bx + 10, "out")
    AK(t - 0.30, "k_ready", ax + 10, "out")
    AK(t - 0.12, "k_cut_wind", ax + 40, "out")
    AK(t, "k_cut", ax + 40, "snap")
    BK(t - 0.08, "t_ready", bx + 8, "io")
    BK(t - 0.02, "t_block2_hi", bx + 4, "snap", uab=110, fab=60, sw2=40)
    E(t, "clash", v=1.0, blade=2)
    stop(t, 0.06)
    ax += 40
    # he spins right round and the sickle comes again from the other side
    s = t + 0.42
    A.face(t + 0.18, -1)
    A.face(t + 0.30, 1)
    AK(t + 0.22, "k_low", ax + 4, "out", T=40)
    AK(s - 0.08, "k_chop_wind", ax + 10, "snap")
    AK(s, "k_chop", ax + 20, "snap")
    BK(s - 0.10, "t_block2_hi", bx + 2, "out")
    BK(s + 0.01, "t_clutch", bx + 30, "snap")
    E(s, "hit", by="A", on="B", v=1.1, big=True, dmg=20, limb=("sho", "elf", 0.35), blood=18)
    stop(s, 0.12)
    E(s - 0.05, "slowmo", a0=s - 0.05, a1=s + 0.12, rate=0.45)
    ax += 20
    bx += 30         # 114

    # =========================================================== beat 11: he staggers, clutching it; Kusari strolls, cocky
    t = s + 0.20      # 11.47
    BK(t + 0.25, "t_clutch_lo", bx + 30, "out")
    E(t + 0.25, "step", who="B", v=0.5)
    BK(t + 0.60, "t_clutch", bx + 44, "io")
    E(t + 0.60, "step", who="B", v=0.4)
    BK(t + 1.00, "t_clutch_lo", bx + 56, "io", T=30)
    bx += 56         # 170
    AK(t + 0.30, "k_taunt", ax - 6, "out")
    E(t + 0.30, "chain", mode="spin", dur=1.3, r=34, turns=1.6, plane="side", c=(18, -6))
    E(t + 0.30, "chainspin", dur=1.3, v=0.45)
    AK(t + 0.75, "k_stroll1", ax + 10)
    E(t + 0.75, "step", who="A", v=0.4)
    AK(t + 1.15, "k_stroll2", ax + 24)
    E(t + 1.15, "step", who="A", v=0.4)
    ax += 24         # 32

    # =========================================================== beat 12: low throw, he jumps it and lands badly
    t = 12.95
    AK(t - 0.14, "k_taunt", ax + 4, "back", T=10, uab=200, fab=190)
    AK(t, "k_sling", ax + 24, "snap", uab=110, fab=120, T=30)
    E(t - 0.06, "chain", mode="path", dur=0.27, ease="out",
      pts=[(ax + 80, 40), ("Jf", "B", "knf", 18, -10), (bx + 120, 30)], lead=0.12)
    E(t - 0.06, "chainthrow", v=0.8)
    BK(t - 0.02, "t_clutch_lo", bx + 4, "back", sq=-0.14)
    BK(t + 0.14, "t_tuck", bx + 30, "out", air=58, uab=140, fab=18, sw2=-20)
    E(t + 0.22, "chain", mode="free")
    BK(t + 0.34, "t_clutch_lo", bx + 44, "in", sq=-0.14)
    E(t + 0.34, "ground", x=bx + 44, v=0.5)
    BK(t + 0.52, "t_kneel", bx + 46, "snap")          # the leg gives
    E(t + 0.52, "thud", v=0.6)
    bx += 46         # 216
    AK(t + 0.40, "k_ready", ax + 20, "out")
    ax += 20         # 52

    # =========================================================== beat 13: Kusari walks in for the kill; blocked on one knee
    t = 13.70
    AK(t, "k_stroll1", ax + 20)
    E(t, "step", who="A", v=0.5)
    AK(t + 0.36, "k_stroll2", ax + 36)
    E(t + 0.36, "step", who="A", v=0.5)
    ax += 36
    BK(t + 0.30, "t_kneel", bx, "io", H=0, uab=150, fab=95)
    tc = 14.62
    AK(tc - 0.34, "k_chop_wind", ax + 8, "out", sq=0.06)       # sickle high, held
    AK(tc - 0.12, "k_chop_wind", ax + 6, "io", T=-18, H=-14)
    E(tc - 0.40, "heart", v=1.0)
    AK(tc, "k_chop", ax + 16, "snap", T=40, H=30)
    BK(tc - 0.16, "t_kneel", bx, "io")
    BK(tc - 0.03, "t_kneel_block", bx, "snap")
    E(tc, "clash", v=1.3, big=True, blade=2)
    stop(tc, 0.14)
    E(tc - 0.05, "slowmo", a0=tc - 0.05, a1=tc + 0.15, rate=0.35)
    AK(tc + 0.48, "k_chop", ax + 20, "lin", T=46, H=34, sq=-0.06)   # bearing down
    BK(tc + 0.48, "t_kneel_block", bx - 2, "lin", T=18, uab=45, fab=5)
    ax += 20

    # =========================================================== 15-23 THE COMEBACK
    # beat 14: he drives up out of the kneel and shoves the sickle off
    t = 15.15
    BK(t, "t_shove", bx - 14, "snap")
    E(t, "zip", v=0.8)
    AK(t + 0.02, "k_head_back", ax - 18, "snap")
    E(t + 0.02, "swoosh", v=0.8)
    AK(t + 0.30, "k_ready", ax - 50, "out")
    E(t + 0.30, "skid", x=ax - 50, v=0.7)
    ax -= 50         # 86
    BK(t + 0.26, "t_ready", bx + 20, "out", air=12)
    BK(t + 0.48, "t_ready", bx + 40, "in", sq=-0.08)
    bx += 40         # 242
    # beat 15: the throw (distraction)
    BK(T_THROW2 - 0.14, "t_throw_wind", bx + 4, "back", **L_READY)
    BK(T_THROW2, "t_throw", bx - 10, "snap", **L_READY)
    E(T_THROW2, "loose", id=2, lk="throw", who="B", second=True, td=T_THROW2 + 0.15,
      tc=T_CATCH2, at="A", spin1=1, spin2=-1)
    E(T_THROW2, "thrust", v=0.9)
    AK(T_THROW2 + 0.06, "k_ready", ax - 2, "out", H=-10)
    AK(T_THROW2 + 0.15, "k_deflect", ax - 6, "snap", T=-4, uaf=60, faf=25, sw=-20)
    E(T_THROW2 + 0.15, "clash", v=1.0, nosolve=True, at_loose=2)
    stop(T_THROW2 + 0.15, 0.07)
    AK(T_THROW2 + 0.30, "k_deflect", ax - 8, "out", T=-10, H=-22, uaf=40, faf=10, sw=-30)  # eyes on it
    # beat 16: he is already there; kick to the gut
    t = T_THROW2 + 0.10
    BK(t + 0.12, "t_rush", ax + 175, "lin")
    E(t + 0.04, "zip", v=1.0)
    E(t + 0.04, "dust", x=bx, v=0.8)
    kk = T_THROW2 + 0.42
    BK(kk - 0.08, "t_kick_wind", ax + 140, "out")
    BK(kk, "t_kick", ax + 130, "snap")
    E(kk, "hit", by="B", on="A", v=1.0, dmg=8, part="ftf")
    stop(kk, 0.08)
    AK(kk + 0.02, "k_double", ax - 16, "snap")
    # beat 17: elbow to the face
    ke = kk + 0.20
    BK(ke - 0.06, "t_ready", ax + 110, "out", T=20)
    BK(ke, "t_elbow", ax + 102, "snap")
    E(ke, "hit", by="B", on="A", v=0.9, dmg=6, part="haf")
    stop(ke, 0.06)
    AK(ke + 0.02, "k_head_back", ax - 30, "snap")
    # catches his sword as it falls
    BK(T_CATCH2 - 0.04, "t_catch_hi", ax + 112, "out")
    BK(T_CATCH2, "t_catch_hi", ax + 114, "snap")
    E(T_CATCH2, "catch", v=1.0)
    # beat 18: diagonal cut across the chest
    cc = T_CATCH2 + 0.20
    BK(cc - 0.10, "t_over2_wind", ax + 120, "out")
    BK(cc, "t_over2", ax + 104, "snap")
    AK(cc - 0.10, "k_stagger", ax - 34, "out")
    AK(cc + 0.01, "k_stagger", ax - 44, "snap", T=-26)
    E(cc, "hit", by="B", on="A", v=1.1, big=True, dmg=18, blood=18)
    stop(cc, 0.12)
    E(cc - 0.04, "slowmo", a0=cc - 0.04, a1=cc + 0.10, rate=0.5)
    ax -= 44         # 42
    bx = ax + 148
    # beat 19: spinning back kick sends him tumbling
    sk = cc + 0.40
    B.face(sk - 0.20, 1)
    BK(sk - 0.18, "t_kick_wind", bx - 6, "out")
    B.face(sk - 0.06, -1)
    BK(sk, "t_kick", bx - 40, "snap", thf=190, shf=184, thb=88, shb=92, T=-34)   # back leg
    E(sk, "hit", by="B", on="A", v=1.2, big=True, dmg=10, part="ftb")
    stop(sk, 0.10)
    AK(sk + 0.02, "recoil", ax - 40, "snap", sw=60, uab=230, fab=250)
    AK(sk + 0.30, "tumble", ax - 150, "out", air=30, sw=60)
    AK(sk + 0.55, "kneel", ax - 210, "in", sw=60, uab=170, fab=120)
    E(sk + 0.55, "skid", x=ax - 210, v=1.1)
    E(sk + 0.55, "thud", v=0.8)
    ax -= 210        # -168 (past his first sword at XL1=-298? no: sword lies behind him)
    bx -= 40         # 116
    BK(sk + 0.30, "t_ready", bx - 10, "out")

    # beat 20: Kusari whirls the weight to keep him off; he slides under it to his sword
    t = sk + 0.75     # ~18.5
    AK(t, "k_whirl", ax + 6, "out")
    E(t - 0.05, "chain", mode="spin", dur=0.70, r=44, turns=2.6, plane="side", c=(14, -2))
    E(t - 0.05, "chainspin", dur=0.7, v=0.9)
    BK(t + 0.10, "t_ready", bx - 20, "io")
    tt = t + 0.75
    AK(tt - 0.06, "k_whirl", ax + 10, "back", T=-10)
    AK(tt + 0.08, "k_sling", ax + 30, "snap")
    E(tt, "chain", mode="path", dur=0.24, ease="out",
      pts=[(ax + 120, 120), ("Jf", "B", "head", 10, 0), (bx + 80, 110)])
    E(tt, "chainthrow", v=1.0)
    BK(tt - 0.04, "t_ready", bx - 24, "back", sq=-0.14)
    BK(tt + 0.12, "t_slide", bx - 120, "snap")
    E(tt + 0.12, "zip", v=0.9)
    E(tt + 0.14, "dust", x=bx - 120, v=1.0)
    E(tt + 0.26, "chain", mode="free")
    # he slides right past Kusari's feet to the sword in the ground
    BK(T_PICK1 - 0.20, "t_slide", XL1 + 60, "out")
    E(T_PICK1 - 0.20, "skid", x=XL1 + 60, v=1.0)
    ax += 30         # -138
    AK(tt + 0.40, "k_ready", ax, "out")
    A.face(tt + 0.42, -1)
    AK(tt + 0.48, "k_ready", ax - 4, "snap")
    # beat 21: pulls it out of the ground: both swords again
    B.face(T_PICK1 - 0.12, 1)
    BK(T_PICK1 - 0.06, "t_reach_dn", XL1 + 26, "out")
    BK(T_PICK1, "t_reach_dn", XL1 + 22, "snap", nosw=0, sw=10, uaf=172, faf=176)
    E(T_PICK1, "swordland", v=0.6)
    OB.append((T_PICK1 + 0.30, 360, -360))
    BK(T_PICK1 + 0.30, "t_ready", XL1 + 30, "out")
    E(T_PICK1 + 0.22, "twirl", dur=0.5)
    bx = XL1 + 30    # -268  (now he is on the left, facing right)
    BK(T_PICK1 + 0.80, "t_ready", bx + 6, "io", T=18)
    RB[0] = 0

    # =========================================================== beat 22: three-cut combo, the third opens his thigh
    # (Twin faces right now, Kusari faces left)
    t = 20.55
    BK(t - 0.14, "t_ready", bx - 6, "back", sq=-0.14, T=26)
    BK(t + 0.06, "t_high1_wind", ax - 190, "out")
    E(t - 0.08, "zip", v=0.9)
    h1 = t + 0.16
    BK(h1, "t_high1", ax - 168, "snap")
    AK(h1 - 0.04, "k_block_hi", ax + 4, "snap")
    E(h1, "clash", v=1.0, blade=1)
    stop(h1, 0.06)
    ax += 10
    h2 = h1 + 0.20
    BK(h2 - 0.10, "t_low2_wind", ax - 150, "out")
    BK(h2, "t_low2", ax - 136, "snap")
    AK(h2 - 0.04, "k_taut_v", ax + 4, "snap")
    E(h2, "clash", v=1.0, blade=2, chain=True)
    stop(h2, 0.06)
    ax += 10
    h3 = h2 + 0.24
    BK(h3 - 0.12, "t_thrust_wind", ax - 150, "out")
    BK(h3, "t_thrust", ax - 150, "snap")
    AK(h3 - 0.06, "k_slip", ax + 6, "snap")
    AK(h3 + 0.02, "k_hurt_side", ax + 20, "snap")
    E(h3, "hit", by="B", on="A", v=1.1, big=True, dmg=16, limb=("hip", "knf", 0.45), blood=16)
    stop(h3, 0.10)
    ax += 20
    bx = ax - 150
    # beat 23: Kusari answers with a push kick to buy room
    pk = h3 + 0.38
    AK(pk - 0.12, "kick_wind", ax - 2, "back", uaf=150, faf=20, sw=-10, uab=200, fab=170)
    AK(pk, "kick", ax - 36, "snap", uaf=150, faf=20, sw=-10, uab=210, fab=180)
    E(pk, "hit", by="A", on="B", v=1.0, dmg=8, part="ftf")
    stop(pk, 0.08)
    BK(pk - 0.10, "t_thrust", bx + 4, "io")
    BK(pk + 0.02, "t_hurt", bx - 40, "snap")
    BK(pk + 0.30, "t_hurt", bx - 110, "out", T=-12)
    E(pk + 0.30, "skid", x=bx - 110, v=0.9)
    bx -= 110
    AK(pk + 0.30, "k_hurt_side", ax - 10, "out")
    ax -= 10
    # both reset: breathing, limping
    t = pk + 0.60     # ~22.15
    BK(t + 0.20, "t_breathe", bx - 6, "io")
    BK(t + 0.70, "t_breathe", bx - 6, "io", T=26, H=16)
    BK(t + 1.10, "t_ready", bx, "io")
    AK(t + 0.30, "k_hurt_side", ax + 6, "io", T=28)
    AK(t + 0.80, "k_hurt_side", ax + 10, "io", T=18)

    # =========================================================== 23-32 THE TWIST
    t = 23.20
    AK(t, "k_spin_over", ax + 6, "out")
    E(t, "chain", mode="spin", dur=1.48, r=78, turns=4.0, plane="over", c=(-4, 14))
    E(t, "chainspin", dur=1.45, v=1.1)
    AK(t + 0.70, "k_spin_over", ax + 10, "io", T=-10)
    ax += 10
    E(t + 0.10, "cam", until=26.35, zoom=1.22, bars=True, ease=0.5)
    # beat 24: he walks in with the front sword raised high, open, on purpose
    BK(t + 0.20, "t_bait", bx + 10, "out", sw2=100)
    BK(t + 0.55, "t_bait_walk1", bx + 34, sw2=100)
    E(t + 0.55, "step", who="B", v=0.6)
    BK(t + 0.95, "t_bait_walk2", bx + 44, sw2=100)
    E(t + 0.95, "step", who="B", v=0.6)
    BK(t + 1.30, "t_bait", bx + 50, "io", sw2=100)
    bx += 50
    E(t + 1.0, "heart", v=1.0)
    # beat 25: the chain takes the bait and wraps the raised sword
    tw = 24.75
    AK(tw - 0.10, "k_spin_over", ax + 12, "back", T=-14)
    AK(tw + 0.06, "k_sling", ax - 20, "snap")
    E(tw - 0.08, "chain", mode="path", dur=0.16, ease="out", pts=[("J", "B", "hilt0", 0, 26)])
    E(tw + 0.08, "chain", mode="attach", dur=T_RELEASE - tw - 0.08, to=("B", "hilt0", "guard", 0.5),
      blend=0.03)
    E(tw + 0.08, "chainwrap", v=1.1)
    E(tw + 0.08, "hit", by="A", on="B", v=0.6, dmg=0, part="chain", nosolve=True, at_weight=True)
    stop(tw + 0.08, 0.08)
    E(tw + 0.02, "slowmo", a0=tw + 0.02, a1=tw + 0.24, rate=0.4)
    BK(tw + 0.10, "t_bait", bx + 2, "snap", uaf=40, faf=30, sw=20, sw2=100)
    # beat 26: Kusari heaves... and Twin simply lets go
    AK(T_RELEASE - 0.14, "k_sling", ax - 24, "out")
    AK(T_RELEASE + 0.02, "k_heave", ax - 40, "snap")
    E(T_RELEASE, "chainyank", v=1.3)
    XL3 = ax - 190
    E(T_RELEASE, "loose", id=3, lk="fling", who="B", second=False, tl=T_RELEASE + 0.48,
      xl=XL3, spin=-1, land_ang=205)
    E(T_RELEASE, "chain", mode="loose", sword=3, dur=0.48)
    E(T_RELEASE + 0.48, "swordland", v=1.0)
    E(T_RELEASE + 0.48, "chain", mode="path", dur=1.9, pts=[("L", 3, "mid")], hold=True)
    BK(T_RELEASE, "t_release", bx + 4, "snap", sw2=100)
    # with nothing pulling back, the heave throws Kusari off his feet
    AK(T_RELEASE + 0.20, "k_flail", ax - 66, "out")
    AK(T_RELEASE + 0.34, "k_slip", ax - 70, "snap")        # ducks his own weight flying back
    # Twin rides that pull straight in
    BK(T_RELEASE + 0.10, "t_rush", ax + 10 - 140, "out", sw2=100)
    E(T_RELEASE + 0.06, "zip", v=1.1)
    E(T_RELEASE + 0.06, "dust", x=bx, v=1.0)
    # beat 27: the cut that takes the sickle out of his hand
    BK(T_SICKLE - 0.12, "t_hand_wind", ax - 70 - 150, "out", sw2=-100)
    BK(T_SICKLE, "t_hand_cut", ax - 70 - 122, "snap", sw2=150)
    AK(T_SICKLE - 0.10, "k_slip", ax - 70, "io")
    AK(T_SICKLE + 0.01, "k_hurt_hand", ax - 60, "snap", uaf=120, faf=60)
    E(T_SICKLE, "hit", by="B", on="A", v=1.3, big=True, dmg=18, limb=("elf", "haf", 0.7), blood=20)
    stop(T_SICKLE, 0.16)
    E(T_SICKLE - 0.06, "slowmo", a0=T_SICKLE - 0.06, a1=T_SICKLE + 0.18, rate=0.3)
    ax -= 60
    bx = ax - 122
    # beat 28: knee to the chest, Kusari goes down
    kn = T_SICKLE + 0.34
    BK(kn - 0.10, "t_ready", bx + 20, "out", sw2=100)
    BK(kn, "t_knee", bx + 44, "snap", sw2=200)
    E(kn, "hit", by="B", on="A", v=1.1, dmg=8, part="knf")
    stop(kn, 0.08)
    AK(kn + 0.02, "recoil", ax + 30, "snap", sw=60, uaf=170, faf=60)
    AK(kn + 0.40, "fallen", ax + 120, "in", sw=60)
    E(kn + 0.40, "thud", v=1.0)
    E(kn + 0.40, "dust", x=ax + 120, v=1.0)
    ax += 120
    BK(kn + 0.40, "t_ready", bx + 60, "out", sw2=100)
    bx += 60
    # he rolls up, tears the weight off the stuck sword
    ru = kn + 1.10
    AK(ru - 0.30, "kneel", ax + 20, "out", sw=60, uab=200, fab=190)
    AK(ru, "k_hurt_hand", ax + 30, "out")
    AK(ru + 0.16, "k_yank", ax + 20, "snap", reel=30)
    E(ru + 0.16, "chain", mode="path", dur=0.30, ease="out",
      pts=[("J", "A", "hab", 30, 40), ("J", "A", "hab", 10, -14)])
    E(ru + 0.16, "chainyank", v=0.9)
    E(ru + 0.46, "chain", mode="free")
    SA.append((ru + 0.16, 99, dict(reel=30)))
    ax += 20
    BK(ru, "t_ready", bx + 4, "io", sw2=100)

    # =========================================================== beat 29-30: he presses; Kusari, bare-handed, dodges and kicks the shoulder
    t = 28.20
    BK(t - 0.14, "t_ready", bx + 6, "back", sq=-0.14, T=24)
    BK(t + 0.06, "t_rise2_wind", ax - 150, "out", sw2=232)
    p1 = t + 0.16
    BK(p1, "t_rise2", ax - 132, "snap", sw2=22)
    AK(p1 - 0.04, "k_sway", ax + 22, "snap", uaf=170, faf=60)
    ax += 22
    p2 = p1 + 0.30
    BK(p2 - 0.12, "t_h2_wind", ax - 150, "out", sw2=-88)
    BK(p2, "t_h2", ax - 126, "snap", sw2=92)
    AK(p2 - 0.06, "k_hop", ax + 40, "out", air=24, uaf=170, faf=60)
    AK(p2 + 0.14, "k_hurt_hand", ax + 64, "in", sq=-0.1)
    E(p2 + 0.14, "ground", x=ax + 64, v=0.5)
    ax += 64
    bx = ax - 126
    kq = p2 + 0.42
    AK(kq - 0.12, "kick_wind", ax + 2, "back", uaf=170, faf=50, uab=150, fab=60)
    AK(kq, "kick", ax - 52, "snap", uaf=170, faf=50, uab=150, fab=60, thf=70, shf=78)
    E(kq, "hit", by="A", on="B", v=1.1, dmg=10, part="ftf")
    stop(kq, 0.09)
    BK(kq - 0.10, "t_h2", bx - 4, "io", sw2=92)
    BK(kq + 0.02, "t_clutch", bx - 40, "snap", sw2=-20)       # right on the old wound
    BK(kq + 0.34, "t_clutch_lo", bx - 96, "out", sw2=-20)
    E(kq + 0.34, "skid", x=bx - 96, v=0.9)
    bx -= 96
    AK(kq + 0.30, "k_hurt_hand", ax + 4, "out")
    ax += 4
    # both hurt: breathing; Kusari pays out the sickle chain and starts it turning
    t = kq + 0.60     # ~29.8
    BK(t + 0.40, "t_clutch_lo", bx - 4, "io", sw2=-20, T=30)
    BK(t + 1.00, "t_breathe", bx, "io", sw2=110)
    BK(t + 1.60, "t_breathe", bx + 4, "io", sw2=110, T=26)
    AK(t + 0.30, "k_hurt_hand", ax + 2, "io", T=26, hold=62)
    AK(t + 1.00, "k_whirl", ax, "out", hold=120)
    SA.append((t + 1.0, 99, dict(hold=120)))
    E(t + 0.90, "chain", end="sickle", mode="spin", dur=2.1, r=104, turns=3.2, plane="side",
      c=(10, -4))
    E(t + 0.90, "chainspin", dur=2.0, v=0.8)
    AK(t + 1.60, "k_whirl", ax + 4, "io", T=10)

    # =========================================================== 32-40 LAST EXCHANGE
    # beat 31: the sickle flies at his head; he knocks it away
    t = 32.10
    AK(t - 0.06, "k_whirl", ax + 6, "back", T=-12)
    AK(t + 0.10, "k_hurl", ax + 26, "snap")
    E(t + 0.04, "chain", end="sickle", mode="path", dur=0.22, ease="out",
      pts=[(ax - 60, 150), ("M", "B", "guardb", "tipb", 0.62)])
    E(t + 0.04, "chainthrow", v=1.0)
    BK(t + 0.06, "t_breathe", bx + 2, "back", sw2=110)
    BK(t + 0.22, "t_block2_hi", bx - 4, "snap", sw2=95, uab=30, fab=0)
    E(t + 0.26, "clash", v=1.1, nosolve=True, at_sickle=True)
    stop(t + 0.26, 0.08)
    BK(t + 0.40, "t_ready", bx + 6, "out", sw2=100)
    ax += 26
    AK(t + 0.40, "k_whirl", ax - 6, "out")
    # beat 32: he lunges; Kusari steps off it and stamps his knee
    t = 32.95
    BK(t - 0.14, "t_ready", bx + 4, "back", sq=-0.14, T=24, sw2=100)
    BK(t + 0.14, "t_thrust", ax - 150, "snap", sw2=232)
    E(t, "zip", v=0.9)
    AK(t + 0.10, "k_slip", ax + 12, "snap")
    bx = ax - 150
    ks = t + 0.36
    AK(ks - 0.10, "kick_wind", ax + 8, "back", uaf=170, faf=50, uab=150, fab=60)
    AK(ks, "kick", ax - 4, "snap", uaf=170, faf=50, uab=150, fab=60, thf=120, shf=150)
    E(ks, "hit", by="A", on="B", v=1.0, dmg=8, part="ftf")
    stop(ks, 0.08)
    BK(ks + 0.02, "t_kneel", bx - 20, "snap", sw2=60)
    E(ks + 0.02, "thud", v=0.7)
    bx -= 20
    AK(ks + 0.30, "k_whirl", ax + 30, "out")
    ax += 30
    # beat 33: everything into one last throw: overhead whirl, a long wind-up
    t = 34.00
    AK(t, "k_whirl_hi", ax + 6, "out")
    E(t - 0.05, "chain", end="sickle", mode="spin", dur=2.3, r=110, turns=4.2, plane="over",
      c=(-6, 20))
    E(t - 0.05, "chainspin", dur=2.3, v=1.2)
    AK(t + 1.10, "k_whirl_hi", ax + 8, "io", T=-14)
    E(t + 0.40, "cam", until=37.0, zoom=1.18, bars=True, ease=0.5)
    E(t + 1.20, "heart", v=1.1)
    E(t + 1.80, "heart", v=1.2)
    BK(t + 0.60, "t_kneel", bx, "io", sw2=60, T=14)
    BK(t + 1.50, "t_breathe", bx + 6, "io", sw2=110)        # rises, slowly
    BK(t + 2.10, "t_ready", bx + 10, "io", sw2=100, T=26, sq=-0.08)
    bx += 10
    th = 36.35
    AK(th - 0.12, "k_whirl_hi", ax + 2, "back", T=-20)
    AK(th + 0.10, "k_hurl", ax + 30, "snap")
    E(th, "chain", end="sickle", mode="path", dur=0.30, ease="out",
      pts=[(ax - 40, 170), ("Jf", "B", "neck", 10, 6), (bx - 120, 40)], lead=0.0)
    E(th, "chainthrow", v=1.3)
    E(th + 0.30, "chain", end="sickle", mode="free")
    ax += 30
    # =========================================================== 40-45 the finish
    # beat 34: he drops and slides under it, straight at him
    BK(th + 0.06, "t_ready", bx + 4, "back", sq=-0.18, T=30, sw2=100)
    BK(th + 0.20, "t_slide", bx + 90, "snap", sw2=250)
    E(th + 0.14, "slowmo", a0=th + 0.14, a1=th + 0.36, rate=0.3)
    E(th + 0.18, "zip", v=1.1)
    E(th + 0.20, "dust", x=bx + 90, v=1.0)
    # beat 35: one cut, straight through
    tk = th + 0.58
    BK(tk - 0.14, "t_hand_wind", ax - 40, "out", sw2=-100)
    BK(tk, "t_pass", ax + 150, "lin", sw2=100)
    E(tk - 0.02, "iai")
    AK(tk - 0.10, "k_hurl", ax + 2, "io")
    AK(tk + 0.02, "k_cut_thru", ax - 2, "snap")
    E(tk, "hit", by="B", on="A", v=1.3, big=True, dmg=40, blood=24, nosolve=True,
      contact=None)
    E(tk + 0.01, "kill", song=True)
    stop(tk, 0.06)
    fz = tk + 0.12
    BK(fz, "t_pass_hold", ax + 158, "out", sw2=135)
    AK(fz, "k_cut_thru", ax - 4)
    E(fz, "freezeframe", dur=1.3, zoom=0.20, x=ax + 80)
    # the frame lets go: blood, he drops
    E(fz + 0.04, "dmg", who="A", by="B", amt=0, big=True)
    AK(fz + 0.55, "kneel", ax + 4, "in", sw=150, uaf=170, faf=150)
    E(fz + 0.55, "thud", v=0.8)
    AK(fz + 1.30, "fallen", ax + 20, "in", sw=100)
    E(fz + 1.30, "thud", v=1.0)
    E(fz + 1.30, "dust", x=ax + 60, v=1.0)
    BK(fz + 0.70, "t_pass_hold", ax + 160, "io", sw2=135)
    BK(fz + 1.25, "t_flick", ax + 162, "snap", sw2=210)          # flicks the blood off
    E(fz + 1.25, "swoosh", v=0.8)
    BK(fz + 1.90, "t_stand_win", ax + 162, "io", sw2=200)
    E(fz + 1.0, "winner", name="TWIN SWORDS WINS", color=RED)
    end = fz + 2.6
    AK(end, "fallen", ax + 20, sw=100)
    BK(end, "t_stand_win", ax + 162, sw2=200, T=2)
    return dict(fighters=[("A", A, KUSARI), ("B", B, TWIN)], events=ev, end=end,
                title=(("CHAIN SICKLE", ORANGE), ("TWIN SWORDS", RED)),
                springy=True, fluid=True, drawn=drawn, theme="meadow", red_hits=True)
