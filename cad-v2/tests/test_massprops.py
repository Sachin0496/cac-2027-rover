import pytest
from build123d import Box, Pos

from checks.massprops import mass_properties
from params import AXLE_X_FRONT, AXLE_X_REAR
from lib.model import Assembly, printed_item


def one(x, mass):
    a = Assembly()
    it = a.add(printed_item("f", "p", "m", Pos(x, 0, 50) * Box(10, 10, 10), Pos(0, 0, 0), "#000000"))
    it.mass_g = mass
    return a


def test_cg_and_front_share():
    r = mass_properties(one(AXLE_X_FRONT, 100.0))
    assert r["mass_g"] == pytest.approx(100.0)
    assert r["cg"][0] == pytest.approx(AXLE_X_FRONT, abs=1e-6)
    assert r["front_share"] == pytest.approx(1.0)


def test_sand_moves_the_balance():
    r = mass_properties(one(AXLE_X_FRONT, 100.0), sand_g=100.0, sand_at=(AXLE_X_REAR, 0, 50))
    assert r["front_share"] == pytest.approx(0.5)
    assert r["mass_g"] == pytest.approx(200.0)


def test_printed_mass_falls_back_to_volume():
    a = Assembly(); a.add(printed_item("f", "p", "m", Box(10, 10, 10), Pos(0, 0, 0), "#000000"))
    assert mass_properties(a)["mass_g"] == pytest.approx(0.9525, abs=1e-3)
