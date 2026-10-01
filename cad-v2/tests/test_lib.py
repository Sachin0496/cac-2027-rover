import pytest
from build123d import Cylinder, Pos, Rot, Align

from lib import cots, fasteners
from lib.profile2020 import extrusion
from lib.model import at

AX = (Align.CENTER, Align.CENTER, Align.MIN)


def pin(d, y0, y1):
    """Cylinder along +Y from y0 to y1."""
    return Pos(0, y0, 0) * Rot(-90, 0, 0) * Cylinder(d / 2, y1 - y0, align=AX)


def test_extrusion_profile():
    e = extrusion(100)
    assert e.is_valid and len(e.solids()) == 1
    assert 180 < e.volume / 100 < 260                       # section area in mm2
    bb = e.bounding_box()
    assert (bb.size.X, bb.size.Y, bb.size.Z) == pytest.approx((20, 20, 100), abs=1e-6)
    assert bb.min.Z == pytest.approx(0, abs=1e-6)


def test_bolt_nut_washer_geometry():
    b = fasteners.bolt(5, 10, "button")
    bb = b.bounding_box()
    assert bb.max.Z == pytest.approx(10, abs=1e-6) and bb.min.Z == pytest.approx(-2.75, abs=1e-6)
    h = fasteners.bolt(8, 75, "hex").bounding_box()
    assert h.min.Z == pytest.approx(-5.3, abs=1e-6)
    n = fasteners.nut(8, nyloc=True).bounding_box()
    assert n.size.Z == pytest.approx(8, abs=1e-6)
    assert fasteners.washer(8).bounding_box().size.Z == pytest.approx(1.6, abs=1e-6)


def test_tnut_hole_takes_the_bolt():
    tn = fasteners.tnut()
    bolt = fasteners.bolt(5, 12, "button")
    assert (tn & bolt).volume < 1.0                        # bolt sits in the hole, no overlap
    assert tn.bounding_box().min.Z == pytest.approx(0, abs=1e-6)


def test_tnut_and_bolt_fit_the_top_slot():
    """Profile along Z, +Y slot: T-nut under the lip and a bolt from outside clear the extrusion."""
    e = extrusion(60)
    tn = at((0, 8.2, 30), (0, -1, 0), (1, 0, 0)) * fasteners.tnut()
    bolt = at((0, 14, 30), (0, -1, 0), (1, 0, 0)) * fasteners.bolt(5, 10, "button")
    assert (e & tn).volume < 1.0
    assert (e & bolt).volume < 1.0 and (tn & bolt).volume < 1.0


def test_bearing_608():
    b = cots.bearing_608()
    assert (b & pin(8, -5, 12)).volume < 1.0                # 8 mm pin fits the bore
    assert (b & pin(8.3, -5, 12)).volume > 1.0              # bore is really 8 mm
    assert b.bounding_box().size.Y == pytest.approx(7, abs=1e-6)


def test_coupler_accepts_6_and_8():
    c = cots.coupler_6_8()
    assert (c & pin(6, -10, 12.5)).volume < 1.0 and (c & pin(8, 12.5, 40)).volume < 1.0
    assert (c & pin(8, -10, 12.4)).volume > 1.0            # 8 mm does not fit the 6 mm side


def test_motor_layout():
    m = cots.motor_johnson()
    bb = m.bounding_box()
    assert bb.max.Y == pytest.approx(22, abs=1e-6) and bb.min.Y == pytest.approx(-63, abs=1e-6)
    assert bb.max.Z == pytest.approx(7.5 + 18.5, abs=1e-6)  # gearbox axis 7.5 above the shaft


def test_corner_bracket_is_20_tall():
    assert cots.corner_bracket().bounding_box().size.Z == pytest.approx(20, abs=1e-6)
