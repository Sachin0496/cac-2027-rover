"""Sensor tower (spec 7.5): a 280 mm 2020 post on the rear cross member, dressed with stacked collars that slide on
from the top (each clamped by two M5 screws into the post's front and rear slots): base, sleeve, E-stop shelf, sleeve,
energy-meter housing, camera head with an SG90 pan servo and the webcam. Rear-looking ToF on the base."""
from __future__ import annotations

from math import cos, radians, sin, tan

from build123d import Box, BuildPart, BuildSketch, Cone, Cylinder, Plane, Polygon, Pos, Rot, extrude

from lib import cots, fasteners
from lib.model import Assembly, at, bought_item, printed_item
from lib.profile2020 import LIP_UNDERSIDE, extrusion
from lib.shapes import AX, box, cyl
from params import COLORS, CROSS_REAR_X, RAIL_Z0, TOL_TRAP, TUBE

TX = CROSS_REAR_X                                # tower axis x (over the rear cross member), y = 0
POST_Z = (141.0, 381.0)
Z_TOP_SLOT = RAIL_Z0 + TUBE / 2 + LIP_UNDERSIDE
STACK = {"socket": (141.0, 171.0), "sleeve_a": (171.0, 251.0), "sleeve_b": (251.0, 291.0), "pzem": (291.0, 351.0),
         "head": (351.0, 401.0)}
COL = 30.0                                       # collar outer size
ESTOP_Y = 62.0                                   # E-stop pedestal axis, to the left of the tower (battery is on the right)
ESTOP_Z = 251.0                                  # panel plane (top of the pedestal)
SERVO_POCKET_Z = 381.0
TOF_TILT = 20.0                                  # rear ToF looks 20 deg below horizontal (steeper would overhang)


def _collar(z0, z1, clamp_holes=True, blind_top=False):
    c = box(TX - COL / 2, TX + COL / 2, -COL / 2, COL / 2, z0, z1)
    c -= box(TX - 10.2, TX + 10.2, -10.2, 10.2, z0 - 1, (POST_Z[1] if blind_top else z1 + 1))
    if clamp_holes:
        zc = (z0 + z1) / 2
        for s in (-1, 1):                          # M5 clamp screws through the left and right walls (rear side carries plates)
            c -= Pos(TX, s * 12.6, zc) * Rot(90, 0, 0) * cyl(2.75, 12.0, -6.0)
    return c


def tower_base():
    """Plate on the rear cross member (two M5), socket around the post foot, wedge for the rear ToF."""
    z0, z1 = 136.0, STACK["socket"][0]
    b = box(TX - 39, TX + 25, -30, 30, z0, z1)
    b += _collar(*STACK["socket"], clamp_holes=True)
    for s in (-1, 1):
        b -= Pos(TX, s * 22.0, 0) * cyl(2.75, 8, z0 - 1)
        b -= Pos(TX, s * 22.0, 0) * cyl(4.9, 4.0, z1 - 3.2)
    xa, h = TX - 27.0, 20.0
    with BuildPart() as w:                        # rear face leans back 20 degrees: its normal points 20 degrees below the rear horizontal
        with BuildSketch(Plane.XZ):
            Polygon((xa, z1 - 0.01), (xa - h * tan(radians(TOF_TILT)), z1 + h), (TX - 14.0, z1 + h), (TX - 14.0, z1 - 0.01), align=None)
        extrude(amount=12, both=True)
    return b + w.part


def tower_sleeve(length: float = 80.0):
    """Hollow 30 x 30 tube, local z 0..length, centred on the tower axis at x = TX."""
    return box(TX - COL / 2, TX + COL / 2, -COL / 2, COL / 2, 0, length) - box(TX - 12.2, TX + 12.2, -12.2, 12.2, -1, length + 1)


