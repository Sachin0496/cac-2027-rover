"""A8 competition rules and A9 sensor views, evaluated on the assembled model (world frame, carry pose by default).

Rays are cast against a coarse mesh of the whole rover with trimesh; the E-stop approach probes are solids tested
against the exact shapes. Nothing here changes the model: a failure means a design change.
"""
from __future__ import annotations

from math import cos, radians, sin

import numpy as np
import trimesh
from build123d import Cylinder, Pos, Rot

from checks.interference import overlap_volume
from lib.shapes import AX

STOWED_MAX = (1500.0, 750.0, 750.0)        # length x width x height, mm (rules digest section 4)
ESTOP_MIN_HEAD = 40.0
APPROACH_LEN = 100.0
PZEM_ARC_DEG, PZEM_MIN_Z = 30.0, 250.0
CAM_HALF_H, CAM_HALF_V = 35.0, 25.0        # camera cone half angles
ESTOP_OWN = ("estop_head", "estop_body", "estop_pedestal", "ped_bolt", "ped_tnut")
CAMERA_OWN = ("webcam", "camera_mount", "servo")


def stowed_size(asm) -> tuple[float, float, float]:
    bbs = [it.shape.bounding_box() for it in asm.items]
    lo = np.array([[b.min.X, b.min.Y, b.min.Z] for b in bbs]).min(axis=0)
    hi = np.array([[b.max.X, b.max.Y, b.max.Z] for b in bbs]).max(axis=0)
    return tuple(float(v) for v in (hi - lo))


def _own(item_id: str, prefixes) -> bool:
    return any(item_id.startswith(p) for p in prefixes)


def _scene(asm, exclude_prefixes=()):
    """One trimesh of every item not excluded, plus the item id of each triangle."""
    verts, faces, owner, ids = [], [], [], []
    base = 0
    for it in asm.items:
        if _own(it.id, exclude_prefixes):
            continue
        v, t = it.shape.tessellate(0.4, 0.4)
        if not len(t):
            continue
        verts.append(np.array([[p.X, p.Y, p.Z] for p in v], dtype=float))
        faces.append(np.array(t, dtype=int) + base)
        base += len(v)
        owner.append(np.full(len(t), len(ids)))
        ids.append(it.id)
    mesh = trimesh.Trimesh(np.vstack(verts), np.vstack(faces), process=False)
    return mesh, np.concatenate(owner), ids


def _hits(mesh, owner, ids, origins, dirs) -> set[str]:
    tri, _, _ = mesh.ray.intersects_id(np.asarray(origins), np.asarray(dirs), multiple_hits=False, return_locations=True)
    return {ids[owner[k]] for k in tri}


def _pyramid(axis_sign: float, half_h: float, half_v: float, step: float = 5.0):
    dirs = []
    for az in np.arange(-half_h, half_h + 1e-9, step):
        for el in np.arange(-half_v, half_v + 1e-9, step):
            a, e = radians(az), radians(el)
            dirs.append((axis_sign * cos(e) * cos(a), sin(a) * cos(e), sin(e)))
    return np.array(dirs)


def _cone(axis, half_deg: float) -> np.ndarray:
    """Axis plus two rings of rays out to the cone's edge."""
    z = np.asarray(axis, float) / np.linalg.norm(axis)
    x = np.cross(z, (0, 0, 1) if abs(z[2]) < 0.9 else (1, 0, 0))
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    dirs = [z]
    for frac, n in ((0.5, 6), (1.0, 12)):
        a = radians(half_deg * frac)
        for k in range(n):
            phi = 2 * np.pi * k / n
            dirs.append(cos(a) * z + sin(a) * (cos(phi) * x + sin(phi) * y))
    return np.array(dirs)


