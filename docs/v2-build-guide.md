# Rover v2: design and build guide

![Rover v2 at the carry pose](img/v2/front_left.png)

v2 keeps v1's idea (a light four-wheel skid-steer rover with a rotating bucket drum on a lift arm) and re-engineers everything
around it so a student team can build it with a 3D printer, hand tools and **no drilling, no tapping and no heat-set inserts**.
The whole rover is a parametric CAD model (`cad-v2/`, Python on the OpenCascade kernel, the same one FreeCAD uses). Every number
in this guide is generated from that model, and every claim is backed by a script that fails if it stops being true.

## 1. The numbers

<!-- BEGIN:numbers -->
| What | Value |
| :--- | :--- |
| Stowed size (carry pose) | 601 x 478 x 445 mm (limit 1500 x 750 x 750) |
| Wheelbase, track | 260 mm, 380 mm between wheel centres |
| Empty mass | 7.94 kg = 7.69 kg modelled + 250 g wiring allowance (limit 8.0 kg, goal 7.5 kg) |
| Mass with a full drum | 10.04 kg (2.1 kg of sand) |
| Front-axle share | 53 % empty, 74 % with a full drum at the carry pose (limit 75 %; v1: 80 %) |
| Centre of gravity, empty | x = 29, y = 7, z = 157 mm (x from the frame centre, forward positive) |
| Arm range | press -28 deg (teeth 10 mm below grade), dig -25 deg (4 mm below), level 0, mid +20, carry +35 deg (teeth 147 mm up) |
| Lift | M8 x 1.25 rod with two brass nuts, stroke 59 mm, self-locking |
| Printed parts | 43 part types, 2.55 kg of PETG (v1 rule: volume x 1.27 x 0.75), largest 137 g, no supports |
| Purchased | 48 SKUs, 352 pieces; total budget INR 24,715 with filament (cap 25,000; v1 22,120) |
<!-- END:numbers -->

![Top view](img/v2/top.png)

## 2. What changed from v1

| v1 weak spot (from its own guide) | v2 |
|---|---|
| Wheels cantilevered on the gearbox shafts | Each wheel turns on two 608 bearings in a printed housing that bolts to the rail. The motor drives an M8 axle bolt through a helical coupler, so the gearbox carries torque only. |
| 80 % of the loaded weight on the front axle | 74 % with a full drum (2.1 kg of sand at the carry pose). The wheelbase is 260 mm and the electronics sit behind the axle centre. |
| Motor dimensions unmeasured, everything printed to guesses | A one-hour fit-test kit calibrates three tolerances first; every motor clamp is two pieces with slotted bolts; the measure-first list (section 9) says which parts depend on which measurement. |
| A one-piece drum that prints for about 20 hours | Four identical-height rings (101 g each, about 4 h) and two identical end plates (65 g), held by four M4 tie rods. Rings alternate by 45 degrees so the teeth are staggered. |
| Mesh-only STEP files | Proper B-rep STEP (opens in FreeCAD with 0 invalid shapes) and watertight STLs, one per part type. |
| Plywood deck and aluminium tube, heat-set inserts | 2020 T-slot frame and drop-in T-nuts; screws go into M4 nuts held in printed hex traps. |
| Wiring and boards loose in a box | A removable two-piece tray with standoffs for every board, a battery cradle, and a hood that hides all of it. |
| No way to prove it fits | Exact-solid collision checks at five arm poses, a 2 mm clearance sweep for every moving part, a floating-hardware check, a print-without-supports check, and hand-calculated load paths (section 8). |

## 3. Before you print anything: the fit-test kit

Print `out/stl/fit_test_kit.stl` first (about an hour, 100 x 66 mm). Left to right in each row the clearance grows:

| Row | What it holds | Columns |
|---|---|---|
| Bearing seats | 608 bearing, 22 mm | seat diameter 22.0 / 22.1 / 22.2 mm |
| Nut traps | M4 nut and M8 nut | hex across-flats +0.2 / +0.4 / +0.6 mm |
| Holes | M4 and M5 bolts | diameter +0.2 / +0.4 / +0.6 mm |
| Motor slice | the Johnson gearbox, 37 mm | the saddle at the right-hand end |

Push a real 608, M4 nut, M8 nut, M4 and M5 bolts, and the motor gearbox into the columns. Pick the first column that goes in by hand without
force and does not rattle. Then set the numbers in `cad-v2/params.py` and regenerate:

```python
TOL_BEARING = 0.2   # bearing seat = 22.0 + this   (kit columns: 0.0 / 0.1 / 0.2)
TOL_TRAP = 0.4      # hex trap across-flats = nut + this   (0.2 / 0.4 / 0.6)
TOL_HOLE = 0.4      # bolt hole = bolt + this   (0.2 / 0.4 / 0.6)
```

```bash
cd cad-v2 && source .venv/bin/activate && python tasks.py all
```

Until you have done this, print nothing large. If the motor does not sit in the saddle, measure the gearbox (`JM_GEAR_D`, `JM_SHAFT_OFF` in `params.py`).

## 4. Print list

Settings that all parts assume: PETG, 0.4 mm nozzle, 0.2 mm layers, 4 walls, 25 % gyroid infill, **no supports**, 5 mm brim on the tall thin parts
(`tower_*`, `estop_pedestal`, `body_handle`). The thin-walled parts (hood, wheels, drum rings, plates) are almost all walls, so infill hardly matters
for them. Every STL is already turned into its print position. Masses use v1's rule (volume x 1.27 g/cm3 x 0.75); weigh one wheel after printing
and change `FILL` in `params.py` if it is far off, then regenerate.

<!-- BEGIN:print -->
**Drive modules**

| Part (STL name) | Qty | Size in print position, mm | g each | g total | Colour |
| :--- | ---: | :--- | ---: | ---: | :--- |
| `drv_mount` | 4 | 64 x 76 x 57 | 68 | 271 | graphite |
| `drv_cradle_roof` | 4 | 76 x 54 x 8 | 24 | 95 | graphite |
| `drv_cradle_cap` | 4 | 56 x 28 x 35 | 24 | 98 | graphite |
| `axle_spacer_mid` | 4 | 11 x 11 x 23 | 1 | 3 | graphite |
| `axle_spacer_end` | 9 | 11 x 11 x 2 | 0 | 1 | graphite |
| `wheel` | 4 | 174 x 174 x 60 | 111 | 444 | graphite |
| `wheel_cap` | 4 | 44 x 44 x 8 | 10 | 39 | yellow |

**Excavator: drum, arms, lift**

| Part (STL name) | Qty | Size in print position, mm | g each | g total | Colour |
| :--- | ---: | :--- | ---: | ---: | :--- |
| `pivot_bracket_l` | 1 | 62 x 56 x 68 | 36 | 36 | graphite |
| `pivot_bracket_r` | 1 | 62 x 56 x 68 | 36 | 36 | graphite |
| `lift_channel` | 1 | 141 x 32 x 30 | 45 | 45 | graphite |
| `lift_bearing_block` | 2 | 26 x 26 x 14 | 5 | 11 | graphite |
| `lift_cradle_base` | 1 | 29 x 62 x 27 | 29 | 29 | graphite |
| `lift_cradle_cap` | 1 | 29 x 62 x 22 | 21 | 21 | graphite |
| `arm_drive` | 1 | 199 x 78 x 106 | 137 | 137 | yellow |
| `arm_idler` | 1 | 195 x 78 x 12 | 73 | 73 | yellow |
| `arm_motor_cap` | 1 | 56 x 25 x 22 | 15 | 15 | yellow |
| `clamp_block` | 2 | 40 x 40 x 16 | 17 | 34 | graphite |
| `lever` | 1 | 63 x 48 x 16 | 26 | 26 | yellow |
| `lift_link` | 2 | 114 x 14 x 7 | 10 | 20 | graphite |
| `lift_carriage` | 1 | 24 x 24 x 43 | 15 | 15 | graphite |
| `drum_plate` | 2 | 175 x 175 x 12 | 65 | 130 | yellow |
| `drum_ring_a` | 2 | 181 x 181 x 48 | 101 | 203 | yellow |
| `drum_ring_b` | 2 | 175 x 175 x 48 | 101 | 203 | yellow |
| `axle_spacer_62` | 3 | 11 x 11 x 6 | 0 | 1 | graphite |
| `axle_spacer_drum_mid` | 1 | 11 x 11 x 19 | 1 | 1 | graphite |

**Electronics tray and battery**