def tower_pzem():
    """Collar with a bezel plate on its rear face; the PZEM display sits on the plate looking rearward (-x)."""
    z0, z1 = STACK["pzem"]
    c = _collar(z0, z1)
    xr = TX - COL / 2
    zc = (z0 + z1) / 2
    c += box(xr - 4.0, xr + 0.5, -28.0, 28.0, z0 + 5.0, z1 - 5.0)                        # plate
    for sy in (-1, 1):                                                                   # side rims, 0.6 mm clear of the module
        c += box(xr - 10.0, xr - 4.0 + 0.01, sy * 23.6, sy * 26.0, zc - 15.5, zc + 15.5)
    c += box(xr - 10.0, xr - 4.0 + 0.01, -26.0, 26.0, zc + 16.1, zc + 18.5)              # top rim
    return c


def tower_head():
    """Top collar: blind hole over the post end, servo pocket above it."""
    z0, z1 = STACK["head"]
    c = _collar(z0, z1, blind_top=True)
    c -= Pos(TX + 5.25, 0, 0) * box(-11.8, 11.8, -6.4, 6.4, SERVO_POCKET_Z, z1 + 1)
    return c


def camera_mount():
    """Rotating cradle on the servo horn (one flat platform, two end cheeks); local origin on the servo shaft axis."""
    m = box(-16, 16, -40, 40, 0, 4.0)
    for s in (-1, 1):
        m += box(-16, 16, s * 38.0 - 2.0 * s + (0 if s > 0 else 0), s * 38.0 + 2.0 * s, 3.99, 30.0)
    m -= cyl(2.6, 6, -1)
    return m


def estop_pedestal():
    """Hollow pedestal on the rear cross member holding the panel-mount E-stop; 45 degree conical flare to the panel."""
    y_c = ESTOP_Y
    z0, z_top = 136.0, ESTOP_Z
    p = box(TX - 22, TX + 22, y_c - 30, y_c + 30, z0, z0 + 6.0)
    p += Pos(TX, y_c, 0) * cyl(19.5, (z_top - 13.5) - z0, z0)
    p += Pos(TX, y_c, z_top - 13.5) * Cone(19.5, 33.0, 13.5, align=AX)
    p -= Pos(TX, y_c, 0) * cyl(17.0, (z_top - 4) - z0 + 1, z0 - 1)                  # bore for the E-stop body (32 mm)
    p -= Pos(TX, y_c, 0) * cyl(11.2, 10, z_top - 6)                                 # 22.4 panel hole
    for s in (-1, 1):
        p -= Pos(TX, y_c + s * 22.0, 0) * cyl(2.75, 8, z0 - 1)
        p -= Pos(TX, y_c + s * 22.0, 0) * cyl(4.9, 4.0, z0 + 6.0 - 3.2)
    return p


