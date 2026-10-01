"""A10: closed-form load-path checks. Every line prints its inputs; a check passes at safety factor >= 2.

Loads (all worst case, deliberately conservative):
  full mass 10.2 kg (8.1 kg empty + 2.1 kg sand), front axle 75 %, so 37.5 N static per front wheel, x3 shock;
  lateral skid force 0.6 x vertical at the ground contact; drum + arm + sand 3.6 kg (x3 shock) at the drum axis;
  60 N horizontal digging reaction at the tooth tip. PETG design stress: 20 MPa in the layer plane, 10 MPa across layers.
"""
from __future__ import annotations

from math import atan, cos, degrees, pi, radians, tan

from params import ARM_LEN, HOUSING_R, LINK_LEN, LINK_T, LINK_W, RAIL_Y

G = 9.81
SIGMA_XY, SIGMA_Z, E_PETG = 20.0, 10.0, 1800.0     # MPa
SHOCK = 3.0


def wheel_housing():
    fv = 0.75 * 10.2 * G / 2 * SHOCK                          # N per front wheel
    fl = 0.6 * fv
    m_root = fv * 30.0 + fl * 87.0                           # N mm at the housing root (30 mm out, 87 mm ground lever)
    r_o, r_i = HOUSING_R, 11.1
    inertia = pi / 4 * (r_o ** 4 - r_i ** 4)
    sigma = m_root * r_o / inertia
    return ("wheel housing root (bending across layers)", sigma, SIGMA_Z, {"Fv N": round(fv), "Fl N": round(fl), "M N.m": round(m_root / 1000, 2)})


def wheel_bearings():
    fv = 0.75 * 10.2 * G / 2 * SHOCK
    fl = 0.6 * fv
    m_root = fv * 30.0 + fl * 87.0
    span = 30.0
    load = m_root / span + fv / 2                              # N on the worse bearing
    return ("608 bearing static load", load, 1290.0, {"N": round(load), "rating N": 1290})


def mount_bolts():
    fv = 0.75 * 10.2 * G / 2 * SHOCK
    fl = 0.6 * fv
    m_root = fv * 30.0 + fl * 87.0
    tension = m_root / 20.0 / 2                                # two bolts, 20 mm lever
    return ("M5 T-nut pull-out (mount plate)", tension, 800.0, {"N per bolt": round(tension)})


def axle_bolt():
    fv = 0.75 * 10.2 * G / 2 * SHOCK
    m = fv * 18.0
    sigma = 32 * m / (pi * 8 ** 3)
    return ("M8 axle bolt bending", sigma, 640.0, {"M N.mm": round(m)})


def lift_loads():
    w = 3.6 * G * SHOCK                                        # N at the drum axis
    dig = 60.0
    m_pivot = w * ARM_LEN / 1000 + dig * ARM_LEN / 1000        # N m, arm horizontal
    r_lever = 57.0 / 1000
    f_link = m_pivot / r_lever
    return w, dig, m_pivot, f_link


def pivot_wall_bearing():
    w, dig, m_pivot, f_link = lift_loads()
    reaction = (w ** 2 + (dig + f_link * 0.5) ** 2) ** 0.5     # N, resultant on the pivot bolt
    couple = reaction * 13.0                                   # N mm, bolt bearing sits 13 mm from the wall centre
    wall_t = 10.0
    force = couple / wall_t
    sigma = force / (8.4 * wall_t / 2)
    return ("pivot bracket wall bearing stress", sigma, SIGMA_XY, {"reaction N": round(reaction), "wall mm": wall_t})


def arm_section():
    w, dig, m_pivot, f_link = lift_loads()
    m = (w + dig) * (ARM_LEN - 25.0)                           # N mm at the crossbar section
    h, rim, web, t = 60.0, 5.0, 4.0, 12.0
    inertia = 2 * (t * rim ** 3 / 12 + t * rim * (h / 2 - rim / 2) ** 2) + web * (h - 2 * rim) ** 3 / 12
    return ("arm bending at the crossbar (in the layer plane)", m * (h / 2) / inertia, SIGMA_XY, {"M N.m": round(m / 1000, 1)})


