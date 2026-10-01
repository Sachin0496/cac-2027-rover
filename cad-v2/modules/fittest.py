"""Fit-test kit (spec 9.2): a short print that calibrates the three tolerances in params.py.

Left to right in every row the clearance grows: bearing seats 22.0 / 22.1 / 22.2 mm, hex traps and
holes at +0.2 / +0.4 / +0.6 mm. Print it first (about an hour), try a 608 bearing, an M4 nut, an M8
bolt head, M4/M5 bolts and the motor gearbox, then set TOL_BEARING, TOL_TRAP and TOL_HOLE in params.py
to the columns that fit.
"""
from __future__ import annotations

from build123d import Cylinder, Pos, Rot

from lib.shapes import AX, box, cyl, hexprism

PLATE = (100.0, 66.0, 4.0)                  # x, y, z of the base plate (centred on x, y)
CLEAR = (0.2, 0.4, 0.6)
FEATURES = {
    "bearing_seats": [(-30 + 30 * i, 21.0, 22.0 + 0.1 * i) for i in range(3)],
    "nut_traps": ([(-38 + 12 * i, 0.0, "M4", 7.0 + c) for i, c in enumerate(CLEAR)]
                  + [(2 + 22 * i, 0.0, "M8", 13.0 + c) for i, c in enumerate(CLEAR)]),
    "holes": ([(-38 + 12 * i, -21.0, "M4", 4.0 + c) for i, c in enumerate(CLEAR)]
              + [(2 + 14 * i, -21.0, "M5", 5.0 + c) for i, c in enumerate(CLEAR)]),
}
DEPTH = 3.0
SLICE = (50.0, 14.0, 26.0)                  # motor cradle slice: x length, y thickness, height above the plate


def build():
    z0, z1 = 0.0, PLATE[2]
    k = box(-PLATE[0] / 2, PLATE[0] / 2, -PLATE[1] / 2, PLATE[1] / 2, z0, z1)
    x0 = PLATE[0] / 2 - 0.5
    k += box(x0, x0 + SLICE[0], -PLATE[1] / 2, -PLATE[1] / 2 + SLICE[1], z0, z1 + SLICE[2])
    k -= Pos(x0 + SLICE[0] / 2, -PLATE[1] / 2 - 1, z1 + SLICE[2]) * Rot(-90, 0, 0) * Cylinder(37.4 / 2, SLICE[1] + 2, align=AX)
    for x, y, d in FEATURES["bearing_seats"]:
        k -= Pos(x, y, 0) * cyl(d / 2, DEPTH + 1, z1 - DEPTH)
    for x, y, size, af in FEATURES["nut_traps"]:
        k -= Pos(x, y, 0) * hexprism(af, DEPTH + 1, z1 - DEPTH)
    for x, y, size, d in FEATURES["holes"]:
        k -= Pos(x, y, 0) * cyl(d / 2, PLATE[2] + 2, -1.0)
    return k
