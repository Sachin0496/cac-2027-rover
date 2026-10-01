import pytest
from build123d import Cylinder, Pos, Rot

from checks.interference import overlap_volume
from checks.printfit import check_oriented, printed_mass_g
from lib.model import to_bed
from lib.shapes import AX
from modules import lift
from params import LIFT, SCREW_X, SCREW_Z

ORIENT = {"channel": None, "bearing_block": Rot(0, 90, 0), "carriage": None, "cradle_base": None, "cradle_cap": Rot(180, 0, 0)}


@pytest.mark.parametrize("name", list(ORIENT))
def test_part_is_valid_single_solid_and_printable(name):
    part = getattr(lift, name)()
    assert part.is_valid and len(part.solids()) == 1
    o = to_bed(ORIENT[name] * part if ORIENT[name] is not None else part)
    assert check_oriented(name, o) == []
    assert printed_mass_g(o) < 180


def screw(x0, x1, r=4.0):
    return Pos(x0, 0, SCREW_Z) * Rot(0, 90, 0) * Cylinder(r, x1 - x0, align=AX)


def test_screw_passes_both_blocks_and_the_carriage_bore():
    rear = Pos(LIFT["block_rear_x"][0], 0, 0) * lift.bearing_block()
    front = Pos(LIFT["block_front_x"][1], 0, 0) * Rot(0, 0, 180) * lift.bearing_block()
    s = screw(*SCREW_X)
    assert overlap_volume(rear, s) < 1.0 and overlap_volume(front, s) < 1.0
    assert overlap_volume(Pos(50, 0, 0) * lift.carriage(), s) < 1.0


def test_carriage_ear_takes_a_5mm_pin_at_pin_height():
    c = Pos(50, 0, 0) * lift.carriage()
    from params import CARRIAGE_PIN_Z
    pin = Pos(50, -12, CARRIAGE_PIN_Z) * Rot(-90, 0, 0) * Cylinder(2.5, 24, align=AX)
    assert overlap_volume(c, pin) < 1.0


def test_cradle_holds_the_motor_gearbox_and_clears_it():
    from lib import cots
    m = Pos(LIFT["motor_gear_face_x"], 0, SCREW_Z) * Rot(0, 0, -90) * cots.motor_johnson()
    assert overlap_volume(lift.cradle_base(), m) < 1.0 and overlap_volume(lift.cradle_cap(), m) < 1.0
