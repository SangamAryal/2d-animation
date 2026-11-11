"""Stick-figure rig: poses, forward kinematics, keyframe tracks.

World units, y points up, ground at y = 0. A figure is about 160 units tall.
Every angle is absolute in the fighter's own frame, in degrees:
0 = straight up, 90 = forward (the way the fighter faces), 180 = straight down,
-90 (or 270) = backward. Facing -1 mirrors the figure.
"""
import math

L_TORSO = 50.0
L_NECK = 15.0
R_HEAD = 12.5
L_UARM = 29.0
L_FARM = 27.0
L_THIGH = 36.0
L_SHIN = 35.0
FOOT_R = 4.0

# Pose keys that are angles (interpolated linearly), and scalar keys.
ANGLE_KEYS = ["T", "H", "uaf", "faf", "uab", "fab", "thf", "shf", "thb", "shb", "sw"]
SCALAR_KEYS = ["grip", "air", "dy", "rot"]
STEP_KEYS = ["sheath", "broken", "headless", "hidden"]

BASE = dict(T=0, H=0, uaf=175, faf=165, uab=185, fab=190, thf=170, shf=180,
            thb=192, shb=182, sw=120, grip=0, air=0, dy=0, rot=0, sheath=0, broken=0, headless=0, hidden=0)


def d(a):
    r = math.radians(a)
    return math.sin(r), math.cos(r)


# ---------------------------------------------------------------- poses
P = {}


def pose(name, parent=None, **kw):
    p = dict(P[parent] if parent else BASE)
    p.update(kw)
    P[name] = p
    return p


pose("stand", sw=150)
pose("stand_sheathed", "stand", sheath=1, uaf=165, faf=95, uab=180, fab=110)
# iai stance: crouched, hand on hilt, sword still in the scabbard
pose("iai", T=28, H=18, uaf=150, faf=100, uab=185, fab=95,
     thf=118, shf=178, thb=238, shb=215, sheath=1)
pose("iai_deep", "iai", T=38, H=25, thf=110, shf=172, thb=245, shb=230)
# draw-cut finish: low lunge, sword arm swept forward and up, blade forward
pose("iai_cut", T=42, H=30, uaf=70, faf=62, uab=230, fab=250, sw=75,
     thf=102, shf=165, thb=252, shb=262, sheath=0)
pose("iai_hold", "iai_cut", T=30, H=20, uaf=125, faf=135, sw=165)
# two-handed mid guard
pose("guard", T=6, H=6, uaf=150, faf=95, sw=52, grip=1,
     thf=150, shf=178, thb=212, shb=195)
pose("guard_low", "guard", T=16, thf=135, shf=180, thb=225, shb=205)
pose("walk1", "guard", thf=160, shf=185, thb=200, shb=215)
pose("walk2", "guard", thf=200, shf=188, thb=162, shb=176)
pose("run1", T=22, H=12, uaf=150, faf=100, uab=230, fab=180, sw=70, grip=0,
     thf=110, shf=170, thb=225, shb=280)
pose("run2", "run1", thf=215, shf=275, thb=125, shb=180, uaf=200, faf=150,
     uab=120, fab=60, sw=110)
pose("run1_g", "run1", uaf=150, faf=95, sw=55, grip=1)
pose("run2_g", "run2", uaf=150, faf=95, sw=55, grip=1)
# overhead attack
pose("high_wind", T=-6, H=-4, uaf=15, faf=-15, sw=-115, grip=1,
     thf=145, shf=182, thb=210, shb=192)
pose("high_cut", T=28, H=22, uaf=120, faf=140, sw=140, grip=1,
     thf=122, shf=175, thb=238, shb=222)
# horizontal attack (from back to front)
pose("side_wind", T=-10, H=0, uaf=225, faf=-30, sw=-95, grip=1,
     thf=150, shf=180, thb=212, shb=196)
pose("side_cut", T=20, H=15, uaf=100, faf=95, sw=95, grip=1,
     thf=125, shf=178, thb=235, shb=218)
# rising attack (from low back to high front)
pose("rise_wind", T=24, H=20, uaf=200, faf=225, sw=230, grip=1,
     thf=130, shf=178, thb=230, shb=212)
pose("rise_cut", T=-8, H=-6, uaf=40, faf=40, sw=20, grip=1,
     thf=150, shf=180, thb=205, shb=192, air=4)
