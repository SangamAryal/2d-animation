"""Elemental powers (fire / ice) for the fight renderer.

Everything here is a pure function of animation time, so hit-stops and slow
motion freeze the effects together with the fighters.
"""
import math

import numpy as np
import skia

from draw import col, fill, stroke, polyline
from rig import R_HEAD

FIRE = ["#e8421c", "#ff8a1f", "#ffd23f"]
ICE_FILL, ICE_EDGE, ICE_HI = "#bfe9ff", "#4f9fd1", "#f2fbff"
KINDS = {"proj", "wall", "spikes", "firetrail", "wave", "frost", "freeze", "burst",
         "orb", "shatter", "aura", "mark", "edmg", "boom"}


def lerp(a, b, u):
    return a + (b - a) * u


def clamp(u):
    return max(0.0, min(1.0, u))


# ------------------------------------------------------------ primitives
def flame(c, x, y, h, t, seed=0.0, a=1.0, w=None):
    hh = h * (0.82 + 0.18 * math.sin(t * 23 + seed * 1.7))
    sway = math.sin(t * 17 + seed) * hh * 0.14
    w = w or hh * 0.55
    for color, k in zip(FIRE, (1.0, 0.7, 0.4)):
        ww, lh = w * k, hh * k
        p = skia.Path()
        p.moveTo(x - ww / 2, y)
        p.quadTo(x - ww / 2, y + lh * 0.5, x + sway * k, y + lh)
        p.quadTo(x + ww / 2, y + lh * 0.5, x + ww / 2, y)
        p.quadTo(x, y - ww * 0.45, x - ww / 2, y)
        c.drawPath(p, fill(col(color, a)))


def crystal(c, x, y, h, w, lean=0.0, a=1.0):
    """Ice prism growing up from (x, y)."""
    if h <= 1:
        return
    tx = x + lean * h
    p = skia.Path()
    p.moveTo(x - w / 2, y)
    p.lineTo(lerp(x, tx, 0.75) - w * 0.42, y + h * 0.75)
    p.lineTo(tx, y + h)
    p.lineTo(lerp(x, tx, 0.7) + w * 0.42, y + h * 0.7)
    p.lineTo(x + w / 2, y)
    p.close()
    c.drawPath(p, fill(col(ICE_FILL, 0.92 * a)))
    c.drawPath(p, stroke(col(ICE_EDGE, a), 2.4))
    c.drawLine(x - w * 0.12, y + h * 0.08, lerp(x, tx, 0.8) - w * 0.1, y + h * 0.8,
               stroke(col(ICE_HI, 0.9 * a), 2.2))


def shard(c, x, y, r, ang, a=1.0):
    p = skia.Path()
    for i, (rr, da) in enumerate(((1.0, 0), (0.35, 1.9), (0.8, 3.3), (0.3, 4.6))):
        px, py = x + math.cos(ang + da) * r * rr, y + math.sin(ang + da) * r * rr
        p.moveTo(px, py) if i == 0 else p.lineTo(px, py)
    p.close()
    c.drawPath(p, fill(col(ICE_FILL, 0.95 * a)))
    c.drawPath(p, stroke(col(ICE_EDGE, a), 1.6))


def puff(c, x, y, r, a, color="#ffffff"):
    c.drawCircle(x, y, r, fill(col(color, a)))


