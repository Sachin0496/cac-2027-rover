"""Electronics tray (spec 7.4): two 3 mm plate halves resting on the rails either side of the lift, a tie plate
behind the lift motor, hanging ribs, standoffs and screw bosses; the battery cradle on the rear cross member;
the boards as boxes. Everything in world coordinates."""
from __future__ import annotations

import math

from build123d import Box, Cylinder, Pos, Rot

from lib import cots, fasteners
from lib.model import Assembly, at, bought_item, printed_item
from lib.profile2020 import LIP_UNDERSIDE
from lib.shapes import AX, box, cyl, hexprism
from params import COLORS, CROSS_REAR_X, RAIL_Y, RAIL_Z0, TOL_HOLE, TOL_TRAP, TUBE

PLATE_T = 2.0
PLATE_Z = (136.0, 136.0 + PLATE_T)
TRAY_X = (-125.0, 75.0)
LEFT_Y, RIGHT_Y = (32.0, 150.0), (-150.0, -32.0)
STANDOFF_H = 9.0
BOARD_Z0 = PLATE_Z[1] + STANDOFF_H
RIB_X = (-105.0, -65.0, -25.0, 15.0, 55.0)
RIB_H = 6.0
BOSS_R, BOSS_H = 5.5, 6.0                       # hood-screw bosses rise from the plate; the hood post holds the nut in
Z_TOP_SLOT = RAIL_Z0 + TUBE / 2 + LIP_UNDERSIDE
TRAY_BOLTS_X = (-118.0, 66.0)                   # M5 x 8 into the rail's top slot, y = +-140 (clear of the boards)

LAYOUT = {   # id: (sku, x, y, rotation about z in deg) board centres; power bay right (y < 0, next to the battery), compute bay left
    "bts_1": ("bts7960", -84.0, -120.0, 0.0), "bts_2": ("bts7960", -32.0, -120.0, 0.0), "bts_3": ("bts7960", 20.0, -120.0, 0.0),
    "bts_4": ("bts7960", -84.0, -69.0, 0.0), "relay": ("relay", -40.0, -62.0, 0.0), "buck": ("buck", 18.0, -62.0, 0.0),
    "fuse_1": ("fuse_holder", 60.0, -98.0, 90.0), "fuse_2": ("fuse_holder", 60.0, -66.0, 90.0),
    "pi5": ("pi5", -66.0, 100.0, 0.0), "esp32": ("esp32", 10.0, 112.0, 0.0), "mpu6050": ("mpu6050", 10.0, 88.0, 0.0),
}
HOOD_POSTS = {   # (x, y) of hood screws; the inner pair on each side is at y = +-38, x = -20 also takes the handle
    "left": [(-116.0, 122.0), (64.0, 122.0), (10.0, 63.0), (-100.0, 38.0), (-20.0, 38.0)],
    "right": [(-116.0, -122.0), (64.0, -122.0), (-25.0, -86.0), (-100.0, -38.0), (-20.0, -38.0)],
}
TIE_X, TIE_Y, TIE_Z = (-122.0, -112.0), 52.0, (PLATE_Z[1], PLATE_Z[1] + 6.0)
TIE_BOLTS = [(-117.0, 42.0), (-117.0, -42.0)]


def _standoff_points(sku, cx, cy, rot=0.0):
    x, y, _, _ = cots.BOARDS[sku]
    ix, iy = x / 2 - 4.0, y / 2 - 4.0
    if sku in ("esp32", "mpu6050", "fuse_holder", "relay", "buck"):
        pts = [(-ix, 0.0), (ix, 0.0)]
    else:
        pts = [(sx * ix, sy * iy) for sx in (-1, 1) for sy in (-1, 1)]
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(cx + px * c - py * s, cy + px * s + py * c) for px, py in pts]


