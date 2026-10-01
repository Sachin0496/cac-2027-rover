"""A1b: nothing floats. Two items are linked when their solids come within `tol` mm (touching faces, a bolt in its
clearance hole); every item must end up in the same connected group as the chassis rails."""
from __future__ import annotations

import numpy as np


def contact_groups(asm, tol: float = 0.5):
    """Return (groups, links): groups is a list of sets of item ids, biggest first."""
    items = asm.items
    n = len(items)
    lo = np.array([[b.min.X, b.min.Y, b.min.Z] for b in (it.shape.bounding_box() for it in items)]) - tol
    hi = np.array([[b.max.X, b.max.Y, b.max.Z] for b in (it.shape.bounding_box() for it in items)]) + tol
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    links = []
    for i in range(n):
        near = np.where(np.all(lo[i + 1:] <= hi[i], axis=1) & np.all(hi[i + 1:] >= lo[i], axis=1))[0] + i + 1
        for j in near:
            if find(i) == find(j):
                continue                                   # already connected: the pair adds nothing
            if items[i].shape.distance_to(items[j].shape) <= tol:
                parent[find(i)] = find(j)
                links.append((items[i].id, items[j].id))
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), set()).add(items[i].id)
    return sorted(groups.values(), key=len, reverse=True), links


def floating_items(asm, tol: float = 0.5):
    """Ids that are not connected to the main group."""
    groups, _ = contact_groups(asm, tol)
    return sorted(set().union(*groups[1:])) if len(groups) > 1 else []


FASTENER_PREFIXES = ("bolt_", "nut_", "tnut_", "washer_")


def under_supported(asm, tol: float = 0.5):
    """Fasteners that touch fewer than two other items (a bolt must clamp something, a T-nut must sit in a slot
    and meet its bolt). Returns {id: [ids it touches]}."""
    items = asm.items
    boxes = [it.shape.bounding_box() for it in items]
    out = {}
    for i, it in enumerate(items):
        if not it.part.startswith(FASTENER_PREFIXES):
            continue
        bi = boxes[i]
        touching = []
        for j, other in enumerate(items):
            if i == j:
                continue
            bj = boxes[j]
            if (bi.max.X + tol < bj.min.X or bj.max.X + tol < bi.min.X or bi.max.Y + tol < bj.min.Y
                    or bj.max.Y + tol < bi.min.Y or bi.max.Z + tol < bj.min.Z or bj.max.Z + tol < bi.min.Z):
                continue
            if it.shape.distance_to(other.shape) <= tol:
                touching.append(other.id)
        if len(touching) < 2:
            out[it.id] = touching
    return out