def link_buckling():
    w, dig, m_pivot, f_link = lift_loads()
    inertia = LINK_W * LINK_T ** 3 / 12
    p_cr = 2 * pi ** 2 * E_PETG * inertia / LINK_LEN ** 2      # two plates, pinned ends
    return ("lift link buckling (2 plates)", f_link, p_cr, {"load N": round(f_link), "P_cr N": round(p_cr)})


def link_tension():
    w, dig, m_pivot, f_link = lift_loads()
    return ("lift link tension", f_link / (2 * LINK_T * LINK_W), SIGMA_XY, {})


def drum_torque_path():
    torque = 1.9e3                                             # N mm, ~stall of a 30 RPM Johnson (measure first)
    force = torque / (84.0 * 4)                                # N per tie rod at r = 84
    return ("drum torque through the lugs (per rod, N)", force, 400.0, {"torque N.m": 1.9})


def screw_self_locking():
    """M8 x 1.25 rod, 60 deg thread: effective friction = mu / cos(30). Brass on steel is 0.15-0.20 dry."""
    lead_angle = degrees(atan(1.25 / (pi * 7.188)))
    mu_needed = tan(radians(lead_angle)) * cos(radians(30.0))
    return ("M8 rod: friction needed to self-lock (dry brass on steel: 0.15)", mu_needed, 0.15, {"lead angle deg": round(lead_angle, 2)})


def screw_force_capacity():
    """Information only: what the lift motor must deliver at the link load (motor torque is measure-first)."""
    w, dig, m_pivot, f_link = lift_loads()
    torque = f_link * 0.00125 / (2 * pi * 0.24) * 1000         # N mm at efficiency 0.24 (M8 rod, brass nut)
    return f_link, torque / 98.1                               # N, kg.cm


def tray_plate():
    """Tray half as five T-ribs (plate strip + 3 x 6 rib) cantilevered off the rail; the heavier bay's boards, x3 shock, at the tip.
    A10 asks for a deflection of at most 1 mm at 3x the static load, so this row needs a factor of 1 on that limit."""
    from lib import cots
    from modules import electronics as el
    pitch, rib_w = 40.0, 3.0
    bay: dict[bool, float] = {}
    for sku, cx, cy, rot in el.LAYOUT.values():
        bay[cy > 0] = bay.get(cy > 0, 0.0) + cots.BOARDS[sku][3]
    force = max(bay.values()) / 1000.0 * G * SHOCK / len(el.RIB_X)          # N per rib
    length = (RAIL_Y - 10.0) - el.LEFT_Y[0]                                   # rail's inner face to the tray's free edge
    a1, z1 = pitch * el.PLATE_T, el.PLATE_T / 2
    a2, z2 = rib_w * el.RIB_H, el.PLATE_T + el.RIB_H / 2
    zc = (a1 * z1 + a2 * z2) / (a1 + a2)
    inertia = pitch * el.PLATE_T ** 3 / 12 + a1 * (zc - z1) ** 2 + rib_w * el.RIB_H ** 3 / 12 + a2 * (z2 - zc) ** 2
    defl = force * length ** 3 / (3 * E_PETG * inertia)
    return ("tray plate deflection at 3x load (mm; limit 1)", defl, 1.0, {"boards g": round(max(bay.values())), "span mm": round(length), "I mm4": round(inertia)})


CHECKS = [wheel_housing, wheel_bearings, mount_bolts, axle_bolt, pivot_wall_bearing, arm_section, link_buckling,
          link_tension, drum_torque_path, screw_self_locking, tray_plate]
REQUIRED = {tray_plate: 1.0}                                   # every other row needs a safety factor of 2


def run(verbose: bool = True):
    rows = []
    for fn in CHECKS:
        name, demand, capacity, inputs = fn()
        sf = capacity / demand if demand else float("inf")
        req = REQUIRED.get(fn, 2.0)
        rows.append((name, demand, capacity, sf, req, inputs))
        if verbose:
            print(f"{'PASS' if sf >= req else 'FAIL'}  SF {sf:5.1f} (need {req:g})  {name}: demand {demand:.2f} vs capacity {capacity:.2f}  {inputs}")
    if verbose:
        f, kgcm = screw_force_capacity()
        print(f"INFO  lift link load {f:.0f} N needs about {kgcm:.1f} kg.cm at the M8 rod (Johnson 300 RPM: measure stall; "
              f"the 100 RPM motor fits the same cradle)")
    return rows


if __name__ == "__main__":
    run()