| Part (STL name) | Qty | Size in print position, mm | g each | g total | Colour |
| :--- | ---: | :--- | ---: | ---: | :--- |
| `tray_left` | 1 | 200 x 118 x 11 | 55 | 55 | graphite |
| `tray_right` | 1 | 200 x 118 x 11 | 59 | 59 | graphite |
| `tray_tie` | 1 | 10 x 104 x 6 | 6 | 6 | graphite |
| `batt_cradle` | 1 | 76 x 66 x 32 | 40 | 40 | graphite |

**Sensor tower and E-stop**

| Part (STL name) | Qty | Size in print position, mm | g each | g total | Colour |
| :--- | ---: | :--- | ---: | ---: | :--- |
| `tower_base` | 1 | 64 x 60 x 35 | 39 | 39 | graphite |
| `tower_sleeve_80` | 1 | 30 x 30 x 80 | 23 | 23 | graphite |
| `tower_sleeve_40` | 1 | 30 x 30 x 40 | 12 | 12 | graphite |
| `tower_pzem` | 1 | 40 x 56 x 60 | 40 | 40 | yellow |
| `tower_head` | 1 | 30 x 30 x 50 | 25 | 25 | yellow |
| `estop_pedestal` | 1 | 66 x 66 x 115 | 54 | 54 | graphite |
| `camera_mount` | 1 | 32 x 80 x 30 | 16 | 16 | yellow |

**Body**

| Part (STL name) | Qty | Size in print position, mm | g each | g total | Colour |
| :--- | ---: | :--- | ---: | ---: | :--- |
| `hood_left` | 1 | 200 x 150 x 58 | 74 | 74 | yellow |
| `hood_right` | 1 | 200 x 150 x 58 | 73 | 73 | yellow |
| `body_side_cover_l` | 1 | 80 x 72 x 2 | 11 | 11 | yellow |
| `body_side_cover_r` | 1 | 80 x 72 x 2 | 11 | 11 | yellow |
| `body_handle` | 1 | 22 x 98 x 46 | 26 | 26 | graphite |
| `body_arrow` | 1 | 90 x 30 x 1 | 1 | 1 | white |
| `body_arrow_double` | 2 | 90 x 30 x 1 | 1 | 2 | white |

Total 2.55 kg of PETG in 43 part types (about 102 print hours at 25 g/h; the longest single print is 137 g, about 5 h). Every STL in `cad-v2/out/stl/` is already turned into its print position and sits on z = 0.
<!-- END:print -->

Print in this order so you can start assembling early: fit-test kit, drive module parts (mounts, cradles, wheels, caps), electronics tray, excavator, tower, body.
Colours follow function: yellow for the parts that work the ground (drum, arms, hood, tower head), graphite for structure and drive, white for the arrow plates.

## 5. Buy list

See [`v2-order-list.md`](v2-order-list.md) (generated from the model, priced, with the aluminium cut list) and [`../hardware/bom_v2.csv`](../hardware/bom_v2.csv).

## 6. Assembly

Suggested order: frame, four drive modules, electronics tray, excavator, tower, body. Two people can work in parallel (one on the drive modules and excavator, one on the electronics and tower). Use a drop of thread-locker on the M8 axle nuts only if you use plain nuts; the nylon-insert nuts in the list do not need it. Tighten M4 screws
into printed traps until snug, no further: PETG creeps under a hard-tightened screw.

Open `out/rover_v2_viewer.html` in a browser next to this guide. Hover any part to see its name, drag the *Explode* slider to see how it stacks up, and switch the
hood off to see the tray.

![Exploded view](img/v2/exploded.png)

### 6.1 Frame (no printed parts)

1. Cut the 2020 to the lengths in the order list: two rails 402 mm, two cross members 260 mm, the spine 259 mm, the arm crossbar 212 mm and the tower post 240 mm.
2. Lay the rails 260 mm apart (inside faces) and put a corner bracket at each inside corner of the two cross members: one on the front face and one on the back face
   at every end of both cross members (eight in all). The rear cross member sits at x = -185 mm, the front one at x = +94 mm. The rails stick out 17 mm behind the
   rear cross member; that stub holds the outer brackets.
3. Fit the spine between the cross members with four more brackets, two at each end.
4. Every bracket takes two M5 x 8 button screws into drop-in T-nuts. Check the frame is square (diagonals within 1 mm) before tightening.