def build(asm: Assembly) -> None:
    G, Y, K, R = COLORS["graphite"], COLORS["yellow"], COLORS["black"], COLORS["red"]
    asm.add(printed_item("tower_base", "tower_base", "tower", tower_base(), Pos(0, 0, 0), G))
    for tag, name in (("a", "sleeve_a"), ("b", "sleeve_b")):
        length = STACK[name][1] - STACK[name][0]
        asm.add(printed_item(f"tower_sleeve_{tag}", f"tower_sleeve_{length:.0f}", "tower", tower_sleeve(length), Pos(0, 0, STACK[name][0]), G))
    asm.add(printed_item("tower_pzem", "tower_pzem", "tower", tower_pzem(), Pos(0, 0, 0), Y))
    asm.add(printed_item("tower_head", "tower_head", "tower", tower_head(), Pos(0, 0, 0), Y))
    asm.add(printed_item("estop_pedestal", "estop_pedestal", "tower", estop_pedestal(), Pos(0, 0, 0), G))
    zp0, zp1 = POST_Z
    asm.add(bought_item("tower_post", "tower_post", "tower", Pos(TX, 0, zp0) * extrusion(zp1 - zp0), Pos(0, 0, 0), COLORS["alu"],
                        0.52 * (zp1 - zp0), kind="stock", sku="2020 T-slot", cut_mm=zp1 - zp0))
    head, body = cots.estop_model()
    asm.add(bought_item("estop_head", "estop", "tower", Pos(TX, ESTOP_Y, ESTOP_Z) * head, Pos(0, 0, 0), R, 40.0, sku="estop"))
    asm.add(bought_item("estop_body", "estop_body", "tower", Pos(TX, ESTOP_Y, ESTOP_Z) * body, Pos(0, 0, 0), K, 50.0, sku="estop_body"))
    z0p, z1p = STACK["pzem"]
    xr = TX - COL / 2
    asm.add(bought_item("pzem", "pzem051", "tower", Pos(xr - 4.0 - 10.0, 0, (z0p + z1p) / 2 - 15.5) * cots.pzem_module(), Pos(0, 0, 0), K, 100.0, sku="pzem051"))
    servo_z = SERVO_POCKET_Z                                    # body stands on the pocket floor, top 2.7 above the collar
    asm.add(bought_item("servo", "servo_sg90", "tower", Pos(TX, 0, servo_z) * cots.servo_sg90(), Pos(0, 0, 0), K, 9.0, sku="servo_sg90", moving="pan"))
    z_h = servo_z + 30.2 - 0.0
    asm.add(printed_item("camera_mount", "camera_mount", "tower", camera_mount(), Pos(TX, 0, z_h), Y, moving="pan"))
    asm.add(bought_item("webcam", "webcam", "tower", Pos(TX, 0, z_h + 4.0) * cots.webcam_body(), Pos(0, 0, 0), K, 75.0, sku="webcam", moving="pan",
                        sensor={"origin": (TX + 12.5, 0.0, z_h + 4.0 + 15.0), "dir": (1.0, 0.0, 0.0), "pan_axis_x": TX}))
    tilt = radians(TOF_TILT)
    zf = STACK["socket"][0] + 10.0
    p_rear = (TX - 27.0 - 10.0 * tan(tilt), 0.0, zf)
    n_rear = (-cos(tilt), 0.0, -sin(tilt))
    asm.add(bought_item("tof_rear", "tof_vl53", "tower", at(p_rear, n_rear, (0, 1, 0)) * cots.tof_board(), Pos(0, 0, 0), K, 2.5, sku="tof_vl53",
                        sensor={"origin": tuple(p_rear[k] + 3.0 * n_rear[k] for k in range(3)), "dir": n_rear, "full_angle": 27.0}))
    for name, zc in (("socket", 156.0), ("pzem", sum(STACK["pzem"]) / 2), ("head", sum(STACK["head"]) / 2)):
        for s in (-1, 1):
            asm.add(bought_item(f"tw_screw_{name}{s:+d}", "bolt_m5x10s", "tower", fasteners.bolt(5, 10, "socket"),
                                at((TX, s * COL / 2, zc), (0, -s, 0), (1, 0, 0)), COLORS["steel"], 4.0, sku="M5x10 socket"))
            asm.add(bought_item(f"tw_tnut_{name}{s:+d}", "tnut_m5", "tower", fasteners.tnut(),
                                at((TX, s * LIP_UNDERSIDE, zc), (0, -s, 0), (1, 0, 0)), COLORS["steel"], 3.0, sku="T-nut M5 spring"))
    for s in (-1, 1):
        asm.add(bought_item(f"tw_base_bolt{s:+d}", "bolt_m5x8", "tower", fasteners.bolt(5, 8, "button"),
                            at((TX, s * 22.0, STACK["socket"][0] - 3.2), (0, 0, -1), (1, 0, 0)), COLORS["steel"], 3.0, sku="M5x8 button"))
        asm.add(bought_item(f"tw_base_tnut{s:+d}", "tnut_m5", "tower", fasteners.tnut(),
                            at((TX, s * 22.0, Z_TOP_SLOT), (0, 0, -1), (1, 0, 0)), COLORS["steel"], 3.0, sku="T-nut M5 spring"))
        asm.add(bought_item(f"ped_bolt{s:+d}", "bolt_m5x8", "tower", fasteners.bolt(5, 8, "button"),
                            at((TX, ESTOP_Y + s * 22.0, 136.0 + 6.0 - 3.2), (0, 0, -1), (1, 0, 0)), COLORS["steel"], 3.0, sku="M5x8 button"))
        asm.add(bought_item(f"ped_tnut{s:+d}", "tnut_m5", "tower", fasteners.tnut(),
                            at((TX, ESTOP_Y + s * 22.0, Z_TOP_SLOT), (0, 0, -1), (1, 0, 0)), COLORS["steel"], 3.0, sku="T-nut M5 spring"))
