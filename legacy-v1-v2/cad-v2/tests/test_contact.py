from build123d import Box, Pos

from checks.contact import contact_groups, floating_items, under_supported
from lib.model import Assembly, bought_item, printed_item


def asm_of(*pairs):
    a = Assembly()
    for i, (part, shape) in enumerate(pairs):
        maker = bought_item if part.startswith(("bolt_", "nut_", "tnut_")) else None
        if maker:
            a.add(bought_item(f"i{i}", part, "m", shape, Pos(0, 0, 0), "#000000", 1.0))
        else:
            a.add(printed_item(f"i{i}", part, "m", shape, Pos(0, 0, 0), "#000000"))
    return a


def test_touching_parts_form_one_group_and_a_far_part_floats():
    a = asm_of(("p", Box(10, 10, 10)), ("q", Pos(10, 0, 0) * Box(10, 10, 10)), ("r", Pos(60, 0, 0) * Box(10, 10, 10)))
    groups, links = contact_groups(a)
    assert [len(g) for g in groups] == [2, 1]
    assert floating_items(a) == ["i2"]


def test_small_gap_counts_as_contact_but_a_large_one_does_not():
    assert floating_items(asm_of(("p", Box(10, 10, 10)), ("q", Pos(10.3, 0, 0) * Box(10, 10, 10)))) == []
    assert floating_items(asm_of(("p", Box(10, 10, 10)), ("q", Pos(11.5, 0, 0) * Box(10, 10, 10)))) != []


def test_bolt_must_hold_two_parts():
    plate = Box(40, 40, 4)
    nut = Pos(0, 0, -4) * Box(8, 8, 3)                           # sits under the plate, touches it and the bolt
    bolt = Pos(0, 0, 4) * Box(4, 4, 8)                           # stands on the plate, passes into the nut region
    good = asm_of(("p", plate), ("nut_m4", nut), ("bolt_m4x8", Pos(0, 0, 0) * Box(4, 4, 10)))
    assert under_supported(good) == {}
    lonely = asm_of(("p", plate), ("bolt_m4x8", bolt))
    assert list(under_supported(lonely)) == ["i1"]
