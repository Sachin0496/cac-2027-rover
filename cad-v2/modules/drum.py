"""Bucket drum (RASSOR-style, spec 7.3): four rings between two identical end plates, clamped by four
M4 tie rods through external lugs. Ring A and ring B differ only by a 45 deg rotation of the teeth,
scoops and baffles; the lugs sit at fixed angles so the rods run straight.

Axis +Z. Drum frame: drive plate z 0..4, rings at z 4, 52, 100, 148 (48 mm each), idler plate z 196..200.
Digging: spin so each tooth bites and the spiral baffle carries sand to the core; reverse to dump.
"""
from __future__ import annotations

from math import cos, hypot, radians, sin

from build123d import BuildPart, BuildSketch, Circle, Locations, Mode, Polygon, extrude

from lib.shapes import cyl, hexprism
from params import DRUM_R, DRUM_TIP_R, TOL_HOLE, TOL_TRAP

SHELL_T = 1.6
R_IN = DRUM_R - SHELL_T                     # 78
SCOOPS = 4
SCOOP_W = 30.0                              # deg, opening behind each tooth
SCOOP_H = 22.0                              # mm, how far the mouth dives inwards
SWEEP = 150.0                               # deg, spiral length
R_CORE = 26.0                               # the spiral ends here and releases sand into the core
BAFFLE_T, TOOTH_T = 1.6, 3.2
RING_H, PLATE_T = 48.0, 4.0
BOSS_R, BOSS_H = 15.0, 8.0
LUG_ANGLES = [9.5 + 90.0 * k for k in range(4)]   # between every A and B scoop mouth
LUG_R, LUG_W = 84.0, 10.0
FLANGE_T, FLANGE_R_IN = 1.5, 58.0            # bed-side annulus that joins the four shell arcs into one part
ROD_HOLE_R = 2.0 + TOL_HOLE / 2


def pol(r: float, a_deg: float):
    return (r * cos(radians(a_deg)), r * sin(radians(a_deg)))


def _band(p1, p2, t):
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    n = hypot(dx, dy)
    nx, ny = -dy / n * t / 2, dx / n * t / 2
    return [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)]


def _baffle_path(base: float):
    """Centre line for a tooth at angle `base`: dives in behind the mouth, then spirals to the core."""
    pts = [pol(R_IN - SCOOP_H * sin(radians(90 * i / 6)), base - SCOOP_W * i / 6) for i in range(7)]
    for i in range(1, 25):
        t = i / 24
        pts.append(pol(R_IN - SCOOP_H - (R_IN - SCOOP_H - R_CORE) * t, base - SCOOP_W - SWEEP * t))
    return pts


def _lug_quad(a: float):
    u, v = (cos(radians(a)), sin(radians(a))), (-sin(radians(a)), cos(radians(a)))
    c = lambda r: (r * u[0], r * u[1])
    return [(c(78.5)[0] + 5 * v[0], c(78.5)[1] + 5 * v[1]), (c(88)[0] + 5 * v[0], c(88)[1] + 5 * v[1]),
            (c(88)[0] - 5 * v[0], c(88)[1] - 5 * v[1]), (c(78.5)[0] - 5 * v[0], c(78.5)[1] - 5 * v[1])]


def ring(clock: float = 0.0):
    """One 48 mm ring; `clock` rotates the teeth, scoops and baffles (0 = ring A, 45 = ring B)."""
    with BuildPart() as bp:
        with BuildSketch():
            Circle(DRUM_R)
            Circle(R_IN, mode=Mode.SUBTRACT)
            for k in range(SCOOPS):
                base = clock + 90 * k
                Polygon((0, 0), *[pol(DRUM_R + 5, base + a) for a in (-SCOOP_W, -22.5, -15, -7.5, 0)],
                        align=None, mode=Mode.SUBTRACT)
            for k in range(SCOOPS):
                base = clock + 90 * k
                path = _baffle_path(base)
                for p1, p2 in zip(path, path[1:]):
                    Polygon(*_band(p1, p2, BAFFLE_T), align=None)
                for p in path:
                    with Locations(p):
                        Circle(BAFFLE_T / 2)
                Polygon(*_band(pol(DRUM_TIP_R, base + 4), pol(R_IN - 3, base - 1), TOOTH_T), align=None)
            for a in LUG_ANGLES:
                Polygon(*_lug_quad(a), align=None)
            for a in LUG_ANGLES:
                with Locations(pol(LUG_R, a)):
                    Circle(ROD_HOLE_R, mode=Mode.SUBTRACT)
        extrude(amount=RING_H)
    # outer edge at r = 79 lies inside the 2 mm shell wall (no coincident faces: keeps the boolean valid)
    return bp.part + (cyl(DRUM_R - 1.0, FLANGE_T) - cyl(FLANGE_R_IN, FLANGE_T))


def plate():
    """End plate: disc with lugs, inner boss holding the M8 head in a hex pocket. Two per drum (the
    second one turned over about the axis at 9.5 deg, which maps the lug pattern onto itself)."""
    with BuildPart() as bp:
        with BuildSketch():
            Circle(DRUM_R)
            for a in LUG_ANGLES:
                Polygon(*_lug_quad(a), align=None)
            for a in LUG_ANGLES:
                with Locations(pol(LUG_R, a)):
                    Circle(ROD_HOLE_R, mode=Mode.SUBTRACT)
        extrude(amount=PLATE_T)
    p = bp.part + cyl(BOSS_R, BOSS_H, PLATE_T - 0.01)
    p -= hexprism(13.0 + TOL_TRAP, 5.5 + 1.0, PLATE_T + BOSS_H - 5.5, rot=LUG_ANGLES[0])   # invariant under the flip
    p -= cyl(4.2, PLATE_T + BOSS_H + 1, -0.5)
    p -= cyl(56.0, 2.0, PLATE_T - 2.0) - cyl(17.5, 2.0, PLATE_T - 2.0)        # lightening pocket in the inner face, clear of the ring flange
    return p


def spacer_long(length: float):
    """Printed spacer sleeve on the drum axle, axis +Z, z 0..length."""
    return cyl(5.5, length) - cyl(4.2, length)