def check_stowed(asm) -> tuple[list[str], dict]:
    dims = stowed_size(asm)
    problems = [f"stowed size {dims[0]:.0f} x {dims[1]:.0f} x {dims[2]:.0f} mm exceeds {STOWED_MAX[0]:.0f} x {STOWED_MAX[1]:.0f} x {STOWED_MAX[2]:.0f}"
                for _ in [0] if dims[0] > STOWED_MAX[0] or dims[1] > STOWED_MAX[1] or dims[2] > STOWED_MAX[2]]
    return problems, {"stowed_mm": tuple(round(v) for v in dims)}


def check_estop(asm) -> tuple[list[str], dict]:
    """Head at least 40 mm; a hand-sized probe (Ø60, 100 mm long) reaches the head from above, behind, outboard
    and on the two 45 degree diagonals between them without touching anything but the E-stop's own mount."""
    head = asm.get("estop_head").shape
    bb = head.bounding_box()
    dia = min(bb.max.X - bb.min.X, bb.max.Y - bb.min.Y)
    cx, cy = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2
    zc = (bb.min.Z + bb.max.Z) / 2
    r = dia / 2
    problems = []
    if dia < ESTOP_MIN_HEAD:
        problems.append(f"E-stop head {dia:.0f} mm is under {ESTOP_MIN_HEAD:.0f} mm")
    side = 1.0 if cy > 0 else -1.0                                # outboard is away from the centre line
    dirs = {"above": (0, 0, 1), "behind": (-1, 0, 0), "outboard": (0, side, 0),
            "above-behind": (-0.7071, 0, 0.7071), "above-outboard": (0, 0.7071 * side, 0.7071)}
    others = [it for it in asm.items if not _own(it.id, ESTOP_OWN)]
    centre = np.array([cx, cy, zc])
    corners = np.array([[x, y, z] for x in (bb.min.X, bb.max.X) for y in (bb.min.Y, bb.max.Y) for z in (bb.min.Z, bb.max.Z)]) - centre
    for name, d in dirs.items():
        d = np.array(d, float)
        d /= np.linalg.norm(d)
        reach = float((corners @ d).max())                        # how far the head extends along the approach
        start = centre + d * (reach + 1.0)
        probe = Pos(*(start + d * APPROACH_LEN / 2)) * _rotate_to(Cylinder(r, APPROACH_LEN), d)      # centred on its axis
        pb = probe.bounding_box()
        for it in others:
            b = it.shape.bounding_box()
            if (b.max.X < pb.min.X or b.min.X > pb.max.X or b.max.Y < pb.min.Y or b.min.Y > pb.max.Y or b.max.Z < pb.min.Z or b.min.Z > pb.max.Z):
                continue
            if overlap_volume(probe, it.shape) > 1.0:
                problems.append(f"E-stop approach from {name} is blocked by {it.id}")
                break
    return problems, {"estop_head_mm": round(dia, 1)}


def _rotate_to(shape, d):
    """Rotate a shape built along +Z so that its axis points along unit vector d."""
    from build123d import Plane
    d = np.asarray(d, float)
    if abs(d[2]) > 0.999999:
        return shape if d[2] > 0 else Rot(180, 0, 0) * shape
    pl = Plane(origin=(0, 0, 0), z_dir=tuple(d), x_dir=tuple(np.cross((0, 0, 1), d)))
    return pl.location * shape


def check_pzem(asm) -> tuple[list[str], dict]:
    """Display faces rearward within 30 degrees, centre at least 250 mm up, and the view cone is open."""
    pz = asm.get("pzem").shape
    bb = pz.bounding_box()
    cx, cy, cz = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2
    problems = []
    if cz < PZEM_MIN_Z:
        problems.append(f"PZEM display centre {cz:.0f} mm is below {PZEM_MIN_Z:.0f} mm")
    origin = np.array([bb.min.X - 0.5, cy, cz])                    # the rear face is the display
    dirs = _cone((-1, 0, 0), PZEM_ARC_DEG)
    mesh, owner, ids = _scene(asm, exclude_prefixes=("pzem",))
    hit = _hits(mesh, owner, ids, np.tile(origin, (len(dirs), 1)), dirs)
    if hit:
        problems.append(f"PZEM display view (+-{PZEM_ARC_DEG:.0f} deg) is blocked by {sorted(hit)}")
    return problems, {"pzem_centre_z": round(cz), "pzem_faces": "rear (-x)"}


