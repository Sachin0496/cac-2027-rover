import numpy as np
import pytest
from build123d import Box, Pos

from checks import rules
from lib.model import Assembly, printed_item
from modules import body, tower


def copy_with(asm, *extra):
    b = Assembly()
    for it in asm.items:
        b.add(it)
    for i, (shape, module) in enumerate(extra):
        b.add(printed_item(f"blocker{i}", "blocker", module, shape, Pos(0, 0, 0), "#ffffff"))
    return b


@pytest.fixture(scope="module")
def tower_asm():
    a = Assembly()
    tower.build(a)
    return a


@pytest.fixture(scope="module")
def body_asm():
    a = Assembly()
    body.build(a)
    return a


def test_tower_passes_pzem_estop_and_view_rules(tower_asm):
    assert rules.check_pzem(tower_asm)[0] == []
    assert rules.check_estop(tower_asm)[0] == []
    problems, info = rules.check_views(tower_asm)
    assert problems == [] and info["camera_pan0_sees"] == [] and info["camera_pan180_sees"] == []


def test_a_part_in_front_of_the_pzem_display_is_caught(tower_asm):
    blocker = Pos(tower.TX - 120.0, 0, 320.0) * Box(20, 60, 60)
    problems, _ = rules.check_pzem(copy_with(tower_asm, (blocker, "body")))
    assert any("PZEM display view" in p for p in problems)


@pytest.mark.parametrize("where", [(0, 0, 60), (-70, 0, 0), (0, 70, 0)])
def test_a_part_in_the_estop_approach_is_caught(tower_asm, where):
    c = np.array([tower.TX, tower.ESTOP_Y, tower.ESTOP_Z + 12.0]) + np.array(where)
    blocker = Pos(*c) * Box(30, 30, 30)
    problems, _ = rules.check_estop(copy_with(tower_asm, (blocker, "body")))
    assert any("E-stop approach" in p for p in problems)


def test_camera_may_see_the_excavator_but_nothing_else(tower_asm):
    cam = tower_asm.get("webcam").meta["sensor"]["origin"]
    ahead = Pos(cam[0] + 200.0, 0, cam[2]) * Box(20, 60, 40)
    assert rules.check_views(copy_with(tower_asm, (ahead, "excavator")))[0] == []
    assert any("pan 0" in p for p in rules.check_views(copy_with(tower_asm, (ahead, "body")))[0])
    behind = Pos(tower.TX - 200.0, 0, cam[2]) * Box(20, 60, 40)
    assert any("pan 180" in p for p in rules.check_views(copy_with(tower_asm, (behind, "excavator")))[0])


def test_rear_tof_cone_must_be_free(tower_asm):
    s = tower_asm.get("tof_rear").meta["sensor"]
    o, d = np.array(s["origin"]), np.array(s["dir"])
    blocker = Pos(*(o + d * 90.0)) * Box(30, 60, 30)
    assert any("tof_rear" in p for p in rules.check_views(copy_with(tower_asm, (blocker, "body")))[0])


def test_stowed_size_limit(tower_asm):
    assert rules.check_stowed(tower_asm)[0] == []
    long = Pos(0, 0, 300) * Box(1600, 10, 10)
    assert rules.check_stowed(copy_with(tower_asm, (long, "body")))[0]


def test_three_arrows_rest_on_the_hood(body_asm):
    assert rules.check_arrows(body_asm)[0] == []
    lifted = Assembly()
    for it in body_asm.items:
        if it.id == "arrow_len":
            it = printed_item(it.id, it.part, it.module, Pos(0, 0, 5) * it.local, Pos(0, 0, 0), it.color)
        lifted.add(it)
    assert any("arrow_len does not rest" in p for p in rules.check_arrows(lifted)[0])