# blocks
pose("block_high", T=-4, H=4, uaf=60, faf=-10, sw=95, grip=1,
     thf=145, shf=180, thb=215, shb=198)
pose("block_mid", T=-6, H=-2, uaf=135, faf=30, sw=5, grip=1,
     thf=150, shf=180, thb=215, shb=198)
pose("parry", T=-12, H=-8, uaf=110, faf=15, sw=-30, grip=1,
     thf=160, shf=185, thb=218, shb=200)
# getting hit / pushed back
pose("recoil", T=-22, H=-25, uaf=200, faf=215, uab=230, fab=250, sw=170,
     thf=160, shf=176, thb=215, shb=200, grip=0)
pose("stagger", T=-12, H=-10, uaf=170, faf=140, uab=215, fab=230, sw=120,
     thf=150, shf=180, thb=205, shb=195)
# kick
pose("kick_wind", T=-8, H=0, uaf=140, faf=100, sw=60, grip=1,
     thf=60, shf=200, thb=185, shb=182)
pose("kick", T=-28, H=-12, uaf=150, faf=110, sw=70, grip=1,
     thf=88, shf=92, thb=190, shb=184)
# jump
pose("crouch", T=25, H=15, uaf=150, faf=95, sw=60, grip=1,
     thf=110, shf=200, thb=215, shb=258)
pose("jump_tuck", T=10, H=0, uaf=10, faf=-20, sw=-110, grip=1,
     thf=100, shf=210, thb=140, shb=230)
pose("land_cut", T=40, H=30, uaf=135, faf=150, sw=132, grip=1,
     thf=110, shf=180, thb=250, shb=270)
pose("brace", T=8, H=10, uaf=40, faf=-20, sw=95, grip=1,
     thf=120, shf=195, thb=235, shb=225)
# defeat
pose("frozen", "iai_cut")
pose("kneel", T=30, H=40, uaf=170, faf=150, uab=180, fab=160, sw=150, grip=0,
     thf=95, shf=185, thb=150, shb=265)
pose("fallen", T=93, H=96, uaf=95, faf=90, uab=150, fab=110, sw=100, grip=0,
     thf=266, shf=272, thb=262, shb=268)
pose("sheathing", T=12, H=8, uaf=110, faf=40, uab=165, fab=95, sw=-80,
     thf=150, shf=180, thb=215, shb=196)


# ---------------------------------------------------------------- easing
def ease(kind, u):
    u = min(1.0, max(0.0, u))
    if kind == "lin":
        return u
    if kind == "in":
        return u * u * u
    if kind == "out":  # fast start, soft stop (attacks)
        return 1 - (1 - u) ** 4
    if kind == "snap":  # nearly instant, then settles
        return 1 - (1 - u) ** 8
    if kind == "hold":
        return 0.0 if u < 1 else 1.0
    if kind == "back":  # small anticipation
        c = 1.6
        return u * u * ((c + 1) * u - c)
    return u * u * (3 - 2 * u)  # io


def lerp(a, b, u):
    return a + (b - a) * u


class Track:
    """Keyframes for one fighter: (t, pose_name_or_dict, x, ease, overrides)."""

    def __init__(self, facing=1):
        self.keys = []
        self.facing_keys = [(-1e9, facing)]

    def key(self, t, pose_name, x, e="io", **over):
        p = dict(P[pose_name]) if isinstance(pose_name, str) else dict(pose_name)
        p.update(over)
        self.keys.append((t, p, x, e))
        self.keys.sort(key=lambda k: k[0])
        return self

    def face(self, t, f):
        self.facing_keys.append((t, f))
        self.facing_keys.sort()
        return self

    def facing(self, t):
        f = 1
        for kt, kf in self.facing_keys:
            if kt <= t:
                f = kf
        return f

    def sample(self, t):
        ks = self.keys
        if t <= ks[0][0]:
            return dict(ks[0][1]), ks[0][2]
        if t >= ks[-1][0]:
            return dict(ks[-1][1]), ks[-1][2]
        for i in range(len(ks) - 1):
            t0, p0, x0, _ = ks[i]
            t1, p1, x1, e = ks[i + 1]
            if t0 <= t < t1:
                u = ease(e, (t - t0) / max(1e-6, t1 - t0))
                p = {}
                for k in ANGLE_KEYS + SCALAR_KEYS:
                    p[k] = lerp(p0[k], p1[k], u)
                for k in STEP_KEYS:
                    p[k] = p1[k] if u >= 1 else p0[k]
                return p, lerp(x0, x1, u)
        return dict(ks[-1][1]), ks[-1][2]


