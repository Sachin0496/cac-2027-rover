#!/usr/bin/env python3
"""Build rover_v1.FCStd and rover_v1.step (for FreeCAD, Onshape or any CAD).

Each assembly group is exported from OpenSCAD as a mesh in its assembled
position, then FreeCAD turns it into solids (flat faces merged) and saves the
lot. The OpenSCAD files stay the editable master; re-run this after changes.
Needs `openscad` on PATH and FreeCAD 1.x installed.

    python3 export_freecad.py
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
FREECADCMD = shutil.which("freecadcmd") or "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
LIFT = 35   # stowed / carrying pose

GROUPS = {  # object name: OpenSCAD call (all modules come from the files below)
    "frame_tubes": "rails();",
    "deck": "deck();",
    "wheels": "drivetrain(motors = false, clamps = false, wheels = true);",
    "drive_motors": "drivetrain(motors = true, clamps = false, wheels = false);",
    "drive_clamps": "drivetrain(motors = false, clamps = true, wheels = false);",
    "lift_and_drum": f"lift_assembly({LIFT});",
    "lift_actuator": f"actuator_assembly({LIFT});",
    "electronics_and_mast": "electronics_assembly();",
}

HEADER = """include <params.scad>
use <lib.scad>
use <frame.scad>
use <arm.scad>
use <actuator.scad>
use <electronics.scad>
$fn = 48;
"""

FREECAD_SCRIPT = r'''
import sys, FreeCAD, Mesh, Part, Import
names, stl_dir, fcstd, step = sys.argv[-4].split(","), sys.argv[-3], sys.argv[-2], sys.argv[-1]
doc = FreeCAD.newDocument("rover_v1")
objs = []
for n in names:
    mesh = Mesh.Mesh(f"{stl_dir}/{n}.stl")
    raw = Part.Shape()
    raw.makeShapeFromMesh(mesh.Topology, 0.05)
    solids = []
    for shell in raw.Shells:
        s = Part.Solid(shell)
        try:
            merged = s.removeSplitter()          # merge coplanar triangles into flat faces
            if merged.isValid():
                s = merged
        except Exception:
            pass
        if not s.isValid():
            try:
                s.fix(0.01, 0.01, 0.01)
            except Exception:
                pass
        if abs(s.Volume) < 1:                 # drop degenerate slivers from the mesh
            continue
        solids.append(s)
    obj = doc.addObject("Part::Feature", n)
    obj.Shape = Part.makeCompound(solids)
    objs.append(obj)
    print(f"{n}: {len(solids)} solids, {len(obj.Shape.Faces)} faces, valid={obj.Shape.isValid()}")
doc.recompute()
doc.saveAs(fcstd)
Import.export(objs, step)
'''


def main():
    env = dict(os.environ, OPENSCADPATH=str(HERE))   # lets the temp files include our .scad files
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        for name, call in GROUPS.items():
            scad = tmp / f"{name}.scad"
            scad.write_text(HEADER + call + "\n")
            res = subprocess.run(["openscad", "--backend=manifold", "--export-format=binstl",
                                  "-o", str(tmp / f"{name}.stl"), str(scad)],
                                 capture_output=True, text=True, env=env)
            if res.returncode != 0 or "WARNING: Can't open" in res.stderr:
                sys.exit(res.stderr)
            print("meshed", name)
        script = tmp / "build.py"
        script.write_text(FREECAD_SCRIPT)
        fcstd, step = HERE / "rover_v1.FCStd", HERE / "rover_v1.step"
        for f in (fcstd, step):
            f.unlink(missing_ok=True)
        res = subprocess.run([FREECADCMD, "-c",
                              f"import sys; sys.argv = ['x', {','.join(GROUPS)!r}, {str(tmp)!r}, "
                              f"{str(fcstd)!r}, {str(step)!r}]; exec(open({str(script)!r}).read())"],
                             capture_output=True, text=True)
        print("\n".join(l for l in res.stdout.splitlines() if "solids" in l))
        if not step.exists():
            sys.exit(res.stdout + res.stderr)
    for f in (fcstd, step):
        print(f"{f.name}: {f.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
