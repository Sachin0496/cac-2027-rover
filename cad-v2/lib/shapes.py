"""Small geometry helpers shared by the part modules."""
from __future__ import annotations

from math import sqrt

from build123d import Align, Box, BuildPart, BuildSketch, Cylinder, Mode, Pos, RegularPolygon, Rot, extrude

AX = (Align.CENTER, Align.CENTER, Align.MIN)          # cylinder/box standing on its z = 0 face


def cyl(r: float, h: float, z0: float = 0.0):
    """Cylinder along +Z from z0 to z0 + h."""
    return Pos(0, 0, z0) * Cylinder(r, h, align=AX)


def hexprism(af: float, h: float, z0: float = 0.0, rot: float = 0.0):
    """Hexagonal prism (across flats `af`) along +Z from z0 to z0 + h."""
    with BuildPart() as bp:
        with BuildSketch():
            RegularPolygon(radius=af / sqrt(3), side_count=6, rotation=rot)
        extrude(amount=h)
    return Pos(0, 0, z0) * bp.part


def box(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from corner coordinates (each pair may be given in either order)."""
    x0, x1, y0, y1, z0, z1 = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1)
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def along_y(shape):
    """Rotate a +Z-axis shape so its axis points along +Y (z 0..h becomes y 0..h)."""
    return Rot(-90, 0, 0) * shape


def obround_x(width_x: float, height_y: float, z0: float, z1: float, cx: float = 0.0, cy: float = 0.0):
    """Slot: two circles of diameter `height_y` joined, long in X, from z0 to z1."""
    r = height_y / 2
    half = (width_x - height_y) / 2
    s = box(cx - half, cx + half, cy - r, cy + r, z0, z1)
    return s + Pos(cx - half, cy, z0) * Cylinder(r, z1 - z0, align=AX) + Pos(cx + half, cy, z0) * Cylinder(r, z1 - z0, align=AX)
