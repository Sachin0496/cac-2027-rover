from math import cos, radians, sin

import pytest
from build123d import Axis, Cylinder, Pos, Rot

from checks.interference import overlap_volume
from checks.printfit import check_oriented, printed_mass_g
from lib.model import to_bed
from lib.shapes import cyl, hexprism
from modules import drum

FLIP = Axis((0, 0, 0), (cos(radians(9.5)), sin(radians(9.5)), 0))


def stack():
    """plate, A, B, A, B, plate along z 0..200 (the second plate is the first one turned over)."""
    parts = [drum.plate()]
    for i, clock in enumerate((0, 45, 0, 45)):
        parts.append(Pos(0, 0, 4 + 48 * i) * drum.ring(clock))
    parts.append(Pos(0, 0, 200) * drum.plate().rotate(FLIP, 180))
    return parts


def test_ring_is_a_valid_printable_solid():
    r = drum.ring(0)
    bb = r.bounding_box()
    assert r.is_valid and len(r.solids()) == 1
    assert bb.size.Z == pytest.approx(48, abs=1e-6)
    assert max(abs(bb.min.X), abs(bb.max.X), abs(bb.min.Y), abs(bb.max.Y)) <= 91.0   # raked teeth reach 90.7
    assert 70 < printed_mass_g(r) < 150
    assert check_oriented("ring", to_bed(r)) == []


def test_rings_a_and_b_are_the_same_shape_turned():
    a, b = drum.ring(0), drum.ring(45)
    assert a.is_valid and b.is_valid and len(a.solids()) == 1 and len(b.solids()) == 1
    assert a.volume == pytest.approx(b.volume, rel=1e-3)


def test_tie_rod_holes_are_open_in_every_ring():
    for clock in (0, 45):
        r = drum.ring(clock)
        for k in range(4):
            a = radians(9.5 + 90 * k)
            rod = Pos(84 * cos(a), 84 * sin(a), 0) * cyl(2.0, 48)
            assert overlap_volume(r, rod) < 1.0


def test_plate_hex_pocket_and_hole():
    p = drum.plate()
    assert p.is_valid and len(p.solids()) == 1
    head = hexprism(13.0, 5.3, 6.7, rot=9.5)                # M8 head sitting on the pocket floor
    assert overlap_volume(p, head) < 1.0
    assert overlap_volume(p, cyl(4.0, 13, -1)) < 1.0        # 8 mm bolt shank passes
    assert printed_mass_g(p) < 100 and check_oriented("plate", to_bed(p)) == []


def test_stacked_drum_is_200_long_with_no_collisions():
    parts = stack()
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            assert overlap_volume(parts[i], parts[j]) < 1.0, (i, j)
    zs = [p.bounding_box() for p in parts]
    assert min(b.min.Z for b in zs) == pytest.approx(0, abs=1e-6) and max(b.max.Z for b in zs) == pytest.approx(200, abs=1e-6)


def test_spacer_long():
    s = drum.spacer_long(6.2)
    assert s.bounding_box().size.Z == pytest.approx(6.2, abs=1e-6)