def _half(side: int):
    """One plate half (side +1 left, -1 right). All features rise from the top face, so it prints plate-down."""
    y0, y1 = LEFT_Y if side > 0 else RIGHT_Y
    x0, x1 = TRAY_X
    p = box(x0, x1, y0, y1, *PLATE_Z)
    top = PLATE_Z[1]
    for x in RIB_X:
        p += box(x - 1.5, x + 1.5, y0 + 26.0 if side > 0 else y1 - 26.0, y1 - 20.0 if side > 0 else y0 + 20.0, top - 0.01, top + RIB_H)
    edge = (y0, y0 + 3.0) if side > 0 else (y1 - 3.0, y1)
    p += box(TIE_X[1] + 1.0, 0.0, edge[0], edge[1], top - 0.01, top + RIB_H)   # stops short of the tie plate and the hood front
    key = "left" if side > 0 else "right"
    for x, y in HOOD_POSTS[key]:
        p += Pos(x, y, 0) * cyl(BOSS_R, BOSS_H + 0.01, top - 0.01)
        p -= Pos(x, y, 0) * hexprism(7.0 + TOL_TRAP, 3.8, top + BOSS_H - 3.8)
        p -= Pos(x, y, 0) * cyl(2.2, BOSS_H + 6, PLATE_Z[0] - 1)
    for bx, by in TIE_BOLTS:
        if (by > 0) == (side > 0):
            p -= Pos(bx, by, 0) * cyl(2.2, 6, PLATE_Z[0] - 1)
    for lid, (sku, cx, cy, rot) in LAYOUT.items():
        if (cy > 0) == (side > 0):
            for sx, sy in _standoff_points(sku, cx, cy, rot):
                p += Pos(sx, sy, 0) * cyl(3.0, STANDOFF_H + 0.01, top - 0.01)
                p -= Pos(sx, sy, 0) * cyl(1.2, STANDOFF_H + 2, top + 1.0)
    for x in TRAY_BOLTS_X:
        p -= Pos(x, side * RAIL_Y, 0) * cyl(2.75, 6, PLATE_Z[0] - 1)
    return p


def tray_left():
    return _half(1)


def tray_right():
    return _half(-1)


def tray_tie():
    """Lies on both halves behind the lift motor; M4 nuts sit in traps on its underside (print upside down)."""
    t = box(TIE_X[0], TIE_X[1], -TIE_Y, TIE_Y, *TIE_Z)
    for bx, by in TIE_BOLTS:
        t -= Pos(bx, by, 0) * hexprism(7.0 + TOL_TRAP, 3.8, TIE_Z[0] - 0.5)
        t -= Pos(bx, by, 0) * cyl(2.2, 4.0, TIE_Z[0] + 2.0)
    return t


BATT = {"center": (-170.0, -72.0), "wall": 2.4, "base": 6.0, "clear": 0.6, "height": 32.0}


def batt_cradle():
    bx, by, bz = cots.BOARDS["battery_3s2p"][:3]
    cx, cy = BATT["center"]
    ix, iy = bx / 2 + BATT["clear"], by / 2 + BATT["clear"]
    w, b = BATT["wall"], BATT["base"]
    c = box(cx - ix - w, cx + ix + w, cy - iy - w, cy + iy + w, PLATE_Z[0], PLATE_Z[0] + b)
    c += box(cx - ix - w, cx + ix + w, cy - iy - w, cy - iy, PLATE_Z[0], PLATE_Z[0] + BATT["height"])
    c += box(cx - ix - w, cx + ix + w, cy + iy, cy + iy + w, PLATE_Z[0], PLATE_Z[0] + BATT["height"])
    c += box(cx - ix - w, cx - ix, cy - iy, cy + iy, PLATE_Z[0], PLATE_Z[0] + BATT["height"])
    for s in (-1, 1):                                                         # strap slots through the long walls
        c -= box(cx - 8, cx + 8, cy + s * (iy - 0.5), cy + s * (iy + w + 0.5), PLATE_Z[0] + 12, PLATE_Z[0] + 24)
    for s in (-1, 1):                                                         # M5 feet into the rear cross member's top slot
        c -= Pos(CROSS_REAR_X, cy + s * 22.0, 0) * cyl(2.75, b + 2, PLATE_Z[0] - 1)
        c -= Pos(CROSS_REAR_X, cy + s * 22.0, 0) * cyl(4.9, 4.0, PLATE_Z[0] + b - 3.2)
    return c


