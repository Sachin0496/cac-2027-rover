#!/usr/bin/env python3
"""python tasks.py check | export | render | all"""
from __future__ import annotations

import argparse
import pathlib
import sys

QUICK = False
REUSE = False
TAG = None
VIEWS = None
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
BOM = HERE.parent / "hardware" / "bom_v2.csv"


def cmd_check(quick: bool = False) -> int:
    import calcs
    from assemble import rover
    from checks import massprops, runner
    from params import POSES
    asm = rover(35)
    problems, info = runner.run_checks(asm, full=not quick)
    m, b = info["mass"], info["balance"]
    print(f"items: {info['items']}   empty mass {m['mass_g'] / 1000:.2f} kg (model {(m['mass_g'] - massprops.WIRING_G) / 1000:.2f} + wiring allowance "
          f"{massprops.WIRING_G:.0f} g; limit {runner.MASS_LIMIT_G / 1000:.1f}, goal 7.5)   CG ({m['cg'][0]:.0f}, {m['cg'][1]:.0f}, {m['cg'][2]:.0f}) mm")
    if b["loaded"]:
        print(f"A7: front-axle share {m['front_share'] * 100:.1f} % empty, {b['loaded']['front_share'] * 100:.1f} % with {massprops.SAND_G / 1000:.1f} kg of sand "
              f"in the drum at the carry pose (limit {runner.FRONT_SHARE_LIMIT * 100:.0f} %)")
    if "rules" in info:
        r = info["rules"]
        print(f"A8/A9: stowed {r['stowed_mm'][0]} x {r['stowed_mm'][1]} x {r['stowed_mm'][2]} mm, E-stop head {r['estop_head_mm']:.0f} mm, "
              f"PZEM at z = {r['pzem_centre_z']} facing rear; camera at pan 0 sees {len(r['camera_pan0_sees'])} excavator parts, at pan 180 nothing")
    if not quick:
        print("A1: collisions at poses", [p for p in POSES if p != 35], "...")
        problems += runner.pose_collisions([p for p in POSES if p != 35])
        sweep = (-28, -20, -10, 0, 10, 20, 30, 35)
        print("A1: 2 mm clearance, moving vs static, at poses", sweep, "...")
        problems += runner.sweep_check(sweep)
    print("A10: load paths")
    for name, demand, capacity, sf, req, _ in calcs.run(verbose=False):
        print(f"   {'ok  ' if sf >= req else 'FAIL'} SF {sf:5.1f} (need {req:g})  {name}")
        if sf < req:
            problems.append(f"load path {name}: safety factor {sf:.2f} < {req:g}")
    for p in problems:
        print("FAIL:", p)
    print("ALL CHECKS PASS" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def cmd_export() -> int:
    from assemble import rover
    from export import export_all
    from checks.validity import freecad_step_check, stl_watertight
    info = export_all(rover(), OUT, BOM)
    print(f"exported to {OUT}; BOM total Rs {info['bom_total']:,.0f}")
    solids, invalid = freecad_step_check(OUT / "rover_v2.step")
    leaky = [p.name for p in sorted((OUT / "stl").glob("*.stl")) if not stl_watertight(p)]
    print(f"A2: STEP re-opens in FreeCAD with {solids} solids, {invalid} invalid; STLs not watertight: {', '.join(leaky) or 'none'}")
    for r in info["printed"]:
        print(f"  {r['part']:<18}x{r['qty']:<3} {r['x_mm']:>4} x {r['y_mm']:>3} x {r['z_mm']:>3} mm  {r['grams_each']:>4} g")
    print(f"printed total {sum(r['grams_total'] for r in info['printed']) / 1000:.2f} kg in {len(info['printed'])} part types")
    return 1 if invalid or leaky else 0


def cmd_render(pose: float | None = None, tag: str | None = None, views=None, reuse: bool = False) -> int:
    """Export the viewer assets (static rover once, arm parts at every design pose) and shoot the named views."""
    from export import export_viewer_assets
    from render import render
    if not reuse:
        export_viewer_assets(OUT)
    return render.main(tag=tag, views=views or render.VIEWS)


def cmd_docs() -> int:
    import docs_gen
    return docs_gen.main()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["check", "export", "render", "docs", "all"])
    ap.add_argument("--quick", action="store_true", help="check: pose 35 and calcs only")
    ap.add_argument("--reuse", action="store_true", help="render: reuse out/viewer instead of re-exporting the models")
    ap.add_argument("--tag", default=None, help="render: copy PNGs to docs/img/v2/<tag>_<view>.png (default: no prefix)")
    ap.add_argument("--views", default=None, help="render: comma separated view names")
    args = ap.parse_args()
    cmd = args.command
    global QUICK, REUSE, TAG, VIEWS
    QUICK, REUSE, TAG = args.quick, args.reuse, "" if args.tag is None else args.tag     # pictures always go to docs/img/v2/
    VIEWS = args.views.split(",") if args.views else None
    steps = {"check": [cmd_check], "export": [cmd_export], "render": [cmd_render],
             "docs": [cmd_docs], "all": [cmd_check, cmd_export, cmd_render, cmd_docs]}[cmd]
    steps = [(lambda f=f: f(QUICK)) if f is cmd_check else (lambda f=f: f(None, TAG, VIEWS, REUSE)) if f is cmd_render else f for f in steps]
    for step in steps:
        rc = step()
        if rc:
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
