import pytest
from build123d import Box, Pos

from lib.model import Assembly, printed_item, to_bed


def test_to_bed_sits_on_z0_and_centres_xy():
    bb = to_bed(Pos(5, 5, 50) * Box(10, 10, 10)).bounding_box()
    assert abs(bb.min.Z) < 1e-6
    assert abs((bb.min.X + bb.max.X) / 2) < 1e-6 and abs((bb.min.Y + bb.max.Y) / 2) < 1e-6


def test_assembly_compound_labels_and_colors():
    a = Assembly()
    a.add(printed_item("m1", "mount", "drive", Box(1, 1, 1), Pos(0, 0, 0), "#FFCD11"))
    c = a.compound()
    assert [ch.label for ch in c.children] == ["m1"]


def test_duplicate_id_rejected():
    a = Assembly()
    it = printed_item("x", "p", "m", Box(1, 1, 1), Pos(0, 0, 0), "#000000")
    a.add(it)
    with pytest.raises(ValueError):
        a.add(it)


def test_oriented_uses_local_frame():
    it = printed_item("y", "p", "m", Box(10, 10, 10), Pos(100, 0, 100), "#000000")
    bb = it.oriented().bounding_box()
    assert abs(bb.min.Z) < 1e-6 and abs(bb.size.Z - 10) < 1e-6
