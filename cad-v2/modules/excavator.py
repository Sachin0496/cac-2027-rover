"""Excavator assembly for one arm angle (spec 7.3): pivot brackets, arms, drum and its drive, crossbar,
lever, links and the lift screw drive with its carriage.

`pose` is the arm angle in degrees (positive = raised). Arm-local frame: origin at the pivot, +X along the
arm, +Z perpendicular; the whole frame is rotated about the world y axis by -pose.
"""
from __future__ import annotations

from math import atan2, cos, degrees, hypot, radians, sin, sqrt, tan

from build123d import Axis, Cylinder, Location, Plane, Pos, Rot, mirror

from lib import cots, fasteners
from lib.model import Assembly, at, bought_item, printed_item
from lib.profile2020 import LIP_UNDERSIDE, extrusion
from lib.shapes import AX
from modules import arms, drive_parts, drum, lift
from params import (ARM_LEN, ARM_Y, BLOCK_HOLE_A, BLOCK_W, CARRIAGE_PIN_Z, LINK_T, COLORS, CROSSBAR_LEN, EAR_AT, LEVER_PIN_AT, LIFT, LINK_LEN, PIVOT_WALL_Y,
                    PIVOT_X, PIVOT_Z, RAIL_Y, RAIL_Z0, SCREW_X, SCREW_Z, TUBE, Y_DRUM)

Y0, Y1 = ARM_Y
Z_TOP_SLOT = RAIL_Z0 + TUBE / 2 + LIP_UNDERSIDE            # lip underside of a top slot (134.2)
G, YEL, BLK, STEEL = COLORS["graphite"], COLORS["yellow"], COLORS["black"], COLORS["steel"]
LUG = drum.LUG_ANGLES
HEXDIR = (cos(radians(LUG[0])), 0, sin(radians(LUG[0])))     # bolt-head flats match the drum plate pocket
TIE_LEN, TIE_Z0 = 211.0, -5.5


def arm_frame(pose: float) -> Location:
    return Pos(PIVOT_X, 0, PIVOT_Z) * Rot(0, -pose, 0)


def pin_world(pose: float, local):
    """World (x, z) of an arm-local point (along, up)."""
    a, u = local
    t = radians(pose)
    return (PIVOT_X + a * cos(t) - u * sin(t), PIVOT_Z + a * sin(t) + u * cos(t))


def carriage_x(pose: float) -> float:
    px, pz = pin_world(pose, LEVER_PIN_AT)
    return px - sqrt(LINK_LEN ** 2 - (pz - CARRIAGE_PIN_Z) ** 2)


def _hw(asm, id_, part, shape, loc, sku, module="excavator", moving=None, color=STEEL):
    asm.add(bought_item(id_, part, module, shape, loc, color, fasteners.steel_mass_g(shape), sku=sku, moving=moving))


def _flip_about_lug_axis() -> Location:
    """180 deg rotation about the axis at LUG[0] degrees: maps the drum lug pattern onto itself."""
    a = LUG[0]
    return Rot(0, 0, a) * Rot(180, 0, 0) * Rot(0, 0, -a)


