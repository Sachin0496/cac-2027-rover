import csv

import pytest

from checks.validity import freecad_step_check, stl_watertight
from export import bom_rows, cut_plan, export_all, extra_rows, printed_table
from lib.model import Assembly
from modules import chassis, drive


@pytest.fixture(scope="module")
def asm():
    a = Assembly()
    chassis.build(a)
    drive.build_all(a)
    return a


@pytest.fixture(scope="module")
def exported(asm, tmp_path_factory):
    out = tmp_path_factory.mktemp("out")
    info = export_all(asm, out, out / "bom.csv")
    return out, info


def test_step_reopens_in_freecad_without_invalid_shapes(exported):
    out, _ = exported
    solids, invalid = freecad_step_check(out / "rover_v2.step")
    assert solids >= 100 and invalid == 0


def test_one_watertight_stl_per_printed_part_type(asm, exported):
    out, _ = exported
    types = {it.part for it in asm.items if it.kind == "printed"}
    files = {p.stem for p in (out / "stl").glob("*.stl")}
    assert files == types | {"fit_test_kit"}
    assert all(stl_watertight(out / "stl" / f"{t}.stl") for t in types | {"fit_test_kit"})


def test_glb_written(exported):
    out, _ = exported
    assert (out / "rover_v2.glb").stat().st_size > 10_000


def test_bom_total_matches_rows_and_has_no_unpriced_items(asm, exported):
    out, info = exported
    rows = bom_rows(asm) + extra_rows(asm)
    assert all(r["total_inr"] > 0 or r["price_basis"] == "have" for r in rows)
    assert info["bom_total"] == sum(r["total_inr"] for r in rows)
    body = list(csv.DictReader((out / "bom.csv").open()))
    assert body[-1]["item"].startswith("TOTAL")


def test_printed_table_quantities(asm):
    t = {r["part"]: r["qty"] for r in printed_table(asm)}
    assert t["wheel"] == 4 and t["axle_spacer_end"] == 8 and t["drv_mount"] == 4


def test_cut_plan_packs_the_extrusions_into_three_metre_bars():
    cuts = [402, 402, 260, 260, 259, 240, 212]
    bars = cut_plan(cuts)
    assert len(bars) == 3 and sorted(c for b in bars for c in b) == sorted(cuts)
    assert all(sum(b) + 3 * (len(b) - 1) <= 990 for b in bars)                 # 10 mm slack per bar
    assert len(cut_plan([600, 600])) == 2                      # two 600 mm pieces cannot share a 1 m bar
