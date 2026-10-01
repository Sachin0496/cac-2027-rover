import calcs


def test_every_load_path_meets_its_required_safety_factor():
    rows = calcs.run(verbose=False)
    assert len(rows) >= 11
    for name, demand, capacity, sf, req, inputs in rows:
        assert sf >= req, f"{name}: SF {sf:.2f} < {req}"


def test_tray_plate_deflects_less_than_1_mm_at_three_times_the_load():
    name, defl, limit, inputs = calcs.tray_plate()
    assert defl <= 1.0 and limit == 1.0
    assert inputs["span mm"] == 98


def test_lift_screw_self_locks_with_brass_on_steel():
    name, mu_needed, mu_have, _ = calcs.screw_self_locking()
    assert mu_needed < mu_have / 2