### 6.2 Drive modules, four times

Each module is a motor, a coupler, a mount plate with a two-bearing housing, a two-piece motor clamp and a wheel. Front axle x = +150, rear axle x = -110.

1. **Mount plate** (`drv_mount`): two M5 x 12 screws with T-nuts into the rail's outer slot. The housing points outward.
2. **Bearings**: press one 608 into each end of the housing (the seats are open at both ends; the web in the middle stops them).
3. **Motor clamp**: `drv_cradle_roof` goes under the rail with two M5 x 14 screws into the rail's bottom slot (the holes are slotted 3 mm along the rail, so you can
   line the motor up). The roof carries two M4 nuts in hex traps.
4. **Axle**, from the outside in: `wheel_cap` with the M8 x 75 bolt head in its hex pocket, the wheel (four M4 x 14 screws join cap and wheel; the nuts are in the hub),
   spacer, bearing, the long spacer, bearing, spacer, washer, and the nyloc nut on the inside. Tighten until the wheel still spins freely with a finger.
5. **Motor**: slide the coupler over the bolt end, put the motor shaft into the other end, lay the motor gearbox in the roof's saddle, close it with `drv_cradle_cap`
   (two M4 x 40 from below into the roof's nuts) and tighten the coupler screws on the shaft flat.

### 6.3 Electronics tray

1. `tray_left` and `tray_right` rest on the rails either side of the spine; two M5 x 8 screws each go into T-nuts in the rails' top slots (at x = -118 and +66).
2. `tray_tie` joins the two halves behind the lift motor: two M4 x 8 from underneath into nuts in its underside.
3. Boards go on the standoffs (M2.5 self-tapping screws): four BTS7960 drivers, relay, 5 V buck and two fuse holders on the **right** half (the power bay, next to the battery);
   Raspberry Pi 5, ESP32 and MPU6050 on the **left** half (the compute bay).
4. `batt_cradle` bolts to the rear cross member (two M5 x 8). The battery sits in it with a 16 mm hook-and-loop strap through the two slots.
5. Wire before the hood goes on. Mandatory by the rules: the PZEM-051 sits between the battery and the E-stop, and one press of the E-stop cuts the battery from all controllers.
   Cable routes are not modelled, but the space is there: motor cables come up through the 22 mm gap between the spine / lift channel and the tray edges (y = 16 to 32 mm) and stay under the hood;
   the drum-motor cable follows the left arm to the pivot (leave a service loop there) and enters through the front port; the E-stop wires run down the pedestal bore.
   The PZEM's 50 A shunt is a separate bar: cable-tie it to a tray rib next to the fuse holders.

### 6.4 Excavator

1. **Pivot brackets**: each stands on a rail top with two M5 x 10 screws at x = 139 and 179. The front ToF sensor goes on its sloping pad (25 degrees below forward).
2. **Arms**: press a 608 into each arm's root, from the outer face. The arm goes on the bracket with an M8 x 35 bolt through the wall (head outside), a washer between wall and arm,
   the bearing, a washer and a nyloc nut. The arms swing freely with no side play.
3. **Drum**: end plate, ring A, ring B, ring A, ring B, second end plate (turn the second plate over about the axis: the four lug holes still line up). Four M4 rods
   211 mm long pass through the lugs; a nyloc nut on each end. Rings A and B are the same part turned 45 degrees in the print (`drum_ring_a`, `drum_ring_b`).
4. **Drum axle**: M8 x 70 on the drive side (head in the plate's hex pocket), M8 x 40 on the idler side, each through two 608 in the arm boss; spacers as in the model.
   The drum motor sits in `arm_drive` and `arm_motor_cap` (two M4 x 30) and drives the axle through a coupler.
5. **Crossbar and lever**: the 212 mm crossbar spans the arms. `clamp_block` (one per arm) is held on the arm by two M4 x 25 and pinches the crossbar with two M5 x 16.
   The `lever` is clamped to the middle of the crossbar the same way.
6. **Lift**: `lift_channel` stands on the spine and the front cross member (four M5 x 8). The two bearing blocks sit inside it, joined by the M8 rod with the coupler
   to the lift motor (`lift_cradle_base` and `lift_cradle_cap`, two M4 x 30, on the spine). The carriage holds two brass M8 nuts, one in each end.
   Two links (`lift_link`) connect the carriage to the lever with M5 x 35 pins and nyloc nuts.
7. Two micro limit switches are **not** in the model: put one at each end of the channel so the carriage trips them at x = 13 mm and x = 86 mm (the working range is 20 to 79.5 mm).

### 6.5 Sensor tower

1. `tower_base` bolts to the rear cross member (two M5 x 8). The rear ToF looks 20 degrees below horizontal from its wedge.
2. The 240 mm post stands in the base's socket. Every collar (`tower_base` socket, `tower_pzem`, `tower_head`) clamps with two M5 x 10 screws into T-nuts in the post's side slots.
   The two sleeves (`tower_sleeve_80`, `tower_sleeve_40`) just slide down over the post from the top.
3. The PZEM-051 sits on the rear plate of `tower_pzem`, display facing back, 321 mm above the ground.
4. The SG90 servo drops into the pocket in `tower_head`; `camera_mount` goes on its horn; the webcam sits on the platform, lens forward at pan 0.
5. `estop_pedestal` bolts to the rear cross member left of the tower (two M5 x 8). The E-stop clamps in its 22.4 mm hole and the contact block hangs in the bore.

### 6.6 Body

1. Lay `hood_left` and `hood_right` on the tray. Ten M4 screws (eight M4 x 60 button heads and two M4 x 100 through the handle) go down the posts into the nuts in the tray bosses.
   The two halves meet with a 0.6 mm reveal down the centre line.
2. The handle (`body_handle`) stands on the two inner posts at x = -20 mm; its two M4 x 100 bolts run right through it.
3. `body_side_cover_l` and `_r` go on the rails' outer faces between the wheels (two M5 x 8, washer and T-nut each).
4. Three arrow plates lie on the hood roof with double-sided tape: forward (single head, points +x), length (double head along x), width (double head along y).

![Hood off: the tray and the lift](img/v2/hood_off.png)

## 7. Arm poses

The lift rod moves the carriage 60 mm; the links turn that into the arm angle. The table is from the model.

<!-- BEGIN:poses -->
| Arm angle | Name | Lowest tooth tip, mm above ground | Highest point of the drum, mm | Carriage on the rod, x mm |
| ---: | :--- | ---: | ---: | ---: |
| -28 deg | press | -10 | 160 | 79.5 |
| -25 deg | dig | -4 | 168 | 76.9 |
| +0 deg | level | +57 | 239 | 53.0 |
| +20 deg | mid | +117 | 285 | 33.1 |
| +35 deg | carry / dump | +147 | 327 | 20.0 |
<!-- END:poses -->

![Dig pose](img/v2/side_dig.png)

Digging is done by spinning the drum with the arm lowered to the dig or press pose while the rover creeps forward; the spiral baffles carry sand to the core.
Reverse the drum to dump. At the carry pose the teeth are about 147 mm above the ground and the rover is 601 x 478 x 445 mm.

## 8. Mass, balance and load paths

<!-- BEGIN:mass -->
| Module | Items | Printed g | Bought g | Total g |
| :--- | ---: | ---: | ---: | ---: |
| chassis | 65 | 0 | 1052 | 1052 |
| drive | 140 | 950 | 1654 | 2604 |
| excavator | 126 | 1036 | 1246 | 2283 |
| electronics | 32 | 160 | 636 | 796 |
| tower | 34 | 209 | 467 | 677 |
| body | 40 | 198 | 86 | 284 |
| **modelled total** | 437 | **2553** | **5142** | **7695** |
| wiring allowance (not modelled) |  |  |  | 250 |
| **empty** |  |  |  | **7945** |
<!-- END:mass -->

The wiring allowance (250 g) stands in for cables, connectors and ties, which are not modelled. Printed masses follow v1's rule; if your prints come out heavier, the
empty mass is over the 8.0 kg limit before you start: the cheapest ways to take mass off are listed in [`v2-changelog.md`](v2-changelog.md).

Load paths (hand calculations, `cad-v2/calcs.py`): worst case is the full rover (10.2 kg) with a shock factor of 3, a lateral skid force of 0.6 of the vertical load,
3.6 kg at the drum axis and a 60 N digging reaction at the tooth tip. PETG design stress is 20 MPa in the layer plane and 10 MPa across layers. Each row needs a
safety factor of 2, except the tray plate, which must deflect less than 1 mm at three times the load.

<!-- BEGIN:calcs -->
| Load path | Demand | Capacity | Safety factor | Needed | Inputs |
| :--- | ---: | ---: | ---: | ---: | :--- |
| wheel housing root (bending across layers) | 3.3 | 10 | 3.0 | 2 | Fv N 113, Fl N 68, M N.m 9.25 |
| 608 bearing static load | 365 | 1.29e+03 | 3.5 | 2 | N 365, rating N 1290 |
| M5 T-nut pull-out (mount plate) | 231 | 800 | 3.5 | 2 | N per bolt 231 |
| M8 axle bolt bending | 40.3 | 640 | 15.9 | 2 | M N.mm 2026 |
| pivot bracket wall bearing stress | 9.47 | 20 | 2.1 | 2 | reaction N 306, wall mm 10.0 |
| arm bending at the crossbar (in the layer plane) | 4.92 | 20 | 4.1 | 2 | M N.m 21.7 |
| lift link buckling (2 plates) | 454 | 1.42e+03 | 3.1 | 2 | load N 454, P_cr N 1422 |
| lift link tension | 2.32 | 20 | 8.6 | 2 |  |
| drum torque through the lugs (per rod, N) | 5.65 | 400 | 70.7 | 2 | torque N.m 1.9 |
| M8 rod: friction needed to self-lock (dry brass on steel: 0.15) | 0.0479 | 0.15 | 3.1 | 2 | lead angle deg 3.17 |
| tray plate deflection at 3x load (mm; limit 1) | 0.884 | 1 | 1.1 | 1 | boards g 272, span mm 98, I mm4 316 |
<!-- END:calcs -->

## 9. Measure-first list and known limits

- **Johnson motors:** the gearbox diameter and shaft offset set the four drive cradles, the arm clamp and the lift clamp. Measure one motor and check `JM_*` in `params.py`.
- **Boards and cells:** BTS7960, relay, buck, fuse holders, PZEM-051, battery pack and webcam sizes are listing values (`lib/cots.py`). Board holders are slotted (+-3 mm).
  The battery cradle is sized to the pack: check `BATT` in `modules/electronics.py`.
- **Not modelled:** wiring, connectors, the PZEM shunt, the two lift limit switches, the hook-and-loop strap, thread-locker, the AprilTag stands.
- **Empty mass** is 0.06 kg under the 8.0 kg limit, so it is over the 7.5 kg goal. It also depends on your slicer settings: weigh a wheel.
- **E-stop:** the model has a 60 mm head. The rules ask for at least 40 mm, so any twist-release red mushroom of that size fits the 22.4 mm hole. The tower stands 47 mm from
  the E-stop on its inboard side, so the E-stop can be reached from above, behind and from the outboard side, but not from the tower side.
- **Camera view:** at pan 0 the camera sees the drum and arms (useful) and nothing else; at pan 180 it sees no part of the rover.
- **Sand:** the hood keeps sand off the boards from above; the tray plate is solid, but the underside of the rover is open. Do not drive through deep sand with the hood off.

## 10. Files and how to regenerate

| What | Where |
|---|---|
| Parametric model (every dimension) | `cad-v2/params.py`, modules in `cad-v2/modules/` |
| Print files | `cad-v2/out/stl/*.stl` (43 part types plus the fit-test kit) |
| Whole rover as STEP | `cad-v2/out/rover_v2.step` |
| Interactive viewer (one self-contained file) | `cad-v2/out/rover_v2_viewer.html` |
| Pictures | `docs/img/v2/*.png` |
| Priced bill of materials | `hardware/bom_v2.csv`, `docs/v2-order-list.md` |

```bash
cd cad-v2
uv venv --python 3.12 .venv && source .venv/bin/activate && uv pip install -r requirements.txt
python tasks.py check     # every acceptance check, about 3 minutes
python tasks.py export    # STEP, STLs, BOM (validated in FreeCAD)
python tasks.py render    # viewer and pictures (needs Node and Google Chrome)
python tasks.py docs      # refresh the tables in this guide and the order list
python tasks.py all       # everything
python -m pytest          # 120 tests
```

Change a dimension in `params.py` and run `python tasks.py all`: the model, STLs, BOM, pictures and the tables above all follow. If a check fails,
the message names the parts that clash.
