import pytest
from build123d import Pos, Rot

from checks.interference import overlap_volume
from checks.printfit import check_oriented, printed_mass_g
from lib.model import to_bed
from lib.shapes import cyl
from modules import arms
from params import ARM_LEN, LEVER_PIN_AT, LINK_LEN, LINK_W, PIVOT_Z

ORIENT = {"arm_drive": Rot(90, 0, 0), "arm_idler": Rot(90, 0, 0), "arm_motor_cap": Rot(180, 0, 0),
          "pivot_bracket": Rot(90, 0, 0), "clamp_block": Rot(90, 0, 0), "lever": Rot(90, 0, 0), "link": Rot(90, 0, 0)}


@pytest.mark.parametrize("name", list(ORIENT))
def test_part_is_valid_single_solid_and_printable(name):
    part = getattr(arms, name)()
    assert part.is_valid and len(part.solids()) == 1
    assert check_oriented(name, to_bed(ORIENT[name] * part)) == []


def test_arms_are_12_thick_and_the_right_length_and_light_enough():
    for name in ("arm_drive", "arm_idler"):
        bb = getattr(arms, name)().bounding_box()
        assert bb.min.Y == pytest.approx(106, abs=1e-6)
        assert bb.max.X - bb.min.X > ARM_LEN + 20
    assert printed_mass_g(arms.arm_idler()) < 100
    assert printed_mass_g(arms.arm_drive()) < 180


def test_pivot_bracket_takes_an_m8_pin_and_the_m5_bolts():
    b = arms.pivot_bracket()
    pin = Pos(0, 0, 0) * Rot(-90, 0, 0) * cyl(4.0, 30)                    # along +y from y = 0
    pin = Pos(0, 100, PIVOT_Z) * pin
    assert overlap_volume(b, pin) < 1.0
    for x in (-20, 20):
        assert overlap_volume(b, Pos(x, 140, 0) * cyl(2.5, 9, 135)) < 1.0


def test_lever_pin_position_and_link_length():
    lv = arms.lever()
    dx, dz = LEVER_PIN_AT[0] - 25.0, LEVER_PIN_AT[1] - 35.0
    pin = Pos(dx, -12, dz) * Rot(-90, 0, 0) * cyl(2.6, 24)
    assert overlap_volume(lv, pin) < 1.0                                  # Ø5.4 hole takes a 5 mm pin
    lk = arms.link().bounding_box()
    assert lk.max.X - lk.min.X == pytest.approx(LINK_LEN + LINK_W, abs=1e-6)  # pin centres 100 apart, round ends


def test_clamp_and_lever_blocks_take_the_2020_crossbar():
    from lib.profile2020 import extrusion
    bar = Rot(-90, 0, 0) * extrusion(60)
    bar = Pos(0, -30, 0) * bar                                            # along y, centred
    for part in (arms.clamp_block(), arms.lever()):
        assert overlap_volume(part, bar) < 1.0
