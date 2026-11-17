"""Fight 06 v2: SAMURAI vs KNIGHT where the armoured knight wins."""
import choreo_knight


def build():
    return choreo_knight.build(knight_wins=True, armoured=True)
