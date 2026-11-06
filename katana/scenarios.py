"""Every video type, as data: physics settings + how it looks + the words on screen."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from sim import SimConfig


@dataclass
class Scenario:
    title: str
    subtitle: str
    sim: SimConfig
    cutter: str = "katana"          # katana | shuriken | laser | none
    palette: tuple = ()             # empty = default neon run
    accent: str = "#9B7BFF"         # ring glow
    note_base: float = 330.0        # pitch of the cut sounds
    end_text: dict = field(default_factory=lambda: {"full": "RING FULL"})


SCENARIOS: dict[str, Scenario] = {
    "katana": Scenario(
        title="KATANA", subtitle="EVERY CUT  =  ×2", cutter="katana",
        sim=SimConfig(spin_start=1.0, spin_end=1.4, cut_cooldown=3.2),
    ),
    "shuriken": Scenario(
        title="SHURIKEN", subtitle="IT BOUNCES.  EVERY CUT  =  ×2",
        sim=SimConfig(
            blades=tuple((k * math.pi / 2, 0.0, 140.0) for k in range(4)),
            cut_from=0.0, blade_half_width=7.0,
            spin_start=0.9, spin_end=1.2, spin_ramp=40.0,
            pivot_moves=True, pivot_radius=140.0, pivot_start=(-150.0, -200.0), pivot_vel=(1000.0, 0.0),
            cut_cooldown=1.8, max_balls=2000, seed=11,
            start_balls=((180.0, -100.0, -150.0, 0.0),),
        ),
        cutter="shuriken", accent="#3EE6C9", note_base=392.0,
        palette=("#FFFFFF", "#9BF6FF", "#4DD8FF", "#4D9BFF", "#6A5CFF", "#A24DFF", "#E04DFF",
                 "#FF4DA6", "#FF5C5C", "#FF9A3D", "#FFD23F", "#B6F23A", "#4DF08A"),
    ),
    "laser": Scenario(
        title="LASER", subtitle="EVERY HIT  =  ×3",
        sim=SimConfig(
            blades=((0.0, -455.0, 455.0),), cut_from=0.0, blade_half_width=3.0,
            spin_start=0.2, spin_end=0.3, spin_ramp=40.0,
            split_into=3, split_kick=300.0, cut_cooldown=5.5, max_balls=2200, seed=5,
            start_balls=((0.0, -300.0, 180.0, 0.0),),
        ),
        cutter="laser", accent="#FF3B6B", note_base=294.0,
        palette=("#FFFFFF", "#FFE066", "#FFB347", "#FF7A45", "#FF4D6D", "#E83F9C", "#B04DFF",
                 "#6E5CFF", "#3F8CFF", "#2EC8FF", "#2EF0C0"),
    ),
    "blackhole": Scenario(
        title="BLACK HOLE", subtitle="WALL HIT  =  ×2      HOLE  =  GONE",
        sim=SimConfig(
            blades=(), gravity=0.0, wall_restitution=1.0,
            wall_split=True, wall_split_speed=150.0, cut_cooldown=0.9,
            hole_radius=34.0, hole_growth=0.2, hole_pull=700.0, swirl_drag=0.2,
            max_balls=2000, min_balls_end=True, max_seconds=60.0, seed=3,
            start_balls=((-200.0, -120.0, 700.0, -600.0),),
        ),
        cutter="none", accent="#FFB347", note_base=262.0,
        end_text={"full": "BALLS WIN", "empty": "HOLE WINS", "time": "TIME"},
    ),
}
