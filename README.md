# CAC 2027 Rover

Our entry for the Caterpillar Autonomy Challenge 2027 (Shaastra, IIT Madras): a small,
light lunar-construction rover that crosses an obstacle field, digs sand, carries it and
builds a berm — first by remote control, then autonomously.

- **Start here:** [CONTEXT.md](CONTEXT.md) — rules, scoring, strategy, design, budget, timeline, risks.
- **Parts and budget:** [hardware/bom.csv](hardware/bom.csv) — update `purchase_status` as things arrive.

## Planned layout

```
cad/        STEP/STL exports + link to the Onshape document
hardware/   BOM, wiring diagram, power budget
firmware/   ESP32 motor/sensor firmware
ros2_ws/    ROS 2 Jazzy workspace (teleop, drivers, localisation, mission state machine)
docs/       inspection checklist, mock-run logs, test results
```
