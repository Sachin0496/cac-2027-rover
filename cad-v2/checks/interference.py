"""A1: collisions between solids (exact boolean volume) and clearance between moving and static parts.

Mating features are modelled with clearance, so any overlap above TOUCH_MM3 is a real error:
there is deliberately no allow-list for overlaps. RUNNING_FITS lists moving/static pairs that are
*designed* to sit closer than the 2 mm clearance rule, with their designed gap (minimum 0.4 mm).
"""
from __future__ import annotations

import numpy as np

TOUCH_MM3 = 1.0
MIN_CLEARANCE_MM = 2.0
RUNNING_FITS: dict[frozenset, float] = {}   # frozenset({id_a, id_b}) -> designed gap, mm
# Designed close fits between a moving and a static item, as (regex, regex, designed gap in mm). Gap 0 means the
# two are seated on each other (bearing in its pocket, nut on its screw). Anything else closer than 2 mm fails.
RUNNING_PATTERNS = [
    (r"arm_(drive|idler)", r"pivot_bearing_[lr]", 0.0),          # 608 seated in the arm root
    (r"arm_(drive|idler)", r"pivot_washer_i_[lr]", 0.4),         # washer inside the 17 mm floor hole
    (r"arm_(drive|idler)", r"pivot_nut_[lr]", 0.9),              # nyloc nut inside the same hole
    (r"arm_(drive|idler)", r"pivot_bracket_[lr]", 1.5),          # arm to bracket wall, washer gap
    (r"lift_nut_[ab]", r"lift_screw", 0.0),                      # brass nuts on the rod
    (r"lift_carriage", r"lift_channel", 0.9),                    # carriage sliding in the channel
    (r"lift_carriage", r"lift_screw", 0.4),                      # rod bore around the M8 rod
    (r"lift_carriage", r"lift_foot_\d", 1.4),                   # carriage above the channel-foot screw heads
]


def _boxes(items):
    out = np.empty((len(items), 6))
    for k, it in enumerate(items):
        bb = it.shape.bounding_box()
        out[k] = (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)
    return out


def overlap_volume(a, b) -> float:
    r = a & b
    if r is None:
        return 0.0
    v = r.volume
    return float(v) if v == v else 0.0


def find_collisions(asm, ids=None) -> list[tuple[str, str, float]]:
    """All pairs overlapping by more than TOUCH_MM3 (optionally only pairs involving `ids`)."""
    items = asm.items
    bx = _boxes(items)
    hits = []
    for i in range(len(items)):
        lo, hi = bx[i, :3], bx[i, 3:]
        cand = np.where(np.all(bx[i + 1:, :3] < hi - 1e-6, axis=1) & np.all(bx[i + 1:, 3:] > lo + 1e-6, axis=1))[0]
        for j in cand + i + 1:
            if ids is not None and items[i].id not in ids and items[j].id not in ids:
                continue
            v = overlap_volume(items[i].shape, items[j].shape)
            if v > TOUCH_MM3:
                hits.append((items[i].id, items[j].id, v))
    return hits


def min_clearance(asm, moving_ids, static_ids, margin: float = 25.0):
    """Smallest distance between any moving and any static item (mm); 0 if they touch."""
    mv = [asm.get(i) for i in moving_ids]
    st = [asm.get(i) for i in static_ids]
    sb = _boxes(st) if st else np.empty((0, 6))
    best = float("inf")
    for m in mv:
        bb = m.shape.bounding_box()
        lo = np.array([bb.min.X, bb.min.Y, bb.min.Z]) - margin
        hi = np.array([bb.max.X, bb.max.Y, bb.max.Z]) + margin
        near = np.where(np.all(sb[:, 3:] > lo, axis=1) & np.all(sb[:, :3] < hi, axis=1))[0]
        for j in near:
            best = min(best, m.shape.distance_to(st[j].shape))
    return best


def allowed_gap(id_a: str, id_b: str) -> float:
    """Minimum allowed gap for a moving/static pair: its declared running fit, or the 2 mm rule."""
    import re
    g = RUNNING_FITS.get(frozenset({id_a, id_b}))
    for ra, rb, gap in RUNNING_PATTERNS:
        if (re.fullmatch(ra, id_a) and re.fullmatch(rb, id_b)) or (re.fullmatch(ra, id_b) and re.fullmatch(rb, id_a)):
            g = gap if g is None else min(g, gap)
    return MIN_CLEARANCE_MM if g is None else max(g - 0.05, 0.0)


def sweep_problems(asm, moving_ids, static_ids) -> list[str]:
    """Clearance rule for one pose: every moving/static pair at least 2 mm apart unless a running fit."""
    problems = []
    st = [asm.get(i) for i in static_ids]
    sb = _boxes(st)
    for mid in moving_ids:
        m = asm.get(mid)
        bb = m.shape.bounding_box()
        lo = np.array([bb.min.X, bb.min.Y, bb.min.Z]) - MIN_CLEARANCE_MM
        hi = np.array([bb.max.X, bb.max.Y, bb.max.Z]) + MIN_CLEARANCE_MM
        for j in np.where(np.all(sb[:, 3:] > lo, axis=1) & np.all(sb[:, :3] < hi, axis=1))[0]:
            gap = m.shape.distance_to(st[j].shape)
            allowed = allowed_gap(mid, st[j].id)
            if gap < allowed - 1e-6:
                problems.append(f"{mid} vs {st[j].id}: clearance {gap:.2f} mm < {allowed:.2f} mm")
    return problems
