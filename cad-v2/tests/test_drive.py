import pytest

from checks.interference import find_collisions
from checks.printfit import check_oriented
from lib.model import Assembly
from params import AXLE_X_FRONT, AXLE_X_REAR
from modules import chassis, drive


def full():
    a = Assembly()
    chassis.build(a)
    drive.build_all(a)
    return a


@pytest.fixture(scope="module")
def asm():
    return full()


def test_no_collisions(asm):
    assert find_collisions(asm) == []


def test_four_wheels_reach_the_ground_and_are_174_tall(asm):
    wheels = [i for i in asm.items if i.part == "wheel"]
    assert len(wheels) == 4
    for it in wheels:
        bb = it.shape.bounding_box()
        assert abs(bb.min.Z) < 0.6 and abs(bb.size.Z - 174) < 1.0


def test_wheel_track_and_wheelbase(asm):
    def mid(it, axis):
        bb = it.shape.bounding_box()
        return round((getattr(bb.min, axis) + getattr(bb.max, axis)) / 2)
    wheels = [i for i in asm.items if i.part == "wheel"]
    assert sorted(mid(i, "Y") for i in wheels) == [-190, -190, 190, 190]
    assert sorted(mid(i, "X") for i in wheels) == [AXLE_X_REAR, AXLE_X_REAR, AXLE_X_FRONT, AXLE_X_FRONT]


def test_the_four_modules_share_one_stl_shape(asm):
    for part in ("drv_mount", "drv_cradle_roof", "drv_cradle_cap", "wheel", "wheel_cap"):
        vols = [round(i.local.volume, 3) for i in asm.items if i.part == part]
        assert len(vols) == 4 and len(set(vols)) == 1, part


def test_printed_parts_pass_printfit(asm):
    seen = set()
    for it in asm.items:
        if it.kind == "printed" and it.part not in seen:
            seen.add(it.part)
            assert check_oriented(it.part, it.oriented()) == [], it.part


def test_gearbox_ground_clearance(asm):
    for it in asm.items:
        if it.part in ("motor", "drv_mount"):
            assert it.shape.bounding_box().min.Z >= 60 - 1e-6, it.id


def test_hardware_counts(asm):
    skus = [i.meta.get("sku") for i in asm.items]
    assert skus.count("M8x75 hex") == 4 and skus.count("M4x14 socket") == 16 and skus.count("bearing_608") == 8
