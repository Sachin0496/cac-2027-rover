"""Run every check on an assembly; returns (problems, info)."""
from __future__ import annotations

from checks import interference, massprops, printfit, validity

# Requirements from the spec: A6 (empty mass, wiring allowance included) and A7 (front-axle share with 2.1 kg of sand at the drum).
MASS_LIMIT_G = 8000.0
FRONT_SHARE_LIMIT = 0.75


def sweep_check(poses) -> list[str]:
    """A1 over the arm sweep: no collision at the key poses, 2 mm clearance moving-vs-static at every pose."""
    from assemble import rover
    problems: list[str] = []
    for pose in poses:
        asm = rover(pose)
        mv = [i.id for i in asm.items if i.moving in ("arm", "carriage")]
        st = [i.id for i in asm.items if i.moving is None]
        problems += [f"pose {pose}: {m}" for m in interference.sweep_problems(asm, mv, st)]
    return problems


def pose_collisions(poses) -> list[str]:
    """A1 exact-solid collisions at the key arm poses."""
    from assemble import rover
    out = []
    for pose in poses:
        out += [f"pose {pose}: collision {a} x {b}: {v:.1f} mm3" for a, b, v in interference.find_collisions(rover(pose))]
    return out


def run_checks(asm, full: bool = False) -> tuple[list[str], dict]:
    """Checks that need one assembly. `full` adds the slow ones: nothing floats (contact graph) and the A8/A9 rules."""
    problems: list[str] = []
    problems += validity.check_valid(asm)
    problems += printfit.check_assembly(asm)
    for a, b, v in interference.find_collisions(asm):
        problems.append(f"collision {a} x {b}: {v:.1f} mm3")
    bal = massprops.balance(asm)
    mp = bal["empty"]
    if MASS_LIMIT_G is not None and mp["mass_g"] > MASS_LIMIT_G:
        problems.append(f"empty mass {mp['mass_g']:.0f} g (with {massprops.WIRING_G:.0f} g wiring allowance) above limit {MASS_LIMIT_G:.0f} g")
    if bal["loaded"] is not None and FRONT_SHARE_LIMIT is not None and bal["loaded"]["front_share"] > FRONT_SHARE_LIMIT:
        problems.append(f"front-axle share with a full drum {bal['loaded']['front_share'] * 100:.1f} % above limit {FRONT_SHARE_LIMIT * 100:.0f} %")
    info = {"mass": mp, "balance": bal, "items": len(asm.items)}
    if full:
        from checks import contact, rules
        for fid, touching in contact.under_supported(asm).items():
            problems.append(f"fastener {fid} holds {len(touching)} part(s): {touching}")
        problems += [f"floating: {i}" for i in contact.floating_items(asm)]
        rp, rinfo = rules.check_rules(asm)
        problems += rp
        info["rules"] = rinfo
    return problems, info
