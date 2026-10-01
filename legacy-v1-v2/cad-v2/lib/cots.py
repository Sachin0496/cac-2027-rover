"""Purchased parts, modelled from listings / datasheets (measure-first where noted).

Local frames: motor, bearing, coupler have their axis along +Y (see each docstring).
PRICES: sku -> (unit price INR, basis 'listed'|'estimate', source, note). Used by the BOM generator.
"""
from __future__ import annotations

from build123d import Align, Box, Cylinder, Pos, Rot

from params import (B608_D, B608_ID, B608_W, JM_CAN_D, JM_CAN_LEN, JM_GEAR_D, JM_GEAR_LEN, JM_SHAFT_D,
                    JM_SHAFT_FLAT, JM_SHAFT_LEN, JM_SHAFT_OFF)

AX = (Align.CENTER, Align.CENTER, Align.MIN)
MASS_G = {"motor": 280.0, "bearing_608": 12.0, "coupler": 20.0, "corner_bracket": 10.0}

PRICES = {
    "motor_johnson_30rpm": (500, "listed", "Robokits / Robu", "Johnson 12 V ~30 RPM side-shaft (measure first)"),
    "motor_johnson_300rpm": (500, "estimate", "Robokits / Robu", "Johnson 12 V ~300 RPM (lift screw)"),
    "bearing_608": (35, "estimate", "local / Robu", "608-2RS"),
    "coupler_6_8": (200, "estimate", "Amazon.in / Robu", "flexible helical coupler 6 to 8 mm, D20 x L25"),
    "corner_bracket": (25, "estimate", "Amazon.in", "2020 inside corner bracket"),
}


def _along_y(shape):
    return Rot(-90, 0, 0) * shape          # maps local +Z to +Y


def motor_johnson(offset: float = JM_SHAFT_OFF):
    """Johnson side-shaft gearmotor. Shaft axis = +Y through the origin; gear face at y = 0; gearbox
    occupies y -25..0, can y -63..-25, shaft y 0..22. Gearbox and can axis sits `offset` above the shaft."""
    gear = Pos(0, -JM_GEAR_LEN, offset) * _along_y(Cylinder(JM_GEAR_D / 2, JM_GEAR_LEN, align=AX))
    can = Pos(0, -JM_GEAR_LEN - JM_CAN_LEN, offset) * _along_y(Cylinder(JM_CAN_D / 2, JM_CAN_LEN, align=AX))
    shaft = _along_y(Cylinder(JM_SHAFT_D / 2, JM_SHAFT_LEN, align=AX))
    # D-flat on the +Z side of the shaft: flat is JM_SHAFT_FLAT across (2.5 mm from the axis)
    flat_z = JM_SHAFT_FLAT - JM_SHAFT_D / 2
    shaft -= Pos(0, JM_SHAFT_LEN / 2, flat_z + 1.0) * Box(JM_SHAFT_D, JM_SHAFT_LEN, 2.0)
    return gear + can + shaft


def bearing_608():
    """608 ball bearing, axis +Y, y 0..7."""
    ring = Cylinder(B608_D / 2, B608_W, align=AX) - Cylinder(B608_ID / 2, B608_W, align=AX)
    return _along_y(ring)


def coupler_6_8():
    """Flexible coupler D20 x 25, axis +Y, y 0..25: 6 mm bore for y 0..12.5, 8 mm bore for y 12.5..25."""
    body = Cylinder(10, 25, align=AX)
    body -= Cylinder(3, 12.5, align=AX)
    body -= Pos(0, 0, 12.5) * Cylinder(4, 12.5, align=AX)
    return _along_y(body)


