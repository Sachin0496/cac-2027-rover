"""A3/A4: does every printed part fit the bed, print without supports, and stay light?

Overhang rule (spec A3): a downward-facing surface steeper than 45 deg from vertical
(outward normal n_z < -cos 45) must lie on the bed or be a bridge no wider than 8 mm.
Bridge width = diameter of the largest circle that fits inside the patch (XY projection).
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

from params import BED, BRIDGE_MAX, FILL, MAX_PRINT_G, OVERHANG_DEG, PETG

CELL = 0.25          # raster cell for the bridge-width measurement, mm
BED_Z_TOL = 0.2      # faces lower than this are "on the bed"


def printed_mass_g(shape) -> float:
    return shape.volume / 1000.0 * PETG * FILL


def _mesh(shape, tol=0.05, ang=0.1):
    verts, tris = shape.tessellate(tol, ang)
    v = np.array([[p.X, p.Y, p.Z] for p in verts], dtype=float)
    t = np.array(tris, dtype=int)
    # weld vertices shared between faces so patches can span faces
    key = np.round(v, 3)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    return uniq, inv[t]


def _span(tri_xy: np.ndarray) -> float:
    """Diameter of the largest inscribed circle of the union of XY triangles (n, 3, 2)."""
    lo = tri_xy.reshape(-1, 2).min(axis=0) - 2 * CELL
    hi = tri_xy.reshape(-1, 2).max(axis=0) + 2 * CELL
    nx, ny = (np.ceil((hi - lo) / CELL).astype(int) + 1)
    mask = np.zeros((nx, ny), bool)
    for tri in (tri_xy - lo) / CELL:
        a, b, c = tri
        x0, x1 = int(np.floor(tri[:, 0].min())), int(np.ceil(tri[:, 0].max()))
        y0, y1 = int(np.floor(tri[:, 1].min())), int(np.ceil(tri[:, 1].max()))
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1), indexing="ij")
        d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(d) < 1e-12:
            continue
        l1 = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / d
        l2 = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / d
        ok = (l1 >= -1e-9) & (l2 >= -1e-9) & (1 - l1 - l2 >= -1e-9)
        mask[xs[ok], ys[ok]] = True
    return float(distance_transform_edt(mask).max()) * 2 * CELL


def overhang_patches(shape, limit_deg: float = OVERHANG_DEG) -> list[dict]:
    """Downward-facing patches steeper than limit_deg off the bed, largest first."""
    v, t = _mesh(shape)
    p0, p1, p2 = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    n = np.cross(p1 - p0, p2 - p0)
    twice_area = np.linalg.norm(n, axis=1)
    nz = n[:, 2] / np.maximum(twice_area, 1e-12)
    zmin = np.minimum(np.minimum(p0[:, 2], p1[:, 2]), p2[:, 2])
    bad = (nz < -np.cos(np.radians(limit_deg)) - 1e-3) & (zmin > BED_Z_TOL) & (twice_area > 1e-9)
    idx = np.where(bad)[0]
    if idx.size == 0:
        return []
    tb = t[idx]
    edges = np.concatenate([tb[:, [0, 1]], tb[:, [1, 2]], tb[:, [2, 0]]])
    g = coo_matrix((np.ones(len(edges)), (edges[:, 0], edges[:, 1])), shape=(len(v), len(v)))
    _, labels = connected_components(g, directed=False)
    out = []
    for lab in np.unique(labels[tb[:, 0]]):
        sel = tb[labels[tb[:, 0]] == lab]
        pts = v[sel]                                   # (m, 3, 3)
        area = 0.5 * twice_area[idx][labels[tb[:, 0]] == lab].sum()
        out.append({"area": float(area), "span": _span(pts[:, :, :2]), "z_min": float(pts[:, :, 2].min())})
    return sorted(out, key=lambda d: -d["area"])


def check_oriented(name: str, shape) -> list[str]:
    """Problems for a printed part already sitting on the bed in its print orientation."""
    problems = []
    bb = shape.bounding_box()
    size = (bb.size.X, bb.size.Y, bb.size.Z)
    xy, bed_xy = sorted(size[:2]), sorted(BED[:2])
    if xy[0] > bed_xy[0] + 1e-6 or xy[1] > bed_xy[1] + 1e-6 or size[2] > BED[2] + 1e-6:
        problems.append(f"{name}: {size[0]:.0f} x {size[1]:.0f} x {size[2]:.0f} mm does not fit the bed {BED}")
    if abs(bb.min.Z) > 0.01:
        problems.append(f"{name}: not sitting on the bed (min z = {bb.min.Z:.2f})")
    for p in overhang_patches(shape):
        if p["span"] > BRIDGE_MAX:
            problems.append(f"{name}: overhang of {p['area']:.0f} mm2 spans {p['span']:.1f} mm at z = {p['z_min']:.1f}")
    g = printed_mass_g(shape)
    if g > MAX_PRINT_G:
        problems.append(f"{name}: {g:.0f} g exceeds {MAX_PRINT_G:.0f} g")
    return problems


def check_assembly(asm) -> list[str]:
    """Check one instance of every printed part type."""
    problems, seen = [], set()
    for it in asm.items:
        if it.kind == "printed" and it.part not in seen:
            seen.add(it.part)
            problems += check_oriented(it.part, it.oriented())
    return problems
