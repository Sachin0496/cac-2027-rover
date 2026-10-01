"""Printed parts of the drive module (spec 7.2). Every function returns a solid in the module frame:
world-like coordinates for a left-side module at x = 0 (axle axis along +Y through z = AXLE_Z, y outward),
except the wheel, wheel cap and spacers which are built with their own axis along +Z (see drive.py)."""
from __future__ import annotations

from math import cos, radians, sin

from build123d import (Axis, Box, BuildPart, BuildSketch, Cylinder, Mode, Plane, Polygon, Pos, Rot, extrude, fillet)

from lib.shapes import AX, box, cyl, hexprism, obround_x
from params import (AXLE_Z, B608_D, HOUSING_R, HOUSING_Y, JM_GEAR_D, JM_SHAFT_OFF, MOUNT_PLATE_Y, RAIL_Z0, TOL_BEARING,
                    TOL_HOLE, TOL_TRAP, TUBE, WHEEL_D, WHEEL_W, Y_STACK)

SEAT_D = B608_D + TOL_BEARING                   # 22.2
GEAR_AXIS_Z = AXLE_Z + JM_SHAFT_OFF             # 94.5
SADDLE_D = JM_GEAR_D + 0.4                      # 37.4
ROOF_Z = (108.0, RAIL_Z0)                       # roof underside / rail bottom
ROOF_Y = (96.0, 149.5)
CAP_Z = (73.0, 108.0)
CLAMP_Y = (96.0, 124.0)
BOLT_X_ROOF, BOLT_Y_ROOF = 32.0, 140.0          # M5 into the rail's bottom slot
BOLT_X_CLAMP, BOLT_Y_CLAMP = 23.0, 110.0        # M4 through cap into roof nut traps
RIB_ANGLES = [60 * k for k in range(6)]


def _along_y_cyl(r, y0, y1, x=0.0, z=AXLE_Z):
    return Pos(x, y0, z) * Rot(-90, 0, 0) * Cylinder(r, y1 - y0, align=AX)


def mount():
    """Plate on the rail's outer face with a two-bearing housing reaching into the wheel."""
    y0, y1 = MOUNT_PLATE_Y
    hy0, hy1 = HOUSING_Y
    plate = fillet(box(-32, 32, y0, y1, 60, 136).edges().filter_by(Axis.Y), 6)
    housing = _along_y_cyl(HOUSING_R, y0, hy1)
    m = plate + housing
    # bearing bore: rear seat from the rail side, web, front seat
    m -= _along_y_cyl(SEAT_D / 2, y0 - 1, Y_STACK["bearing_B"][1] + 0.0)
    m -= _along_y_cyl(7.0, Y_STACK["bearing_B"][1] - 0.5, Y_STACK["bearing_A"][0] + 0.5)
    m -= _along_y_cyl(SEAT_D / 2, Y_STACK["bearing_A"][0], hy1 + 1)
    # two M5 clearance holes with counterbores from the outer (wheel-side) face
    for x in (-20.0, 20.0):
        m -= _along_y_cyl(2.5 + TOL_HOLE / 2 + 0.05, y0 - 1, y1 + 1, x=x, z=126.0)
        m -= _along_y_cyl(4.9, y1 - 3.2, y1 + 1, x=x, z=126.0)
    return m


def cradle_roof():
    """Top half of the motor clamp, bolted under the rail's bottom slot."""
    r = box(-38, 38, ROOF_Y[0], ROOF_Y[1], ROOF_Z[0], ROOF_Z[1])
    for sx in (-1, 1):                                   # relief where the lift arm passes over the front module
        r -= box(min(sx * 28.5, sx * 40.0), max(sx * 28.5, sx * 40.0), ROOF_Y[0] - 1, 122.0, ROOF_Z[0] - 1, ROOF_Z[1] + 1)
    # saddle about the gearbox axis, only over the clamp length
    r -= Pos(0, CLAMP_Y[0] - 1, GEAR_AXIS_Z) * Rot(-90, 0, 0) * Cylinder(SADDLE_D / 2, CLAMP_Y[1] - CLAMP_Y[0] + 2, align=AX)
    for sx in (-1, 1):
        # M5 slots (long along the rail, +-1.5 mm)
        r -= obround_x(8.5, 5.5, ROOF_Z[0] - 1, ROOF_Z[1] + 1, cx=sx * BOLT_X_ROOF, cy=BOLT_Y_ROOF)
        # M4 nut trap open on the mating face, blind hole above it
        r -= Pos(sx * BOLT_X_CLAMP, BOLT_Y_CLAMP, 0) * hexprism(7.0 + TOL_TRAP, 4.1, ROOF_Z[0] - 0.5, rot=0)
        r -= Pos(sx * BOLT_X_CLAMP, BOLT_Y_CLAMP, 0) * cyl(2.2, 6.5, ROOF_Z[0] - 0.5)
    return r


