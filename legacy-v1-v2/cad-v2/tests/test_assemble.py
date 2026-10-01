import pytest

from assemble import rover
from checks import massprops
from checks.runner import FRONT_SHARE_LIMIT, MASS_LIMIT_G, run_checks


@pytest.fixture(scope="module")
def full():
    asm = rover(35)
    return asm, run_checks(asm, full=True)


def test_rover_has_every_module(full):
    asm, _ = full
    assert {i.module for i in asm.items} == {"chassis", "drive", "excavator", "electronics", "tower", "body"}
    assert len({i.id for i in asm.items}) == len(asm.items) > 400


def test_carry_pose_passes_every_single_assembly_check(full):
    _, (problems, info) = full
    assert problems == []
    assert info["rules"]["arrows"] == 3


def test_empty_mass_is_within_the_limit_with_the_wiring_allowance(full):
    _, (problems, info) = full
    m = info["mass"]["mass_g"]
    assert 6500 < m <= MASS_LIMIT_G
    assert m == pytest.approx(sum(i.mass() for i in full[0].items) + massprops.WIRING_G, rel=1e-9)


def test_front_axle_share_with_a_full_drum_is_within_the_limit(full):
    _, (problems, info) = full
    loaded = info["balance"]["loaded"]
    assert 0.6 < loaded["front_share"] <= FRONT_SHARE_LIMIT
    assert info["mass"]["front_share"] < loaded["front_share"]          # sand in the drum moves weight forward
    assert abs(info["mass"]["cg"][1]) < 15.0                             # lateral offset of the centre of gravity, mm