# ---------------------------------------------------------------- kinematics
def ik2(sx, sy, tx, ty, l1, l2, bend):
    """Two-bone IK. Returns elbow point. bend = +1/-1 picks the side."""
    dx, dy = tx - sx, ty - sy
    dist = math.hypot(dx, dy)
    dist = max(1e-3, min(dist, l1 + l2 - 1e-3))
    a = (l1 * l1 + dist * dist - l2 * l2) / (2 * l1 * dist)
    a = math.acos(max(-1, min(1, a)))
    base = math.atan2(dy, dx)
    ang = base + a * bend
    return sx + l1 * math.cos(ang), sy + l1 * math.sin(ang)


def solve(p, x, facing, ground=0.0, size=1.0, blade=84.0):
    """Joint positions in world space for pose p at hip x.

    size scales the whole figure; p["rot"] spins the whole body (flips,
    tumbling); the figure is snapped so its lowest point touches the ground,
    then lifted by p["air"] + p["dy"].
    """
    rot = p.get("rot", 0.0)

    def v(a, length):
        s, c = d(a + rot)
        return s * length * size * facing, c * length * size

    def add(pt, a, length):
        dx, dy = v(a, length)
        return (pt[0] + dx, pt[1] + dy)

    J = {}
    hip = (0.0, 0.0)
    J["hip"] = hip
    J["knf"] = add(hip, p["thf"], L_THIGH)
    J["ftf"] = add(J["knf"], p["shf"], L_SHIN)
    J["knb"] = add(hip, p["thb"], L_THIGH)
    J["ftb"] = add(J["knb"], p["shb"], L_SHIN)
    neck = add(hip, p["T"], L_TORSO)
    J["neck"] = neck
    J["head"] = add(neck, p["H"], L_NECK)
    shoulder = add(neck, p["T"] + 180, 4)
    J["sho"] = shoulder
    J["elf"] = add(shoulder, p["uaf"], L_UARM)
    J["haf"] = add(J["elf"], p["faf"], L_FARM)
    elb = add(shoulder, p["uab"], L_UARM)
    hab = add(elb, p["fab"], L_FARM)
    g = p["grip"]
    if g > 0.01:
        tgt = add(J["haf"], p["sw"], 9)
        e2 = ik2(shoulder[0], shoulder[1], tgt[0], tgt[1], L_UARM * size,
                 L_FARM * size, -facing)
        elb = (lerp(elb[0], e2[0], g), lerp(elb[1], e2[1], g))
        hab = (lerp(hab[0], tgt[0], g), lerp(hab[1], tgt[1], g))
    J["elb"], J["hab"] = elb, hab
    J["hilt0"] = add(J["haf"], p["sw"], -8)
    J["guard"] = add(J["haf"], p["sw"], 12)
    J["tip"] = add(J["haf"], p["sw"], 12 + blade)
    sc_a = -115 + p["T"] * 0.6
    J["sc0"] = add(add(hip, p["T"], 8), 90, 10)
    J["sc1"] = add(J["sc0"], sc_a, 72)
    # ground snap
    low = min(J["ftf"][1], J["ftb"][1], J["knf"][1] - 2, J["knb"][1] - 2,
              J["head"][1] - (R_HEAD - FOOT_R) * size, neck[1] - 2)
    hy = ground - low + FOOT_R + p["air"] + p["dy"]
    for k in list(J):
        J[k] = (J[k][0] + x, J[k][1] + hy)
    J["sw_dir"] = v(p["sw"], 1.0 / size)
    J["sc_a"] = sc_a + rot
    J["facing"] = facing
    J["size"] = size
    J["p"] = p
    return J


# ---------------------------------------------------------------- speed vs power
pose("shoulder", T=4, H=4, uaf=165, faf=25, uab=195, fab=175, sw=-130, grip=0,
     thf=155, shf=180, thb=207, shb=186)
pose("heavy1", "shoulder", thf=150, shf=195, thb=205, shb=180, T=8)
pose("heavy2", "shoulder", thf=200, shf=185, thb=158, shb=172, T=8)
pose("drag1", T=14, H=10, uaf=205, faf=215, uab=195, fab=175, sw=240, grip=0,
     thf=150, shf=190, thb=210, shb=185)