def build(asm: Assembly) -> None:
    G = COLORS["graphite"]
    asm.add(printed_item("tray_left", "tray_left", "electronics", tray_left(), Pos(0, 0, 0), G))
    asm.add(printed_item("tray_right", "tray_right", "electronics", tray_right(), Pos(0, 0, 0), G))
    asm.add(printed_item("tray_tie", "tray_tie", "electronics", tray_tie(), Pos(0, 0, 0), G))
    asm.add(printed_item("batt_cradle", "batt_cradle", "electronics", batt_cradle(), Pos(0, 0, 0), G))
    for lid, (sku, cx, cy, rot) in LAYOUT.items():
        mass = cots.BOARDS[sku][3]
        asm.add(bought_item(lid, sku, "electronics", Pos(cx, cy, BOARD_Z0) * Rot(0, 0, rot) * cots.board(sku), Pos(0, 0, 0), cots.BOARD_COLOR[sku],
                            mass, sku=sku))
    bx, by, bz, mass = cots.BOARDS["battery_3s2p"]
    cx, cy = BATT["center"]
    asm.add(bought_item("battery", "battery_3s2p", "electronics", Pos(cx, cy, PLATE_Z[0] + BATT["base"]) * cots.board("battery_3s2p"),
                        Pos(0, 0, 0), cots.BOARD_COLOR["battery_3s2p"], mass, sku="battery_3s2p"))
    for side, tag in ((1, "l"), (-1, "r")):
        for x in TRAY_BOLTS_X:
            asm.add(bought_item(f"tray_bolt_{tag}{x:+.0f}", "bolt_m5x8", "electronics", fasteners.bolt(5, 8, "button"),
                                at((x, side * RAIL_Y, PLATE_Z[1]), (0, 0, -1), (1, 0, 0)), COLORS["steel"], 3.0, sku="M5x8 button"))
            asm.add(bought_item(f"tray_tnut_{tag}{x:+.0f}", "tnut_m5", "electronics", fasteners.tnut(),
                                at((x, side * RAIL_Y, Z_TOP_SLOT), (0, 0, -1), (0, 1, 0)), COLORS["steel"], 3.0, sku="T-nut M5 spring"))
    for s in (-1, 1):
        cy = BATT["center"][1] + s * 22.0
        asm.add(bought_item(f"batt_bolt_{s:+d}", "bolt_m5x8", "electronics", fasteners.bolt(5, 8, "button"),
                            at((CROSS_REAR_X, cy, PLATE_Z[0] + BATT["base"] - 3.2), (0, 0, -1), (1, 0, 0)), COLORS["steel"], 3.0, sku="M5x8 button"))
        asm.add(bought_item(f"batt_tnut_{s:+d}", "tnut_m5", "electronics", fasteners.tnut(),
                            at((CROSS_REAR_X, cy, Z_TOP_SLOT), (0, 0, -1), (1, 0, 0)), COLORS["steel"], 3.0, sku="T-nut M5 spring"))
    for bx_, by_ in TIE_BOLTS:
        asm.add(bought_item(f"tie_bolt_{by_:+.0f}", "bolt_m4x8", "electronics", fasteners.bolt(4, 8, "socket"),
                            at((bx_, by_, PLATE_Z[0]), (0, 0, 1), (1, 0, 0)), COLORS["steel"], 2.0, sku="M4x8 socket"))
        asm.add(bought_item(f"tie_nut_{by_:+.0f}", "nut_m4", "electronics", fasteners.nut(4),
                            at((bx_, by_, TIE_Z[0]), (0, 0, 1), (1, 0, 0)), COLORS["steel"], 1.0, sku="M4 nut"))