def _brackets_and_pivots(asm: Assembly) -> None:
    b = arms.pivot_bracket()
    for side, sy in (("l", 1), ("r", -1)):
        local = b if sy > 0 else mirror(b, Plane.XZ)
        asm.add(printed_item(f"pivot_bracket_{side}", f"pivot_bracket_{side}", "excavator", local, Pos(PIVOT_X, 0, 0), G,
                             orient=Rot(90, 0, 0) if sy > 0 else Rot(-90, 0, 0)))
        for x in (-20.0, 20.0):                                    # ears bolt into the rail's top slot (M5 x 10)
            _hw(asm, f"br_bolt_{side}{x:+.0f}", "bolt_m5x10", fasteners.bolt(5, 10, "button"),
                at((PIVOT_X + x, sy * RAIL_Y, 139.8), (0, 0, -1), (1, 0, 0)), "M5x10 button")
            _hw(asm, f"br_tnut_{side}{x:+.0f}", "tnut_m5", fasteners.tnut(),
                at((PIVOT_X + x, sy * RAIL_Y, Z_TOP_SLOT), (0, 0, -1), (0, 1, 0)), "T-nut M5 spring")
        # pivot bolt: head on the wall's outer face, washer spacer, 608 in the arm root, inner washer, nyloc nut
        wy1 = PIVOT_WALL_Y[1]
        pv = lambda y, zd: at((PIVOT_X, sy * y, PIVOT_Z), (0, -sy * zd, 0), (1, 0, 0))
        _hw(asm, f"pivot_bolt_{side}", "bolt_m8x35", fasteners.bolt(8, 35, "hex"), pv(wy1, 1), "M8x35 hex")
        _hw(asm, f"pivot_washer_o_{side}", "washer_m8", fasteners.washer(8), pv(PIVOT_WALL_Y[0] - 1.6, -1), "M8 washer")
        _hw(asm, f"pivot_washer_i_{side}", "washer_m8", fasteners.washer(8), pv(Y1 - 8.8, -1), "M8 washer")
        _hw(asm, f"pivot_nut_{side}", "nut_m8_nyloc", fasteners.nut(8, nyloc=True), pv(Y1 - 16.8, -1), "M8 nyloc")
        yb0 = Y1 - 7.2 if sy > 0 else -(Y1 - 7.2) - 7.0             # 608 in the arm root pocket, 0.2 mm recessed
        asm.add(bought_item(f"pivot_bearing_{side}", "bearing_608", "excavator", cots.bearing_608(),
                            Pos(PIVOT_X, yb0, PIVOT_Z), G, cots.MASS_G["bearing_608"], sku="bearing_608"))


def _tof_front(asm: Assembly) -> None:
    """Front ToF sensors on the bracket pads, normal 25 degrees below the forward horizontal."""
    tilt = radians(25.0)
    n = (cos(tilt), 0.0, -sin(tilt))
    t = (sin(tilt), 0.0, cos(tilt))
    for tag, sy in (("l", 1), ("r", -1)):
        p = (PIVOT_X + 25.0 + 7.0 * tan(tilt), sy * 178.0, 185.0)
        face = tuple(p[k] + 3.0 * n[k] for k in range(3))
        asm.add(bought_item(f"tof_front_{tag}", "tof_vl53", "excavator", at(p, n, t) * cots.tof_board(), Pos(0, 0, 0), BLK, 2.5,
                            sku="tof_vl53", sensor={"origin": face, "dir": n, "full_angle": 27.0}))


