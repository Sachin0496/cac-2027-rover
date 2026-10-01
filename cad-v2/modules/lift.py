"""Lift screw drive (spec 7.3): T8 x 2 lead screw with a brass flange nut in a sliding carriage, guided in a
printed channel that stands on the spine and the front cross member; a Johnson 300 RPM motor drives it
through the same flexible coupler as the wheels. All parts are in world coordinates (screw axis y = 0,
z = SCREW_Z, x forward); the carriage is built at x = 0 and translated.
"""
from __future__ import annotations

from build123d import Box, Cylinder, Pos, Rot

from lib.shapes import AX, box, cyl, hexprism
from params import (B608_D, CARRIAGE_PIN_Z, JM_GEAR_D, JM_SHAFT_OFF, LIFT, SCREW_Z, TOL_BEARING, TOL_HOLE, TOL_TRAP)

SEAT_D = B608_D + TOL_BEARING
BZ0, BZ1 = LIFT["base_z"]
X0, X1 = LIFT["channel_x"]
GEAR_Z = SCREW_Z + JM_SHAFT_OFF
SADDLE_R = (JM_GEAR_D + 0.4) / 2
CX0, CX1 = LIFT["cradle_x"]
CW = LIFT["cradle_half_w"]
CROSS_BOLT_Z = 164.0
CROSS_BOLT_X = (-8.6, 107.6)
CRADLE_BOLT_X, CRADLE_BOLT_Y = (CX0 + CX1) / 2, 24.5
CRADLE_FEET_X = (-70.0, -52.0)
CHANNEL_WALL = 3.2                            # channel wall and base edge thickness


def _x_cyl(r, x0, x1, y=0.0, z=SCREW_Z):
    return Pos(x0, y, z) * Rot(0, 90, 0) * Cylinder(r, x1 - x0, align=AX)


def _y_cyl(r, y0, y1, x=0.0, z=0.0):
    return Pos(x, y0, z) * Rot(-90, 0, 0) * Cylinder(r, y1 - y0, align=AX)


def channel():
    """U channel on the spine and the front cross member; four M5 feet, two cross-bolt holes per block."""
    iw = LIFT["inner_w"] / 2
    wt = CHANNEL_WALL
    c = box(X0, X1, -iw - wt, iw + wt, BZ0, BZ1)
    for s in (-1, 1):
        c += box(X0, X1, s * iw if s > 0 else -iw - wt, iw + wt if s > 0 else -iw, BZ1 - 0.01, LIFT["wall_z_top"])
    for x, y in LIFT["feet"]:
        c -= Pos(x, y, 0) * cyl(2.75, BZ1 - BZ0 + 2, BZ0 - 1)
        c -= Pos(x, y, 0) * cyl(4.9, 4.0, BZ1 - 3.2)
    for x in CROSS_BOLT_X:
        c -= _y_cyl(2.2, -iw - wt - 1, iw + wt + 1, x, CROSS_BOLT_Z)
    return c


def bearing_block():
    """Bearing block, local x 0..14 with the 608 pocket open at x = 14 (the inner face); rotate 180 deg
    about z to get the front one. Cross-bolt hole through the solid end wall."""
    z0, z1 = LIFT["block_z"]
    w = LIFT["inner_w"] - 0.4
    b = box(0, 14, -w / 2, w / 2, z0, z1)
    b -= _x_cyl(SEAT_D / 2, 14 - 7.2, 15)
    b -= _x_cyl(4.5, -1, 14 - 6.9)
    b -= _y_cyl(2.2 + TOL_HOLE / 2 - 0.2, -w, w, 3.4, CROSS_BOLT_Z)
    return b


def carriage():
    """Sliding carriage at x = 0 (24 long): rod bore, a brass M8 nut captured at each end, link ear."""
    z0, z1 = LIFT["carriage_z"]
    h = LIFT["carriage_len"] / 2
    c = box(-h, h, -12.0, 12.0, z0, z1) + box(-7.0, 7.0, -8.0, 8.0, z1 - 0.01, LIFT["ear_top"])
    c -= _x_cyl(4.4, -h - 1, h + 1)                                                       # M8 rod, 0.4 mm clearance
    c -= Pos(-h - 0.5, 0, SCREW_Z) * Rot(0, 90, 0) * hexprism(13.0 + TOL_TRAP, 7.2, 0.0)   # brass nut, corner up
    c -= Pos(h - 6.7, 0, SCREW_Z) * Rot(0, 90, 0) * hexprism(13.0 + TOL_TRAP, 7.2, 0.0)
    c -= _y_cyl(2.7, -9, 9, 0, CARRIAGE_PIN_Z)
    return c


def cradle_base():
    """Lower half of the lift-motor clamp on the spine: saddle, two counterbored M5 feet, two M4 nut traps."""
    z_axis = GEAR_Z
    b = box(CX0, CX1, -CW, CW, BZ0, z_axis)
    b -= _x_cyl(SADDLE_R, CX0 - 1, CX1 + 1, 0.0, z_axis)
    for x in CRADLE_FEET_X:
        b -= Pos(x, 0, 0) * cyl(2.75, 30, BZ0 - 1)
        b -= Pos(x, 0, 0) * cyl(4.9, 4.0, z_axis - SADDLE_R - 3.2)
    for s in (-1, 1):
        b -= Pos(CRADLE_BOLT_X, s * CRADLE_BOLT_Y, 0) * hexprism(7.0 + TOL_TRAP, 4.6, z_axis - 4.1)
        b -= Pos(CRADLE_BOLT_X, s * CRADLE_BOLT_Y, 0) * cyl(2.2, 6.0, z_axis - 10.0)
    return b


def cradle_cap():
    """Upper half of the lift-motor clamp (print flipped, saddle up)."""
    z_axis = GEAR_Z
    c = box(CX0, CX1, -CW, CW, z_axis, z_axis + SADDLE_R + 3.0)
    c -= _x_cyl(SADDLE_R, CX0 - 1, CX1 + 1, 0.0, z_axis)
    for s in (-1, 1):
        c -= Pos(CRADLE_BOLT_X, s * CRADLE_BOLT_Y, 0) * cyl(2.2, SADDLE_R + 6.0, z_axis - 1)
    return c
