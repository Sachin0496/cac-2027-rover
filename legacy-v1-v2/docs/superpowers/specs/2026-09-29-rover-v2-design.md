# CAC 2027 rover v2 — design specification

Date: 2026-09-29 · Branch: `v2` · Status: approved in chat ("do it") and built through drop 3 (tags `v2-drop1` to `v2-drop3`). Where this document and the model disagree, the model wins; §16 is the as-built record and `docs/v2-changelog.md` lists every departure.

## 1. Purpose

Rover v1 (`cad/`, OpenSCAD) is a four-wheel skid-steer rover with a rotating bucket drum on a lift arm, for the Caterpillar Autonomy Challenge (CAC) 2027. v2 keeps that concept and re-engineers everything around it so that the machine

1. looks like a finished product, not a prototype;
2. can be built by students with a college 3D printer and hand tools, without drilling metal;
3. is verified by scripts (collisions, print fit, mass, balance, rules, load paths) instead of by eye.

The mission, rules, strategy, electronics and software plan in `CONTEXT.md` do not change.

## 2. Scope

**In scope:** every printed part; the mounting of every purchased part; the check suite; exports (STEP, STL, glTF, PNG renders, interactive viewer); BOM v2 and order list; build guide v2; v1→v2 change log; an update to `CONTEXT.md`.

**Out of scope:** firmware, ROS 2 and any software; wiring diagrams (only the physical mounting of electronics); URDF or simulation; suspension or tracks; a different motor family; finite-element analysis (hand calculations only); Blender renders; pushing to GitHub (only when the user says so). v1 stays untouched in `cad/`.

## 3. v1 baseline (measured from the repo)

