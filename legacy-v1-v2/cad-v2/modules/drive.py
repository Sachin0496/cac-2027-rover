"""Drive module x4 (spec 7.2): motor, flexible coupler, two-bearing axle housing, wheel.

All four modules are the same parts: a left-front module is built at x = 0 and placed by translation;
right-side modules are the left ones rotated 180 deg about the vertical axis, so no part is ever mirrored.
"""
from __future__ import annotations

from math import cos, radians, sin

from build123d import Location, Pos, Rot

from lib import cots, fasteners
from lib.model import Assembly, at, bought_item, printed_item
from lib.profile2020 import LIP_UNDERSIDE
from modules import drive_parts as dp
from params import AXLE_X_FRONT, AXLE_X_REAR, AXLE_Z, COLORS, RAIL_Y, RAIL_Z0, TUBE, WHEEL_W, Y_STACK, MOUNT_PLATE_Y

CORNER = {(1, 1): "lf", (1, -1): "rf", (-1, 1): "lr", (-1, -1): "rr"}    # (sign of x, side)
RAIL_MID_Z = RAIL_Z0 + TUBE / 2
Y0 = lambda name: Y_STACK[name][0]
Y1 = lambda name: Y_STACK[name][1]


def placement(x: float, side: int) -> Location:
    """Left-front module frame -> module at axle x on the given side (+1 left, -1 right)."""
    return Pos(x, 0, 0) if side > 0 else Rot(0, 0, 180) * Pos(-x, 0, 0)


def _steel(asm, id_, part, shape, loc, sku):
    asm.add(bought_item(id_, part, "drive", shape, loc, COLORS["steel"], fasteners.steel_mass_g(shape), sku=sku))


