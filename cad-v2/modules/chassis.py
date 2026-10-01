"""Chassis: 2020 T-slot rails and cross members, joined with inside corner brackets (no drilling)."""
from __future__ import annotations

from build123d import Pos, Rot

from lib import cots, fasteners
from lib.model import Assembly, at, bought_item
from lib.profile2020 import LIP_UNDERSIDE, extrusion
from params import (COLORS, CROSS_FRONT_X, CROSS_LEN, CROSS_REAR_X, RAIL_LEN, RAIL_X0, RAIL_Y, RAIL_Z0, SPINE_X, TUBE)

ALU_G_PER_MM3 = 2.7e-3
Z_MID = RAIL_Z0 + TUBE / 2


def _stock(asm: Assembly, id_: str, shape, length: float) -> None:
    it = bought_item(id_, id_, "chassis", shape, Pos(0, 0, 0), COLORS["alu"], shape.volume * ALU_G_PER_MM3,
                     kind="stock", sku="2020 T-slot", cut_mm=length)
    asm.add(it)


def _bracket_set(asm: Assembly, name: str, vertex_x: float, vertex_y: float, sx: int, sy: int) -> None:
    """One inside corner bracket at the interior angle between a rail face (plane y = vertex_y) and a
    cross-member face (plane x = vertex_x). sx: direction along the rail away from the cross member;
    sy: direction along the cross member away from the rail."""
    flip = sx * sy
    z0 = RAIL_Z0 if flip > 0 else RAIL_Z0 + TUBE
    frame = at((vertex_x, vertex_y, z0), (0, 0, flip), (sx, 0, 0))
    asm.add(bought_item(name, "corner_bracket", "chassis", cots.corner_bracket(), frame, COLORS["alu"],
                        cots.MASS_G["corner_bracket"], sku="corner bracket 2020"))
    # (local point, local z_dir) for the two screws and their T-nuts, in the bracket frame
    for tag, head_pt, nut_pt, zdir in (("a", (12, 3, 10), (12, -(TUBE / 2 - LIP_UNDERSIDE), 10), (0, -1, 0)),
                                       ("b", (3, 12, 10), (-(TUBE / 2 - LIP_UNDERSIDE), 12, 10), (-1, 0, 0))):
        screw = fasteners.bolt(5, 8, "button")
        nut = fasteners.tnut()
        asm.add(bought_item(f"{name}_s{tag}", "bolt_m5x8", "chassis", screw, frame * at(head_pt, zdir, (0, 0, 1)),
                            COLORS["steel"], fasteners.steel_mass_g(screw), sku="M5x8 button"))
        asm.add(bought_item(f"{name}_n{tag}", "tnut_m5", "chassis", nut, frame * at(nut_pt, zdir, (0, 0, 1)),
                            COLORS["steel"], fasteners.steel_mass_g(nut), sku="T-nut M5 spring"))


def build(asm: Assembly) -> None:
    for name, y in (("rail_l", RAIL_Y), ("rail_r", -RAIL_Y)):
        _stock(asm, name, Pos(RAIL_X0, y, Z_MID) * Rot(0, 90, 0) * extrusion(RAIL_LEN), RAIL_LEN)
    for name, x in (("cross_rear", CROSS_REAR_X), ("cross_front", CROSS_FRONT_X)):
        _stock(asm, name, Pos(x, -CROSS_LEN / 2, Z_MID) * Rot(-90, 0, 0) * extrusion(CROSS_LEN), CROSS_LEN)
    inner = RAIL_Y - TUBE / 2                       # |y| of the rails' inner faces
    for cm, xc in (("f", CROSS_FRONT_X), ("r", CROSS_REAR_X)):
        for side, ysign in (("l", 1), ("r", -1)):
            for d, sx in (("p", 1), ("m", -1)):
                _bracket_set(asm, f"br_{side}{cm}{d}", xc + sx * TUBE / 2, ysign * inner, sx, -ysign)
    # centre spine along X between the cross members (carries the lift and the tray)
    spine_len = SPINE_X[1] - SPINE_X[0]
    _stock(asm, "spine", Pos(SPINE_X[0], 0, Z_MID) * Rot(0, 90, 0) * extrusion(spine_len), spine_len)
    for vx, sx, tag in ((SPINE_X[0], 1, "r"), (SPINE_X[1], -1, "f")):
        for ys in (1, -1):
            _bracket_set(asm, f"br_s{tag}{'l' if ys > 0 else 'r'}", vx, ys * TUBE / 2, sx, ys)
