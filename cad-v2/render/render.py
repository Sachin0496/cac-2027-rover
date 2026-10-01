"""Render named views of the exported model with headless Chrome. `python tasks.py render`."""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "out"
IMG = HERE.parent.parent / "docs" / "img" / "v2"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SHOTS = {   # name -> viewer hash parameters (the six fixed views of spec 8.4, plus two extras)
    "front_left": "view=front_left&pose=35",
    "rear_right": "view=rear_right&pose=35",
    "side_dig": "view=side&pose=-25",
    "front": "view=front&pose=35",
    "top": "view=top&pose=35",
    "exploded": "view=front_left&pose=35&explode=1",
    "dig_iso": "view=front_left&pose=-25",
    "hood_off": "view=rear_right&pose=35&hood=0",
}
VIEWS = list(SHOTS)


def build_viewer() -> None:
    if not (HERE / "node_modules").exists():
        subprocess.run(["npm", "install", "--silent"], cwd=HERE, check=True)
    subprocess.run(["node", "build.mjs", str(OUT)], cwd=HERE, check=True)


def shoot(name: str, dest: pathlib.Path, size=(1600, 1000), scale=2) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"file://{OUT / 'rover_v2_viewer.html'}#shot&{SHOTS[name]}"
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", f"--window-size={size[0]},{size[1]}",
                    f"--force-device-scale-factor={scale}", "--virtual-time-budget=25000",
                    "--run-all-compositor-stages-before-draw", f"--screenshot={dest}", url],
                   check=True, capture_output=True, timeout=600)


def main(tag: str | None = None, views=VIEWS, suffix: str = "") -> int:
    build_viewer()
    for v in views:
        shoot(v, OUT / "renders" / f"{v}{suffix}.png")
        if tag is not None:
            IMG.mkdir(parents=True, exist_ok=True)
            shutil.copy(OUT / "renders" / f"{v}{suffix}.png", IMG / (f"{tag}_{v}{suffix}.png" if tag else f"{v}{suffix}.png"))
        print("rendered", v)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
