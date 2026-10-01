# Rover v2: what changed, and what differs from the spec

Read [`v2-build-guide.md`](v2-build-guide.md) to build it and [`v2-order-list.md`](v2-order-list.md) to buy it. This file is the honest ledger: how v2
compares with v1, where the finished model departs from the approved design spec (`docs/superpowers/specs/2026-09-29-rover-v2-design.md`), and what did not come out
as hoped.

## v1 and v2 side by side

| | v1 (OpenSCAD, 2026-09-28) | v2 (build123d, 2026-09-29) |
|---|---|---|
| Model | mesh-derived STEP, 30 STLs | B-rep STEP (0 invalid shapes in FreeCAD), 43 part types + fit-test kit as watertight STLs |
| Frame | aluminium tube + plywood deck, heat-set inserts | 2020 T-slot, 12 corner brackets, drop-in T-nuts; no drilling, no tapping, no inserts |
| Wheels | cantilevered on the gearbox shaft | two 608 bearings per wheel in a printed housing on the rail, coupler drive |
| Drum | one 490 g piece, about 20 h | 4 rings + 2 plates, largest print 101 g |
| Empty mass, same accounting | about 7.0 kg (its own table says 7.5) | 7.69 kg modelled + 0.25 kg wiring = 7.94 kg |
| Front-axle share, full drum | 80 % | 74 % |
| Cost | INR 22,120 | INR 23,329 (cap 25,000) |
| Printed | 29 types, 2.6 kg | 43 types, 2.55 kg |
| Checks | interference at four arm angles | 120 tests; collisions at five poses, 2 mm sweep clearance, floating hardware, no-support printing, load paths, rules, sensor views, mass and balance |

v2 is about 0.9 kg heavier than v1 on the same accounting. What that buys: bearings on every axle, a covered electronics bay, a proper mast and a real hood. The mass
term of the score scales as 1/mass (the organisers' example: 344.6 of 695 points), so +13 % mass costs about 12 % of that term. The spec budgeted 0.75 kg (11 %); the built rover is 0.95 kg (13 %) above v1.

## Departures from the spec, and why

| Spec said | Built | Why |
|---|---|---|
| Arm poses -25, -20, 0, +20, +35 | -28 (press), -25 (dig), 0, +20, +35 | at -25 the teeth reached only 4 mm below grade; -28 adds a deeper press pose and both are checked |
| Arm pivot at x = 159, z = 145; arm 150 mm | pivot z = 148, arm 156 mm, pivot on two brackets that stand on the rails | the front motor and cradle clashed with the arm at the low poses; the brackets lift the pivot clear |
| T8 x 2 lead screw with a brass flange nut | M8 x 1.25 zinc rod with two brass M8 nuts captured in the carriage | the T8 needs a friction coefficient of about 0.18 to stay put with a safety factor of 2 and brass on steel gives 0.15; the M8 rod locks with a factor of 3 and costs about INR 40 |
| No centre spine | 2020 spine (259 mm) between the cross members | carries the lift channel, the lift motor and the tray's inner edge; also stiffens the frame |
| Rails 380 mm, axles at +-150 | rails 402 mm (x -212 to +190), axles at +150 and -110 (wheelbase 260) | the front bracket ears and cradle bolts need rail under them; the shorter wheelbase moves the loaded front share from 76 % to 74 % |
| Hood: three panels with a raised spine over the lift | two halves split down the centre line, flat roof at z = 196, a two-step port in the front wall for the lift links | a raised spine cannot print roof-down without support; the centre seam also keeps every panel line clear of the vents |
| E-stop on a shelf on the tower | E-stop on its own pedestal left of the tower, panel at z = 251 | the tower's cross-section is 30 x 30; a 60 mm head does not fit on it, and the pedestal keeps the camera view clean |
| E-stop reachable from above, behind and both sides | above, behind and outboard (the tower is 47 mm from the inboard side) | the tower is on the centre line; the rules ask only for a red mushroom of at least 40 mm |
| Tower 280 mm | post 240 mm, camera at 445 mm, PZEM at 321 mm | 31 g and one 40 mm sleeve less; still above the 250 mm the spec wants for the meter |
| Arrow marks as 0.8 mm recesses | three 0.8 mm plates lying on the hood, forward / length / width | a recess in a 1.2 mm roof would cut through it |
| Power bay left, compute bay right | power bay right (next to the battery), compute bay left | shorter power wiring, and it moved the sideways centre of gravity from 12 mm to 7 mm off the centre line |
| Side covers 104 mm | 80 mm, sized to the gap between the wheels | the shorter wheelbase left an 86 mm gap |
| Empty mass budget 7.74 kg, goal 7.5, limit 8.0 | 7.94 kg with the wiring allowance | see below |
| ToF noses on the brackets | ToF boards on 25-degree pads on the pivot brackets | fewer parts; the cone (27 degrees) is checked free at the carry pose |

Also new, not in the spec: a contact-graph check that no fastener floats (it caught four T-nuts hanging off the rail ends), a tray deflection check (0.88 mm at three times the
load, limit 1 mm), and automatic cut-planning of the aluminium into three 1 m bars.

## What did not come out as hoped

- **Mass.** The approved budget was 7.74 kg, the goal 7.5 kg and the limit 8.0 kg. The finished model is 7.94 kg with the wiring allowance: inside the limit by 55 g, 0.44 kg over the goal.
  A lightening pass already took about 0.4 kg off the printed parts (thinner wheel rims and hood walls, pocketed drum plates, a narrower boss on the drum arm, a 2.0 mm tray plate, a 40 mm shorter mast).
  Ways to take off more, cheapest first: drop the two side covers and the three arrow plates (about 45 g with their screws; the arrows can be stickers); drop the two tower sleeves (35 g);
  thin the hood from 1.2 to 1.0 mm (about 25 g); shorten the tower again. Nothing else can go without a redesign.
- **Print weight is a rule of thumb.** Masses follow v1's rule (volume x 1.27 x 0.75). Thin-walled parts print nearly solid, chunky ones lighter, so real prints may differ by a few
  hundred grams either way. Weigh one wheel and one hood half and correct `FILL` in `params.py`.
- **Front-axle share** ended at 74 %, not the spec's 72 %, because the excavator ended up heavier than budgeted. It passes the 75 % limit with 1 point to spare only
  because the rear axle moved forward (with the original wheelbase of 300 mm it was 76 %). The limit is checked at the carry pose, which is how the rover drives when loaded;
  with a full drum and the arm left level it would be 78 %.
- **Cost.** INR 23,329 fits the cap of 25,000 with INR 1,700 to spare. Only the extrusion, the Johnson motors, the BTS7960 drivers, the ToF sensors and the corner brackets are store listings;
  everything else is an estimate (see `v2-order-list.md`). The PZEM-051 is booked at v1's INR 2,000 and is probably cheaper.
- **Not verified by a real print.** Every printability claim is geometric (no overhang steeper than 45 degrees off the bed or a bridge wider than 8 mm). Print the fit-test kit first.

## Open items for the team

1. Print the fit-test kit, set `TOL_BEARING`, `TOL_TRAP`, `TOL_HOLE`; measure one Johnson motor.
2. Order by 5 October (the list is ready).
3. Measure the boards, relay, PZEM and battery when they arrive; update `lib/cots.py` and `BATT`.
4. Mount the two lift limit switches and decide the carriage software limits (working range 20 to 79.5 mm).
5. Decide whether the 0.44 kg over the 7.5 kg goal matters enough to drop the cosmetic parts above.
