"""Lift arms, pivot brackets, crossbar clamp blocks, lever and link (spec 7.3).

Arm-local frame: origin at the pivot, +X along the arm, +Z up (perpendicular), Y = world y (thickness).
The arm angle rotates this frame about the world y axis; see excavator.py.
"""
from __future__ import annotations

from math import atan2, cos, degrees, radians, sin, tan

from build123d import (Box, BuildPart, BuildSketch, Circle, Cylinder, Plane, Polygon, Pos, Rectangle, Rot, Sketch, Solid, Wire, Edge, extrude, make_hull, mirror, offset)

from lib.shapes import AX, box, cyl, hexprism, obround_x
from params import (ARM_LEN, ARM_Y, B608_D, CROSSBAR_LEN, EAR_AT, LEVER_PIN_AT, LINK_LEN, PIVOT_Z, R_BOSS, R_EAR,
                    BLOCK_HOLE_A, BLOCK_W, LINK_T, LINK_W, R_ROOT, R_TIP, PIVOT_WALL_Y, TOL_BEARING, TOL_HOLE, TOL_TRAP, Y_DRUM, JM_GEAR_D, JM_SHAFT_OFF)

Y0, Y1 = ARM_Y
SEAT_D = B608_D + TOL_BEARING
GEAR_AXIS_U = JM_SHAFT_OFF                    # gearbox axis above the drum axis, arm-local
SADDLE_R = (JM_GEAR_D + 0.4) / 2
CLAMP_A = 23.0                                # M4 clamp bolts at drum axis +- this, arm-local
CLAMP_HALF_W = 28.0


def _y_cyl(r, y0, y1, a=0.0, u=0.0):
    """Cylinder along world y from y0 to y1 at arm-local (a, u)."""
    return Pos(a, y0, u) * Rot(-90, 0, 0) * Cylinder(r, y1 - y0, align=AX)


def _plate(sketch, y0, y1):
    """Extrude a sketch drawn in arm-local (along, up) into a plate spanning world y0..y1."""
    return Pos(0, y1, 0) * Rot(90, 0, 0) * extrude(sketch, amount=y1 - y0)


def _hull(circles):
    edges = []
    for x, y, r in circles:
        edges += (Pos(x, y, 0) * Circle(r)).edges()
    return make_hull(edges)


def _outline():
    return _hull([(0, 0, R_ROOT), (EAR_AT[0], EAR_AT[1], R_EAR), (ARM_LEN, 0, R_TIP)])


def _base_arm():
    """Plate with lightening pocket on the outer face, root bearing pocket and crossbar-clamp holes."""
    hull = _outline()
    arm = _plate(hull, Y0, Y1)
    keep = Pos(0, 0, 0) * Circle(R_ROOT + 3) + Pos(ARM_LEN, 0, 0) * Circle(R_TIP + 4) + Pos(EAR_AT[0], EAR_AT[1], 0) * Circle(R_EAR - 1)
    pocket = offset(hull, amount=-5) - keep
    arm -= _plate(pocket, Y1 - 8.0, Y1 + 0.01)
    # root: 608 pocket from the outer face, 17 mm hole through the remaining floor
    arm -= _y_cyl(SEAT_D / 2, Y1 - 7.2, Y1 + 1)
    arm -= _y_cyl(8.5, Y0 - 1, Y1 - 6.9)
    # crossbar clamp block screws: two M4 through holes with counterbores from the outer face
    for da in (-BLOCK_HOLE_A, BLOCK_HOLE_A):
        arm -= _y_cyl(2.2 + TOL_HOLE / 2 - 0.2, Y0 - 1, Y1 + 1, EAR_AT[0] + da, EAR_AT[1])
        arm -= _y_cyl(3.9, Y1 - 4.6, Y1 + 1, EAR_AT[0] + da, EAR_AT[1])
    return arm


def _trap(a, y):
    """M4 nut trap open on the clamp mating plane (arm-local +u), with a blind bolt-tip hole below."""
    return (Pos(a, y, GEAR_AXIS_U - 4.1) * hexprism(7.0 + TOL_TRAP, 4.6, 0.0)
            + Pos(a, y, GEAR_AXIS_U - 9.5) * cyl(2.2, 6.0))