def corner_bracket():
    """2020 inside corner bracket: two 20 x 3 legs, 20 mm tall, meeting at the inner corner (origin).
    Leg A along +X (y 0..3), leg B along +Y (x 0..3); Ø5.5 holes at mid-leg, mid-height."""
    legA = Pos(10, 1.5, 10) * Box(20, 3, 20)
    legB = Pos(1.5, 10, 10) * Box(3, 20, 20)
    b = legA + legB
    b -= Pos(12, 1.5, 10) * Rot(90, 0, 0) * Cylinder(2.75, 4, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    b -= Pos(1.5, 12, 10) * Rot(0, 90, 0) * Cylinder(2.75, 4, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    return b


# ---------------------------------------------------------------- electronics (drop 3), sizes from listings; measure-first
BOARDS = {   # sku: (x, y, z, mass_g)
    "pi5": (85.0, 56.0, 24.0, 60.0),               # Raspberry Pi 5 with active cooler (the team has it: excluded from the BOM total)
    "esp32": (51.0, 28.0, 12.0, 10.0),
    "bts7960": (48.0, 48.0, 25.0, 45.0),            # 43 A driver module with heatsink
    "buck": (55.0, 27.0, 15.0, 28.0),               # 5 V / 5 A step-down
    "relay": (30.0, 28.0, 26.0, 40.0),              # 12 V 40 A automotive relay (fails open)
    "fuse_holder": (26.0, 14.0, 14.0, 12.0),
    "mpu6050": (20.0, 16.0, 3.0, 2.0),
    "battery_3s2p": (70.0, 60.0, 40.0, 250.0),      # Li-ion pack with BMS, default size
}
BOARD_COLOR = {"pi5": "#1A1A1A", "esp32": "#1A1A1A", "bts7960": "#1A1A1A", "buck": "#1A1A1A", "relay": "#1A1A1A",
               "fuse_holder": "#1A1A1A", "mpu6050": "#1A1A1A", "battery_3s2p": "#1A1A1A"}


def board(sku: str):
    """Box board, centred in x and y, standing on z = 0."""
    x, y, z, _ = BOARDS[sku]
    return Box(x, y, z, align=(Align.CENTER, Align.CENTER, Align.MIN))


PRICES.update({
    "pi5": (0, "have", "team stock", "Raspberry Pi 5 (excluded from the budget, as in v1)"),
    "esp32": (500, "estimate", "Robu / Amazon.in", "ESP32 dev board"),
    "bts7960": (300, "listed", "Robokits", "BTS7960 43 A driver, 4 needed (v1 price)"),
    "buck": (250, "estimate", "Robu", "5 V 5 A step-down"),
    "relay": (500, "estimate", "Amazon.in", "12 V 40 A automotive relay; one press of the E-stop must cut every controller"),
    "fuse_holder": (150, "estimate", "Amazon.in", "inline blade fuse holder with fuse"),
    "mpu6050": (200, "estimate", "Robu", "IMU without magnetometer"),
    "battery_3s2p": (2500, "estimate", "BatteryWorks / local", "3S2P Li-ion, BMS at least 20 A, with charger"),
    "estop": (350, "estimate", "Amazon.in", "red mushroom, 22 mm panel mount, twist release, head at least 40 mm (modelled 60 mm), unmodified"),
    "pzem051": (2000, "estimate", "Robu", "DC energy meter with shunt; price not listed, size measure-first"),
    "webcam": (1000, "estimate", "Amazon.in", "USB webcam 720p"),
    "servo_sg90": (150, "estimate", "Robu", "camera pan"),
    "tof_vl53": (500, "listed", "Robokits", "VL53L1X, Class 1 laser (v1 price)"),
    "wiring": (1100, "estimate", "Amazon.in / local", "wire, XT60 connectors, lugs, heat-shrink, cable ties"),
})


# ---------------------------------------------------------------- sensor tower parts (drop 3), sizes from listings; measure-first
def estop_model():
    """22 mm panel-mount mushroom E-stop, axis +Z, origin at the panel top: head Ø60 x 25 above, body Ø32 x 40 below."""
    head = Cylinder(30, 25, align=AX) + Pos(0, 0, -6) * Cylinder(11, 6.5, align=AX)
    body = Pos(0, 0, -46) * Cylinder(16, 40, align=AX)
    return head, body


def pzem_module():
    """PZEM-051 display: 20 deep (x) x 46 wide (y) x 31 high (z), centred, standing on z = 0. Measure first."""
    return Box(20, 46, 31, align=(Align.CENTER, Align.CENTER, Align.MIN))


def webcam_body():
    """USB webcam: 25 deep (x) x 62 wide (y) x 30 high (z) centred on x, y, standing on z = 0, lens toward +x."""
    return Box(25, 62, 30, align=(Align.CENTER, Align.CENTER, Align.MIN))


def servo_sg90():
    """SG90: body 22.5 x 12.2 x 22.7 with the output shaft 5.25 mm from the body centre toward +x; origin at the
    shaft axis on the body's bottom face; horn Ø7 x 4 on the shaft top."""
    body = Pos(5.25, 0, 0) * Box(22.5, 12.2, 22.7, align=(Align.CENTER, Align.CENTER, Align.MIN))
    shaft = Pos(0, 0, 22.7) * Cylinder(2.4, 3.5, align=AX)
    horn = Pos(0, 0, 26.2) * Cylinder(3.5, 4.0, align=AX)
    return body + shaft + horn


def tof_board():
    """VL53L1X breakout 13 x 18 x 3, sensor facing +Z (local), standing on z = 0."""
    return Box(13, 18, 3, align=(Align.CENTER, Align.CENTER, Align.MIN))
