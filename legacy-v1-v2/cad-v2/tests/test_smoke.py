from build123d import Box, Cylinder, export_step


def test_build123d_roundtrip(tmp_path):
    p = Box(20, 20, 20) - Cylinder(5, 30)
    assert p.is_valid
    assert abs(p.volume - (8000 - 3.14159265 * 25 * 20)) < 1
    export_step(p, str(tmp_path / "t.step"))
    assert (tmp_path / "t.step").stat().st_size > 1000