def _skirt(y_end, depth):
    """Ruled flare from the round boss to the rectangular motor-clamp block (45 degrees at most), so the block's
    underside needs no support when the arm prints plate-down. Both sections have four edges."""
    u0, u1 = GEAR_AXIS_U - SADDLE_R - 3.0, GEAR_AXIS_U
    w, r = CLAMP_HALF_W, R_BOSS - 0.3
    corners = [(w, -u1), (w, -u0), (-w, -u0), (-w, -u1)]                       # local (a, -u), counter-clockwise
    ang = [degrees(atan2(y, x)) for x, y in corners]
    ang = [ang[0]] + [a if a > ang[0] else a + 360.0 for a in ang[1:]] + [ang[0] + 360.0]
    arcs = [Edge.make_circle(r, Plane.XY, ang[k], ang[k + 1]) for k in range(4)]
    start = Wire(arcs)
    end = Wire.make_polygon([(x, y, depth) for x, y in corners], close=True)
    return Pos(ARM_LEN, y_end - depth, 0) * Rot(-90, 0, 0) * Solid.make_loft([start, end], ruled=True)


def arm_drive():
    """Left arm: drum-axle housing (two 608 + web), coupler chamber, lower half of the motor clamp."""
    arm = _base_arm()
    y2 = Y_DRUM["clamp"][0]
    arm += _y_cyl(R_BOSS, Y1 - 1.0, y2, ARM_LEN, 0.0)
    arm += _skirt(y2, 15.0)
    arm += box(ARM_LEN - CLAMP_HALF_W, ARM_LEN + CLAMP_HALF_W, y2 - 0.01, Y_DRUM["clamp"][1],
               GEAR_AXIS_U - SADDLE_R - 3.0, GEAR_AXIS_U)
    b1, b2 = Y_DRUM["bearing_1"], Y_DRUM["bearing_2"]
    arm -= _y_cyl(SEAT_D / 2, Y0 - 1, b1[1], ARM_LEN, 0)
    arm -= _y_cyl(7.0, b1[1] - 0.5, b2[0] + 0.5, ARM_LEN, 0)
    arm -= _y_cyl(SEAT_D / 2, b2[0], b2[1] + 0.5, ARM_LEN, 0)
    arm -= _y_cyl(13.0, b2[1], y2 + 1, ARM_LEN, 0)
    arm -= _y_cyl(SADDLE_R, y2 - 1, Y_DRUM["clamp"][1] + 1, ARM_LEN, GEAR_AXIS_U)
    ymid = (Y_DRUM["clamp"][0] + Y_DRUM["clamp"][1]) / 2
    for s_ in (-1, 1):
        arm -= _trap(ARM_LEN + s_ * CLAMP_A, ymid)
    return arm


def arm_motor_cap():
    """Upper half of the drum-motor clamp, in arm-local coordinates with the drum axis at a = 0."""
    y0, y1 = Y_DRUM["clamp"]
    cap = box(-CLAMP_HALF_W, CLAMP_HALF_W, y0, y1, GEAR_AXIS_U, GEAR_AXIS_U + SADDLE_R + 3.0)
    cap -= _y_cyl(SADDLE_R, y0 - 1, y1 + 1, 0, GEAR_AXIS_U)
    for s_ in (-1, 1):
        cap -= Pos(s_ * CLAMP_A, (y0 + y1) / 2, GEAR_AXIS_U - 1) * cyl(2.2, SADDLE_R + 6.0)
    return cap


def arm_idler():
    """Right arm, built in the left frame (y > 0): one 608 pocket from the inner face; mirror it to install."""
    arm = _base_arm()
    b1 = Y_DRUM["bearing_1"]
    arm -= _y_cyl(SEAT_D / 2, Y0 - 1, b1[1], ARM_LEN, 0)
    arm -= _y_cyl(8.5, b1[1] - 0.5, Y1 + 1, ARM_LEN, 0)
    return arm


