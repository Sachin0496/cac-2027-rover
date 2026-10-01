"""A6/A7: mass, centre of gravity and front-axle share (empty, or with sand in the drum)."""
from __future__ import annotations

import numpy as np

from params import AXLE_X_FRONT, AXLE_X_REAR

WIRING_G = 250.0        # cables, connectors and cable ties are not modelled: allowance, assumed at the centre of gravity
SAND_G = 2100.0         # a full drum for the balance check


def mass_properties(asm, sand_g: float = 0.0, sand_at=None, wiring_g: float = 0.0) -> dict:
    total, moment = 0.0, np.zeros(3)
    for it in asm.items:
        g = it.mass()
        c = it.shape.center()
        total += g
        moment += g * np.array([c.X, c.Y, c.Z])
    if wiring_g:
        moment += wiring_g * moment / total          # placed at the centre of gravity of the modelled parts
        total += wiring_g
    if sand_g:
        total += sand_g
        moment += sand_g * np.array(sand_at, dtype=float)
    cg = moment / total
    return {"mass_g": total, "cg": tuple(float(v) for v in cg),
            "front_share": float((cg[0] - AXLE_X_REAR) / (AXLE_X_FRONT - AXLE_X_REAR))}


def drum_centre(asm):
    """Centre of the drum (mean of its rings), or None when the assembly has no drum."""
    rings = [it.shape.center() for it in asm.items if it.part.startswith("drum_ring")]
    if not rings:
        return None
    return (float(np.mean([c.X for c in rings])), float(np.mean([c.Y for c in rings])), float(np.mean([c.Z for c in rings])))


def balance(asm) -> dict:
    """Empty and loaded (2.1 kg of sand at the drum centre) mass, centre of gravity and front-axle share, wiring included."""
    empty = mass_properties(asm, wiring_g=WIRING_G)
    at = drum_centre(asm)
    loaded = mass_properties(asm, sand_g=SAND_G, sand_at=at, wiring_g=WIRING_G) if at else None
    return {"empty": empty, "loaded": loaded, "drum_centre": at}
