"""Exports: named+coloured STEP, print-orientation STLs, GLB for the viewer, BOM and printed-parts table."""
from __future__ import annotations

import csv
import math
import pathlib
from collections import OrderedDict

from build123d import export_gltf, export_step, export_stl

from checks.printfit import printed_mass_g
from lib.model import Assembly
from lib.prices import PRICES, STOCK_PER_M

HERE = pathlib.Path(__file__).resolve().parent
KERF_MM = 3.0


def printed_types(asm: Assembly):
    """(part, first item, quantity) for every printed part type, in first-seen order."""
    out: "OrderedDict[str, list]" = OrderedDict()
    for it in asm.items:
        if it.kind == "printed":
            out.setdefault(it.part, [it, 0])[1] += 1
    return [(k, v[0], v[1]) for k, v in out.items()]


def printed_table(asm: Assembly) -> list[dict]:
    rows = []
    for part, it, qty in printed_types(asm):
        s = it.oriented()
        bb = s.bounding_box()
        rows.append({"part": part, "qty": qty, "x_mm": round(bb.size.X), "y_mm": round(bb.size.Y), "z_mm": round(bb.size.Z),
                     "grams_each": round(printed_mass_g(s)), "grams_total": round(printed_mass_g(s) * qty)})
    return rows


def cut_plan(cuts, stock: float = 1000.0, kerf: float = KERF_MM, slack: float = 10.0) -> list[list[float]]:
    """First-fit-decreasing packing of the extrusion cuts into stock lengths, kerf between cuts, and `slack` mm
    left over per bar (stock bars are not exactly 1 m and a hacksaw wanders)."""
    bars: list[list[float]] = []
    for c in sorted(cuts, reverse=True):
        for bar in bars:
            if sum(bar) + kerf * (len(bar) - 1) + kerf + c <= stock - slack + 1e-9:
                bar.append(c)
                break
        else:
            bars.append([c])
    return bars


def bom_rows(asm: Assembly) -> list[dict]:
    """Purchased items grouped by SKU (with the modules that use them); extrusions bought as 1 m lengths and cut."""
    counts: "OrderedDict[str, int]" = OrderedDict()
    used: dict[str, list[str]] = {}
    for it in asm.items:
        if it.kind == "purchased":
            sku = it.meta["sku"]
            counts[sku] = counts.get(sku, 0) + 1
            if it.module not in used.setdefault(sku, []):
                used[sku].append(it.module)
    rows = []
    for sku, qty in counts.items():
        price, basis, source, note = PRICES[sku]
        rows.append({"item": sku, "qty": qty, "unit_price_inr": price, "total_inr": round(price * qty), "price_basis": basis,
                     "source": source, "purchase_status": "have" if basis == "have" else "to buy", "used_in": "/".join(used[sku]), "notes": note})
    cuts = [it.meta["cut_mm"] for it in asm.items if it.kind == "stock"]
    if cuts:
        bars = cut_plan(cuts)
        price, basis, source, note = STOCK_PER_M["2020 T-slot"]
        plan = "; ".join("+".join(str(int(c)) for c in bar) for bar in bars)
        rows.insert(0, {"item": "2020 T-slot, 1 m lengths", "qty": len(bars), "unit_price_inr": price, "total_inr": price * len(bars),
                        "price_basis": basis, "source": source, "purchase_status": "to buy", "used_in": "chassis/excavator/tower",
                        "notes": f"{note}; one bar each: {plan}"})
    return rows


def extra_rows(asm: Assembly) -> list[dict]:
    """Lines that are not modelled: filament for the printed total, wiring, practice sand, spares."""
    from lib.prices import EXTRA_LINES, FILAMENT_PER_KG
    printed_g = sum(r["grams_total"] for r in printed_table(asm))
    kg = max(1, math.ceil(printed_g * 1.10 / 1000.0))
    price, basis, source, note = FILAMENT_PER_KG
    rows = [{"item": "PETG filament, 1 kg spools", "qty": kg, "unit_price_inr": price, "total_inr": price * kg, "price_basis": basis,
             "source": source, "purchase_status": "to buy", "used_in": "all printed parts", "notes": f"printed total {printed_g / 1000:.2f} kg; {note}"}]
    for item, qty, unit, basis, source, note in EXTRA_LINES:
        rows.append({"item": item, "qty": qty, "unit_price_inr": unit, "total_inr": unit * qty, "price_basis": basis, "source": source,
                     "purchase_status": "to buy", "used_in": "", "notes": note})
    return rows