def pivot_bracket():
    """Left bracket standing on the rail top; pivot at x = 0, absolute world y and z. Wall carries the
    pivot bolt head on its outer face; two ears bolt into the rail's top slot (M5 x 10)."""
    wy0, wy1 = PIVOT_WALL_Y
    arch = _poly([(-30, 136), (30, 136), (30, PIVOT_Z), (-30, PIVOT_Z)]) + Pos(0, PIVOT_Z, 0) * Circle(30)
    wall_sk = Sketch() + (arch & (Pos(0, 136 + 50, 0) * Rectangle(200, 100)))
    wall = _plate(wall_sk, wy0, wy1)
    b = wall
    for x0, x1 in ((12, 30), (-30, -12)):
        b += box(x0, x1, wy0, 150.0, 136.0, 143.0)
    b -= _y_cyl(4.2, wy0 - 2, wy1 + 1, 0, PIVOT_Z)
    b += box(10.0, 28.0, wy0, wy1, 160.0, 192.0)                           # shoulder carrying the ToF horn
    b += box(14.0, 25.0, wy1 - 0.01, 188.0, 182.0, 192.0)                  # beam over the wheel, pointing outward (+y)
    with BuildPart() as pad:                                               # ToF pad: face normal 25 deg below the forward horizontal
        with BuildSketch(Plane.XZ):
            Polygon((11.0, 178.0), (25.0, 178.0), (25.0 + 14.0 * tan(radians(25.0)), 192.0), (11.0, 192.0), align=None)
        extrude(amount=10.0, both=True)
    b += Pos(0, 178.0, 0) * pad.part
    for x in (-20.0, 20.0):
        b -= Pos(x, 140.0, 0) * cyl(2.75, 9.0, 135.0)
        b -= Pos(x, 140.0, 0) * cyl(4.9, 5.0, 139.8)
    return b


def _poly(pts):
    from build123d import Polygon
    return Polygon(*pts, align=None)


def _screw_holes(faces):
    """Cutters for the M5 clamp-screw holes through the wall of a 40 mm block, on the requested faces."""
    mid = (10.2 + BLOCK_W / 2) / 2
    out = None
    for f in faces:
        h = (Pos(0, 0, (1 if f == "u" else -1) * mid) * cyl(2.75, 12.0, -6.0) if f in "ud"
             else Pos((1 if f == "f" else -1) * mid, 0, 0) * Rot(0, 90, 0) * cyl(2.75, 12.0, -6.0))
        out = h if out is None else out + h
    return out


def _block_solid(length=16.0, faces=("u", "d")):
    """40 x 40 clamp body around the 2020 crossbar, axis along y, centred on the origin; an M5 clamp screw hole
    through the wall on each requested face: u (+up), d (-up), f (+along), b (-along)."""
    b = Box(BLOCK_W, length, BLOCK_W) - Box(20.4, length + 2, 20.4)
    if faces:
        b -= _screw_holes(faces)
    return b


def clamp_block():
    """Crossbar-to-arm block, y from -8 to +8: two M4 holes (a = +-15) with nut traps on the inner end."""
    b = _block_solid()
    for da in (-BLOCK_HOLE_A, BLOCK_HOLE_A):
        b -= _y_cyl(2.2 + TOL_HOLE / 2 - 0.2, -9, 9, da, 0)
        b -= Pos(da, -8.0, 0) * Rot(-90, 0, 0) * hexprism(7.0 + TOL_TRAP, 3.8, -0.5, rot=30)
    return b


def lever():
    """Lever on the crossbar centre: block plus a full-thickness plate to the pin lobe at arm-local
    (LEVER_PIN_AT); local origin = crossbar centre, y from -8 to +8."""
    dx, dz = LEVER_PIN_AT[0] - EAR_AT[0], LEVER_PIN_AT[1] - EAR_AT[1]
    plate = _plate(_hull([(0, 0, 20.0), (dx, dz, 8.0)]), -8.0, 8.0)
    lv = _block_solid(faces=()) + plate
    lv -= Box(20.4, 18, 20.4)
    lv -= _screw_holes(("f", "d"))
    lv -= _y_cyl(2.7, -9, 9, dx, dz)
    return lv


def link():
    """One of two link plates: pin centres 100 mm apart along +X, LINK_T thick (y 0..LINK_T), LINK_W wide."""
    body = (Pos(LINK_LEN / 2, LINK_T / 2, 0) * Box(LINK_LEN, LINK_T, LINK_W) + _y_cyl(LINK_W / 2, 0, LINK_T, 0, 0)
            + _y_cyl(LINK_W / 2, 0, LINK_T, LINK_LEN, 0))
    body -= _y_cyl(2.7, -1, LINK_T + 1, 0, 0) + _y_cyl(2.7, -1, LINK_T + 1, LINK_LEN, 0)
    return body
