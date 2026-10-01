# CAC 2027 Rover

Our entry for the Caterpillar Autonomy Challenge 2027 (Shaastra, IIT Madras): a small, light lunar-construction rover with a rotating bucket drum that crosses an
obstacle field, digs sand, carries it and builds a berm, first by remote control and then autonomously.

Start with [`CONTEXT.md`](CONTEXT.md): rules, scoring, strategy, budget, timeline, risks and the 2026-10-01 design review (section 17).

## Repository layout

```
CONTEXT.md        project context, shared by everything below
legacy-v1-v2/     the finished CAD-first designs (v1 and v2): CAD, docs, bill of materials
proto/            (next) the bare, minimal prototype: new work goes here, not in legacy-v1-v2/
firmware/         (next) ESP32 motor / encoder / sensor firmware
ros2_ws/          (next) ROS 2 Jazzy workspace
```

`proto/`, `firmware/` and `ros2_ws/` do not exist yet. Nothing outside `legacy-v1-v2/` depends on it, and nothing in it depends on them.

## Prototype direction

The prototype is deliberately minimal: bare chassis and drive, drum and lift, electronics mounted open, **no hood, side covers or other casings**. Casing was part of
the v2 design (hood, tray cover, side covers, handle); it adds mass and print time and hides the wiring we still need to debug. Add it back only after the
prototype digs, carries and dumps reliably.

## legacy-v1-v2/

Everything built so far lives in one folder so new work cannot tangle with it. Paths inside it are unchanged relative to each other.

| What | Where |
|---|---|
| v2 build guide, print list, mass and load paths | [`legacy-v1-v2/docs/v2-build-guide.md`](legacy-v1-v2/docs/v2-build-guide.md) |
| v2 priced order list and BOM | [`legacy-v1-v2/docs/v2-order-list.md`](legacy-v1-v2/docs/v2-order-list.md), [`legacy-v1-v2/hardware/bom_v2.csv`](legacy-v1-v2/hardware/bom_v2.csv) |
| What changed in v2 and where it departs from the plan | [`legacy-v1-v2/docs/v2-changelog.md`](legacy-v1-v2/docs/v2-changelog.md) |
| v2 parametric CAD (build123d), checks, STLs | `legacy-v1-v2/cad-v2/` |
| v1 CAD (OpenSCAD), build guide, BOM | `legacy-v1-v2/cad/`, [`legacy-v1-v2/docs/v1-build-guide.md`](legacy-v1-v2/docs/v1-build-guide.md), `legacy-v1-v2/hardware/bom.csv` |

### v2 at a glance

Four-wheel skid steer, drum digger on a lift arm. Stowed 601 x 478 x 445 mm, empty 7.94 kg, 74 % of the loaded weight on the front axle, BOM about INR 24.7k
(cap 25,000). It is a parametric Python model with scripted checks for collisions, mass, balance, printing, load paths and the competition rules.

```
cd legacy-v1-v2/cad-v2
uv venv --python 3.12 .venv && source .venv/bin/activate && uv pip install -r requirements.txt
python tasks.py check    # about 15 minutes on a laptop; prints ALL CHECKS PASS
python tasks.py all      # + STEP/STL export (needs FreeCAD), BOM, viewer, pictures, docs
```

`legacy-v1-v2/cad-v2/params.py` holds every dimension. Pictures are in `legacy-v1-v2/docs/img/v2/`.

### Design review, 2026-10-01

Reviewed against the 2027 problem statement. Fixed: the BOM had no wheel encoders (two encoder motors added), the ESP32's Wi-Fi/Bluetooth must be switched
off for the comms inspection, the 5 V converter was under-rated, and the score estimate was about twice too optimistic. See `CONTEXT.md` section 17 for these and
the bench tests still to do (dig depth, camera view, hazard-sensor blind zones, stall currents).