def write_bom(asm: Assembly, path) -> float:
    rows = bom_rows(asm) + extra_rows(asm)
    total = sum(r["total_inr"] for r in rows)
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
        w.writerow({"item": "TOTAL (excludes the Raspberry Pi 5, which the team owns, the dual-band router, laptops, printer and travel)", "total_inr": total})
    return total


def export_all(asm: Assembly, out, bom_path=None) -> dict:
    out = pathlib.Path(out)
    (out / "stl").mkdir(parents=True, exist_ok=True)
    comp = asm.compound()
    export_step(comp, str(out / "rover_v2.step"))
    keep = set()
    for part, it, _ in printed_types(asm):
        export_stl(it.oriented(), str(out / "stl" / f"{part}.stl"), tolerance=0.05, angular_tolerance=0.1)
        keep.add(f"{part}.stl")
    from modules import fittest
    export_stl(fittest.build(), str(out / "stl" / "fit_test_kit.stl"), tolerance=0.05, angular_tolerance=0.1)
    keep.add("fit_test_kit.stl")
    for old in (out / "stl").glob("*.stl"):
        if old.name not in keep and not old.name.startswith("_"):
            old.unlink()
    export_gltf(comp, str(out / "rover_v2.glb"), binary=True, linear_deflection=0.08, angular_deflection=0.12)
    total = write_bom(asm, bom_path) if bom_path else None
    return {"bom_total": total, "printed": printed_table(asm)}


def _compound(items, label: str):
    """Compound of the given items, each child labelled with its id and coloured (for glTF node names and materials)."""
    from build123d import Color, Compound, Location
    kids = []
    for it in items:
        sh = it.shape.moved(Location())
        sh.label = it.id
        sh.color = Color(it.color)
        kids.append(sh)
    return Compound(label=label, children=kids)


def export_viewer_assets(out, poses=None) -> dict:
    """Files for the interactive viewer: the static rover once, the arm-driven parts once per pose, and a table of
    what every item is (module, part, kind) so the viewer can explode and hide by group. Returns the manifest."""
    import json
    from assemble import rover
    from params import POSES
    poses = tuple(poses or POSES)
    out = pathlib.Path(out) / "viewer"
    out.mkdir(parents=True, exist_ok=True)
    carry = max(poses)
    base = rover(carry)
    moving = ("arm", "carriage")
    kw = dict(binary=True, linear_deflection=0.08, angular_deflection=0.12)
    export_gltf(_compound([i for i in base.items if i.moving not in moving], "static"), str(out / "static.glb"), **kw)
    files = {"static": "static.glb", "arm": {}}
    for pose in poses:
        asm = base if pose == carry else rover(pose)
        export_gltf(_compound([i for i in asm.items if i.moving in moving], f"arm_{pose:g}"), str(out / f"arm_{pose:g}.glb"), **kw)
        files["arm"][f"{pose:g}"] = f"arm_{pose:g}.glb"
    parts = {}
    for asm in (base,):
        for i in asm.items:
            parts[i.id] = {"m": i.module, "p": i.part, "k": i.kind, "mv": i.moving or ""}
    manifest = {"poses": [f"{p:g}" for p in poses], "files": files, "parts": parts}
    (out / "manifest.json").write_text(json.dumps(manifest))
    return manifest


def export_glb(asm: Assembly, out) -> pathlib.Path:
    """GLB only (fast): used for renders of other arm poses."""
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    export_gltf(asm.compound(), str(out / "rover_v2.glb"), binary=True, linear_deflection=0.08, angular_deflection=0.12)
    return out / "rover_v2.glb"
