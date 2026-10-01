import pytest
from build123d import Box, Pos

from checks.interference import find_collisions, min_clearance
from lib.model import Assembly, printed_item


def asm_of(*shapes):
    a = Assembly()
    for i, s in enumerate(shapes):
        a.add(printed_item(f"b{i}", "p", "m", s, Pos(0, 0, 0), "#000000"))
    return a


def test_overlap_is_found():
    hits = find_collisions(asm_of(Box(10, 10, 10), Pos(5, 0, 0) * Box(10, 10, 10)))
    assert len(hits) == 1 and hits[0][2] == pytest.approx(500.0, rel=1e-3)


def test_touching_and_separate_boxes_are_fine():
    assert find_collisions(asm_of(Box(10, 10, 10), Pos(10, 0, 0) * Box(10, 10, 10))) == []
    assert find_collisions(asm_of(Box(10, 10, 10), Pos(50, 0, 0) * Box(10, 10, 10))) == []


def test_tiny_overlap_below_threshold_ignored():
    assert find_collisions(asm_of(Box(10, 10, 10), Pos(9.99, 0, 0) * Box(10, 10, 10))) == []


def test_min_clearance():
    a = asm_of(Box(10, 10, 10), Pos(14, 0, 0) * Box(10, 10, 10))
    assert min_clearance(a, ["b0"], ["b1"]) == pytest.approx(4.0, abs=1e-6)