pose("drag2", "drag1", thf=205, shf=185, thb=158, shb=176)
pose("dash", T=58, H=45, uaf=235, faf=255, uab=245, fab=265, sw=-95, grip=0,
     thf=110, shf=160, thb=250, shb=268)
pose("slam", T=48, H=44, uaf=140, faf=140, sw=100, grip=1,
     thf=112, shf=178, thb=242, shb=238)
pose("heavy_wind", T=-14, H=-8, uaf=5, faf=-40, sw=-150, grip=1,
     thf=145, shf=180, thb=212, shb=195)
pose("sweep_wind", T=-14, H=4, uaf=235, faf=250, sw=-80, grip=1,
     thf=155, shf=182, thb=215, shb=196)
pose("sweep", T=22, H=14, uaf=95, faf=85, sw=82, grip=1,
     thf=125, shf=178, thb=235, shb=220)
pose("tumble", T=0, H=0, uaf=60, faf=30, uab=-70, fab=-40, sw=20, grip=0,
     thf=135, shf=110, thb=225, shb=250)
pose("broken_look", "iai_hold", H=55, T=24, broken=1)


# ---------------------------------------------------------------- unarmed (fire vs ice)
pose("fist_guard", T=8, H=6, uaf=120, faf=40, uab=150, fab=50,
     thf=150, shf=185, thb=205, shb=195)
pose("stroll1", T=4, H=2, uaf=200, faf=175, uab=155, fab=130,
     thf=150, shf=185, thb=205, shb=215)
pose("stroll2", "stroll1", uaf=155, faf=130, uab=200, fab=178,
     thf=200, shf=190, thb=160, shb=176)
pose("idle", T=2, H=0, uaf=168, faf=150, uab=190, fab=175, thf=165, shf=180, thb=195, shb=184)
pose("throw_wind", T=-12, H=0, uaf=250, faf=330, uab=105, fab=80,
     thf=150, shf=180, thb=210, shb=195)
pose("throw", T=26, H=18, uaf=85, faf=88, uab=215, fab=230,
     thf=125, shf=180, thb=232, shb=215)
pose("cast2", T=14, H=8, uaf=82, faf=86, uab=96, fab=92,
     thf=135, shf=180, thb=225, shb=205)
pose("raise", T=-4, H=-12, uaf=10, faf=-8, uab=-10, fab=8,
     thf=158, shf=180, thb=202, shb=186)
pose("palm_ground", T=58, H=42, uaf=142, faf=168, uab=200, fab=185,
     thf=95, shf=185, thb=150, shb=265)
pose("stomp_wind", T=-8, H=-4, uaf=25, faf=-10, uab=-25, fab=10,
     thf=78, shf=178, thb=186, shb=182)
pose("stomp", T=22, H=14, uaf=140, faf=120, uab=215, fab=200,
     thf=128, shf=180, thb=218, shb=200)
pose("upper_wind", T=36, H=25, uaf=205, faf=140, uab=160, fab=60,
     thf=115, shf=180, thb=235, shb=225)
pose("upper", T=-12, H=-16, uaf=28, faf=4, uab=200, fab=232,
     thf=160, shf=180, thb=200, shb=190)
pose("power", T=-6, H=-14, uaf=128, faf=55, uab=232, fab=305,
     thf=140, shf=185, thb=220, shb=195)
pose("slide", T=-22, H=-4, uaf=205, faf=185, uab=232, fab=250,
     thf=108, shf=112, thb=232, shb=200)
pose("meteor", T=62, H=42, uaf=128, faf=132, uab=242, fab=272,
     thf=150, shf=232, thb=240, shb=262)
pose("flip", T=20, H=10, uaf=120, faf=60, uab=150, fab=70,
     thf=100, shf=210, thb=140, shb=230)

# ---------------------------------------------------------------- time stop vs future sight
pose("tcast", T=-8, H=-10, uaf=172, faf=155, sw=168, grip=0, uab=50, fab=25,
     thf=148, shf=186, thb=208, shb=195)
pose("swalk1", "walk1", sheath=1, uaf=165, faf=95, uab=180, fab=110, grip=0)
pose("swalk2", "walk2", sheath=1, uaf=165, faf=95, uab=180, fab=110, grip=0)
pose("taunt", T=-10, H=-16, uaf=200, faf=175, sw=200, grip=0, uab=150, fab=60,
     thf=158, shf=182, thb=202, shb=186)
