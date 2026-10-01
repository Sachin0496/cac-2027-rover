import math

import pytest
from build123d import Box, BuildPart, BuildSketch, Plane, Polygon, Pos, Rot, Cylinder, extrude

from checks.printfit import check_oriented, overhang_patches, printed_mass_g


def shelf(phi_deg, L=20.0, depth=30.0):
    """Wall with a shelf whose underside slopes at phi degrees from horizontal."""
    t = L * math.tan(math.radians(phi_deg))
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            Polygon((0, 0), (10, 0), (10, 60 - t), (10 + L, 60), (0, 60), align=None)
        extrude(amount=depth)
    return bp.part


def horiz_hole(d):
    return Pos(0, 0, 15) * Box(40, 40, 30) - Pos(0, 0, 15) * Rot(90, 0, 0) * Cylinder(d / 2, 60)


def test_mass_formula():
    assert printed_mass_g(Box(10, 10, 10)) == pytest.approx(0.9525, abs=1e-3)


def test_flat_part_on_bed_has_no_overhang():
    assert overhang_patches(Pos(0, 0, 5) * Box(50, 50, 10)) == []


def test_wide_ceiling_flagged_narrow_bridge_ok():
    table = Pos(0, 0, 20) * Box(40, 40, 3) + Pos(-18, -18, 9.25) * Box(4, 4, 18.5) \
        + Pos(18, 18, 9.25) * Box(4, 4, 18.5)
    assert max(p["span"] for p in overhang_patches(table)) > 8
    bridge = Pos(0, 0, 6.5) * Box(30, 6, 3) + Pos(-14, 0, 2.5) * Box(2, 6, 5) + Pos(14, 0, 2.5) * Box(2, 6, 5)
    assert all(p["span"] <= 8 for p in overhang_patches(bridge))


def test_45_and_60_degree_faces_ok_30_degree_flagged():
    assert overhang_patches(shelf(45)) == []
    assert overhang_patches(shelf(60)) == []
    assert overhang_patches(shelf(30)) != []


def test_horizontal_holes_small_ok_large_flagged():
    assert all(p["span"] <= 8 for p in overhang_patches(horiz_hole(4.4)))
    assert max(p["span"] for p in overhang_patches(horiz_hole(22.2))) > 8


def test_bed_and_mass_limits_reported():
    assert any("bed" in m for m in check_oriented("big", Pos(0, 0, 5) * Box(250, 10, 10)))
    assert any("exceeds 180 g" in m for m in check_oriented("heavy", Pos(0, 0, 50) * Box(100, 100, 100)))
    assert check_oriented("ok", Pos(0, 0, 5) * Box(100, 100, 10)) == []