# ------------------------------------------------------------ event prep
def prepare(r, t, vt, k, kw):
    """Called for every event; returns True if it was an elemental one."""
    if k not in KINDS:
        return False
    f = r.f
    e = dict(kw, t=t, vt=vt, kind=k, seed=len(r.el) * 7 + 3)

    def cue(name, at=None, **p):
        from render import video_time
        r.cues.append((video_time(r.frames, at if at is not None else t), name, p))

    def sub(kind, at, **p):
        from render import video_time
        prepare(r, at, video_time(r.frames, at), kind, p)

    if k == "proj":
        J = f.joints(kw["by"], t)
        e["p0"] = J["haf"]
        if "to" in kw:
            e["p1"] = kw["to"]
        else:
            B = f.joints(kw["on"], t + kw["dur"])
            e["p1"] = ((B["hip"][0] + B["neck"][0]) / 2, (B["hip"][1] + B["neck"][1]) / 2)
        el = kw.get("el", "fire")
        cue("el_fireball" if el == "fire" else "el_shard", v=1.3 if kw.get("big") else 1.0)
        end = kw.get("end", "hit")
        t1 = t + kw["dur"]
        if end == "steam":
            sub("burst", t1, x=e["p1"][0], y=e["p1"][1], el="steam", v=1.0)
            cue("el_steam", t1)
        elif end != "none":
            sub("burst", t1, x=e["p1"][0], y=e["p1"][1], el=el, v=1.5 if kw.get("big") else 1.0)
            cue("el_firehit" if el == "fire" else "el_icehit", t1)
    elif k == "wall":
        cue("el_iceform", v=1.0)
        if kw.get("break_t"):
            cue("el_icebreak", kw["break_t"], v=1.0)
            sub("burst", kw["break_t"], x=kw["x"], y=kw.get("h", 180) * 0.5, el="steam", v=1.4)
    elif k == "spikes":
        n = kw.get("n", 9)
        for i in range(0, n, 2):
            cue("el_iceform", t + kw["dur"] * i / n, v=0.6)
        cue("el_icebreak", t + kw["dur"] + kw.get("life", 1.0), v=0.5)
    elif k in ("firetrail", "wave"):
        cue("el_roar", v=1.3 if k == "wave" else 0.9, dur=kw["dur"] + 0.6)
    elif k == "frost":
        cue("el_frost", dur=kw["dur"] + 0.2)
    elif k == "freeze":
        cue("el_freeze", dur=kw["full"])
        if kw.get("glow_t"):
            cue("el_rumble", kw["glow_t"], dur=kw["break_t"] - kw["glow_t"])
        e["J"] = f.joints(kw["who"], t + kw["full"])
        xs = [p[0] for key, p in e["J"].items() if isinstance(p, tuple) and len(p) == 2
              and key not in ("sw_dir", "tip", "guard", "hilt0", "sc0", "sc1")]
        ys = [p[1] for key, p in e["J"].items() if isinstance(p, tuple) and len(p) == 2
              and key not in ("sw_dir", "tip", "guard", "hilt0", "sc0", "sc1")]
        e["box"] = (min(xs) - 26, 0, max(xs) + 26, max(ys) + 34)
    elif k == "orb":
        cue("el_roar", v=0.7, dur=kw["t1"] - t)
        if kw.get("fizzle"):
            cue("el_steam", kw["t1"])
    elif k == "shatter":
        e["J"] = f.joints(kw["who"], t - 0.001)
        cue("el_icebreak", v=1.4)
        cue("el_icebreak", t + 0.05, v=1.0)
    elif k == "aura":
        cue("el_roar", v=1.0, dur=kw["dur"])
    elif k == "edmg":
        A, B = f.joints(kw["by"], t), f.joints(kw["who"], t)
        pt = ((B["hip"][0] + B["neck"][0]) / 2, (B["hip"][1] + B["neck"][1]) / 2)
        r.damage.append((vt, kw["who"], kw["amt"]))
        rng = np.random.default_rng(e["seed"])
        # they are ordinary people: every hit cuts and bleeds
        dirx = 1.0 if B["hip"][0] > A["hip"][0] else -1.0
        bpt = (B["hip"][0] * 0.4 + B["neck"][0] * 0.6, B["hip"][1] * 0.4 + B["neck"][1] * 0.6)
        big = kw.get("big") or kw["amt"] >= 15
        r.add_wound(vt, kw["who"], B, bpt, e["seed"])
        if big:
            r.add_wound(vt, kw["who"], B, bpt, e["seed"] + 1)
        r.blood.append((vt, bpt, dirx, 30 if big else 16, e["seed"]))
        if kw.get("el", "fire") == "fire" and kw.get("mark", True):
            r.el_marks.setdefault(kw["who"], []).append(
                (t, rng.uniform(0.2, 0.85), "fire", rng.uniform(0, 6)))
        if kw.get("burst", True):
            sub("burst", t, x=pt[0], y=pt[1], el=kw.get("el", "fire"),
                v=1.6 if kw.get("big") else 1.0)
        if kw.get("big"):
            r.fx.append((vt, "boom", dict(v=0.8, big=True, seed=e["seed"])))
        cue("el_firehit" if kw.get("el", "fire") == "fire" else "el_icehit",
            v=1.3 if kw.get("big") else 1.0)
        if kw.get("phys"):
            cue("thud", v=0.9)
    elif k == "boom":
        r.fx.append((vt, "boom", dict(v=kw.get("v", 1.0), big=True, seed=e["seed"])))
        if kw.get("crater"):
            r.craters.append((vt, kw["x"], 1.0, e["seed"]))
        cue("el_explode", v=kw.get("v", 1.0))
        sub("burst", t, x=kw["x"], y=kw.get("y", 40), el="fire", v=2.6)
        sub("burst", t, x=kw["x"], y=kw.get("y", 40), el="steam", v=1.6)
    elif k == "burst":
        pass
    elif k == "mark":
        if kw.get("el") == "fire":
            cue("step", v=0.45)
        else:
            cue("el_frost", dur=0.12, v=0.5)
            cue("step", v=0.3)
    r.el.append(e)
    return True