def cradle_cap():
    """Bottom half of the motor clamp."""
    c = box(-28, 28, CLAMP_Y[0], CLAMP_Y[1], CAP_Z[0], CAP_Z[1])
    c -= Pos(0, CLAMP_Y[0] - 1, GEAR_AXIS_Z) * Rot(-90, 0, 0) * Cylinder(SADDLE_D / 2, CLAMP_Y[1] - CLAMP_Y[0] + 2, align=AX)
    for sx in (-1, 1):
        c -= Pos(sx * BOLT_X_CLAMP, BOLT_Y_CLAMP, 0) * cyl(2.2, CAP_Z[1] - CAP_Z[0] + 2, CAP_Z[0] - 1)
    return c


def spacer(length: float):
    """Printed spacer sleeve on the axle bolt, axis +Z, z 0..length."""
    return cyl(5.5, length) - cyl(4.2, length)


# ---------------------------------------------------------------- wheel and wheel cap (axis +Z)
R_RIM_O, R_RIM_I = WHEEL_D / 2 - 10.0, WHEEL_D / 2 - 10.0 - 2.0     # 77 / 75
GROUSERS, GROUSER_T = 12, 2.2
WALL_T, BOSS_R, BOSS_Z0 = 3.0, 20.0, 49.8                           # hub boss face stays at z = 49.8 (y = 209.8) whatever the wall
CIRCLE_R = 14.0                                                    # M4 bolt circle radius


def _sector(r_in, r_out, ang_deg, z0, z1, corner=4.0):
    ring = cyl(r_out, z1 - z0, z0) - cyl(r_in, z1 - z0, z0)
    half, big = ang_deg / 2, r_out + 8
    with BuildPart() as w:
        with BuildSketch(Plane.XY.offset(z0)):
            Polygon((0, 0), (big * cos(radians(-half)), big * sin(radians(-half))),
                    (big * cos(radians(half)), big * sin(radians(half))), align=None)
        extrude(amount=z1 - z0)
    tool = ring & w.part
    return fillet(tool.edges().filter_by(Axis.Z), corner)


def wheel():
    """Grouser wheel, open on the inner side (z = 0), outer wall at z = 56.5..60, hub boss inside."""
    H = WHEEL_W
    wz = H - WALL_T
    w = cyl(R_RIM_O, H) - cyl(R_RIM_I, H)
    for k in range(GROUSERS):
        w += Rot(0, 0, 90 + k * 360 / GROUSERS) * Pos(R_RIM_O + 4.5, 0, H / 2) * Box(11, GROUSER_T, H)
    w += cyl(R_RIM_O, WALL_T, wz)
    for a in RIB_ANGLES:
        w += Rot(0, 0, a) * Pos(48.5, 0, wz - 7.75) * Box(53, 2.2, 16.5)
    w += cyl(BOSS_R, wz + 0.2 - BOSS_Z0, BOSS_Z0)
    for k in range(6):
        w -= Rot(0, 0, 30 + 60 * k) * _sector(24, 66, 48, wz - 1, H + 1)
    w -= cyl(4.2, H, BOSS_Z0 - 1.2)
    for k in range(4):
        a = radians(45 + 90 * k)
        at = Pos(CIRCLE_R * cos(a), CIRCLE_R * sin(a), 0)
        w -= at * cyl(2.2, H, BOSS_Z0 - 1.2)
        w -= at * hexprism(7.0 + TOL_TRAP, 4.0, BOSS_Z0 - 0.7, rot=45 + 90 * k)
    return w


def wheel_cap():
    """Hub cap: hex pocket for the M8 bolt head, four counterbored M4 screws; z 0..8, outer face up."""
    c = cyl(22.0, 8.0)
    c -= hexprism(13.0 + TOL_TRAP, 6.0, 2.5)
    c -= cyl(4.2, 4.0, -0.5)
    for k in range(4):
        a = radians(45 + 90 * k)
        at = Pos(CIRCLE_R * cos(a), CIRCLE_R * sin(a), 0)
        c -= at * cyl(2.2, 9.0, -0.5)
        c -= at * cyl(3.8, 5.0, 3.8)
    return c
