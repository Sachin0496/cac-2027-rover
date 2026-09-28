# CAC 2027 Rover

Our entry for the Caterpillar Autonomy Challenge 2027 (Shaastra, IIT Madras): a small,
light lunar-construction rover with a rotating bucket drum that crosses an obstacle
field, digs sand, carries it and builds a berm — first by remote control, then
autonomously.

![Rover v1](docs/img/rover_carry.png)

- **Start here:** [CONTEXT.md](CONTEXT.md) — rules, scoring, strategy, design, budget, timeline, risks.
- **Build it:** [docs/v1-build-guide.md](docs/v1-build-guide.md) — why a drum, key numbers, cut/drill
  list, print list, hardware, assembly order, first tests, known issues.
- **Parts and budget:** [hardware/bom.csv](hardware/bom.csv) (≈ ₹22k) — update `purchase_status` as things arrive.

## CAD (free tools only)

| Open this | With |
|---|---|
| `cad/rover.scad` — full assembly, the editable master | OpenSCAD (`brew install --cask openscad@snapshot`) |
| `cad/rover_v1.FCStd` — the assembly for viewing and measuring | FreeCAD 1.1 (`brew install --cask freecad`) |
| `cad/rover_v1.step.zip` — the assembly for Onshape or any other CAD | anything that reads STEP |
| `cad/stl/*.stl` — every printed part, already oriented for printing | your slicer |

Change dimensions in `cad/params.scad`, then from `cad/`:

```
python3 check_interference.py   # collisions at four arm angles
python3 export.py               # STLs, printer fit, filament estimate, pictures
python3 export_freecad.py       # FreeCAD + STEP files
```

## Layout

```
cad/        OpenSCAD model (master), print layout, STLs, FreeCAD/STEP exports, check scripts
docs/       build guide and rendered pictures
hardware/   bill of materials
firmware/   ESP32 motor/sensor firmware (next)
ros2_ws/    ROS 2 Jazzy workspace (next)
```
