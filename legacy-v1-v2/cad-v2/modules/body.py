"""Body (spec 7.6): three hood panels over the tray (printed upside down, 1.6 mm walls, hollow screw posts,
vents), yellow side covers, a carry handle bridging the spine, and three arrow plates. World coordinates."""
from __future__ import annotations

from build123d import Axis, Box, BuildPart, BuildSketch, Cylinder, Polygon, Pos, Rot, extrude, fillet

from lib import fasteners
from lib.model import Assembly, at, bought_item, printed_item
from lib.profile2020 import LIP_UNDERSIDE
from lib.shapes import AX, box, cyl
from modules import electronics as el
from params import AXLE_X_FRONT, AXLE_X_REAR, COLORS, RAIL_Y, RAIL_Z0, TUBE, WHEEL_D

WALL = 1.2
Z_BOT, Z_ROOF = el.PLATE_Z[1], 196.0            # tray plate top, roof top
HOOD_X, HOOD_Y = (-125.0, 75.0), 150.0
SEAM = 0.3                                     # half the reveal at the centre split
R_OUT, R_TOP = 3.0, 2.5                         # corner and roof-edge radii; unequal on purpose (equal radii make a spherical corner the STL mesher cracks)
POST_R, POST_BOSS_TOP = 4.5, el.PLATE_Z[1] + el.BOSS_H
PORT = ((29.0, 182.5), (18.0, Z_ROOF - WALL))  # front-wall port for the lift: wide and low for the pin heads, narrow and tall for the links
HANDLE = {"x": (-27.0, -13.0), "leg_y": 38.0, "leg_w": 14.0, "foot_z": (196.0, 200.0), "bar_z": (232.0, 242.0)}
ARROW = (90.0, 30.0, 0.8)
Z_OUTER_SLOT = RAIL_Z0 + TUBE / 2
COVER_X = (AXLE_X_REAR + WHEEL_D / 2 + 3.0, AXLE_X_FRONT - WHEEL_D / 2 - 3.0)     # fills the gap between the wheels, 3 mm each side
COVER_BOLTS = tuple((COVER_X[0] + COVER_X[1]) / 2 + d for d in (-28.0, 28.0))


def _box_round(x0, x1, y0, y1, z0, z1, r=R_OUT, r_top=R_TOP):
    b = box(x0, x1, y0, y1, z0, z1)
    b = fillet(b.edges().filter_by(Axis.Z), r)
    return fillet(b.edges().group_by(Axis.Z)[-1], r_top)


def _full_shell():
    """The whole hood as one hollow shell, open below, wall 1.6 with matching inner radii."""
    x0, x1 = HOOD_X
    outer = _box_round(x0, x1, -HOOD_Y, HOOD_Y, Z_BOT, Z_ROOF)
    inner = _box_round(x0 + WALL, x1 - WALL, -HOOD_Y + WALL, HOOD_Y - WALL, Z_BOT - 1.0, Z_ROOF - WALL, R_OUT - WALL, R_TOP - WALL)
    return outer - inner


def _posts(pts, shell):
    for x, y in pts:
        shell += Pos(x, y, 0) * cyl(POST_R, (Z_ROOF - WALL + 0.01) - POST_BOSS_TOP, POST_BOSS_TOP)
    for x, y in pts:
        shell -= Pos(x, y, 0) * cyl(2.2, Z_ROOF + 2 - POST_BOSS_TOP + 1, POST_BOSS_TOP - 1)
    return shell


def _hood(side: int):
    """One half (side +1 left, -1 right): the shell cut at the centre line, posts, front notch, vent slots."""
    y0, y1 = (SEAM, HOOD_Y + 1.0) if side > 0 else (-HOOD_Y - 1.0, -SEAM)
    h = _full_shell() & box(HOOD_X[0] - 1.0, HOOD_X[1] + 1.0, y0, y1, Z_BOT - 1.0, Z_ROOF + 1.0)
    h = _posts(el.HOOD_POSTS["left" if side > 0 else "right"], h)
    for half_w, z_top in PORT:
        h -= box(HOOD_X[1] - 8.0, HOOD_X[1] + 1.0, min(0.0, side * half_w), max(0.0, side * half_w), Z_BOT - 1.0, z_top)
    if side > 0:                                                    # compute bay: over the Pi 5 and its heat sink
        slots = [(xc, 90.0 + 8.0 * i, 36.0) for xc in (-84.0, -42.0) for i in range(5)]
    else:                                                           # power bay: over the BTS7960 heat sinks
        slots = [(xc, -(98.0 + 8.0 * i), 36.0) for xc in (-84.0, -32.0, 20.0) for i in range(6)]
    for xc, yc, length in slots:
        h -= box(xc - length / 2, xc + length / 2, yc - 1.75, yc + 1.75, 150.0, 250.0)
    return h


def hood_left():
    return _hood(1)


def hood_right():
    return _hood(-1)


def body_side_cover():
    """Left flank cover; the right one is its mirror. Flat plate, two M5 holes."""
    c = box(COVER_X[0], COVER_X[1], 151.0, 153.0, 104.0, 176.0)
    c = fillet(c.edges().filter_by(Axis.Y), 6.0)
    for x in COVER_BOLTS:
        c -= Pos(x, 150.5, Z_OUTER_SLOT) * Rot(-90, 0, 0) * cyl(2.75, 4.0, 0.0)
    return c