def frozen(r, who, t):
    """0..1 how encased the fighter is right now."""
    for e in r.el:
        if e["kind"] == "freeze" and e["who"] == who and e["t"] <= t < e["break_t"]:
            return clamp((t - e["t"]) / e["full"])
    return 0.0


# ------------------------------------------------------------ fighter decoration
def decorate(r, c, who, J, style, t, flat):
    if flat:
        return
    S = J["size"]
    fz = frozen(r, who, t)
    fire = style.get("flame")
    if not (fire or style.get("crystal")):
        return
    # the powers only show on the hands while casting
    g = 0.0
    for e in r.el:
        k, dt = e["kind"], t - e["t"]
        own = e.get("by", e.get("who"))
        if own is None:
            own_el = "fire" if k in ("wave", "firetrail") else (
                "ice" if k in ("wall", "spikes", "frost") else None)
            if own_el is None or (own_el == "fire") != bool(fire):
                continue
        elif own != who or k in ("edmg", "shatter", "mark", "burst"):
            continue
        if k == "freeze":
            continue
        if k in ("aura", "orb"):
            t1 = e["t"] + e["dur"] if k == "aura" else e["t1"]
            if e["t"] - 0.2 <= t <= t1 + 0.2:
                g = max(g, clamp(min(t - e["t"] + 0.2, t1 + 0.2 - t) / 0.2))
        elif -0.32 <= dt <= 0.3:
            g = max(g, clamp((dt + 0.32) / 0.2) if dt < 0 else clamp(1 - dt / 0.3))
    if fz > 0.3:
        g = 0.0
    if g > 0.02:
        for i, key in enumerate(("haf", "hab")):
            x, y = J[key]
            if fire:
                c.drawCircle(x, y, 16 * S * g, fill(col("#ff8a1f", 0.25 * g)))
                c.drawCircle(x, y, 6 * S * g, fill(col(FIRE[1], g)))
                flame(c, x, y - 2, 24 * S * g, t, 2.0 + i * 3, a=g, w=14 * S * g)
            else:
                c.drawCircle(x, y, 16 * S * g, fill(col("#bfe9ff", 0.35 * g)))
                shard(c, x, y, 10 * S * g, t * 4 + i * 2.4, g)
                c.drawCircle(x, y, 3 * S * g, fill(col("#ffffff", g)))
    # burn / frost marks left by elemental hits
    hx, hy = J["hip"]
    nx, ny = J["neck"]
    for mt, u, el, ph in r.el_marks.get(who, []):
        if t < mt:
            continue
        x, y = lerp(hx, nx, u), lerp(hy, ny, u)
        if el == "fire":
            c.drawCircle(x, y, 6.5 * S, fill(col("#1c0f0c", 0.9)))
            c.drawCircle(x + 1, y + 1, 2.4 * S, fill(col("#ff7a1f", 0.6 + 0.4 * math.sin(t * 9 + ph))))
            sm = (t - mt) % 0.9
            puff(c, x + math.sin(ph + t) * 3, y + 8 + sm * 40, 3 + sm * 7, 0.25 * (1 - sm / 0.9), "#4a4038")
        else:
            c.drawCircle(x, y, 7 * S, fill(col("#eaf8ff", 0.95)))
            shard(c, x, y, 8 * S, ph)


