"""Generated documentation: keeps every number in the guides in step with the model.

    python tasks.py docs

rewrites the blocks between `<!-- BEGIN:name -->` and `<!-- END:name -->` in docs/v2-build-guide.md and writes
docs/v2-order-list.md completely. The prose around the blocks is hand-written.
"""
from __future__ import annotations

import pathlib
import re
from collections import OrderedDict, defaultdict

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
DOCS = HERE.parent / "docs"
COLOR_NAMES = {"#FFCD11": "yellow", "#2B2E33": "graphite", "#C9CDD2": "aluminium", "#8A8F98": "steel", "#B5A642": "brass",
               "#1A1A1A": "black", "#D7191C": "red", "#F2F2F2": "white"}
POSE_NAMES = {-28: "press", -25: "dig", 0: "level", 20: "mid", 35: "carry / dump"}
PRINT_G_PER_HOUR = 25.0             # v1's rate: a 180 g part is about 7 h
MODULE_ORDER = ["drive", "excavator", "electronics", "tower", "body"]
MODULE_TITLES = {"drive": "Drive modules", "excavator": "Excavator: drum, arms, lift", "electronics": "Electronics tray and battery",
                 "tower": "Sensor tower and E-stop", "body": "Body"}


def _md_table(head, rows, align=None):
    align = align or ["l"] * len(head)
    sep = ["---:" if a == "r" else ":---" if a == "l" else ":---:" for a in align]
    out = ["| " + " | ".join(head) + " |", "| " + " | ".join(sep) + " |"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def gather() -> dict:
    """Everything the documents quote, computed from the model (about a minute)."""
    import calcs
    from assemble import rover
    from checks import massprops, runner
    from export import bom_rows, cut_plan, extra_rows, printed_table
    from modules.excavator import carriage_x
    from params import AXLE_X_FRONT, AXLE_X_REAR, POSES, WHEEL_IN_Y, WHEEL_OUT_Y

    asm = rover(35)
    bbs = [it.shape.bounding_box() for it in asm.items]
    lo = np.min([[b.min.X, b.min.Y, b.min.Z] for b in bbs], axis=0)
    hi = np.max([[b.max.X, b.max.Y, b.max.Z] for b in bbs], axis=0)
    mods = defaultdict(lambda: [0.0, 0.0, 0])
    for it in asm.items:
        m = mods[it.module]
        m[0 if it.kind == "printed" else 1] += it.mass()
        m[2] += 1
    bal = massprops.balance(asm)
    poses = []
    for p in POSES:
        r = rover(p)
        rings = [it.shape.bounding_box() for it in r.items if it.part.startswith("drum_ring")]
        poses.append({"pose": p, "tip_low": min(b.min.Z for b in rings), "tip_high": max(b.max.Z for b in rings),
                      "front_x": max(b.max.X for b in rings), "carriage_x": carriage_x(p)})
    colours = defaultdict(set)
    for it in asm.items:
        if it.kind == "printed":
            colours[it.part].add(COLOR_NAMES.get(it.color.upper(), it.color))
    part_module = {}
    for it in asm.items:
        if it.kind == "printed":
            part_module.setdefault(it.part, it.module)
    bom, extra = bom_rows(asm), extra_rows(asm)
    cuts = [it.meta["cut_mm"] for it in asm.items if it.kind == "stock"]
    lowest = min(it.shape.bounding_box().min.Z for it in asm.items if it.kind != "printed" or it.module == "drive" and it.part.startswith("drv_cradle"))
    return {"asm": asm, "size": tuple(float(v) for v in hi - lo), "mods": dict(mods), "bal": bal, "poses": poses,
            "printed": printed_table(asm), "colours": colours, "part_module": part_module, "bom": bom, "extra": extra,
            "bom_total": sum(r["total_inr"] for r in bom + extra), "cuts": cuts, "bars": cut_plan(cuts), "calcs": calcs.run(verbose=False),
            "mass_limit": runner.MASS_LIMIT_G, "share_limit": runner.FRONT_SHARE_LIMIT, "wiring": massprops.WIRING_G, "sand": massprops.SAND_G,
            "wheelbase": AXLE_X_FRONT - AXLE_X_REAR, "track": (WHEEL_IN_Y + WHEEL_OUT_Y), "n_purchased": len({r["item"] for r in bom}),
            "tests": None}


# ---------------------------------------------------------------- blocks
def block_numbers(f: dict) -> str:
    b, m = f["bal"], f["mods"]
    empty, loaded = b["empty"], b["loaded"]
    printed_g = sum(r["grams_total"] for r in f["printed"])
    modelled = empty["mass_g"] - f["wiring"]
    dig = next(p for p in f["poses"] if p["pose"] == -25)
    press = next(p for p in f["poses"] if p["pose"] == -28)
    carry = next(p for p in f["poses"] if p["pose"] == 35)
    rows = [
        ("Stowed size (carry pose)", f"{f['size'][0]:.0f} x {f['size'][1]:.0f} x {f['size'][2]:.0f} mm (limit 1500 x 750 x 750)"),
        ("Wheelbase, track", f"{f['wheelbase']:.0f} mm, {f['track'] / 2 + 160 - 160:.0f} mm between wheel centres" if False else f"{f['wheelbase']:.0f} mm, {2 * (160 + 30):.0f} mm between wheel centres"),
        ("Empty mass", f"{empty['mass_g'] / 1000:.2f} kg = {modelled / 1000:.2f} kg modelled + {f['wiring']:.0f} g wiring allowance (limit {f['mass_limit'] / 1000:.1f} kg, goal 7.5 kg)"),
        ("Mass with a full drum", f"{loaded['mass_g'] / 1000:.2f} kg ({f['sand'] / 1000:.1f} kg of sand)"),
        ("Front-axle share", f"{empty['front_share'] * 100:.0f} % empty, {loaded['front_share'] * 100:.0f} % with a full drum at the carry pose (limit {f['share_limit'] * 100:.0f} %; v1: 80 %)"),
        ("Centre of gravity, empty", f"x = {empty['cg'][0]:.0f}, y = {empty['cg'][1]:.0f}, z = {empty['cg'][2]:.0f} mm (x from the frame centre, forward positive)"),
        ("Arm range", f"press -28 deg (teeth {abs(press['tip_low']):.0f} mm below grade), dig -25 deg ({abs(dig['tip_low']):.0f} mm below), level 0, mid +20, carry +35 deg (teeth {carry['tip_low']:.0f} mm up)"),
        ("Lift", f"M8 x 1.25 rod with two brass nuts, stroke {abs(f['poses'][0]['carriage_x'] - carry['carriage_x']):.0f} mm, self-locking"),
        ("Printed parts", f"{len(f['printed'])} part types, {printed_g / 1000:.2f} kg of PETG (v1 rule: volume x 1.27 x 0.75), largest {max(r['grams_each'] for r in f['printed'])} g, no supports"),
        ("Purchased", f"{f['n_purchased']} SKUs, {sum(len([1 for i in f['asm'].items if i.kind == 'purchased']) for _ in [0])} pieces; total budget INR {f['bom_total']:,.0f} with filament (cap 25,000; v1 22,120)"),
    ]
    return _md_table(["What", "Value"], rows)


def block_print(f: dict) -> str:
    rows_by_mod: dict[str, list] = OrderedDict((m, []) for m in MODULE_ORDER)
    for r in f["printed"]:
        rows_by_mod[f["part_module"][r["part"]]].append(r)
    out = []
    total_g = sum(r["grams_total"] for r in f["printed"])
    for mod, rows in rows_by_mod.items():
        if not rows:
            continue
        out.append(f"**{MODULE_TITLES[mod]}**\n")
        out.append(_md_table(["Part (STL name)", "Qty", "Size in print position, mm", "g each", "g total", "Colour"],
                             [(f"`{r['part']}`", r["qty"], f"{r['x_mm']} x {r['y_mm']} x {r['z_mm']}", r["grams_each"], r["grams_total"],
                               "/".join(sorted(f["colours"][r["part"]]))) for r in rows], ["l", "r", "l", "r", "r", "l"]))
        out.append("")
    out.append(f"Total {total_g / 1000:.2f} kg of PETG in {len(f['printed'])} part types "
               f"(about {total_g / PRINT_G_PER_HOUR:.0f} print hours at 25 g/h; the longest single print is "
               f"{max(r['grams_each'] for r in f['printed'])} g, about {max(r['grams_each'] for r in f['printed']) / PRINT_G_PER_HOUR:.0f} h). "
               "Every STL in `cad-v2/out/stl/` is already turned into its print position and sits on z = 0.")
    return "\n".join(out)


def block_poses(f: dict) -> str:
    rows = [(f"{p['pose']:+d} deg", POSE_NAMES[p["pose"]], f"{p['tip_low']:+.0f}", f"{p['tip_high']:.0f}", f"{p['carriage_x']:.1f}") for p in f["poses"]]
    return _md_table(["Arm angle", "Name", "Lowest tooth tip, mm above ground", "Highest point of the drum, mm", "Carriage on the rod, x mm"], rows, ["r", "l", "r", "r", "r"])


def block_mass(f: dict) -> str:
    rows = []
    tp = tb = 0.0
    for m in ["chassis"] + MODULE_ORDER:
        p, b, n = f["mods"][m]
        tp, tb = tp + p, tb + b
        rows.append((m, n, f"{p:.0f}", f"{b:.0f}", f"{p + b:.0f}"))
    rows.append(("**modelled total**", sum(v[2] for v in f["mods"].values()), f"**{tp:.0f}**", f"**{tb:.0f}**", f"**{tp + tb:.0f}**"))
    rows.append(("wiring allowance (not modelled)", "", "", "", f"{f['wiring']:.0f}"))
    rows.append(("**empty**", "", "", "", f"**{tp + tb + f['wiring']:.0f}**"))
    return _md_table(["Module", "Items", "Printed g", "Bought g", "Total g"], rows, ["l", "r", "r", "r", "r"])


def block_calcs(f: dict) -> str:
    rows = []
    for name, demand, capacity, sf, req, inputs in f["calcs"]:
        rows.append((name, f"{demand:.3g}", f"{capacity:.3g}", f"{sf:.1f}", f"{req:g}", ", ".join(f"{k} {v}" for k, v in inputs.items())))
    return _md_table(["Load path", "Demand", "Capacity", "Safety factor", "Needed", "Inputs"], rows, ["l", "r", "r", "r", "r", "l"])



PURPOSE = {
    "2020 T-slot, 1 m lengths": "frame: 2 rails, 2 cross members, spine, arm crossbar, tower post (3 bars, cut list in the order list)",
    "corner bracket 2020": "joins rails, cross members and spine; no drilling",
    "T-nut M5 spring": "every bolted joint into the frame slots",
    "motor_johnson_30rpm": "4 wheel drives and the drum motor: slow and strong for sand",
    "motor_johnson_300rpm": "lift screw motor (about 6 mm/s on the M8 rod)",
    "bearing_608": "2 per wheel axle, 2 on each drum axle, 1 per arm pivot, 2 on the lift rod",
    "coupler_6_8": "motor shaft to M8 axle or lift rod; forgives misalignment",
    "M8 threaded rod 150 mm": "lift screw: self-locking with the brass nuts",
    "M8 brass nut": "the two nuts in the lift carriage",
    "M4 threaded rod 211 mm": "drum tie rods that clamp the rings between the end plates",
    "bts7960": "motor drivers: left drive, right drive, drum, lift",
    "relay": "E-stop contactor, fails open: cuts the battery from every controller",
    "buck": "5 V rail for the Pi and sensors",
    "fuse_holder": "main and branch fuses",
    "pi5": "onboard computer (the team already has it)",
    "esp32": "motor PWM, encoders, limit switches",
    "mpu6050": "IMU, no magnetometer (the compass is banned)",
    "battery_3s2p": "11.1 V pack with a 20 A BMS, and its charger",
    "estop": "rules: unmodified red mushroom of at least 40 mm, twist to release",
    "estop_body": "contact block, comes with the E-stop",
    "pzem051": "rules: energy logger between battery and E-stop, high and visible",
    "servo_sg90": "camera pan, 0 and 180 degrees",
    "webcam": "driving view and AprilTag detection",
    "tof_vl53": "2 front (wheel tracks) and 1 rear hazard sensors (ultrasonic is banned)",
}
NAMES = {
    "2020 T-slot, 1 m lengths": "2020 aluminium T-slot, 1 m bars", "corner bracket 2020": "2020 inside corner brackets", "T-nut M5 spring": "M5 drop-in T-nuts for 2020",
    "motor_johnson_30rpm": "Johnson 12 V 30 RPM side-shaft gearmotor", "motor_johnson_300rpm": "Johnson 12 V 300 RPM gearmotor", "bearing_608": "608-2RS bearings",
    "coupler_6_8": "Aluminium helical coupler 6 to 8 mm", "M8 threaded rod 150 mm": "M8 threaded rod (cut 150 mm)", "M8 brass nut": "M8 brass nuts",
    "M4 threaded rod 211 mm": "M4 threaded rod (cut 4 x 211 mm)", "bts7960": "BTS7960 43 A motor driver", "relay": "12 V 40 A relay with socket",
    "buck": "5 V 5 A buck converter", "fuse_holder": "Inline blade-fuse holder", "pi5": "Raspberry Pi 5 with active cooler", "esp32": "ESP32 dev board",
    "mpu6050": "MPU6050 IMU", "battery_3s2p": "3S2P Li-ion pack and charger", "estop": "22 mm twist-release E-stop", "estop_body": "E-stop contact block",
    "pzem051": "PZEM-051 DC energy meter, 50 A shunt", "servo_sg90": "SG90 micro servo", "webcam": "USB webcam 720p", "tof_vl53": "VL53L1X ToF sensor",
}


def block_buy(f: dict) -> str:
    rows = []
    for r in f["bom"] + f["extra"]:
        name = NAMES.get(r["item"], r["item"])
        why = PURPOSE.get(r["item"]) or r["notes"].split(";")[0]
        price = "have" if r["price_basis"] == "have" else f"{r['unit_price_inr']:g}"
        total = "have" if r["price_basis"] == "have" else f"{r['total_inr']:,}"
        rows.append((name, r["qty"], price, total, why))
    rows.append(("**Total**", "", "", f"**{f['bom_total']:,.0f}**", "excludes the Pi 5 (owned), router, laptops, printer, travel; cap is 25,000"))
    return _md_table(["Part", "Qty", "INR each", "INR total", "What it is for"], rows, ["l", "r", "r", "r", "l"])


BLOCKS = {"buy": block_buy, "numbers": block_numbers, "print": block_print, "poses": block_poses, "mass": block_mass, "calcs": block_calcs}


def rewrite_blocks(path: pathlib.Path, f: dict) -> None:
    text = path.read_text()
    for name, fn in BLOCKS.items():
        pat = re.compile(rf"(<!-- BEGIN:{name} -->\n).*?(<!-- END:{name} -->)", re.S)
        if pat.search(text):
            text = pat.sub(lambda m: m.group(1) + fn(f) + "\n" + m.group(2), text)
    path.write_text(text)


# ---------------------------------------------------------------- order list
CATEGORIES = OrderedDict([
    ("Frame", ["2020 T-slot", "corner bracket 2020", "T-nut M5 spring"]),
    ("Motors and motion", ["motor_johnson_30rpm", "motor_johnson_300rpm", "bearing_608", "coupler_6_8", "M8 threaded rod 150 mm", "M8 brass nut", "M4 threaded rod 211 mm"]),
    ("Electronics and sensors", ["bts7960", "relay", "buck", "fuse_holder", "pi5", "esp32", "mpu6050", "battery_3s2p", "estop", "estop_body", "pzem051", "servo_sg90", "webcam", "tof_vl53"]),
])


def write_order_list(f: dict, path: pathlib.Path) -> None:
    from lib.prices import PRICES
    rows = {r["item"]: r for r in f["bom"]}
    rows["2020 T-slot"] = rows.pop("2020 T-slot, 1 m lengths")
    seen = set()
    sections = []
    for cat, skus in CATEGORIES.items():
        body = []
        for s in skus:
            if s in rows:
                r = rows[s]
                seen.add(s)
                body.append(r)
        sections.append((cat, body))
    fasteners = [r for k, r in rows.items() if k not in seen]
    sections.append(("Fasteners (buy assortments; quantities are what the model uses)", fasteners))

    def table(rs):
        return _md_table(["Item", "Qty", "Unit INR", "Total INR", "Basis", "Where / note"],
                         [(r["item"], r["qty"], f"{r['unit_price_inr']:g}", f"{r['total_inr']:,}", r["price_basis"], f"{r['source']}. {r['notes']}") for r in rs],
                         ["l", "r", "r", "r", "l", "l"])
    out = ["# Rover v2: order list", "",
           "Generated by `python tasks.py docs` from the model (`hardware/bom_v2.csv` has the same lines). Prices are INR including GST. "
           "**listed** = seen in an Indian store listing on 2026-09-29 (or v1's listing of 2026-09-28); **estimate** = a typical price, check before paying; "
           "**have** = the team owns it. Unchanged items keep v1's price so the two budgets compare.", "",
           f"**Total INR {f['bom_total']:,.0f}** with filament, wiring, practice sand and spares (cap INR 25,000; v1 INR 22,120). "
           "Not included: Raspberry Pi 5 (the team has it), the dual-band router (borrow), laptops, the printer, travel.", "",
           "Order by about 5 October 2026 so parts arrive before the working-rover video window (10 October to 10 November).", ""]
    for cat, body in sections:
        sub = sum(r["total_inr"] for r in body)
        out += [f"## {cat}: INR {sub:,}", "", table(body), ""]
    out += ["## Aluminium cut list", "",
            "Buy three 1 m lengths of 2020 (slot 6, B-type) and cut them as below; +-1 mm is fine, nothing else is drilled or tapped. "
            "The plan leaves at least 10 mm spare per bar for the saw kerf (about 3 mm per cut).", ""]
    names = {402: "rail (x2)", 260: "cross member (x2)", 259: "spine", 212: "arm crossbar", 240: "tower post"}
    for i, bar in enumerate(f["bars"], 1):
        parts = " + ".join(f"{int(c)} ({names.get(int(c), 'part')})" for c in bar)
        out.append(f"- Bar {i}: {parts}; {1000 - sum(bar) - 3 * (len(bar) - 1):.0f} mm left")
    out += ["", "Two more cuts, both with a hacksaw: the four 211 mm M4 tie rods for the drum come from one 1 m rod, and the 150 mm M8 lift screw comes from a 1 m rod "
            "(keep the rest as a spare).", "",
            "## Extras that are not in the model", "", table(f["extra"]), "",
            "## Where the money could move", "",
            f"- The budget is under the cap by INR {25000 - f['bom_total']:,.0f}. The PZEM-051 is booked at v1's INR 2,000 because Robu did not show a price; "
            "similar meters list far lower, so expect INR 500 to 1,000 back.",
            "- E-stop: the model uses a 60 mm head; any twist-release red mushroom of at least 40 mm complies, so check the head size of whatever you order. A plastic 22 mm unit "
            "(Evelta XB2-BS542 at INR 198) would do if its head is 40 mm or more; a metal one (Probots ProMax, INR 899) is sturdier.",
            "- Johnson motors: Robokits lists the 30 RPM Grade A at INR 412 and the 300 RPM at INR 477; buy one spare (already inside the INR 1,500 spares line).",
            "- If the printer is slow, the cheapest way to save print time is `body_side_cover_l/r`, the three arrow plates and `tower_sleeve_*` (cosmetic, about 60 g together). Nothing else can go without a redesign.",
            "", "## Measure-first items", "",
            "Sizes of the BTS7960 module, relay, buck converter, fuse holders, PZEM-051, E-stop body, battery pack and webcam are datasheet or listing values "
            "(`cad-v2/lib/cots.py`). Board holders have slotted screw holes (+-3 mm) so a different size still fits; the battery cradle is the one part sized to the pack "
            "(`BATT` in `modules/electronics.py`). Measure each item when it arrives and change the number before printing that part. "
            "The Johnson motor's gearbox diameter (37 mm) and shaft offset (7.5 mm) decide the four `drv_cradle_*` and the arm/lift clamps: measure one motor first.", ""]
    path.write_text("\n".join(out))


def main() -> int:
    f = gather()
    write_order_list(f, DOCS / "v2-order-list.md")
    guide = DOCS / "v2-build-guide.md"
    if guide.exists():
        rewrite_blocks(guide, f)
    readme = DOCS.parent / "README.md"
    if readme.exists():
        rewrite_blocks(readme, f)
    print(f"docs written: {DOCS / 'v2-order-list.md'}" + (f", blocks refreshed in {guide.name}" if guide.exists() else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
