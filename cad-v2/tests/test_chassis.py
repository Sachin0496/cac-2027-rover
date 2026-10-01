import pytest

from checks.interference import find_collisions
from lib.model import Assembly
from modules import chassis


def built():
    a = Assembly()
    chassis.build(a)
    return a


def extr(a):
    return {i.id: i for i in a.items if i.kind == "stock"}


def test_four_extrusions_with_right_lengths():
    e = extr(built())
    assert set(e) == {"rail_l", "rail_r", "cross_rear", "cross_front", "spine"}
    sizes = {k: max(v.shape.bounding_box().size.X, v.shape.bounding_box().size.Y, v.shape.bounding_box().size.Z) for k, v in e.items()}
    assert sizes["rail_l"] == pytest.approx(402, abs=1e-3) and sizes["cross_front"] == pytest.approx(260, abs=1e-3)
    assert sum(sizes.values()) == pytest.approx(1583, abs=1e-3)


def test_rail_and_cross_member_positions():
    e = extr(built())
    rl = e["rail_l"].shape.bounding_box(); rr = e["rail_r"].shape.bounding_box()
    assert (rl.min.Y, rl.max.Y) == pytest.approx((130, 150), abs=1e-6)
    assert (rr.min.Y, rr.max.Y) == pytest.approx((-150, -130), abs=1e-6)
    assert (rl.min.Z, rl.max.Z) == pytest.approx((116, 136), abs=1e-6)
    assert (rl.min.X, rl.max.X) == pytest.approx((-212, 190), abs=1e-6)
    cf = e["cross_front"].shape.bounding_box()
    assert (cf.min.Y, cf.max.Y) == pytest.approx((-130, 130), abs=1e-6)   # butts against both rails


def test_no_collisions():
    assert find_collisions(built()) == []


def test_twelve_brackets_each_with_two_screws_and_two_tnuts():
    a = built()
    br = [i for i in a.items if i.part == "corner_bracket"]
    screws = [i for i in a.items if i.meta.get("sku") == "M5x8 button"]
    tnuts = [i for i in a.items if i.meta.get("sku") == "T-nut M5 spring"]
    assert len(br) == 12 and len(screws) == 24 and len(tnuts) == 24


def test_frame_mass_is_about_half_a_kilo_per_metre():
    a = built()
    m = sum(i.mass() for i in extr(a).values())
    assert 700 < m < 900
