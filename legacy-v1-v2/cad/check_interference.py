#!/usr/bin/env python3
"""Check the rover model for parts that collide.

Intersects each pair of part groups at several arm angles and reports the
overlapping volume. Faces that only touch (a box sitting on the deck) give
~0 mm³; anything above TOUCH_MM3 is a real clash. Needs `openscad` on PATH.

    python3 check_interference.py
"""
import itertools
import pathlib
import struct
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
GROUPS = ["frame", "lift", "actuator", "electronics"]
POSES = [-25, -20, 0, 35]          # arm_press, arm_down, level, arm_up
TOUCH_MM3 = 5.0


def stl_volume_bbox(path):
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
    return abs(vol), lo, hi


def overlap(ga, gb, angle, out):
    cmd = ["openscad", "--backend=manifold", "--export-format=binstl", "-o", str(out),
           "-D", f'pair_a="{ga}"', "-D", f'pair_b="{gb}"', "-D", f"a={angle}",
           str(HERE / "check.scad")]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if "top level object is empty" in res.stderr or not out.exists():
        return 0.0, None
    if res.returncode != 0:
        sys.exit(f"openscad failed for {ga}/{gb} at {angle}°:\n{res.stderr}")
    vol, lo, hi = stl_volume_bbox(out)
    return vol, (lo, hi)


def main():
    clashes = 0
    with tempfile.TemporaryDirectory() as tmp:
        for ga, gb in itertools.combinations(GROUPS, 2):
            for angle in POSES:
                out = pathlib.Path(tmp) / f"{ga}-{gb}-{angle}.stl"
                vol, box = overlap(ga, gb, angle, out)
                if vol > TOUCH_MM3:
                    clashes += 1
                    lo, hi = box
                    print(f"CLASH {ga:>11} × {gb:<11} at {angle:>4}°: {vol:8.0f} mm³  "
                          f"x {lo[0]:.0f}..{hi[0]:.0f}  y {lo[1]:.0f}..{hi[1]:.0f}  z {lo[2]:.0f}..{hi[2]:.0f}")
                else:
                    print(f"ok    {ga:>11} × {gb:<11} at {angle:>4}°")
    print("\nNo collisions." if clashes == 0 else f"\n{clashes} collision(s) found.")
    return 1 if clashes else 0


if __name__ == "__main__":
    sys.exit(main())