def _lift_static(asm: Assembly) -> None:
    fe = LIFT["feet"]
    asm.add(printed_item("lift_channel", "lift_channel", "excavator", lift.channel(), Pos(0, 0, 0), G))
    rear = LIFT["block_rear_x"][0]
    asm.add(printed_item("lift_block_r", "lift_bearing_block", "excavator", lift.bearing_block(), Pos(rear, 0, 0), G,
                         orient=Rot(0, 90, 0)))
    asm.add(printed_item("lift_block_f", "lift_bearing_block", "excavator", lift.bearing_block(),
                         Pos(LIFT["block_front_x"][1], 0, 0) * Rot(0, 0, 180), G, orient=Rot(0, 90, 0)))
    asm.add(printed_item("lift_cradle_base", "lift_cradle_base", "excavator", lift.cradle_base(), Pos(0, 0, 0), G))
    asm.add(printed_item("lift_cradle_cap", "lift_cradle_cap", "excavator", lift.cradle_cap(), Pos(0, 0, 0), G,
                         orient=Rot(180, 0, 0)))
    x0, x1 = SCREW_X
    screw = Pos(x0, 0, SCREW_Z) * Rot(0, 90, 0) * Cylinder(4.0, x1 - x0, align=AX)
    asm.add(bought_item("lift_screw", "m8_rod", "excavator", screw, Pos(0, 0, 0), STEEL, 60.0, sku="M8 threaded rod 150 mm"))
    asm.add(bought_item("lift_coupler", "coupler", "excavator", cots.coupler_6_8(),
                        Pos(LIFT["coupler_x0"], 0, SCREW_Z) * Rot(0, 0, -90), COLORS["alu"], cots.MASS_G["coupler"], sku="coupler_6_8"))
    asm.add(bought_item("lift_motor", "motor", "excavator", cots.motor_johnson(),
                        Pos(LIFT["motor_gear_face_x"], 0, SCREW_Z) * Rot(0, 0, -90), BLK, cots.MASS_G["motor"],
                        sku="motor_johnson_300rpm"))
    for tag, xb in (("r", LIFT["block_rear_x"][1] - 7.0), ("f", LIFT["block_front_x"][0])):
        asm.add(bought_item(f"lift_bearing_{tag}", "bearing_608", "excavator", cots.bearing_608(),
                            Pos(xb, 0, SCREW_Z) * Rot(0, 0, -90), G, cots.MASS_G["bearing_608"], sku="bearing_608"))
    for k, (x, y) in enumerate(fe):
        top = y == 0.0 and x < 84
        _hw(asm, f"lift_foot_{k}", "bolt_m5x8", fasteners.bolt(5, 8, "button"), at((x, y, 138.8), (0, 0, -1), (1, 0, 0)), "M5x8 button")
        _hw(asm, f"lift_foot_tnut_{k}", "tnut_m5", fasteners.tnut(), at((x, y, Z_TOP_SLOT), (0, 0, -1), (0, 1, 0) if top else (1, 0, 0)),
            "T-nut M5 spring")
    iw = LIFT["inner_w"] / 2
    for k, x in enumerate(lift.CROSS_BOLT_X):
        _hw(asm, f"lift_cross_bolt_{k}", "bolt_m4x40", fasteners.bolt(4, 40, "socket"),
            at((x, -iw - lift.CHANNEL_WALL, lift.CROSS_BOLT_Z), (0, 1, 0), (1, 0, 0)), "M4x40 socket")
        _hw(asm, f"lift_cross_nut_{k}", "nut_m4_nyloc", fasteners.nut(4, nyloc=True),
            at((x, iw + lift.CHANNEL_WALL, lift.CROSS_BOLT_Z), (0, 1, 0), (1, 0, 0)), "M4 nyloc")
    for s in (-1, 1):
        _hw(asm, f"lift_cradle_bolt_{s:+d}", "bolt_m4x30", fasteners.bolt(4, 30, "socket"),
            at((lift.CRADLE_BOLT_X, s * lift.CRADLE_BOLT_Y, lift.GEAR_Z + lift.SADDLE_R + 3.0), (0, 0, -1), (1, 0, 0)), "M4x30 socket")
        _hw(asm, f"lift_cradle_nut_{s:+d}", "nut_m4", fasteners.nut(4),
            at((lift.CRADLE_BOLT_X, s * lift.CRADLE_BOLT_Y, lift.GEAR_Z - 4.1), (0, 0, 1), (1, 0, 0)), "M4 nut")
    for k, x in enumerate(lift.CRADLE_FEET_X):
        _hw(asm, f"lift_cradle_foot_{k}", "bolt_m5x10", fasteners.bolt(5, 10, "button"),
            at((x, 0, lift.GEAR_Z - lift.SADDLE_R - 3.2), (0, 0, -1), (1, 0, 0)), "M5x10 button")
        _hw(asm, f"lift_cradle_foot_tnut_{k}", "tnut_m5", fasteners.tnut(), at((x, 0, Z_TOP_SLOT), (0, 0, -1), (0, 1, 0)),
            "T-nut M5 spring")


def _arms_and_drum(asm: Assembly, pose: float) -> None:
    A = arm_frame(pose)
    ad, ai, cap = arms.arm_drive(), arms.arm_idler(), arms.arm_motor_cap()
    asm.add(printed_item("arm_drive", "arm_drive", "excavator", ad, A, YEL, orient=Rot(90, 0, 0), moving="arm"))
    asm.add(printed_item("arm_idler", "arm_idler", "excavator", mirror(ai, Plane.XZ), A, YEL, orient=Rot(-90, 0, 0), moving="arm"))
    asm.add(printed_item("arm_motor_cap", "arm_motor_cap", "excavator", cap, A * Pos(ARM_LEN, 0, 0), YEL,
                         orient=Rot(180, 0, 0), moving="arm"))
    _crossbar_lever_links_carriage(asm, pose, A)
    _drum_and_drive(asm, pose, A)


