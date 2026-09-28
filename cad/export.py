#!/usr/bin/env python3
"""Export every printed part to cad/stl/, check it fits the printer, estimate
filament, and render assembly pictures to docs/img/. Needs `openscad` on PATH.

    python3 export.py            # parts + pictures
    python3 export.py --parts    # parts only
"""
import pathlib
import re
import struct
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
STL = HERE / "stl"
IMG = HERE.parent / "docs" / "img"
BED = (210, 210, 240)          # usable volume of a 220 × 220 × 250 printer
PETG = 1.27                    # g/cm³
FILL = 0.75                    # printed mass vs solid, at 3–4 walls + 25 % infill

VIEWS = {   # name: (lift angle, camera, projection)
    "rover_carry": (35, "0,0,0,62,0,35,0", "p"),
    "rover_dig": (-20, "0,0,0,65,0,210,0", "p"),
    "side_dig": (-20, "0,0,0,90,0,0,0", "o"),
    "front": (35, "0,0,0,90,0,90,0", "o"),
}


def openscad(*args):
    res = subprocess.run(["openscad", "--backend=manifold", *args], capture_output=True, text=True)
    if res.returncode != 0 or "ERROR" in res.stderr:
        sys.exit(res.stderr)
    return res.stderr


def stl_stats(path):
    data = path.read_bytes()
    n = struct.unpack("<I", data[80:84])[0]
    vol, lo, hi = 0.0, [1e9] * 3, [-1e9] * 3
    for i in range(n):
        v = struct.unpack("<12f", data[84 + i * 50: 84 + i * 50 + 48])[3:]
        a, b, c = v[0:3], v[3:6], v[6:9]
        for p in (a, b, c):
            for k in range(3):
                lo[k], hi[k] = min(lo[k], p[k]), max(hi[k], p[k])
        vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6
    return vol / 1000, lo, hi


def export_parts():
    STL.mkdir(exist_ok=True)
    table = re.findall(r'\["(\w+)", (\d+)\]', (HERE / "print.scad").read_text())
    total_g, problems = 0.0, []
    print(f"{'part':<20}{'qty':>4}{'size (mm)':>22}{'g each':>9}")
    for name, qty in table:
        out = STL / f"{name}.stl"
        openscad("--export-format=binstl", "-D", f'part="{name}"', "-o", str(out), str(HERE / "print.scad"))
        vol, lo, hi = stl_stats(out)
        size = [hi[k] - lo[k] for k in range(3)]
        grams = vol * PETG * FILL
        total_g += grams * int(qty)
        print(f"{name:<20}{qty:>4}{' × '.join(f'{s:.0f}' for s in size):>22}{grams:>9.0f}")
        if sorted(size[:2]) > sorted(BED[:2]) or size[2] > BED[2]:
            problems.append(f"{name} ({size[0]:.0f} × {size[1]:.0f} × {size[2]:.0f}) does not fit the bed")
        if abs(lo[2]) > 0.01:
            problems.append(f"{name} is not sitting on the bed (min z = {lo[2]:.2f})")
    names = {name for name, _ in table}
    for old in STL.glob("*.stl"):
        if old.stem not in names:
            old.unlink()
            print("removed stale", old.name)
    print(f"\nFilament ≈ {total_g / 1000:.2f} kg PETG (all parts, estimate)")
    for p in problems:
        print("PROBLEM:", p)
    return not problems


def render_views():
    IMG.mkdir(parents=True, exist_ok=True)
    for name, (lift, cam, proj) in VIEWS.items():
        openscad("--render", "-D", f"lift={lift}", "--imgsize=1600,1100", "--viewall", "--autocenter",
                 f"--camera={cam}", f"--projection={proj}", "--colorscheme=Tomorrow",
                 "-o", str(IMG / f"{name}.png"), str(HERE / "rover.scad"))
        print("rendered", name)


if __name__ == "__main__":
    ok = export_parts()
    if "--parts" not in sys.argv:
        render_views()
    sys.exit(0 if ok else 1)
