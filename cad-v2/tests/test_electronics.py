import math

import pytest
from build123d import Cylinder, Pos

from checks.interference import overlap_volume
from checks.printfit import check_oriented, printed_mass_g
from lib import cots, fasteners
from lib.model import at, to_bed
from lib.shapes import AX
from modules import electronics as el

PARTS = {"tray_left": el.tray_left, "tray_right": el.tray_right, "tray_tie": el.tray_tie, "batt_cradle": el.batt_cradle}


@pytest.mark.parametrize("name", list(PARTS))
def test_part_is_valid_single_solid_printable_and_light(name):
    part = PARTS[name]()
    assert part.is_valid and len(part.solids()) == 1
    o = to_bed(part)
    assert check_oriented(name, o) == []
    assert printed_mass_g(o) < 180


def test_trays_are_mirror_images_in_extent():
    l, r = el.tray_left().bounding_box(), el.tray_right().bounding_box()
    assert (l.min.Y, l.max.Y) == pytest.approx((-r.max.Y, -r.min.Y))
    assert (l.min.X, l.max.X) == pytest.approx((r.min.X, r.max.X))


def footprint(sku, cx, cy, rot):
    x, y = cots.BOARDS[sku][:2]
    if int(rot) % 180 == 90:
        x, y = y, x
    return cx - x / 2, cx + x / 2, cy - y / 2, cy + y / 2


def test_boards_keep_1p5_mm_apart_and_clear_of_the_hood_posts():
    rects = {k: footprint(*v) for k, v in el.LAYOUT.items()}
    keys = list(rects)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            ax0, ax1, ay0, ay1 = rects[a]
            bx0, bx1, by0, by1 = rects[b]
            assert max(bx0 - ax1, ax0 - bx1, by0 - ay1, ay0 - by1) >= 1.5, (a, b)
    for pts in el.HOOD_POSTS.values():
        for px, py in pts:
            for k, (x0, x1, y0, y1) in rects.items():
                d = math.hypot(max(x0 - px, 0, px - x1), max(y0 - py, 0, py - y1))
                assert d >= 4.5 + 1.5, (k, px, py)


def test_power_bay_is_on_the_battery_side():
    assert all(cy < 0 for k, (sku, cx, cy, rot) in el.LAYOUT.items() if sku in ("bts7960", "relay", "buck", "fuse_holder"))
    assert el.BATT["center"][1] < 0


def test_hood_post_bores_and_nut_traps():
    for key, tray in (("left", el.tray_left()), ("right", el.tray_right())):
        for x, y in el.HOOD_POSTS[key]:
            pin = Pos(x, y, el.PLATE_Z[0] - 1) * Cylinder(1.95, el.BOSS_H + 3, align=AX)          # M4 shaft
            assert overlap_volume(tray, pin) < 1.0
            nut = at((x, y, el.PLATE_Z[1] + el.BOSS_H - 3.8 + 0.3), (0, 0, 1), (1, 0, 0)) * fasteners.nut(4)
            assert overlap_volume(tray, nut) < 1.0


def test_tie_bolts_pass_through_plate_and_tie():
    for bx, by in el.TIE_BOLTS:
        tray = el.tray_left() if by > 0 else el.tray_right()
        pin = Pos(bx, by, el.PLATE_Z[0] - 1) * Cylinder(1.95, 12, align=AX)
        assert overlap_volume(tray, pin) < 1.0 and overlap_volume(el.tray_tie(), pin) < 1.0


def test_battery_sits_in_its_cradle():
    bx, by = el.BATT["center"]
    batt = Pos(bx, by, el.PLATE_Z[0] + el.BATT["base"]) * cots.board("battery_3s2p")
    cradle = el.batt_cradle()
    assert overlap_volume(cradle, batt) < 1.0
    assert cradle.distance_to(batt) < 0.7                       # touches the base, 0.6 mm side clearance


def test_rail_bolts_reach_the_slot():
    bolt = Pos(el.TRAY_BOLTS_X[0], el.RAIL_Y, el.PLATE_Z[0] - 1) * Cylinder(2.4, 9, align=AX)
    assert overlap_volume(el.tray_left(), bolt) < 1.0