def check_arrows(asm) -> tuple[list[str], dict]:
    """Three plates lying on upward faces of the hood: forward (single head, points +x), length (double, x), width (double, y)."""
    problems = []
    arrows = [it for it in asm.items if it.id.startswith("arrow_")]
    if sorted(i.id for i in arrows) != ["arrow_fwd", "arrow_len", "arrow_wid"]:
        return [f"expected arrows arrow_fwd, arrow_len, arrow_wid; found {sorted(i.id for i in arrows)}"], {}
    hoods = [it for it in asm.items if it.id.startswith("hood_")]
    for a in arrows:
        b = a.shape.bounding_box()
        if b.max.Z - b.min.Z > 1.5:
            problems.append(f"{a.id} is not a flat plate")
        if min(a.shape.distance_to(h.shape) for h in hoods) > 0.3:
            problems.append(f"{a.id} does not rest on the hood")
    fwd = asm.get("arrow_fwd").shape
    c = fwd.center()
    bb = fwd.bounding_box()
    if not (c.X > (bb.min.X + bb.max.X) / 2 + 1.0):
        problems.append("arrow_fwd does not point along +x")
    ext = lambda i: (asm.get(i).shape.bounding_box().max.X - asm.get(i).shape.bounding_box().min.X,
                     asm.get(i).shape.bounding_box().max.Y - asm.get(i).shape.bounding_box().min.Y)
    if ext("arrow_len")[0] < ext("arrow_len")[1] or ext("arrow_wid")[1] < ext("arrow_wid")[0]:
        problems.append("length arrow must lie along x and width arrow along y")
    return problems, {"arrows": 3}


def check_views(asm) -> tuple[list[str], dict]:
    """A9. Camera at pan 0 sees only the excavator; at pan 180 sees nothing of the rover. Each ToF cone (27 deg) is free."""
    problems = []
    cam = asm.get("webcam").meta["sensor"]
    mesh, owner, ids = _scene(asm, exclude_prefixes=CAMERA_OWN + ("tof_",))
    o = np.array(cam["origin"], float)
    pyr = _pyramid(1.0, CAM_HALF_H, CAM_HALF_V)
    hit = _hits(mesh, owner, ids, np.tile(o + np.array([0.5, 0, 0]), (len(pyr), 1)), pyr)
    non_exc = sorted(h for h in hit if asm.get(h).module != "excavator")
    if non_exc:
        problems.append(f"camera view at pan 0 is blocked by {non_exc}")
    o180 = np.array([2 * cam["pan_axis_x"] - o[0], o[1], o[2]])
    pyr180 = _pyramid(-1.0, CAM_HALF_H, CAM_HALF_V)
    hit180 = _hits(mesh, owner, ids, np.tile(o180 + np.array([-0.5, 0, 0]), (len(pyr180), 1)), pyr180)
    if hit180:
        problems.append(f"camera view at pan 180 is blocked by {sorted(hit180)}")
    for it in asm.items:
        s = it.meta.get("sensor") if it.part == "tof_vl53" else None
        if not s:
            continue
        origin = np.array(s["origin"], float)
        dirs = _cone(s["dir"], s["full_angle"] / 2)
        h = _hits(mesh, owner, ids, np.tile(origin + np.array(s["dir"]) * 0.5, (len(dirs), 1)), dirs)
        if h:
            problems.append(f"{it.id} cone is blocked by {sorted(h)}")
    return problems, {"camera_pan0_sees": sorted(hit), "camera_pan180_sees": sorted(hit180)}


def check_rules(asm) -> tuple[list[str], dict]:
    problems, info = [], {}
    for fn in (check_stowed, check_estop, check_pzem, check_arrows, check_views):
        p, i = fn(asm)
        problems += p
        info.update(i)
    return problems, info
