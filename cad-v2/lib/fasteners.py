"""Fastener solids. Convention: axis +Z, head under-surface at z = 0 (head at z < 0), shank z 0..length.
Nuts and washers occupy z 0..height. All simplified (no threads, no drive sockets)."""
from __future__ import annotations

from math import sqrt

from build123d import Align, BuildPart, BuildSketch, Circle, Cylinder, Mode, Polygon, RegularPolygon, extrude

STEEL_G_PER_MM3 = 7.85e-3
AX = (Align.CENTER, Align.CENTER, Align.MIN)

HEAD = {  # (head diameter or across-flats, head height)
    ("button", 3): (5.7, 1.65), ("button", 4): (7.6, 2.2), ("button", 5): (9.5, 2.75),
    ("socket", 3): (5.5, 3.0), ("socket", 4): (7.0, 4.0), ("socket", 5): (8.5, 5.0),
    ("hex", 5): (8.0, 3.5), ("hex", 8): (13.0, 5.3),
}
NUT = {3: (5.5, 2.4), 4: (7.0, 3.2), 5: (8.0, 4.0), 8: (13.0, 6.5)}       # across flats, height
NYLOC_H = {3: 4.0, 4: 5.0, 5: 5.0, 8: 8.0}
WASHER = {3: (7.0, 0.5, 3.2), 4: (9.0, 0.8, 4.3), 5: (10.0, 1.0, 5.3), 8: (16.0, 1.6, 8.4)}  # OD, thickness, ID


def _hex(af: float, height: float):
    with BuildPart() as bp:
        with BuildSketch():
            RegularPolygon(radius=af / sqrt(3), side_count=6)
        extrude(amount=height)
    return bp.part


def bolt(d: float, length: float, head: str = "button"):
    hd, hh = HEAD[(head, int(d))]
    shank = Cylinder(d / 2, length, align=AX)
    if head == "hex":
        h = _hex(hd, hh)
    else:
        h = Cylinder(hd / 2, hh, align=AX)
    from build123d import Pos
    return shank + Pos(0, 0, -hh) * h


def nut(d: float, nyloc: bool = False):
    af, h = NUT[int(d)]
    if nyloc:
        h = NYLOC_H[int(d)]
    return _hex(af, h) - Cylinder(d / 2, h, align=AX)


def washer(d: float):
    od, t, idd = WASHER[int(d)]
    return Cylinder(od / 2, t, align=AX) - Cylinder(idd / 2, t, align=AX)


def tnut():
    """Spring T-nut for a 2020 slot: axis +Z; top face (against the lip underside) at z = 0,
    body z 0..3.4 (deeper into the cavity), 10 mm long along local Y, M5 hole."""
    from build123d import Plane
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            Polygon((-5.0, 0), (5.0, 0), (3.1, 3.4), (-3.1, 3.4), align=None)
        extrude(amount=5, both=True)
    body = bp.part
    return body - Cylinder(2.5, 3.4, align=AX)


def steel_mass_g(shape) -> float:
    return shape.volume * STEEL_G_PER_MM3
