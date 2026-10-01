"""2020 T-slot aluminium profile (B-type, slot 6 mm, M5): 20 x 20, lip 1.8, T-cavity 11 wide."""
from __future__ import annotations

from build123d import BuildPart, BuildSketch, Circle, Mode, Polygon, RectangleRounded, extrude

# The +Y slot in profile coordinates: opening 6.2 wide through the 1.8 mm lip, then a cavity
# 11 mm wide behind the lip tapering to 5 mm at depth 6.4 (leaves diagonal webs to the core).
SLOT_PTS = [(-3.1, 10.5), (3.1, 10.5), (3.1, 8.2), (5.5, 8.2), (2.5, 3.6), (-2.5, 3.6), (-5.5, 8.2), (-3.1, 8.2)]
LIP_UNDERSIDE = 8.2      # distance from the axis to the underside of the lip


def extrusion(length: float):
    """Profile along +Z, z from 0 to `length`, centred on the axis."""
    with BuildPart() as bp:
        with BuildSketch():
            RectangleRounded(20, 20, 1.0)
            for k in range(4):
                Polygon(*SLOT_PTS, align=None, rotation=90 * k, mode=Mode.SUBTRACT)
            Circle(2.1, mode=Mode.SUBTRACT)
        extrude(amount=length)
    return bp.part