def build(asm: Assembly, x: float, side: int) -> None:
    c = CORNER[(1 if x > 0 else -1, side)]
    P = placement(x, side)
    wheel_frame = Pos(0, 160.0, AXLE_Z) * Rot(-90, 0, 0)          # wheel local z -> world +y (160..220)
    cap_frame = Pos(0, 220.0, AXLE_Z) * Rot(-90, 0, 0)            # cap local z -> world +y (220..228)
    G, Y, K = COLORS["graphite"], COLORS["yellow"], COLORS["black"]

    # ---- printed
    asm.add(printed_item(f"mount_{c}", "drv_mount", "drive", dp.mount(), P, G, orient=Rot(90, 0, 0)))
    asm.add(printed_item(f"roof_{c}", "drv_cradle_roof", "drive", dp.cradle_roof(), P, G, orient=Rot(180, 0, 0)))
    asm.add(printed_item(f"cap_{c}", "drv_cradle_cap", "drive", dp.cradle_cap(), P, G))
    asm.add(printed_item(f"spacer_mid_{c}", "axle_spacer_mid", "drive", dp.spacer(22.6),
                         P * Pos(0, Y0("spacer_mid"), AXLE_Z) * Rot(-90, 0, 0), G, moving="spin"))
    for tag, name in (("in", "spacer_end_in"), ("out", "spacer_end_out")):
        asm.add(printed_item(f"spacer_{tag}_{c}", "axle_spacer_end", "drive", dp.spacer(2.5),
                             P * Pos(0, Y0(name), AXLE_Z) * Rot(-90, 0, 0), G, moving="spin"))
    asm.add(printed_item(f"wheel_{c}", "wheel", "drive", dp.wheel(), P * wheel_frame, G, orient=Rot(180, 0, 0),
                         moving="spin"))
    asm.add(printed_item(f"wheel_cap_{c}", "wheel_cap", "drive", dp.wheel_cap(), P * cap_frame, Y, moving="spin"))

    # ---- purchased: motor train
    asm.add(bought_item(f"motor_{c}", "motor", "drive", cots.motor_johnson(), P * Pos(0, Y_STACK["gear_face"], AXLE_Z), K,
                        cots.MASS_G["motor"], sku="motor_johnson_30rpm"))
    for tag, name in (("b", "bearing_B"), ("a", "bearing_A")):
        asm.add(bought_item(f"bearing_{tag}_{c}", "bearing_608", "drive", cots.bearing_608(), P * Pos(0, Y0(name), AXLE_Z), G,
                            cots.MASS_G["bearing_608"], sku="bearing_608", moving="spin"))
    asm.add(bought_item(f"coupler_{c}", "coupler", "drive", cots.coupler_6_8(), P * Pos(0, Y0("coupler"), AXLE_Z), COLORS["alu"],
                        cots.MASS_G["coupler"], sku="coupler_6_8", moving="spin"))
    _steel(asm, f"axle_bolt_{c}", "bolt_m8x75", fasteners.bolt(8, 75, "hex"),
           P * at((0, Y_STACK["bolt_head_underside"], AXLE_Z), (0, -1, 0), (1, 0, 0)), "M8x75 hex")
    _steel(asm, f"axle_nut_{c}", "nut_m8_nyloc", fasteners.nut(8, nyloc=True),
           P * at((0, Y0("nut"), AXLE_Z), (0, 1, 0), (1, 0, 0)), "M8 nyloc")
    _steel(asm, f"axle_washer_{c}", "washer_m8", fasteners.washer(8),
           P * at((0, Y0("washer"), AXLE_Z), (0, 1, 0), (1, 0, 0)), "M8 washer")

    # ---- mount to the rail's outer slot: M5x12 from the counterbore floor, T-nut under the lip
    cb_floor = MOUNT_PLATE_Y[1] - 3.2
    lip_y = RAIL_Y + LIP_UNDERSIDE
    for sx in (-1, 1):
        _steel(asm, f"mount_bolt_{c}{sx:+d}", "bolt_m5x12", fasteners.bolt(5, 12, "button"),
               P * at((sx * 20.0, cb_floor, RAIL_MID_Z), (0, -1, 0), (1, 0, 0)), "M5x12 button")
        _steel(asm, f"mount_tnut_{c}{sx:+d}", "tnut_m5", fasteners.tnut(),
               P * at((sx * 20.0, lip_y, RAIL_MID_Z), (0, -1, 0), (0, 0, 1)), "T-nut M5 spring")
    # ---- cradle roof to the rail's bottom slot: M5x14 from below, T-nut under the lip
    lip_z = RAIL_MID_Z - LIP_UNDERSIDE
    for sx in (-1, 1):
        _steel(asm, f"roof_bolt_{c}{sx:+d}", "bolt_m5x14", fasteners.bolt(5, 14, "button"),
               P * at((sx * dp.BOLT_X_ROOF, dp.BOLT_Y_ROOF, dp.ROOF_Z[0]), (0, 0, 1), (1, 0, 0)), "M5x14 button")
        _steel(asm, f"roof_tnut_{c}{sx:+d}", "tnut_m5", fasteners.tnut(),
               P * at((sx * dp.BOLT_X_ROOF, dp.BOLT_Y_ROOF, lip_z), (0, 0, 1), (0, 1, 0)), "T-nut M5 spring")
    # ---- clamp: M4x40 from the cap's underside into a nut in the roof trap
    for sx in (-1, 1):
        _steel(asm, f"clamp_bolt_{c}{sx:+d}", "bolt_m4x40", fasteners.bolt(4, 40, "socket"),
               P * at((sx * dp.BOLT_X_CLAMP, dp.BOLT_Y_CLAMP, dp.CAP_Z[0]), (0, 0, 1), (1, 0, 0)), "M4x40 socket")
        _steel(asm, f"clamp_nut_{c}{sx:+d}", "nut_m4", fasteners.nut(4),
               P * at((sx * dp.BOLT_X_CLAMP, dp.BOLT_Y_CLAMP, dp.ROOF_Z[0]), (0, 0, 1), (1, 0, 0)), "M4 nut")
    # ---- wheel cap: M4x14 from the counterbore floor into nuts in the wheel boss
    for k in range(4):
        a = 45 + 90 * k
        px, py = dp.CIRCLE_R * cos(radians(a)), dp.CIRCLE_R * sin(radians(a))
        _steel(asm, f"cap_bolt_{c}{k}", "bolt_m4x14", fasteners.bolt(4, 14, "socket"),
               P * cap_frame * at((px, py, 3.8), (0, 0, -1), (1, 0, 0)), "M4x14 socket")
        _steel(asm, f"cap_nut_{c}{k}", "nut_m4", fasteners.nut(4),
               P * wheel_frame * at((px, py, dp.BOSS_Z0), (0, 0, 1), (cos(radians(a)), sin(radians(a)), 0)),
               "M4 nut")


def build_all(asm: Assembly) -> None:
    for x in (AXLE_X_FRONT, AXLE_X_REAR):
        for side in (1, -1):
            build(asm, x, side)
