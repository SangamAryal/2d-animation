"""Fight script for sample 01: "SPEED vs PATIENCE".

KASA (blue, straw hat) attacks nonstop. RONIN (black, red headband) dodges
without drawing, blocks only when he must, then wins with one quick-draw cut.
All times are animation seconds (before hitstop / slow motion is applied).
"""
from rig import Track

TITLE = ("SPEED", "PATIENCE")  # left word = KASA, right word = RONIN


def build():
    R = Track(facing=1)    # RONIN, starts left facing right
    K = Track(facing=-1)   # KASA, starts right facing left
    ev = []                # (t, kind, dict)

    def E(t, kind, **kw):
        ev.append((t, kind, kw))

    # ---------------- act 0: the stare-down (0 - 2.9)
    R.key(0.0, "iai", -130)
    R.key(1.2, "iai", -130, dy=-2)
    R.key(2.4, "iai_deep", -132)
    K.key(0.0, "walk1", 470)
    t, x = 0.0, 470
    i = 0
    while t < 2.2:
        t += 0.34
        x -= 34
        K.key(t, "walk2" if i % 2 == 0 else "walk1", x)
        E(t, "step", who="K", v=0.5)
        i += 1
    K.key(2.6, "guard_low", x - 10)
    kx = x - 10  # about 220
    E(0.05, "drum", v=1.0)
    E(1.05, "drum", v=0.8)
    E(2.05, "drum", v=1.0)

    # ---------------- act 1: KASA attacks, RONIN dodges sheathed (2.9 - 4.6)
    K.key(2.95, "crouch", kx)
    K.key(3.12, "run1_g", kx - 80, "lin")
    K.key(3.26, "run2_g", kx - 165, "lin")
    E(3.12, "step", who="K", v=0.8)
    E(3.26, "step", who="K", v=0.8)
    K.key(3.40, "high_wind", kx - 230, "out")
    K.key(3.52, "high_cut", kx - 262, "snap")       # cut lands on empty ground
    E(3.53, "ground", x=kx - 262 - 105, v=0.7)
    R.key(3.36, "iai_deep", -132)
    R.key(3.50, "stand_sheathed", -215, "snap", T=-14, H=-12)  # hop back
    R.key(3.75, "iai", -222)
    E(3.50, "dust", x=-215, v=0.6)

    K.key(3.80, "side_wind", kx - 255, "io")
    K.key(3.93, "side_cut", kx - 285, "snap")       # RONIN ducks under it
    R.key(3.86, "iai_deep", -228, "snap", dy=-26, T=50, H=40)
    R.key(4.15, "iai", -236)

    K.key(4.22, "rise_wind", kx - 300, "io")
    K.key(4.34, "rise_cut", kx - 316, "snap")
    # RONIN finally draws and meets the rising cut
    R.key(4.27, "iai_deep", -240, "io")
    R.key(4.34, "block_mid", -250, "snap", sheath=0)
    E(4.29, "draw")
    E(4.34, "clash", v=1.0, big=True)
    E(4.34, "hitstop", dur=0.12)

    # ---------------- act 2: exchange (4.4 - 6.2)
    kx2 = kx - 316          # about -96
    R.key(4.55, "guard", -262)
    K.key(4.55, "guard", kx2 + 30)
    K.key(4.72, "high_wind", kx2 + 10, "out")
    K.key(4.84, "high_cut", kx2 - 10, "snap", sw=100, uaf=105, faf=110)
    R.key(4.78, "block_high", -262, "snap")
    E(4.84, "clash", v=0.8)
    E(4.84, "hitstop", dur=0.06)
    R.key(4.95, "block_high", -270, dy=-6)
    K.key(5.08, "side_wind", kx2 + 5, "io")
    K.key(5.20, "side_cut", kx2 - 20, "snap")
    R.key(5.14, "parry", -268, "snap")
    E(5.20, "clash", v=0.8)
    E(5.20, "hitstop", dur=0.06)
    K.key(5.32, "stagger", kx2 + 5, "out", grip=1, sw=60)
    # RONIN's counter kick
    R.key(5.36, "kick_wind", -215, "io")
    R.key(5.48, "kick", -178, "snap")
    E(5.48, "hit", v=1.0, big=True)
    E(5.48, "hitstop", dur=0.1)
    K.key(5.48, "stagger", kx2 + 10, "lin", grip=1, sw=60)
    K.key(5.60, "recoil", kx2 + 120, "out", air=10)
    K.key(5.90, "stagger", kx2 + 230, "out")
    E(5.92, "dust", x=kx2 + 230, v=1.0)
    K.key(6.20, "guard_low", kx2 + 236)
    R.key(5.75, "guard", -230)

    # ---------------- act 3: stand-off and the jump attack (6.2 - 8.4)
    kx3 = kx2 + 236          # about 140
    R.key(6.9, "guard", -228, dy=-2)
    K.key(6.9, "guard_low", kx3, dy=-3)
    E(6.3, "heart", v=0.8)
    E(6.8, "heart", v=0.9)
    K.key(7.15, "crouch", kx3 - 8)
    K.key(7.40, "jump_tuck", kx3 - 140, "out", air=125)
    K.key(7.58, "jump_tuck", kx3 - 230, "lin", air=95, T=25)
    K.key(7.72, "land_cut", kx3 - 255, "in")
    E(7.17, "dust", x=kx3 - 8, v=0.6)
    E(7.25, "swoosh", v=0.7)
    R.key(7.45, "guard", -232)
    R.key(7.62, "brace", -240, "snap")
    E(7.72, "clash", v=1.0, big=True)
    E(7.72, "ground", x=-230, v=1.2)
    E(7.72, "hitstop", dur=0.14)
    R.key(7.82, "brace", -240, dy=-10)
    K.key(7.82, "land_cut", kx3 - 255, dy=-4)
    # RONIN shoves him away
    R.key(8.02, "side_cut", -205, "snap")
    E(8.02, "clash", v=0.6)
    K.key(8.02, "land_cut", kx3 - 250)
    K.key(8.15, "recoil", kx3 - 150, "out", air=30)
    K.key(8.45, "stagger", kx3 - 70, "out")
    E(8.47, "dust", x=kx3 - 70, v=0.8)

    # ---------------- act 4: RONIN sheathes. Last charge. (8.4 - 10.0)
    R.key(8.45, "guard", -215)
    R.key(8.85, "sheathing", -215)
    R.key(9.10, "iai", -218, "snap", sheath=1)
    E(9.10, "sheathe")
    K.key(8.95, "guard_low", kx3 - 70)
    K.key(9.30, "crouch", kx3 - 75)
    t, x, i = 9.30, kx3 - 75, 0
    while x > -60:
        t += 0.13
        x -= 52
        K.key(t, "run2_g" if i % 2 == 0 else "run1_g", x, "lin")
        E(t, "step", who="K", v=0.9)
        i += 1
    t_charge_end = t
    R.key(9.45, "iai_deep", -220)
    E(9.45, "heart", v=1.0)

    # ---------------- act 5: the quick draw (slow motion around it)
    t_cut = t_charge_end + 0.05
    K.key(t_cut, "high_wind", x - 18, "out")
    R.key(t_cut - 0.04, "iai_deep", -222)
    R.key(t_cut + 0.05, "iai_cut", x + 175, "snap", sheath=0)
    E(t_cut, "iai", x0=-222, x1=x + 175)
    E(t_cut, "slowmo", a0=t_cut - 0.55, a1=t_cut - 0.02, rate=0.22)
    E(t_cut + 0.05, "hitstop", dur=0.05)
    K.key(t_cut + 0.08, "high_wind", x - 20)
    # long silent pause, then the break
    t_brk = t_cut + 1.2
    K.key(t_brk, "high_wind", x - 20, dy=-2)
    R.key(t_brk, "iai_hold", x + 175)
    E(t_brk, "break", who="K")
    K.key(t_brk + 0.01, "high_wind", x - 20, broken=1)
    K.key(t_brk + 0.45, "kneel", x - 14, "in", broken=1)
    E(t_brk + 0.45, "thud", v=0.7)
    K.key(t_brk + 1.10, "fallen", x - 30, "in", broken=1)
    E(t_brk + 1.10, "thud", v=0.9)
    E(t_brk + 1.10, "dust", x=x - 70, v=0.9)
    R.key(t_brk + 1.0, "sheathing", x + 175)
    R.key(t_brk + 1.45, "stand_sheathed", x + 178, "snap")
    E(t_brk + 1.45, "sheathe", final=True)
    end = t_brk + 3.2
    R.key(end, "stand_sheathed", x + 178)
    K.key(end, "fallen", x - 30, broken=1)
    E(t_brk + 1.6, "winner", name="PATIENCE")
    return R, K, ev, end