| Fact | v1 |
|---|---|
| Printed part types (`cad/print.scad`) | 30 (the build guide says 29) |
| Printed mass (v1 `export.py` formula) | 2.57 kg |
| Heaviest single print | drum body, 490 g, about 20 h (≈ 25 g/h) |
| Metal to cut and drill | 4 tube lengths, about 30 holes, plus a cut plywood deck |
| Heat-set inserts | about 30 |
| Lift | 9 printed pieces plus an M8 rod with a printed thread |
| Wheel support | on the 6 mm gearbox shafts; outboard bearings optional |
| Front-axle share with a full drum | 80 % |
| Mass on the same accounting as v2 (§9.3) | about 7.0 kg (v1's own table says 7.5 kg: it double-counts the actuator clamp and uses 230 g wheels against 179 g in `export.py`) |
| STEP / FreeCAD | mesh-derived; the drum reports "invalid" in FreeCAD |
| Collision check | part groups, 4 arm poses, mesh based |
| Renders | flat-shaded OpenSCAD |

## 4. Acceptance criteria

"Flawless" means every row below passes at every drop (§11). Rows A1–A11 are enforced by scripts; A12 is a reviewed checklist.

| ID | Criterion | Requirement | Enforced by |
|---|---|---|---|
| A1 | Collisions | No two solids overlap by more than 1 mm³ at arm poses −25°, −20°, 0°, +20°, +35°. Every moving/static pair has at least 2 mm clearance over the whole −25…+35° sweep in 5° steps, except declared running fits (listed in `checks/interference.py` with their designed gap, minimum 0.4 mm). Mating features are modelled with clearance, so there is no allow-list for overlaps. | `checks/interference.py` |
| A2 | Valid solids | Every part is a valid closed solid; the exported STEP re-opens in FreeCAD 1.1 with 0 invalid shapes; every STL is watertight. | `checks/validity.py` |
| A3 | Print fit | Every printed part fits 210 × 210 × 240 mm (usable volume of a 220 × 220 × 250 printer) in its stated print orientation; every downward-facing surface steeper than 45° from vertical (outward normal with n_z below −0.707) either lies on the bed (z under 0.2 mm) or is a bridge whose smallest width is 8 mm or less; any other patch fails. So: no supports anywhere. | `checks/printfit.py` |
| A4 | Print effort | No single print above 180 g (about 7 h at v1's rate; v1's drum body is 490 g). Printed total is reported. | `checks/printfit.py` |
| A5 | Build effort | 0 drilled or tapped holes in metal; 0 heat-set inserts; the only metal cuts are four M4 tie rods to length (hacksaw). Extrusions are cut to length by the vendor (or by hacksaw, ±1 mm is fine). | BOM generator |
| A6 | Mass | Empty mass at most 8.0 kg (limit); goal 7.5 kg. Budget in §9.3. | `checks/massprops.py` |
| A7 | Balance | Front-axle share with a full drum (2.1 kg sand in the drum) at most 75 % (v1: 80 %); expected about 72 %. | `checks/massprops.py` |
| A8 | Rules | Stowed size at the carry pose at most 1500 × 750 × 750 mm; E-stop head at least 40 mm, with a clear approach (100 mm radius) from above, behind and both sides; energy-meter display facing within ±30° of rearward, centre at least 250 mm above ground; three arrow marks on upward-facing surfaces. | `checks/rules.py` |
| A9 | Sensor views | Camera cone (±35° horizontal, ±25° vertical) free of the rover's own parts at pan 0° and 180°; each ToF cone (27° full angle) free at the carry pose. | `checks/rules.py` |
| A10 | Load paths | Safety factor at least 2 at 3× the static load on: wheel housing and bolts, axle, pivot bracket, both arms, lift link, drum tie rods, tray plate (deflection ≤ 1 mm). Inputs and formulas are printed in the build guide. | `calcs.py` |
| A11 | Cost | BOM generated from the model, priced per item; goal ≤ ₹25k including filament (see §12: the estimate is ₹25.2k, so the order list names a cheaper acceptable substitute for the items that would close the gap). | BOM generator |
| A12 | Looks | The visual checklist in §8.4 passes on six fixed views at every drop. | manual review of renders |

## 5. Conventions

- Units mm, degrees, grams. World frame as v1: +X forward (drum end), +Y left, +Z up, ground at z = 0, frame centred on x = y = 0.
- Arm poses: press −25°, dig −20°, level 0°, mid +20°, carry/dump +35° (v1 values).
- Part ids are snake_case with a module prefix: `drv_`, `wheel`, `drum_`, `arm_`, `pivot_`, `lift_`, `tray_`, `batt_`, `tower_`, `hood_`, `body_`, `tof_`. Each part carries metadata: `kind` (printed / purchased / stock), `module`, `qty_per_rover`, `mass_g`, and for purchased parts `price_inr`, `price_basis` (listed / estimate), `source`, `datasheet` (true / measure-first).
- Printed mass = solid volume × 1.27 g/cm³ (PETG) × 0.75 (v1's factor for 3–4 walls and 25 % gyroid), so v2 and v1 are comparable.

## 6. Layout

All values live in `cad-v2/params.py`. Initial values below; constraints are enforced by the checks.

| Parameter | Initial value | Note |
|---|---|---|
| Wheel | Ø174 mm over grousers × 60 mm, 14 grousers | unchanged, so v1's sand-pit plan and numbers carry over |
| Track (wheel centre to centre) / wheelbase | 380 mm / 300 mm (axles at x = ±150, height 87 mm) | unchanged; overall width 440 mm |
| Rails | 2020 T-slot (20 × 20 mm, slot 6 mm, M5), centre line y = ±140 mm, z = 116…136 mm, x = −210…+170 mm (380 mm long) | if the front-corner clash below needs it, the rails rise by the smallest amount (expected ≤ 8 mm) |
| Cross members | 260 mm, butted between the rails; rear at x = −185, front at x = pivot_x − 65 (clears the arm roots by at least 5 mm at every pose) | joined with two inside corner brackets per joint |
| Arm pivot | pivot_x = 159 mm, z = 126 mm (v1: 199 mm) | 40 mm back gives about 72 % front-axle share on the §9.3 mass table (D4). The layout script keeps the largest shift between 20 mm (74 %) and 40 mm (72 %) for which the front-corner clash below is resolved by raising the rails by no more than 8 mm |
| Arm length, drum | 130 mm pivot to drum axis; drum shell Ø160, tooth tips Ø180, length 200 mm | unchanged |
| Lift | stroke at least 83 mm; T8×2 screw axis on the centre line, 155 mm above ground | |
| Tower | 2020 post 300 mm above the tray plate; overall height at most 620 mm (v1: 581 mm) | |
| Ground clearance | at least 60 mm under motors and mounts on firm ground | v1: about 70 mm |

**Front-corner clash (known):** with the pivot 40 mm back, the arm root at the front rail overlaps the front drive motor's gearbox by about 5 mm in z. The layout script resolves it by raising `rail_z0` (and with it the pivot) by the smallest amount that gives 5 mm clearance at every pose. If that needs more than 8 mm, the script reduces the pivot shift toward 20 mm; if 20 mm is still not enough, the fallback in §13 applies.

## 7. Modules

Six modules, each buildable and testable on its own. Mounting to the chassis is always M5 through round holes into spring T-nuts, with the printed part clamping on flat extrusion faces (nothing engages the slot), so slot differences between vendors do not matter.

### 7.1 Chassis (`modules/chassis.py`)

- **Stock (2020 T-slot, buy 2 × 1 m):** piece A = 380 + 380 + 232 mm (two rails, arm crossbar); piece B = 260 + 260 + 300 mm (two cross members, tower post). Total 1 812 mm.
- **Hardware:** 8 inside corner brackets (2 per joint), about 60 spring T-nuts M5, M5 button-head screws (10, 12 and 16 mm).
- **No plywood deck.** The electronics tray and the hood are the mounting surface.
- **Faces:** top slots carry tray, hood, battery cradle and tower base; outer slots carry the drive mounts; bottom slots carry the motor cradles; inner slots carry the pivot brackets.

### 7.2 Drive module ×4, identical (`modules/drive.py`)

Wheel loads go into two bearings; the motor shaft carries torque only.

- **Purchased (per module):** Johnson 12 V ~30 RPM side-shaft motor; 2 × 608 bearing; M8 × 80 hex bolt (axle); M8 nyloc nut and 2 washers; flexible jaw coupler 6→8 mm (Ø20 × 25 mm); 4 × M5 + T-nut (mount and cradle to rail); M4 bolts and nuts for the cradle.
- **Printed:** `drv_mount` (plate on the rail's outer face, with a two-bearing housing that reaches into the wheel's open inner side), `drv_cradle_roof`, `drv_cradle_cap`, `axle_spacer` (2 per module, one part type), `wheel` (hub and hex pocket for the bolt head are part of the wheel print; 165 g target, v1: 179 g).
- **Axle stack, outboard to inboard:** wheel (bolt head in the hex pocket) → outer spacer → bearing A → housing web → bearing B → inner spacer → washer and nyloc nut → flexible coupler → motor shaft. Tightening the nut clamps the bolt, wheel and both inner races into one rotating body; the housing shoulders and a printed retainer hold the outer races.
- **Motor position:** the gearbox axis sits 7.5 mm above the shaft (v1 convention; parameter `jm_shaft_off`, 0 for a centre-shaft motor). The cradle bolts to the mount through slotted M4 holes (±1.5 mm) so the shaft and axle can be aligned by eye with a straightedge; the coupler absorbs the rest.
- **Why:** a sideways skid loads the shaft through a wheel radius of 87 mm. On the gearbox bushing (span about 10 mm) that is roughly three times the reaction force of a 30 mm bearing span, and it is the failure mode v1's own guide worries about. Any motor with a 6 mm shaft also fits by sliding the cradle, which removes v1's dependence on unmeasured motor dimensions.

### 7.3 Excavator (`modules/excavator.py`, `modules/lift.py`)

- **Drum:** four rings of 48 mm between two 4 mm end plates (200 mm), shell 2.0 mm, four scoops per ring with the v1 baffle spiral (sweep 150°, core Ø52). Two ring designs, `drum_ring_a` and `drum_ring_b` (teeth rotated 45°), stacked A, B, A, B, so one tooth cuts at a time as in v1. Each ring has four external lugs at fixed angles (between the teeth, inside the tooth-tip envelope); four M4 tie rods (threaded rod cut to about 215 mm) clamp the stack with 8 nyloc nuts. End faces have a 2 mm spigot and recess for concentricity. Each ring is about 120 g (v1's one-piece body is 490 g).
- **End plates:** `drum_plate_drive` has a hex pocket for the M8 bolt head and a boss (the drum is driven through the same axle kit as the wheels); `drum_plate_idler` has a 608 pocket.
- **Arms:** `arm_drive` (left) carries the drum motor cradle and a boss with two 608 bearings; `arm_idler` (right) carries the idler bolt (M8 × 50, dead axle). Each arm has an integral square socket that clamps the 2020 crossbar (two M4 pinch bolts with nut traps) — no drilling. The arm root has a 608 bearing on an M8 × 50 pivot bolt held by `pivot_bracket_l` / `pivot_bracket_r`, which clamp on the rails' inner faces.
- **Lift:** T8 lead screw, single start, 2 mm lead (self-locking at a friction coefficient of 0.10 or more; dry brass on steel is 0.15–0.20), brass flange nut in `lift_carriage`, two identical `lift_bearing_block` (608), `lift_channel` (guide), `lift_cradle_roof` / `lift_cradle_cap` for a Johnson 300 RPM motor, the same flexible 6→8 mm coupler as the wheels, two micro limit switches, `lever` (clamped on the crossbar centre) and one `lift_link` (M5 pins). About 10 mm/s at 300 RPM. v1's two pushrods are replaced by one link on the centre line. At each arm pose the carriage position follows from the link length and lever geometry (closed form, as v1's `carriage_x`); the assembly builder derives it, and `interference.py` fails if the carriage would leave the screw's travel or the limit-switch positions.
- **Drum test jig (no new parts):** arms + crossbar + drum + drum motor on a 1 m length of T-slot as a handle; the build guide describes it for v1's "drum on a stick" test.

### 7.4 Electronics tray (`modules/electronics.py`)

- One removable **U-shaped tray** that rests on the rails and nests around the lift screw. Printed in three pieces (`tray_left`, `tray_right`, each at most 120 × 200 mm, and `tray_tie` behind the lift motor), joined by M4 bolts into one rigid unit before wiring. 3 mm plate with 6 mm ribs.
- **Left bay (power):** 4 × BTS7960 drivers, relay/contactor, main fuse and branch fuses, 5 V buck. **Right bay (compute):** Raspberry Pi 5 with cooler, ESP32, MPU6050, connectors to sensors and servo. A cable channel behind the lift motor joins the bays.
- **Battery cradle** (`batt_cradle`, strapped) on the rear cross member; default pack model 70 × 60 × 40 mm, ±3 mm adjustable.
- Every board sits on printed standoffs with slotted holes (±3 mm) so measured sizes can differ from the datasheet.

### 7.5 Sensor tower (`modules/tower.py`)

- 2020 post on the rear cross member with `tower_base` (4 × M5). Two-half cladding (`tower_sleeve_lower`, `tower_sleeve_upper`, wall 2 mm) hides the post and the cables.
- **Top:** `tower_camera_head` — USB webcam on an SG90 pan servo (0°/180°). **Side shelf below the camera line:** `tower_estop_shelf` — 22 mm panel-mount E-stop, modelled with a Ø60 mm head (any ≥ 40 mm head fits), set to the side so it never blocks the camera at either pan angle. **Rear face:** `tower_pzem_housing` — PZEM-051 display window facing back, high and visible. **Base:** `tof_rear_mount` (rear-looking ToF, 35° down).

### 7.6 Body (`modules/body.py`)

- Vented **hood** over the tray (about 200 × 300 mm) with a raised spine over the lift screw, in three panels printed upside down: `hood_left` and `hood_right` (105 mm wide) and `hood_spine` (90 mm wide), each at most 200 mm long, with the end walls built in. Seams are deliberate panel lines with a 0.6 mm reveal, never within 5 mm of a vent. Louvers face down and back to keep sand out; overlapping lips seal the seams. Fixed to the tray with M4 button screws.
- **Side covers** over the rails between the wheels (`body_side_cover`, mirrored), **ToF noses** (`tof_nose_l`, `tof_nose_r`) on the pivot brackets, one **carry handle** (`body_handle`, a bridge over the spine at the empty-mass centre of gravity, 30 mm hand clearance, bolted through the hood into the tray).
- **Three arrow marks**, each a 90 × 30 mm recess 0.8 mm deep on an upward-facing surface: forward on the front of the spine (pointing +x), length on `hood_left` (double-headed along x), width on the rear of the spine (double-headed along y). The size is an assumption; the rules digest gives none.

## 8. Design language

### 8.1 Colour by function

| Group | Colour | Used for |
|---|---|---|
| Working parts | CAT yellow `#FFCD11` | drum, arms, hood, tower head |
| Structure and drive | graphite `#2B2E33` | wheels, mounts, cradles, covers, trays, tower sleeves |
| Frame | natural aluminium `#C9CDD2` | 2020 extrusions |
| Hardware | steel `#8A8F98`, brass `#B5A642` | bolts, nuts, screw and nut |
| Electronics | black `#1A1A1A` | boards, motors, servo, camera |
| Safety | red `#D7191C` | E-stop only |

Colours are parameters in `params.py`; changing them regenerates everything.

### 8.2 Geometry rules

- External radius 3 mm on visible edges, 1.5 mm on small parts, 0.4 mm chamfer where a part meets the bed (elephant foot), 0.6 mm reveal between panels.
- Fastener heads sit in counterbores or hex pockets; no protruding nuts on visible faces; wiring hidden under the hood or in channels.
- The hood and tower share one vent-slot pattern on a 6 mm grid.
- Overhangs are designed in (45° chamfers, teardrop holes, stepped bridges), not left to supports.

### 8.3 Fastener policy

- Frame and mounts: M5 button head into spring T-nuts.
- Printed-to-printed: M4 socket or button head with a nut in a printed hex trap. **No heat-set inserts.**
- Pivots and axles: M8 bolts with nyloc nuts (the smooth shank runs in the bearings).
- Small parts (sensors, covers, switches): M3 with nut traps; self-tapping screws only for non-structural covers.
- Tools for assembly: 2.5, 3 and 4 mm hex keys and one 13 mm spanner (M8 bolts and nuts).

### 8.4 Visual review checklist (A12)

Six fixed views: front-left ¾, rear-right ¾, side at dig pose, front, top, exploded. Each drop must show: no floating or intersecting parts; all panel reveals equal; radii consistent; colours follow §8.1; no bolt sticking out of a visible face; E-stop, energy meter and camera each visible from at least one view; wheels and drum read as one family with the body.

## 9. Verification

Run with one command (`python tasks.py check`); a drop ships only when all checks pass.

### 9.1 Checks

- **`interference.py` (A1):** build the assembly at each pose; bounding-box prefilter, then exact boolean intersection volume for every candidate pair. Moving parts are the arm assembly (arms, drum, drum motor, crossbar, lever), the lift carriage and the link; wheels and the drum are checked as their swept cylinders (grouser-tip and tooth-tip radius). For the sweep, sample points on moving parts and measure the minimum distance to static parts.
- **`validity.py` (A2):** `is_valid` on every part; export the STEP; re-import it headless in FreeCAD 1.1 (`freecadcmd`) and check every shape; check each STL with trimesh for watertightness.
- **`printfit.py` (A3, A4):** place each part in its declared print orientation (`ORIENT` table), then check bounding box, downward-facing triangle areas past 45°, bridge spans, and mass by the §5 formula.
- **`massprops.py` (A6, A7):** mass and centre of gravity of the whole rover, empty and with 2.1 kg of sand at the drum centre, at the carry pose; front-axle share; overall size.
- **`rules.py` (A8, A9):** the geometric rules and cone checks in §4.
- **`calcs.py` (A10):** closed-form checks with the inputs printed. Loads: 3× the worst static wheel load (front axle at 75 %), lateral skid force 0.6 × vertical, drum reaction 60 N horizontal plus 40 N vertical at a tooth tip, the lift link force at the press pose. Material: PETG design stress 20 MPa along layers and 10 MPa across layers; steel bolts by class; brass and aluminium nominal.
- **`tests/`:** pytest on synthetic shapes proves each check catches what it should (an overlapping box pair, a 60° overhang, an oversize part, an unbalanced mass).

### 9.2 Fit-test kit (about 30 min print)

One STL that carries: three 608 seats (22.0, 22.1, 22.2 mm), M4 and M5 nut traps at three clearances, an M8 hex pocket (13 mm across flats) at three clearances, a hole set (M3, M4, M5, M8 at three clearances), and a 20 mm slice of the motor cradle. The user prints it first and sets three numbers in `params.py`: `tol_bearing`, `tol_trap`, `tol_hole`. Nothing large is printed before that.

### 9.3 Mass accounting and budget (grams, empty)

Printed parts by the §5 formula; purchased parts by datasheet or typical weight. v1 is recomputed on the same basis. Targets are for the drop-3 report.

| Item | v1 | v2 budget |
|---|---|---|
| Chassis extrusions and brackets (v1: tube and plywood deck) | 792 | 700 |
| Drive modules ×4, without motor and wheel | 344 | 820 |
| Wheels ×4 | 716 | 660 |
| Drive motors ×4 | 1 120 | 1 120 |
| Excavator without motor (drum, arms, pivots, crossbar, lever, hardware) | 1 057 | 1 111 |
| Drum motor | 280 | 280 |
| Lift (motor, screw drive, printed parts, link, switches) | 540 | 559 |
| Electronics boards and connectors | 390 | 390 |
| Tray and battery cradle | 247 | 240 |
| Battery pack | 250 | 250 |
| Sensor tower (post, cladding, E-stop, PZEM, camera, servo, ToF) | 653 | 699 |
| Body (hood, side covers, handle, ToF noses) | 0 | 410 |
| Wiring | 250 | 250 |
| Fasteners | 350 | 250 |
| **Total** | **≈ 6 990** | **≈ 7 740** |

The v2 budget is about 0.75 kg (11 %) above v1, which costs roughly a tenth of the mass-score component. The drivers are the bearing-supported drive modules (+0.48 kg) and the body (+0.41 kg). Goal 7.5 kg needs about 0.24 kg of lightweighting in drop 3 (thinner hood walls, lighter wheel spokes, lighter tower sleeves, lighter tray ribs); the hard limit is 8.0 kg.

v2 also prints more than v1: about 3.1 kg in roughly 40 part types (v1: 2.57 kg, 30 types), because of the hood, the tower cladding and the drive housings. Each new part is small; none exceeds 180 g, and the longest print falls from about 20 h to about 7 h.

## 10. Toolchain and repository layout

**build123d** (free Python library on the OpenCascade kernel that FreeCAD also uses), in a virtual environment inside `cad-v2/` (Python 3.12, a few hundred MB, nothing installed system-wide). Dependencies are pinned in `pyproject.toml` and mirrored in `requirements.txt`; `numpy`, `scipy`, `trimesh`, `pytest` for the checks. FreeCAD 1.1.3 (already installed; `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd`) is used only to validate the STEP; Chrome (already installed) renders images headlessly.

```
cad-v2/
  pyproject.toml  requirements.txt  tasks.py     # tasks.py: check | export | render | all
  params.py                # every shared dimension, colour, tolerance
  lib/     profile2020.py  cots.py  fasteners.py  style.py
  modules/ chassis.py  drive.py  excavator.py  lift.py  electronics.py  tower.py  body.py
  assemble.py              # rover(pose) -> named, coloured, metadata-carrying compound
  checks/  interference.py  validity.py  printfit.py  massprops.py  rules.py
  calcs.py
  export.py                # STEP, STL in print orientation, glTF, BOM (json and csv)
  render/  viewer.html  render.py
  tests/
  out/                     # generated: rover_v2.step, stl/, rover_v2.glb
docs/v2-build-guide.md  docs/v2-order-list.md  docs/v2-changelog.md  docs/img/v2/
hardware/bom_v2.csv
```

To change a dimension: edit `params.py`, run `python tasks.py all`. The STEP, STLs, BOM, renders and checks all regenerate.

## 11. Deliverables and drops

Each drop is committed on branch `v2` and tagged (`v2-drop1`, `v2-drop2`, `v2-drop3`); all applicable checks pass before the tag.

| Drop | Contents | Why this order |
|---|---|---|
| **1 — mobility kit and order list** | The tooling (params, lib, checks, tests, export, render); chassis, four drive modules, four wheels; the fit-test kit; `hardware/bom_v2.csv` and `docs/v2-order-list.md` covering every purchased part whose spec is fixed by then (extrusions with cut lengths, motors, bearings, couplers, bolts, T-nuts, T8 screw, brass nuts) | The team orders parts around 5 Oct and the chassis must drive on sand around 20 Oct. |
| **2 — excavator** | Drum rings and plates, arms, pivot brackets, crossbar, lever, lift module; the balance study with the real model; calcs for arms, lift and drum; renders of dig, carry and dump; drum test-jig instructions | The drum print and pit test are the biggest unknown and come first. |
| **3 — electronics, tower, body, documents** | Trays, battery cradle, tower, hood, covers, handle, arrows, ToF noses; all checks on the full assembly; lightweighting pass; six fixed renders and an exploded view; the interactive viewer; final BOM; build guide; change log; `CONTEXT.md` update | Everything left, and the look is judged on the finished machine. |

Fastener counts in the order list are final at drop 3; the order list advises buying an assortment with 20 % spare until then.

**Planning:** one implementation plan per drop. The drop-2 and drop-3 plans are written after the previous drop's checks pass, because they depend on its geometry (for example how the front-corner clash resolves).

## 12. BOM and budget

Estimates use v1's sources and price basis (Indian store listings, 2026-09-28) for unchanged items; new items are estimates until priced during drop 1.

| Change against v1 | ₹ |
|---|---|
| Frame: T-slot 2 m (900), brackets (200), 60 spring T-nuts (480), M5 screws (120), minus tube and plywood (−800) | +900 |
| Drive modules: 10 more 608 bearings (350), six flexible couplers at ₹200 less v1's one rigid coupler at ₹100 (1 100), M8 × 80 axle bolts, nuts, washers (150) | +1 600 |
| Lift: T8×2 screw and brass flange nut in place of the M8 rod | +250 |
| Drum tie rods and nyloc nuts | +120 |
| No heat-set inserts | −300 |
| Filament 3.5 kg in place of 3 kg | +500 |
| **v1 ₹22 120 → v2** | **≈ ₹25 200** |

Excluding filament (the college may supply it) v2 is about ₹21 700. Substitutes that recover about ₹1 200 if needed: rigid couplers on the wheel axles (−₹400), less spare stock (−₹500), cheaper T-slot supplier (−₹300).

## 13. Risks, measure-first gates and fallbacks

| Risk | Mitigation or fallback |
|---|---|
| **M1: motor dimensions unmeasured** | Measure one Johnson motor before printing `drv_cradle_*`, `arm_*` motor cradles and `lift_cradle_*`; the fit-test kit includes a cradle slice; cradles slide ±1.5 mm. Fallback: motor family is a parameter block (`jm_*`). |
| **M2: sizes of PZEM-051, relay, buck, BTS7960, E-stop body and battery are unpublished or vary** | Defaults in `cots.py`; holders adjustable ±3 mm; measure when the parts arrive and update `params.py`. |
| Extrusion profile varies between vendors | Printed parts clamp on flat faces only; M5 through round holes into T-nuts. |
| Print tolerance varies between printers | Fit-test kit (§9.2). |
| Front-corner clash (arm root against front motor) | Raise the rails (≤ 8 mm). If more is needed: flip the motor offset on the front modules (ground clearance 60 mm) or lengthen the wheelbase to at most 340 mm (front axle forward); either is raised with the user first. |
| Balance target of 75 % not reachable | Report the achieved value; consider the wheelbase fallback above; no ballast (mass costs score). |
| Mass above 7.5 kg | Lightweighting list in drop 3; the user decides whether the 8.0 kg limit moves. |
| Lift screw back-drives (T8×2 is self-locking only above μ ≈ 0.09) | Lubricate; use the driver's brake mode; or fall back to v1's M8 rod with a printed nut. |
| build123d fillet or boolean failures | Build with simple operations; fillet before booleans; fall back to chamfers; per-feature try/except in the build so the failing feature is named. |
| Sand performance and drum torque | Not provable in CAD: the same measure-first pit tests as v1 (drum on a stick first). |

## 14. Decision log

| # | Decision | Reason | Rejected |
|---|---|---|---|
| D1 | Same concept: drum digger, four-wheel skid steer, same electronics | The user chose it; nothing to test a new concept against before the 10 Nov video | Polish only (capped by OpenSCAD); clean-sheet concept |
| D2 | 2020 T-slot frame with spring T-nuts, no plywood | No drilling; adjustable; hides vendor variation | 20 × 20 tube with drilled holes (about 0.3 kg lighter, harder to build) |
| D3 | Two-bearing axle module with flexible coupler for wheels and drum drive | Removes the sideways-skid load from the gearbox bushing and the dependence on motor dimensions | Wheels on gearbox shafts as in v1 (about 0.3 kg and ₹1 100 cheaper) |
| D4 | Arm pivot 20–40 mm back, battery and tower rearmost | Balance study on the §9.3 mass table (estimated positions): loaded front-axle share 77 % with no shift, 74 % at 20 mm, 73 % at 30 mm, 72 % at 40 mm, 70 % at 60 mm (v1: 80 %). The estimate is good to a few points, so the requirement is 75 % with about 72 % expected; the model's own mass report replaces the study at drop 2. | Ballast (mass costs score); a longer wheelbase (kept as a fallback) |
| D5 | Drum in two ring designs (A/B), four rings, external tie rods | Prints in about 5 h a ring instead of 20 h; a failed ring costs one ring; straight tie rods need fixed lug angles, so two designs rather than four identical rings | Four identical rings with rotating lugs (rods would not align) |
| D6 | T8×2 screw and brass nut, one link | Standard parts replace a printed thread; one link on the centre line | Commercial linear actuator (about ₹2 500 more) |
| D7 | build123d in a project venv | Real solids, fillets, true STEP, exact booleans for the checks | OpenSCAD (mesh STEP, no fillets) |
| D8 | Colour by function, CAT yellow and graphite | One family; the sponsor's colour; parameters | White/silver "lunar" or matte black (still possible: one line) |
| D9 | Pivot brackets clamp on the rail inner faces | Rails cannot be drilled across | Cross-drilled rail as in v1 |
| D10 | U-shaped tray in three pieces | A single tray cannot fit around the lift screw and the 220 mm bed | Two separate trays |

## 15. Assumptions and defaults

- Printer 220 × 220 × 250 mm, PETG, 0.4 mm nozzle; college supplies the printer.
- Hand tools, hex keys, a hacksaw, a soldering iron for electronics; no laser, CNC, lathe or drill press.
- Budget cap ₹25k including filament (`CONTEXT.md` §6); free tools only.
- 2020 T-slot is the B-type, slot 6 mm, M5. Spring T-nuts are M5 drop-in.
- Motor: Johnson 12 V side-shaft, Ø37 × 25 mm gearbox, Ø28.5 × 38 mm can, 6 mm D shaft (22 mm long, 5.5 mm across the flat), shaft offset 7.5 mm (v1 values, measure-first).
- Battery pack 3S2P about 70 × 60 × 40 mm, 250 g (measure-first).
- Arrow marks 90 × 30 mm (the rules digest gives no size).
- E-stop modelled Ø60 mm head, 22 mm panel-mount.
- Nothing is pushed to GitHub, and no artifact is published, without the user's explicit OK.

## 16. As built (2026-09-29)

All three drops are done; `python tasks.py check` prints ALL CHECKS PASS and the 120 tests pass.

| ID | Result |
|---|---|
| A1 | 0 collisions at the five poses (-28, -25, 0, +20, +35); 2 mm clearance moving-vs-static at eight poses from -28 to +35; no floating or half-held fastener (contact-graph check) |
| A2 | STEP re-opens in FreeCAD 1.1 with 438 solids and 0 invalid shapes; 44 STLs, all watertight |
| A3, A4 | every part fits 210 x 210 x 240 mm and prints without supports; largest print 137 g (limit 180); printed total 2.55 kg in 43 part types |
| A5 | 0 drilled or tapped holes, 0 heat-set inserts; the only cuts are the 2020 (three 1 m bars), one M4 rod (four tie rods) and one M8 rod (the lift screw) |
| A6 | 7.94 kg empty including the 250 g wiring allowance: inside the 8.0 kg limit, 0.44 kg over the 7.5 kg goal |
| A7 | front-axle share 74.1 % with 2.1 kg of sand at the carry pose (limit 75 %; v1 80 %); 53 % empty |
| A8 | stowed 601 x 478 x 445 mm; E-stop head 60 mm, reachable from above, behind and outboard; PZEM display faces rearward at 321 mm; three arrow plates on the roof |
| A9 | camera at pan 0 sees only the excavator, at pan 180 nothing; both front ToF cones and the rear cone are free at the carry pose |
| A10 | eleven load paths, lowest safety factor 2.1 (pivot bracket wall); tray plate deflects 0.88 mm at three times the load (limit 1 mm) |
| A11 | INR 23,329 with filament, wiring, sand pit and spares (cap 25,000; v1 22,120); `hardware/bom_v2.csv` |
| A12 | six fixed views plus dig, exploded and hood-off pictures in `docs/img/v2/`; reviewed by the author only, the user's eye is the real test |

Amendments to the decision log: D4's expected 72 % became 74 % (the excavator is heavier than budgeted; the rear axle moved 40 mm forward to compensate); D6 became an M8 x 1.25 rod
with two brass nuts and two link plates; D9's brackets stand on the rail tops instead of clamping on the inner faces; the hood is two halves, not three panels. See `docs/v2-changelog.md`.
