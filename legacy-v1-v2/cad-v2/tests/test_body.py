import pytest
from build123d import Box, Cylinder, Pos, Rot

from checks.interference import overlap_volume
from checks.printfit import check_oriented, printed_mass_g
from lib.model import to_bed
from lib.shapes import AX
from modules import body
from modules import electronics as el

FLIP = Rot(180, 0, 0)


@pytest.fixture(scope="module")
def halves():
    return body.hood_left(), body.hood_right()


@pytest.mark.parametrize("name,fn,orient", [("hood_left", body.hood_left, FLIP), ("hood_right", body.hood_right, FLIP),
                                            ("body_handle", body.body_handle, FLIP), ("body_side_cover", body.body_side_cover, Rot(90, 0, 0)),
                                            ("body_arrow", body.body_arrow, None)])
def test_part_valid_printable_and_light(name, fn, orient):
    part = fn()
    assert part.is_valid and len(part.solids()) == 1
    o = to_bed(orient * part if orient is not None else part)
    assert check_oriented(name, o) == []
    assert printed_mass_g(o) < 180


def test_halves_meet_in_a_0p6_mm_reveal_on_the_centre_line(halves):
    left, right = halves
    assert left.distance_to(right) == pytest.approx(2 * body.SEAM, abs=0.02)
    assert overlap_volume(left, right) == 0.0


def test_hood_stands_on_the_tray_and_has_a_flat_roof(halves):
    for h in halves:
        bb = h.bounding_box()
        assert bb.min.Z == pytest.approx(el.PLATE_Z[1], abs=1e-6)
        assert bb.max.Z == pytest.approx(body.Z_ROOF, abs=1e-6)
    assert halves[0].bounding_box().max.Y == pytest.approx(150.0)


def test_screw_posts_take_an_m4_screw(halves):
    for key, h in zip(("left", "right"), halves):
        for x, y in el.HOOD_POSTS[key]:
            pin = Pos(x, y, body.POST_BOSS_TOP) * Cylinder(1.95, body.Z_ROOF - body.POST_BOSS_TOP + 2, align=AX)
            assert overlap_volume(h, pin) < 1.0
            assert overlap_volume(h, Pos(x, y, body.POST_BOSS_TOP + 1) * Cylinder(2.6, 3.0, align=AX)) > 3.0    # the post is solid around the bore


def test_front_port_passes_link_carriage_and_pin_heads(halves):
    link = Pos(80, 0, 187) * Box(30, 34, 12)                       # |y| <= 17, up to z = 193
    heads = Pos(78, 0, 176) * Box(12, 56, 10)                      # |y| <= 28, z 171..181
    for h in halves:
        assert overlap_volume(h, link) < 1.0 and overlap_volume(h, heads) < 1.0


def test_handle_legs_sit_over_the_inner_posts():
    h = body.body_handle()
    for s in (-1, 1):
        pin = Pos(-20.0, s * 38.0, body.Z_ROOF) * Cylinder(2.0, 45, align=AX)
        assert overlap_volume(h, pin) < 1.0
    assert h.bounding_box().min.Z == pytest.approx(body.HANDLE["foot_z"][0], abs=1e-6)


def test_arrow_plates():
    a, d = body.body_arrow(False), body.body_arrow(True)
    for s in (a, d):
        bb = s.bounding_box()
        assert (bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z) == pytest.approx((90.0, 30.0, 0.8), abs=1e-6)
    assert a.center().X > 0 > d.center().X - 0.5 and abs(d.center().X) < 0.5          # single head points +x, double is symmetric


def test_hood_stls_are_watertight(halves, tmp_path):
    """Equal corner and roof-edge radii make a spherical corner that cracks in the STL mesh; the radii differ on purpose."""
    from build123d import export_stl
    from checks.validity import stl_watertight
    for name, h in zip(("hood_left", "hood_right"), halves):
        export_stl(to_bed(FLIP * h), str(tmp_path / f"{name}.stl"), tolerance=0.05, angular_tolerance=0.1)
        assert stl_watertight(tmp_path / f"{name}.stl")
