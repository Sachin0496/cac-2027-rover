"""A2: every part is a valid closed solid; STEP re-opens in FreeCAD; STLs are watertight."""
from __future__ import annotations

import pathlib
import re
import subprocess

import trimesh

FREECADCMD = "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
FC_SCRIPT = pathlib.Path(__file__).with_name("fc_check.py")


def check_valid(asm) -> list[str]:
    problems = []
    for it in asm.items:
        if not it.shape.is_valid:
            problems.append(f"{it.id}: shape is not a valid solid")
        if it.shape.volume <= 0:
            problems.append(f"{it.id}: non-positive volume")
        if it.local is not None and not it.local.is_valid:
            problems.append(f"{it.id}: local shape is not valid")
    return problems


def stl_watertight(path) -> bool:
    return bool(trimesh.load(str(path), force="mesh").is_watertight)


def freecad_step_check(step) -> tuple[int, int]:
    """(solids, invalid) after importing the STEP into FreeCAD headless."""
    res = subprocess.run([FREECADCMD, str(FC_SCRIPT), str(step)], capture_output=True, text=True, timeout=600)
    m = re.search(r"FC_RESULT solids=(\d+) invalid=(\d+)", res.stdout + res.stderr)
    if not m:
        raise RuntimeError("FreeCAD check produced no result:\n" + res.stdout[-800:] + res.stderr[-800:])
    return int(m.group(1)), int(m.group(2))