# ------------------------------------------------------------ drawing
def draw_ground(r, c, t, flat):
    """Things lying on the ground, behind the fighters."""
    if flat:
        return
    for e in r.el:
        k, dt = e["kind"], t - e["t"]
        if dt < 0:
            continue
        rng = np.random.default_rng(e["seed"])
        if k == "mark":
            a = 0.75 * clamp(1 - (dt - 4) / 3) if dt > 4 else 0.75
            x = e["x"]
            if e["el"] == "fire":
                c.drawOval(skia.Rect(x - 13, -7, x + 13, -1), fill(col("#2a1712", a)))
                if dt < 0.7:
                    flame(c, x, 0, 20 * (1 - dt / 0.7), t, e["seed"])
            else:
                c.drawOval(skia.Rect(x - 16, -7, x + 16, -1), fill(col("#e4f6ff", a)))
                if dt < 2.5:
                    crystal(c, x + 5, 0, 9 * clamp(dt / 0.1), 6, 0.2, clamp(2.5 - dt))
        elif k == "frost":
            u = clamp(dt / e["dur"])
            x0, x1 = e["x0"], lerp(e["x0"], e["x1"], u)
            fa = clamp(1 - (dt - e["dur"] - e.get("life", 3.0)) / 1.2)
            if fa <= 0:
                continue
            c.drawLine(x0, -4, x1, -4, stroke(col("#e4f6ff", 0.95 * fa), 9))
            c.drawLine(x0, -1, x1, -1, stroke(col("#9fd4f2", 0.9 * fa), 2.5))
            n = int(abs(e["x1"] - e["x0"]) / 26)
            for i in range(n + 1):
                xi = lerp(e["x0"], e["x1"], i / max(1, n))
                if (xi - x0) * (x1 - xi) >= 0:
                    crystal(c, xi, 0, rng.uniform(8, 20), 8, rng.uniform(-0.4, 0.4), fa)
                else:
                    rng.uniform(); rng.uniform()
        elif k in ("firetrail", "wave"):
            # scorched ground that stays
            u = clamp(dt / e["dur"])
            x1 = lerp(e["x0"], e["x1"], u)
            c.drawLine(e["x0"], -4, x1, -4, stroke(col("#2a1712", 0.7), 8))


def draw_back(r, c, t, flat):
    """Tall effects behind the fighters."""
    if flat:
        return
    for e in r.el:
        k, dt = e["kind"], t - e["t"]
        if dt < 0:
            continue
        rng = np.random.default_rng(e["seed"])
        if k == "aura" and dt < e["dur"] + 0.4:
            J = r.f.joints(e["who"], t)
            x, y = J["hip"]
            u = clamp(dt / e["dur"])
            fade = clamp((e["dur"] + 0.4 - dt) / 0.4)
            c.drawCircle(x, y + 10, 70 + 60 * u, fill(col("#ff8a1f", 0.16 * fade)))
            for i in range(11):
                fx = x + (i - 5) * 15 + rng.uniform(-5, 5)
                flame(c, fx, 0, (50 + 110 * u) * rng.uniform(0.5, 1.0) * fade, t, i * 1.9,
                      a=0.85)
        elif k == "orb":
            if t > e["t1"] + 0.35:
                continue
            J = r.f.joints(e["who"], min(t, e["t1"]))
            x = (J["haf"][0] + J["hab"][0]) / 2
            u = clamp(dt / (e["t1"] - e["t"]))
            rad = e.get("r", 70) * u
            if t > e["t1"]:
                rad *= clamp(1 - (t - e["t1"]) / 0.3)
            y = max(J["haf"][1], J["hab"][1]) + rad + 6
            if rad > 1:
                c.drawCircle(x, y, rad * 1.5, fill(col("#ff8a1f", 0.18)))
                for i in range(8):
                    an = i / 8 * 2 * math.pi + t * 3
                    flame(c, x + math.cos(an) * rad * 0.7, y + math.sin(an) * rad * 0.5,
                          rad * 0.9, t, i * 2.1, w=rad * 0.5)
                for color, kk in zip(FIRE, (1.0, 0.75, 0.45)):
                    c.drawCircle(x, y, rad * kk, fill(col(color)))


