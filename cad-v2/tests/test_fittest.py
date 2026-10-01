from checks.printfit import check_oriented
from modules import fittest


def test_kit_is_small_valid_and_printable():
    k = fittest.build()
    bb = k.bounding_box()
    assert k.is_valid and len(k.solids()) == 1
    assert bb.size.X <= 210 and bb.size.Y <= 210 and bb.size.Z <= 40
    assert check_oriented("fit_test_kit", k) == []
    assert k.volume / 1000 * 1.27 * 0.75 < 45                 # grams: about an hour


def test_kit_has_all_feature_sets():
    assert len(fittest.FEATURES["bearing_seats"]) == 3
    assert len(fittest.FEATURES["nut_traps"]) == 6            # M4 and M8 x 3 clearances
    assert len(fittest.FEATURES["holes"]) == 6                # M4 and M5 x 3 clearances