def _crossbar_lever_links_carriage(asm: Assembly, pose: float, A: Location) -> None:
    ea, eu = EAR_AT
    bar = Pos(0, -CROSSBAR_LEN / 2, 0) * Rot(-90, 0, 0) * extrusion(CROSSBAR_LEN)
    asm.add(bought_item("crossbar", "crossbar", "excavator", bar, A * Pos(ea, 0, eu), COLORS["alu"], 0.5 * CROSSBAR_LEN,
                        kind="stock", moving="arm", sku="2020 T-slot", cut_mm=CROSSBAR_LEN))
    cb = arms.clamp_block()
    for tag, sy in (("l", 1), ("r", -1)):
        loc = A * Pos(ea, sy * 98.0, eu) * (Rot(0, 0, 0) if sy > 0 else Rot(0, 0, 180))
        asm.add(printed_item(f"clamp_block_{tag}", "clamp_block", "excavator", cb, loc, G, orient=Rot(90, 0, 0), moving="arm"))
        for da in (-BLOCK_HOLE_A, BLOCK_HOLE_A):
            _hw(asm, f"clamp_screw_{tag}{da:+.0f}", "bolt_m4x25", fasteners.bolt(4, 25, "socket"),
                A * at((ea + da, sy * (Y1 - 4.6), eu), (0, -sy, 0), (1, 0, 0)), "M4x25 socket", moving="arm")
            _hw(asm, f"clamp_nut_{tag}{da:+.0f}", "nut_m4", fasteners.nut(4),
                A * at((ea + da, sy * 90.0, eu), (0, sy, 0), (cos(radians(30)), 0, sin(radians(30)))), "M4 nut", moving="arm")
        _crossbar_clamp_hw(asm, f"cb_{tag}", A, ea, eu, sy * 98.0)
    lv = arms.lever()
    asm.add(printed_item("lever", "lever", "excavator", lv, A * Pos(ea, 0, eu), YEL, orient=Rot(90, 0, 0), moving="arm"))
    _crossbar_clamp_hw(asm, "cb_lever", A, ea, eu, 0.0, faces=("f", "d"))
    # links and pins
    p1 = pin_world(pose, LEVER_PIN_AT)
    x_c = carriage_x(pose)
    p2 = (x_c, CARRIAGE_PIN_Z)
    dx, dz = p2[0] - p1[0], p2[1] - p1[1]
    psi = -degrees(atan2(dz, dx))
    for tag, y_off in (("a", 8.4), ("b", -8.4 - LINK_T)):
        asm.add(printed_item(f"link_{tag}", "lift_link", "excavator", arms.link(), Pos(p1[0], y_off, p1[1]) * Rot(0, psi, 0), G,
                             orient=Rot(90, 0, 0), moving="arm"))
    for tag, p, mv in (("lever", p1, "arm"), ("carriage", p2, "carriage")):
        _hw(asm, f"pin_{tag}", "bolt_m5x35", fasteners.bolt(5, 40, "socket"), at((p[0], -8.4 - LINK_T - 5.0, p[1]), (0, 1, 0), (1, 0, 0)),
            "M5x40 socket", moving=mv)
        _hw(asm, f"pin_nut_{tag}", "nut_m5_nyloc", fasteners.nut(5, nyloc=True), at((p[0], 8.4 + LINK_T, p[1]), (0, 1, 0), (1, 0, 0)),
            "M5 nyloc", moving=mv)
    # carriage with its brass nut
    asm.add(printed_item("lift_carriage", "lift_carriage", "excavator", lift.carriage(), Pos(x_c, 0, 0), G, moving="carriage"))
    h = LIFT["carriage_len"] / 2
    for tag, x0 in (("a", x_c - h - 0.5 + 0.2), ("b", x_c + h - 6.7 + 0.2)):
        nut = fasteners.nut(8)
        asm.add(bought_item(f"lift_nut_{tag}", "m8_brass_nut", "excavator", at((x0, 0, SCREW_Z), (1, 0, 0), (0, 0, 1)) * nut, Pos(0, 0, 0),
                            COLORS["brass"], 9.0, sku="M8 brass nut", moving="carriage"))