def draw_front(r, c, t, flat):
    if flat:
        return
    for e in r.el:
        k, dt = e["kind"], t - e["t"]
        if dt < 0:
            continue
        rng = np.random.default_rng(e["seed"])
        if k == "proj" and dt <= e["dur"]:
            u = dt / e["dur"]
            (x0, y0), (x1, y1) = e["p0"], e["p1"]
            arc = e.get("arc", 0)

            def pos(uu):
                return lerp(x0, x1, uu), lerp(y0, y1, uu) + arc * math.sin(math.pi * uu)
            x, y = pos(u)
            big = 1.7 if e.get("big") else 1.0
            if e.get("el", "fire") == "fire":
                for i in range(9, 0, -1):
                    px, py = pos(max(0, u - i * 0.035))
                    rr = (15 - i * 1.3) * big
                    c.drawCircle(px, py + math.sin(t * 40 + i) * 3, max(1, rr),
                                 fill(col(FIRE[0] if i > 4 else FIRE[1], 0.75 - i * 0.07)))
                c.drawCircle(x, y, 26 * big, fill(col("#ff8a1f", 0.25)))
                for color, kk in zip(FIRE, (16, 12, 7)):
                    c.drawCircle(x, y, kk * big, fill(col(color)))
            else:
                ang = math.atan2(y1 - y0, x1 - x0)
                for i in range(1, 6):
                    px, py = pos(max(0, u - i * 0.04))
                    c.drawCircle(px, py, 4 - i * 0.6, fill(col("#e4f6ff", 0.7 - i * 0.12)))
                p = skia.Path()
                ux, uy = math.cos(ang), math.sin(ang)
                L, wd = 30 * big, 7 * big
                p.moveTo(x + ux * L * 0.6, y + uy * L * 0.6)
                p.lineTo(x - uy * wd, y + ux * wd)
                p.lineTo(x - ux * L * 0.6, y - uy * L * 0.6)
                p.lineTo(x + uy * wd, y - ux * wd)
                p.close()
                c.drawPath(p, fill(col(ICE_FILL)))
                c.drawPath(p, stroke(col(ICE_EDGE), 2))
        elif k == "wall":
            bt = e.get("break_t")
            h = e.get("h", 180)
            if bt is None or t < bt:
                g = 1 - (1 - clamp(dt / 0.16)) ** 3
                hits = sum(1 for o in r.el if o["kind"] == "proj" and
                           abs(o["p1"][0] - e["x"]) < 40 and o["t"] + o["dur"] <= t)
                for i, (off, hk, wk, ln) in enumerate(((-34, 0.55, 30, -0.18), (30, 0.7, 34, 0.14),
                                                       (-12, 0.85, 40, -0.05), (12, 1.0, 44, 0.04))):
                    crystal(c, e["x"] + off, 0, h * hk * g, wk, ln)
                for i in range(hits * 4):   # cracks after being hit
                    x = e["x"] + rng.uniform(-25, 25)
                    y = rng.uniform(30, h * 0.8)
                    pts = [(x, y)]
                    for j in range(3):
                        x += rng.uniform(-16, 16)
                        y += rng.uniform(-22, 22)
                        pts.append((x, y))
                    polyline(c, pts, stroke(col("#2f6f9c", 0.9), 2))
            else:
                bd = t - bt
                if bd < 1.4:
                    d = e.get("dir", 1)
                    for i in range(26):
                        vx = d * rng.uniform(60, 520) + rng.uniform(-120, 120)
                        vy = rng.uniform(-40, 520)
                        y0 = rng.uniform(10, h)
                        x = e["x"] + rng.uniform(-30, 30) + vx * bd
                        y = y0 + vy * bd - 800 * bd * bd
                        if y < 2:
                            continue
                        shard(c, x, y, rng.uniform(7, 20), rng.uniform(0, 6) + bd * rng.uniform(-9, 9),
                              clamp(1.4 - bd))
        elif k == "spikes":
            n = e.get("n", 9)
            life = e.get("life", 1.0)
            for i in range(n):
                ti = e["dur"] * i / n
                h = rng.uniform(70, 125) * (1.25 if i == n - 1 else 1)
                w = rng.uniform(22, 30)
                ln = rng.uniform(-0.12, 0.12) + (0.18 if e["x1"] > e["x0"] else -0.18)
                x = lerp(e["x0"], e["x1"], i / (n - 1))
                sd = dt - ti
                if sd < 0:
                    continue
                gone = dt - (e["dur"] + life)
                if gone < 0:
                    g = 1 - (1 - clamp(sd / 0.07)) ** 3
                    crystal(c, x, 0, h * g, w, ln)
                elif gone < 0.5:
                    for j in range(3):
                        vx, vy = rng.uniform(-90, 90), rng.uniform(60, 260)
                        shard(c, x + vx * gone, max(3, h * 0.5 + vy * gone - 900 * gone * gone),
                              rng.uniform(6, 12), gone * 9 + j, clamp(1 - gone / 0.5))
        elif k in ("firetrail", "wave"):
            life = e.get("life", 1.5)
            n = max(2, int(abs(e["x1"] - e["x0"]) / 20))
            for i in range(n + 1):
                x = lerp(e["x0"], e["x1"], i / n)
                ti = e["dur"] * i / n
                sd = dt - ti
                hh = rng.uniform(26, 48)
                if sd < 0 or sd > life:
                    continue
                flame(c, x, 0, hh * (1 - sd / life) ** 0.7, t, i * 1.3 + e["seed"])
            if k == "wave" and dt < e["dur"] + 0.12:
                u = clamp(dt / e["dur"])
                xf = lerp(e["x0"], e["x1"], u)
                d = 1 if e["x1"] > e["x0"] else -1
                fade = clamp((e["dur"] + 0.12 - dt) / 0.12)
                c.drawCircle(xf, 70, 120, fill(col("#ff8a1f", 0.18 * fade)))
                for i in range(9):
                    fx = xf - d * i * 17
                    flame(c, fx, 0, (190 - i * 15) * rng.uniform(0.8, 1.0) * fade, t, i * 2.3,
                          w=62 - i * 3)
        elif k == "freeze":
            bt = e["break_t"]
            x0, y0, x1, y1 = e["box"]
            if t < bt:
                u = clamp(dt / e["full"])
                top = y1 * u
                p = skia.Path()
                p.moveTo(x0 - 8, 0)
                p.lineTo(x0 + 4, top * 0.82)
                p.lineTo(lerp(x0, x1, 0.3), top)
                p.lineTo(lerp(x0, x1, 0.62), top * 0.93)
                p.lineTo(x1 - 6, top * 0.84)
                p.lineTo(x1 + 8, 0)
                p.close()
                gl = e.get("glow_t")
                if gl and t > gl:
                    gu = clamp((t - gl) / (bt - gl))
                    cx_, cy_ = (x0 + x1) / 2, y1 * 0.45
                    c.drawCircle(cx_, cy_, 40 + 70 * gu + 6 * math.sin(t * 30),
                                 fill(col("#ff7a1f", 0.25 + 0.4 * gu)))
                c.drawPath(p, fill(col("#a9defb", 0.62)))
                c.drawPath(p, stroke(col(ICE_HI, 0.95), 3.2))
                for i in range(4):
                    xx = lerp(x0, x1, 0.15 + i * 0.22)
                    c.drawLine(xx, top * 0.1, xx + 16, top * (0.45 + 0.1 * i),
                               stroke(col("#ffffff", 0.55), 2.4))
                if gl and t > gl:
                    gu = clamp((t - gl) / (bt - gl))
                    for i in range(int(2 + gu * 12)):
                        x = rng.uniform(x0 + 10, x1 - 10)
                        y = rng.uniform(15, y1 * 0.9)
                        pts = [(x, y)]
                        for j in range(3):
                            x += rng.uniform(-20, 20)
                            y += rng.uniform(-26, 26)
                            pts.append((x, y))
                        polyline(c, pts, stroke(col("#ffb347", 0.95), 2.4))
                    sm = (t * 1.3) % 1.0
                    puff(c, (x0 + x1) / 2 + math.sin(t * 5) * 20, y1 + sm * 60, 10 + sm * 22,
                         0.4 * gu * (1 - sm))
            else:
                bd = t - bt
                if bd < 1.5:
                    cxm = (x0 + x1) / 2
                    for i in range(34):
                        an = rng.uniform(0, 2 * math.pi)
                        sp = rng.uniform(200, 900)
                        px = rng.uniform(x0, x1)
                        py = rng.uniform(10, y1)
                        x = px + math.cos(an) * sp * bd
                        y = py + (math.sin(an) * sp + 200) * bd - 900 * bd * bd
                        if y < 2:
                            continue
                        shard(c, x, y, rng.uniform(8, 24), an + bd * 12, clamp(1.5 - bd))
        elif k == "burst":
            v = e.get("v", 1.0)
            x, y = e["x"], e["y"]
            el = e.get("el", "fire")
            if el == "fire" and dt < 0.6:
                a = 1 - dt / 0.6
                if dt < 0.16:
                    for color, kk in zip(FIRE, (1.0, 0.72, 0.42)):
                        c.drawCircle(x, y, (22 + dt * 420) * v * kk, fill(col(color, 1 - dt / 0.16)))
                c.drawCircle(x, y, (20 + dt * 300) * v, stroke(col("#ffd23f", a * 0.8), 5 * a + 1))
                for i in range(int(14 * v)):
                    an = rng.uniform(0, 2 * math.pi)
                    sp = rng.uniform(120, 520) * v ** 0.5
                    px = x + math.cos(an) * sp * dt
                    py = y + math.sin(an) * sp * dt + 140 * dt
                    c.drawCircle(px, py, rng.uniform(2, 5) * a + 0.5,
                                 fill(col(FIRE[i % 3], a)))
            elif el == "ice" and dt < 0.7:
                a = 1 - dt / 0.7
                c.drawCircle(x, y, (14 + dt * 260) * v, stroke(col("#ffffff", a * 0.9), 4 * a + 1))
                for i in range(int(11 * v)):
                    an = rng.uniform(0, 2 * math.pi)
                    sp = rng.uniform(120, 460)
                    px = x + math.cos(an) * sp * dt
                    py = y + math.sin(an) * sp * dt - 700 * dt * dt
                    shard(c, px, py, rng.uniform(5, 11), an + dt * 10, a)
            elif el == "steam" and dt < 1.5:
                a = (1 - dt / 1.5) ** 1.3
                for i in range(int(9 * v)):
                    an = rng.uniform(0, 2 * math.pi)
                    sp = rng.uniform(20, 110) * v
                    px = x + math.cos(an) * sp * (1 - math.exp(-dt * 4))
                    py = y + math.sin(an) * sp * 0.5 * (1 - math.exp(-dt * 4)) + dt * rng.uniform(40, 90)
                    puff(c, px, py, (10 + 34 * (1 - math.exp(-dt * 3))) * rng.uniform(0.6, 1.1),
                         0.5 * a)
        elif k == "shatter":
            J = e["J"]
            segs = [("hip", "neck"), ("hip", "knf"), ("knf", "ftf"), ("hip", "knb"), ("knb", "ftb"),
                    ("sho", "elf"), ("elf", "haf"), ("sho", "elb"), ("elb", "hab")]
            body = r.f.tracks[e["who"]][1]["body"]
            g = 1300.0
            for i, (a_, b_) in enumerate(segs + [("head", "head")] * 1 + segs):
                (ax, ay), (bx, by) = J[a_], J[b_]
                mx, my = (ax + bx) / 2, (ay + by) / 2
                half = max(6.0, math.hypot(bx - ax, by - ay) / 2) * (1.0 if i < 10 else 0.5)
                vx = rng.uniform(-330, 330)
                vy = rng.uniform(150, 620)
                w = rng.uniform(-12, 12)
                tl = (vy + math.sqrt(vy * vy + 2 * g * max(my, 1))) / g
                td = min(dt, tl)
                x = mx + vx * td
                y = max(4.0, my + vy * td - 0.5 * g * td * td)
                ang = math.atan2(by - ay, bx - ax) + w * td
                if a_ == "head":
                    c.drawCircle(x, y + 6, R_HEAD * J["size"], fill(col(body)))
                    c.drawCircle(x, y + 6, R_HEAD * J["size"], stroke(col(ICE_HI, 0.9), 2))
                elif i < 10:
                    ex, ey = math.cos(ang) * half, math.sin(ang) * half
                    c.drawLine(x - ex, y - ey, x + ex, y + ey, stroke(col(body), 8.5))
                    c.drawLine(x - ex * 0.6, y - ey * 0.6 + 1, x + ex * 0.6, y + ey * 0.6 + 1,
                               stroke(col(ICE_HI, 0.8), 2))
                else:
                    shard(c, x, y, half * 1.4, ang)