def body_handle():
    """Inverted U: bar on top, two hollow legs over the spine screw posts, a 4 mm foot flange on each leg.
    One M4 x 100 through-bolt per leg runs from the bar down into the tray boss (printed upside down)."""
    x0, x1 = HANDLE["x"]
    ly, lw = HANDLE["leg_y"], HANDLE["leg_w"]
    fz0, fz1 = HANDLE["foot_z"]
    bz0, bz1 = HANDLE["bar_z"]
    h = box(x0, x1, -(ly + lw / 2), ly + lw / 2, bz0, bz1)
    for s in (-1, 1):
        h += box(x0, x1, s * (ly - lw / 2), s * (ly + lw / 2), fz1 - 0.01, bz0 + 0.01)
        h += box(x0 - 4.0, x1 + 4.0, s * (ly - lw / 2 - 4.0), s * (ly + lw / 2 + 4.0), fz0, fz1)
        h -= Pos(-20.0, s * ly, 0) * cyl(2.2, bz1 - fz0 + 2, fz0 - 1)
        h -= Pos(-20.0, s * ly, 0) * cyl(3.9, 4.2, bz1 - 4.2)
    try:
        h = fillet(h.edges().filter_by(Axis.Y), 3.0)
    except Exception:
        pass
    return h


def body_arrow(double: bool = False):
    """Arrow plate 90 x 30 x 0.8, pointing +x (double-headed if asked)."""
    L, W, T = ARROW
    hw = W / 2
    if double:
        pts = [(-L / 2, 0), (-L / 2 + 22, hw), (-L / 2 + 22, 5), (L / 2 - 22, 5), (L / 2 - 22, hw), (L / 2, 0),
               (L / 2 - 22, -hw), (L / 2 - 22, -5), (-L / 2 + 22, -5), (-L / 2 + 22, -hw)]
    else:
        pts = [(-L / 2, 5), (L / 2 - 30, 5), (L / 2 - 30, hw), (L / 2, 0), (L / 2 - 30, -hw), (L / 2 - 30, -5), (-L / 2, -5)]
    with BuildPart() as bp:
        with BuildSketch():
            Polygon(*pts, align=None)
        extrude(amount=T)
    return bp.part


def build(asm: Assembly) -> None:
    Y, G, W = COLORS["yellow"], COLORS["graphite"], "#F2F2F2"
    for key, fn in (("left", hood_left), ("right", hood_right)):
        asm.add(printed_item(f"hood_{key}", f"hood_{key}", "body", fn(), Pos(0, 0, 0), Y, orient=Rot(180, 0, 0)))
    cover = body_side_cover()
    asm.add(printed_item("cover_l", "body_side_cover_l", "body", cover, Pos(0, 0, 0), Y, orient=Rot(90, 0, 0)))
    from build123d import Plane, mirror
    asm.add(printed_item("cover_r", "body_side_cover_r", "body", mirror(cover, Plane.XZ), Pos(0, 0, 0), Y, orient=Rot(-90, 0, 0)))
    asm.add(printed_item("handle", "body_handle", "body", body_handle(), Pos(0, 0, 0), G, orient=Rot(180, 0, 0)))
    asm.add(printed_item("arrow_fwd", "body_arrow", "body", body_arrow(False), Pos(-70.0, 17.0, Z_ROOF), W))
    asm.add(printed_item("arrow_len", "body_arrow_double", "body", body_arrow(True), Pos(-70.0, -17.0, Z_ROOF), W))
    asm.add(printed_item("arrow_wid", "body_arrow_double", "body", body_arrow(True), Pos(44.0, -90.0, Z_ROOF) * Rot(0, 0, 90), W))
    S = COLORS["steel"]
    for side, key in ((1, "left"), (-1, "right")):
        for k, (x, y) in enumerate(el.HOOD_POSTS[key]):
            handle_foot = abs(x + 20.0) < 1e-6 and abs(abs(y) - 38.0) < 1e-6
            top = HANDLE["bar_z"][1] - 4.2 if handle_foot else Z_ROOF
            length = 100 if handle_foot else 60
            asm.add(bought_item(f"hood_bolt_{key}{k}", f"bolt_m4x{length}", "body",
                                fasteners.bolt(4, length, "button" if not handle_foot else "socket"), at((x, y, top), (0, 0, -1), (1, 0, 0)), S, 5.0,
                                sku=f"M4x{length} {'socket' if handle_foot else 'button'}"))
            asm.add(bought_item(f"hood_nut_{key}{k}", "nut_m4", "body", fasteners.nut(4),
                                at((x, y, el.PLATE_Z[1] + el.BOSS_H - 3.8 + 0.3), (0, 0, 1), (1, 0, 0)), S, 1.0, sku="M4 nut"))
    for side, tag in ((1, "l"), (-1, "r")):
        for x in COVER_BOLTS:
            asm.add(bought_item(f"cover_bolt_{tag}{x:+.0f}", "bolt_m5x8", "body", fasteners.bolt(5, 8, "button"),
                                at((x, side * 153.0, Z_OUTER_SLOT), (0, -side, 0), (1, 0, 0)), S, 3.0, sku="M5x8 button"))
            asm.add(bought_item(f"cover_washer_{tag}{x:+.0f}", "washer_m5", "body", fasteners.washer(5),
                                at((x, side * 151.0, Z_OUTER_SLOT), (0, -side, 0), (1, 0, 0)), S, 0.5, sku="M5 washer"))
            asm.add(bought_item(f"cover_tnut_{tag}{x:+.0f}", "tnut_m5", "body", fasteners.tnut(),
                                at((x, side * (RAIL_Y + LIP_UNDERSIDE), Z_OUTER_SLOT), (0, -side, 0), (0, 0, 1)), S, 3.0, sku="T-nut M5 spring"))