def _crossbar_clamp_hw(asm, tag, A, ea, eu, y_c, faces=("u", "d")) -> None:
    """M5 x 16 screws through the block wall into T-nuts under the lip of the crossbar's slots."""
    half = BLOCK_W / 2
    for f in faces:
        d = {"u": (0, 0, 1), "d": (0, 0, -1), "f": (1, 0, 0), "b": (-1, 0, 0)}[f]
        xd = (0, 0, 1) if f in "fb" else (1, 0, 0)
        _hw(asm, f"{tag}_screw_{f}", "bolt_m5x16", fasteners.bolt(5, 16, "socket"),
            A * at((ea + d[0] * half, y_c, eu + d[2] * half), (-d[0], 0, -d[2]), xd), "M5x16 socket", moving="arm")
        _hw(asm, f"{tag}_tnut_{f}", "tnut_m5", fasteners.tnut(),
            A * at((ea + d[0] * LIP_UNDERSIDE, y_c, eu + d[2] * LIP_UNDERSIDE), (-d[0], 0, -d[2]), xd), "T-nut M5 spring", moving="arm")


def _drum_and_drive(asm: Assembly, pose: float, A: Location) -> None:
    D = A * Pos(ARM_LEN, 100.0, 0) * Rot(90, 0, 0)                   # drum local z -> arm y = 100 - z, local y -> up
    plate, ringA, ringB = drum.plate(), drum.ring(0), drum.ring(45)
    asm.add(printed_item("drum_plate_1", "drum_plate", "excavator", plate, D, YEL, moving="arm"))
    asm.add(printed_item("drum_plate_2", "drum_plate", "excavator", plate, D * Pos(0, 0, 200) * _flip_about_lug_axis(), YEL, moving="arm"))
    for i in range(4):
        r, name = (ringA, "drum_ring_a") if i % 2 == 0 else (ringB, "drum_ring_b")
        asm.add(printed_item(f"drum_ring_{i}", name, "excavator", r, D * Pos(0, 0, 4 + 48 * i), YEL, moving="arm"))
    for k, a in enumerate(LUG):                                       # M4 tie rods and nyloc nuts
        rod = Pos(drum.LUG_R * cos(radians(a)), drum.LUG_R * sin(radians(a)), TIE_Z0) * Cylinder(2.0, TIE_LEN, align=AX)
        asm.add(bought_item(f"tie_rod_{k}", "tie_rod", "excavator", D * rod, Pos(0, 0, 0), STEEL, 20.0, sku="M4 threaded rod 211 mm",
                            moving="arm"))
        for z, zd in ((-5.0, 1), (205.0, -1)):
            nut = fasteners.nut(4, nyloc=True)
            _hw(asm, f"tie_nut_{k}_{'a' if z < 0 else 'b'}", "nut_m4_nyloc", nut,
                D * at((drum.LUG_R * cos(radians(a)), drum.LUG_R * sin(radians(a)), z + (0 if zd > 0 else 0)), (0, 0, zd), (1, 0, 0)),
                "M4 nyloc", moving="arm")
    # drive side (left): bolt head in the plate pocket, spacers, two 608 in the arm, coupler, motor
    yb = Y_DRUM["bolt_head_underside"]
    _hw(asm, "drum_bolt_l", "bolt_m8x70", fasteners.bolt(8, Y_DRUM["bolt_len"], "hex"), A * at((ARM_LEN, yb, 0), (0, 1, 0), HEXDIR),
        "M8x70 hex", moving="arm")
    Y = lambda k: Y_DRUM[k]
    axis = lambda y0, zd=(0, 1, 0): A * at((ARM_LEN, y0, 0), zd, (1, 0, 0))
    asm.add(printed_item("drum_s1_l", "axle_spacer_62", "excavator", drum.spacer_long(6.2), A * Pos(ARM_LEN, Y("spacer_s1")[0], 0) * Rot(-90, 0, 0), G, moving="arm"))
    asm.add(printed_item("drum_mid_l", "axle_spacer_drum_mid", "excavator", drum.spacer_long(18.6), A * Pos(ARM_LEN, Y("spacer_mid")[0], 0) * Rot(-90, 0, 0), G, moving="arm"))
    asm.add(printed_item("drum_end_l", "axle_spacer_end", "excavator", drive_parts.spacer(2.5), A * Pos(ARM_LEN, Y("spacer_end")[0], 0) * Rot(-90, 0, 0), G, moving="arm"))
    for tag, k in (("1", "bearing_1"), ("2", "bearing_2")):
        asm.add(bought_item(f"drum_bearing_{tag}", "bearing_608", "excavator", cots.bearing_608(), A * Pos(ARM_LEN, Y(k)[0], 0), G,
                            cots.MASS_G["bearing_608"], sku="bearing_608", moving="arm"))
    _hw(asm, "drum_washer_l", "washer_m8", fasteners.washer(8), axis(Y("washer")[0]), "M8 washer", moving="arm")
    _hw(asm, "drum_nut_l", "nut_m8_nyloc", fasteners.nut(8, nyloc=True), axis(Y("nut")[0]), "M8 nyloc", moving="arm")
    asm.add(bought_item("drum_coupler", "coupler", "excavator", cots.coupler_6_8(), A * Pos(ARM_LEN, Y("coupler")[1], 0) * Rot(0, 0, 180), COLORS["alu"],
                        cots.MASS_G["coupler"], sku="coupler_6_8", moving="arm"))
    asm.add(bought_item("drum_motor", "motor", "excavator", cots.motor_johnson(),
                        A * Pos(ARM_LEN, Y("gear_face"), 0) * Rot(0, 0, 180), BLK, cots.MASS_G["motor"], sku="motor_johnson_30rpm", moving="arm"))
    for s in (-1, 1):
        _hw(asm, f"arm_cap_bolt_{s:+d}", "bolt_m4x30", fasteners.bolt(4, 30, "socket"),
            A * at((ARM_LEN + s * arms.CLAMP_A, (Y("clamp")[0] + Y("clamp")[1]) / 2, arms.GEAR_AXIS_U + arms.SADDLE_R + 3.0), (0, 0, -1), (1, 0, 0)),
            "M4x30 socket", moving="arm")
        _hw(asm, f"arm_cap_nut_{s:+d}", "nut_m4", fasteners.nut(4),
            A * at((ARM_LEN + s * arms.CLAMP_A, (Y("clamp")[0] + Y("clamp")[1]) / 2, arms.GEAR_AXIS_U - 4.1), (0, 0, 1), (1, 0, 0)),
            "M4 nut", moving="arm")
    # idler side (right): mirrored stack, bolt head in the second plate's pocket, one 608 in the arm
    _hw(asm, "drum_bolt_r", "bolt_m8x40", fasteners.bolt(8, 40, "hex"), A * at((ARM_LEN, -yb, 0), (0, -1, 0), HEXDIR),
        "M8x40 hex", moving="arm")
    asm.add(printed_item("drum_s1_r", "axle_spacer_62", "excavator", drum.spacer_long(6.2), A * Pos(ARM_LEN, -Y("spacer_s1")[0], 0) * Rot(90, 0, 0), G, moving="arm"))
    asm.add(bought_item("drum_bearing_r", "bearing_608", "excavator", cots.bearing_608(),
                        A * Pos(ARM_LEN, -Y("bearing_1")[1], 0), G, cots.MASS_G["bearing_608"], sku="bearing_608", moving="arm"))
    asm.add(printed_item("drum_s2_r", "axle_spacer_62", "excavator", drum.spacer_long(6.2), A * Pos(ARM_LEN, -Y("bearing_1")[1] - 6.2, 0) * Rot(-90, 0, 0), G, moving="arm"))
    _hw(asm, "drum_washer_r", "washer_m8", fasteners.washer(8), A * at((ARM_LEN, -119.4, 0), (0, -1, 0), (1, 0, 0)), "M8 washer", moving="arm")
    _hw(asm, "drum_nut_r", "nut_m8_nyloc", fasteners.nut(8, nyloc=True), A * at((ARM_LEN, -121.0, 0), (0, -1, 0), (1, 0, 0)), "M8 nyloc", moving="arm")


def build(asm: Assembly, pose: float) -> None:
    _brackets_and_pivots(asm)
    _tof_front(asm)
    _lift_static(asm)
    _arms_and_drum(asm, pose)
