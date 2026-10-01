import math

import pytest

from checks.interference import find_collisions, overlap_volume
from checks.printfit import check_oriented, printed_mass_g
from lib.model import Assembly, to_bed
from modules import tower


@pytest.fixture(scope="module")
def asm():
    a = Assembly()
    tower.build(a)
    return a


def test_every_printed_part_is_valid_printable_and_light(asm):
    printed = [i for i in asm.items if i.kind == "printed"]
    assert len(printed) >= 7
    for it in printed:
        assert it.shape.is_valid and len(it.shape.solids()) == 1, it.id
        assert check_oriented(it.id, it.oriented()) == [], it.id
        assert printed_mass_g(it.oriented()) < 180, it.id


def test_tower_alone_has_no_collisions(asm):
    assert find_collisions(asm) == []


def test_post_is_a_240_mm_2020_on_the_rear_cross_member(asm):
    bb = asm.get("tower_post").shape.bounding_box()
    assert bb.max.Z - bb.min.Z == pytest.approx(240.0, abs=1e-3)
    assert (bb.min.X + bb.max.X) / 2 == pytest.approx(tower.TX, abs=1e-6)
    assert bb.min.Z == pytest.approx(141.0)


def test_estop_head_is_60_mm_and_sits_on_the_pedestal(asm):
    head = asm.get("estop_head").shape.bounding_box()
    assert head.max.X - head.min.X == pytest.approx(60.0, abs=0.1)
    assert head.min.Z <= tower.ESTOP_Z + 0.01
    assert overlap_volume(asm.get("estop_body").shape, asm.get("estop_pedestal").shape) < 1.0     # body fits the bore
    assert asm.get("estop_pedestal").shape.bounding_box().max.Z == pytest.approx(tower.ESTOP_Z, abs=0.01)


def test_pzem_is_high_and_faces_rearward(asm):
    bb = asm.get("pzem").shape.bounding_box()
    assert (bb.min.Z + bb.max.Z) / 2 >= 250.0
    assert bb.max.X < tower.TX - tower.COL / 2                  # the whole module is behind the collar


def test_rear_tof_looks_20_degrees_below_the_rear_horizontal(asm):
    s = asm.get("tof_rear").meta["sensor"]
    dx, dy, dz = s["dir"]
    assert dx < 0 and math.degrees(math.asin(-dz)) == pytest.approx(tower.TOF_TILT, abs=1e-6)


def test_camera_is_the_only_thing_that_pans(asm):
    assert sorted(i.id for i in asm.items if i.moving == "pan") == ["camera_mount", "servo", "webcam"]
