# CAC 2027 Rover — Project Context

Single source of truth for the team (and for any AI assistant helping us).
Last updated: **2026-09-29** (v2 CAD added: see §10). Rules below are a summary of the official CAC 2027
problem statement — always check the latest PDF (links in §16) before relying on a number.

---

## 1. The challenge in one paragraph

The **Caterpillar Autonomy Challenge (CAC) 2027** is run by Shaastra (IIT Madras's tech fest)
and sponsored by Caterpillar. The rules are adapted from NASA Lunabotics. We build a
lunar-construction rover that starts at a random pose, crosses an obstacle field in a
sandbox, digs sand in the excavation zone, **carries** it (bulldozing is not allowed) and dumps
it into a berm target. Scoring = berm volume normalised by **robot mass** and **energy used**,
plus large bonuses for **autonomy**.

## 2. Key dates, prizes, team rules

| What | When |
|---|---|
| Registration closes (Unstop, free) | **30 Sep 2026, 00:00 IST** |
| Video round: working rover on sand (non-competitive, required) | 10 Oct – 10 Nov 2026 |
| Prelims at IIT Madras: 1 attempt, 10-min run | 2 Jan 2027 (tentative) |
| Finale: 1 attempt, 7-min setup, 15-min run, 5-min removal | 3 Jan 2027 (tentative) |

- **Prizes (₹3.5 L total):** Winner ₹1.25 L · 1st runner-up ₹95k · 2nd runner-up ₹70k ·
  Best Design ₹30k · Judges' Innovation ₹30k.
- **Team:** 1–12 students, any discipline, any college. Max **4** people in Mission Control
  (MCC) and max **4** in the arena for setup/removal. No faculty in the arena or MCC.
- **2026 results:** Winner Team Algo Steam (Sri Eshwar College of Engineering, also Best Design);
  runner-up Team Anveshak (IIT Madras); 2nd runner-up Team Rodix (KPR Institute).
  The organisers' 2027 resources guide says many 2026 teams **had trouble with mobility**.

## 3. Arena (from the 2027 diagram, which is "for reference only")

- ~9 m × 5 m box, ~30 cm of tilled, dry sand.
- **Start zone** (~2 m, top-left, no obstacles) → **Obstacle zone** (~5.5 m) →
  **Excavation zone** (~1.5 m wide strip at the far end).
- **Construction zone** ~2 m × 1.5 m at the bottom-left, next to the start zone;
  **berm target 1.25 m × 0.9 m**. ⇒ Every dig→dump cycle crosses the obstacle zone **twice**.
- Obstacle zone: **≥3 boulders** (30–40 cm diameter, random heights) and **≥3 craters**
  (up to 40–50 cm wide). Smaller boulders may also be in the excavation zone.
- Start position and heading are random (judges spin N/S/E/W). The robot must carry 3 marked
  arrows: length, width and a "forward" reference.

## 4. Robot rules that shape our design

- **Size/mass:** stowed ≤ 1.5 × 0.75 × 0.75 m (may deploy up to +1.75 m in height after the
  start). ≤ 80 kg including any beacons.
- **Banned:** GPS; compass/magnetometer (must be disabled and explained to judges); ultrasonic
  sensors; touch/bump sensors; pneumatic rubber tyres; air- or foam-filled tyres; hydraulics.
  Closed pneumatics only if fully self-contained.
- **No walls:** the robot must not use arena walls for sensing, mapping or collision avoidance,
  and we must prove it. Not disclosing the autonomy sensing method = disqualification.
- **No line-of-sight driving (new in 2027):** operators may only use data/video from the robot
  and the competition monitors.
- **Sand:** only from the excavation zone; must be carried (a small lift is enough). Don't touch
  rocks or cross craters in the obstacle zone (allowed in the excavation zone).
- **Penalties:** wall ram −50 (twice), 3rd ram cancels the run. The robot must move within
  5 min of the timer starting or the run ends.
- **E-stop:** unmodified off-the-shelf red mushroom button, ≥40 mm, twist/pull to reset, one per
  robot. One press must disconnect the battery from **all** controllers (a relay is fine if it
  fails open). An onboard computer may run on its own separate battery.
- **Energy logger:** off-the-shelf logger (organisers' example: PZEM-051) wired **between the
  battery and the E-stop**, mounted high and visible. Wrong wiring = −30 on BCP-energy.
- **Comms:** our own unmodified dual-band 802.11 router (2.4 GHz must be switchable off),
  assigned SSID, WPA2/3, no hidden SSID, 20 MHz channels on 2.4 GHz, no amplifiers; 5 GHz
  allowed. **Average link ≤ 4,000 kbps.** Organisers provide no Wi-Fi. No 2.4 GHz Zigbee;
  Bluetooth class 2/3 only.
- **Markers/beacons:** max 5 (all markers or all beacons) or 2 beacons + 3 markers. Placed on the
  start-zone frame (2 sides) plus one on the start-zone wall; not in the obstacle zone, berm
  zone, other walls, floor or ceiling. Markers ≤ 25 × 25 cm, ≤ 60 cm high, one tag per marker.
  Lasers Class I/II (<5 mW) with eye-safety documentation. The robot must detect and interpret
  markers onboard — no human-in-the-loop.
- **Autonomy mode:** "hands-free" — nobody touches any control device. Announce every start,
  end and failure of an autonomy attempt to the Mission Control Judge **before** doing it.

## 5. Scoring

| Component | Formula / points |
|---|---|
| BCP-mass | V (cm³ above grade, inside target) ÷ (run minutes × robot kg) **× 4.4** |
| BCP-energy | V ÷ (run minutes × Wh used) **× 1.5** |
| Arena cameras | none used = **+120** · first camera (≤60 s) = +60 · second = 0. Onboard cameras are free. |
| Autonomy | see table below |

Organisers' worked example: 77,551 cm³, 15 min, 66 kg, 36 Wh →
344.6 (mass) + 215.4 (energy) + 60 (one arena camera) + 75 (autonomy) = **695**.

| Autonomy tier | Points | Conditions |
|---|---|---|
| Excavation | 75 | **Every** dig autonomous; bucket out of the sand before returning to remote control |
| Dump | 50 | **Every** dump autonomous; hand over to the computer **before** entering the construction zone |
| Travel | 250 | Hands-free from the start zone → excavation zone → construction zone. −30 one-time contact penalty; −50 if attempted after an RC crossing ("breadcrumbs"); no "point and traverse" |
| Full, 1 cycle | 450 | From the run start: traverse, dig, return, dump. May switch to RC afterwards |
| Full, 2+ cycles | 600 | Whole run hands-free, ≥2 cycles, berm points scored. −30 per rock/crater contact (cap −90) |

The resources guide lists possible autonomy totals of 50, 75, 125, 250, 300, 375, 450 and 600,
so the lower tiers appear to stack (e.g. travel + dig + dump = 375). **Confirm with organisers.**

## 6. Our strategy (decided 2026-09-28)

- **Small, light rover (~8–12 kg).** Scoring divides by mass: 12 L of sand in a 15-min run from a
  10 kg robot ≈ 12,000 ÷ (15 × 10) × 4.4 ≈ **352 mass points** — about the same as the
  organisers' 66 kg example moving 77 L.
- **Budget ≤ ₹25k, v1 ≈ ₹22k** (≈ ₹19k if the college provides filament). Excludes the
  Raspberry Pis (we have several), a borrowed router, laptops, the college 3D printer and travel.
- **Excavator = rotating bucket drum** (research-backed, see `docs/v1-build-guide.md`): a light
  rover can't push a front bucket through sand, but a drum takes small bites, and one part
  digs, carries and dumps.
- **Autonomy ladder:** 125 (auto dig + dump) → 375 (+ travel) → **450** (one clean autonomous
  cycle at the run start, then remote control to build berm volume). Go for 600 only if
  practice runs show almost every full cycle succeeding.
- **Never use the arena cameras** (+120) → onboard video must be good enough to drive by.
- **Why not bank on 600:** reliability compounds. One cycle ≈ 10 steps; at 95% success per step a
  cycle succeeds ~60% of the time and two cycles ~36%. At 99% per step: ~90% and ~82%.
- **No VLM/LLM in the control loop.** The mission is a fixed script; use a state machine.
  There is no internet in MCC, so everything runs onboard.

## 7. System design

The v1 CAD model is in `cad/` (open `cad/rover.scad`); the build guide with cut, print and
hardware lists is `docs/v1-build-guide.md`.

### Mechanical (v1)
- 4-wheel skid steer on **Johnson 12 V geared motors, ~30 RPM** (torque first; ~0.27 m/s). The
  100 RPM version is only ~5.7 kg·cm, weak for loose sand. Motors hang under the rail corners in
  printed clamps that also tie each rail to its cross member.
- **3D-printed grouser wheels:** 174 mm over 14 grousers, 60 mm wide, directly on the D-shafts
  with the wheel load right at the gearbox face (outboard 608 bearings are an optional upgrade).
- **Bucket drum** on the front: 160 mm shell, 200 mm long, 8 scoops in two rings clocked 45°,
  internal spiral baffles, ~1.4 L usable. Spins ~30 RPM on a Johnson motor clamped in the left arm.
- **Lift:** two printed arms pivot on the rail ends; a lever and two pushrods connect them to a
  **printed lead-screw actuator** on the deck (M8 rod, ~300 RPM Johnson, ~6 mm/s, 83 mm stroke,
  self-locking). Arm −25° press / −20° dig / +35° carry.
- 20 × 20 aluminium tube frame (420 × 300), 6 mm plywood deck. Stowed 632 × 440 × 581 mm,
  ~7.5 kg empty (estimate), 80 % of the loaded weight on the front axle.
- Sealed printed electronics box, vented driver hood, dust covers.

### Electrical
```
3S Li-ion pack (≥20 A BMS) → PZEM-051 logger → E-stop (+ relay) → main fuse
    ├─ BTS7960 × 2 → drive motors (left side / right side)
    ├─ BTS7960 × 1 → drum motor
    ├─ BTS7960 × 1 → lift actuator motor
    └─ 5 V / 5 A buck → Raspberry Pi 5 → ESP32, sensors
```
- Powering the Pi from the main pack (after the logger) means **all** energy is logged — the
  simplest story at inspection. A separate Pi battery is allowed, but be ready to justify energy.
- Check the BMS current rating against the motors' stall currents; fuse every branch.

### Compute and sensors
- **Raspberry Pi 5 (4 GB)**; a second Pi can take the vision work if one is too slow.
- **ESP32** for motor PWM, encoders and limit switches (real-time jobs off the Pi).
- **1 USB webcam on an SG90 pan mount:** faces forward for driving, turns back to see AprilTags.
- **3 × VL53L1X laser ToF sensors** as the hazard detector: two on plates ahead of the front
  wheels looking 35° down the wheel tracks, one on the mast looking backwards for reversing.
  Rock = range shorter than flat ground; crater = range longer / no return. Class 1 laser →
  allowed (bring the datasheet). Use the XSHUT pins to give each sensor its own I²C address.
- **MPU6050 IMU** (6-axis, no magnetometer → nothing to explain for the compass rule).

### Software (Ubuntu 24.04 + ROS 2 Jazzy on the Pi 5)
- **Teleop:** joystick → `cmd_vel`; H.264 video via GStreamer at ~1–1.5 Mbps (inside the 4 Mbps cap).
- **Drivers:** ESP32 bridge (serial or micro-ROS), IMU, ToF, camera, `apriltag_ros`.
- **Localisation:** `robot_localization` EKF fusing gyro + wheel odometry + AprilTag fixes.
  Expect good fixes near the start/construction zones and dead-reckoning across the obstacle field.
  Rule of thumb (estimate): a 25 cm tag is detectable to ~5 m at 640×480 and ~8 m at 1280×720.
- **Hazards and planning:** ToF hazards on a ~10 cm grid of the known arena layout; A* or
  bug-style avoidance toward the goal. **Not** a fixed path — that is penalised.
- **Mission state machine:** LOCALISE → TRAVERSE → DIG → RETURN → ALIGN → DUMP → repeat.
  Every state gets a timeout and a recovery (back up, retry the dig, re-localise, or declare
  failure and hand over to RC).

## 8. Budget (v1 ≈ ₹22k) — full list in `hardware/bom.csv`

| Group | ₹ |
|---|---|
| 6 Johnson geared motors (4 drive + drum + actuator) | 3,000 |
| 4 BTS7960 motor drivers | 1,200 |
| Lift hardware (608 bearings, M8 rod and bolts, coupler, limit switches) | 570 |
| Fasteners + heat-set inserts | 700 |
| Aluminium tube (3 m) + plywood deck | 800 |
| 3 VL53L1X ToF sensors | 1,500 |
| USB webcam + SG90 pan servo | 1,150 |
| MPU6050 + ESP32 | 700 |
| 3S Li-ion pack (≥20 A BMS) + charger | 2,500 |
| E-stop, relay, fuses, connectors, wire, 5 V buck | 2,500 |
| PZEM-051 energy meter | 2,000 |
| ~3 kg PETG filament (v1 uses ~2.6 kg) | 3,000 |
| Practice sand pit + AprilTag prints | 1,000 |
| Spares | 1,500 |
| **Total** | **≈ 22,120** |

Prices marked "listed" in the CSV came from Indian store listings on 2026-09-28; everything else
is an estimate. The PZEM-051 is sold on Robu but its price wasn't visible.

## 9. 3D printing plan

- **Print:** 29 part types for v1 (list and quantities in `docs/v1-build-guide.md` §3; STLs in
  `cad/stl/`), all within a 220 × 220 mm bed and without supports. Also AprilTag stands
  (weighted bases, ≤60 cm).
- **Settings:** PETG (handles heat and knocks better than PLA), 3–4 walls, 20–25% gyroid infill;
  metal bolts as pivot pins; heat-set inserts wherever screws go into plastic.
- **Don't print:** the main load-bearing rails, the E-stop, the energy meter or the battery.
- The rules allow open honeycomb wheels as long as the edges aren't sharp. No foam.

## 10. CAD and tools

**Decision (2026-09-28): free tools only, no paid licences.**

- **OpenSCAD** (free) — the v1 model is written in OpenSCAD and is the editable master:
  `cad/rover.scad` (assembly), `cad/params.scad` (all shared dimensions), one file per
  subsystem. `check_interference.py` checks for collisions; `export.py` makes the STLs.
  Install on macOS: `brew install --cask openscad@snapshot` (the stable 2021 cask is disabled).
- **FreeCAD 1.1** (free, open-source, offline) — for viewing, measuring and new parts.
  `cad/rover_v1.FCStd` (and `rover_v1.step.zip` for other CAD) is generated from the OpenSCAD
  model by `export_freecad.py`; don't edit it by hand. Install: `brew install --cask freecad`.
- **Onshape (free Education plan)** — optional browser alternative if several people need to edit
  the same model at once; each person signs up with a student account.
- **v2 (2026-09-29): build123d, in `cad-v2/`.** Same concept, re-engineered: parametric Python CAD on the OpenCascade kernel (the one FreeCAD uses), scripted checks for every claim
  (`python tasks.py check`), B-rep STEP + watertight STLs, an interactive viewer (`cad-v2/out/rover_v2_viewer.html`). Guide: `docs/v2-build-guide.md`; ledger of changes: `docs/v2-changelog.md`;
  priced parts: `docs/v2-order-list.md` and `hardware/bom_v2.csv` (≈ ₹23.3k). Empty mass 7.94 kg with a 250 g wiring allowance (v1 ≈ 7.0 kg on the same accounting), front-axle share 74 % with a full drum (v1 80 %).
  v1 in `cad/` is untouched. Print the fit-test kit (`cad-v2/out/stl/fit_test_kit.stl`) before anything else.
- **Day 1:** a 1:1 cardboard mock-up to check the envelope and component layout before CAD.
- Why bother with CAD: envelope inspection, printing, and the ₹30k Best Design Award.

## 11. Timeline

| By | Milestone |
|---|---|
| 29 Sep | **Register on Unstop** (closes 30 Sep 00:00 IST) |
| 5 Oct | Cardboard mock-up + CAD v1; order all parts; build the sand pit |
| 20 Oct | Chassis driving on sand by remote; 3–4 wheel variants tested |
| 10 Nov | Dig + carry + dump by remote, driving from onboard video only → **submit video** |
| 30 Nov | Autonomous dig + dump (125); AprilTag localisation; ToF hazard detection |
| 20 Dec | Travel autonomy → one full autonomous cycle (450); **hardware freeze** |
| 20 Dec – 1 Jan | ≥20 full mock runs with real setup/run/removal timings; pack spares and checklists |
| 2–3 Jan | Prelims + finale at IIT Madras |

## 12. Team roles

- **Mechanical (2–3):** chassis, wheels, bucket, actuator, printing.
- **Electrical (1–2):** power, E-stop, logger, wiring, motor drivers, ESP32 firmware.
- **Software (2–3):** ROS 2, teleop/video, localisation, hazard detection, state machine.
- **Ops lead:** runs mock runs and checklists, owns the rules and inspection, talks to the judges.

## 13. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Rover bogs down in loose sand (the #1 problem flagged in 2026) | Wide grouser wheels, low-RPM motors, test in the pit from week 3, practise climbing out of a dug hole |
| Sand jams the actuator, bearings or motors | Sealed box, dust covers, lead-screw sleeve; clean after every session |
| Battery trips its BMS under load | ≥20 A BMS; measure stall currents; fuse each branch |
| Wi-Fi drops at the venue | Own router on 5 GHz; test with many phones nearby; keep video ≤1.5 Mbps |
| Failing inspection | E-stop and logger wired exactly per rules; ToF datasheet ready; written explanation of the autonomy sensing |
| Only one attempt per round | ≥20 timed mock runs; recovery behaviour in every state; spares kit |
| Localisation drift across the obstacle field | Re-localise on tags near start/construction; gyro-based heading; conservative speeds |
| ToF readings upset by sunlight or dust | Test in the actual lighting; shroud the sensors; have a camera-based fallback |

## 14. Open questions for the organisers

- May markers go anywhere other than the start-zone frame (e.g. the excavation zone)? The 2027
  list of banned zones doesn't mention it, but another rule limits them to the start-zone frame.
- Prelims setup time: 5 min (Unstop page) or 10 min (problem statement)?
- Is the arena indoors or outdoors, and what is the lighting?
- Is a separately powered onboard computer (e.g. a Pi on its own battery) fine for energy accounting?
- Do the autonomy tiers stack exactly (e.g. travel + dig + dump = 375)?
- Stowed height: 0.75 m in 2027 (vs 1 m in 2026) — confirm.

## 15. Research notes and upgrade path (if budget grows later)

- **Stereo on a Jetson:** Lite Any Stereo V2 (Imperial, Jun 2026) — ~81–101 ms/frame on a Jetson
  Orin NX, code released ([paper](https://www.alphaxiv.org/abs/2606.24457),
  [code](https://github.com/TomTomTommi/LiteAnyStereo)). NVIDIA Fast-FoundationStereo
  (CVPR 2026) — near-FoundationStereo accuracy at 10× speed, in Isaac ROS
  ([paper](https://www.alphaxiv.org/abs/2512.11130),
  [code](https://github.com/NVlabs/Fast-FoundationStereo)).
- **Tiny single-camera depth:** ZipDepth (Bologna, Jul 2026, 6.1M params, 34 FPS on Orin NX; 40–45 FPS
  on a laptop CPU — the Pi 5 will be much slower, worth a test) ([paper](https://www.alphaxiv.org/abs/2607.08771)).
  DepthART (Trento, Jul 2026, 6M params, relative + metric) ([paper](https://www.alphaxiv.org/abs/2607.17099)).
- **Heavy models for offline labelling:** Depth Anything 3 ([paper](https://www.alphaxiv.org/abs/2511.10647));
  Sept 2026 survey ([paper](https://www.alphaxiv.org/abs/2609.01172)).
- **Real-world scale cheaply:** VL53L5CX 8×8 ToF + completion model (KAIST/Microsoft, Aug 2026)
  ([paper](https://www.alphaxiv.org/abs/2608.04737)); PTC-Depth — scale from robot motion
  ([paper](https://www.alphaxiv.org/abs/2604.01791)).
- **Terrain:** LuMon — craters are the worst case for every off-the-shelf depth model; retraining on
  your own terrain is what helps ([paper](https://www.alphaxiv.org/abs/2604.09352)).
  PIVOT — VLM used only as a slow fallback to geometric planning ([paper](https://www.alphaxiv.org/abs/2609.20983)).
- **Localisation:** MDE-VIO — small depth model + VINS-Mono on a Jetson AGX Orin, better in low
  texture ([paper](https://www.alphaxiv.org/abs/2602.11323)).
- **Cautionary:** ISRO SAC "Depth-Aware Rover" — UniDepthV2 on a Raspberry Pi 4 took ~7 s per frame;
  stereo calibration kept drifting ([paper](https://www.alphaxiv.org/abs/2604.22331)).
- **Open-source Lunabotics ROS 2 code to borrow from:**
  [College of DuPage](https://github.com/College-of-DuPage-Lunabotics/lunabot_ros),
  [UMN GOFIRST](https://github.com/GOFIRST-Robotics/Lunabotics),
  [Purdue](https://github.com/PurdueLunabotics/purdue_lunabotics).

## 16. Links

- [CAC 2027 on Unstop](https://unstop.com/competitions/caterpillar-autonomy-challenge-iit-madras-1744114)
- [CAC 2027 problem statement (PDF)](https://d8it4huxumps7.cloudfront.net/uploads/attachements/files/3e1cd352-c27c-4d90-b096-f7b5276f3654.pdf)
- [CAC 2027 resources guide and scoring matrix (PDF)](https://d8it4huxumps7.cloudfront.net/uploads/attachements/files/7b2240d9-b289-4a9a-83d5-0ac939919f50.pdf)
- [CAC 2026 rulebook (PDF)](https://cac.shaastra.org/assets/CATERPILLAR%20AUTONOMY%20CHALLENGE_2026-Bo_P5MoA.pdf)
- [Lunabotics mobility workshop (video)](https://youtu.be/bEcldIPXE5c)
- [NASA Lunabotics systems-engineering videos](https://www.attwaterconsulting.com/NASA%20Lunabotics%20Videos.html)
