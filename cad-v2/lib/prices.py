"""Unit prices (INR, incl. GST) for every purchased SKU in the model, keyed by SKU.
basis: 'listed' (an Indian store listing seen 2026-09-29, or v1's listing from 2026-09-28), 'estimate', or 'have' (the team owns it).
Unchanged items keep v1's price so the two BOMs compare like for like."""

_L, _E, _H = "listed", "estimate", "have"
_LOCAL = "local / Amazon.in"

PRICES = {
    # sku: (unit price, basis, source, note)
    # ---- motion
    "motor_johnson_30rpm": (412, _L, "Robokits RKI-1156 (Grade A), 2026-09-29", "Johnson 12 V 30 RPM side-shaft, 32 kg.cm (4 drive + 1 drum); measure one before printing the cradles"),
    "motor_johnson_300rpm": (477, _L, "Robokits RKI-1144 (Grade A), 2026-09-29", "Johnson 12 V 300 RPM for the lift screw"),
    "bearing_608": (35, _E, "local / Robu", "608-2RS"),
    "coupler_6_8": (100, _E, "RoboticsDNA ZRB-19x25 at 65 (out of stock 2026-09-29); Robu 100-150", "aluminium helical coupler 6 to 8 mm, D19 x L25"),
    "M8 threaded rod 150 mm": (40, _E, "local hardware", "lift screw: cut 150 mm from a 1 m zinc or stainless M8 rod (about 100 INR per metre)"),
    "M8 brass nut": (12, _E, "local hardware", "brass hex nut M8, two per carriage"),
    "M4 threaded rod 211 mm": (10, _E, "local hardware", "drum tie rods: buy one 1 m M4 rod (about 40 INR) and cut four 211 mm lengths with a hacksaw"),
    # ---- frame
    "corner bracket 2020": (25, _L, "3DPrintronics 32; IndiaMART 19 per piece", "2020 inside corner bracket"),
    "T-nut M5 spring": (8, _E, "Amazon.in kits / Mech Shop", "M5 drop-in spring T-nut for a 2020 slot 6 (SuperbTech sliding nuts: 10 for 145)"),
    # ---- fasteners
    "M5x8 button": (3, _E, _LOCAL, "ISO 7380 button head"),
    "M5x10 button": (3, _E, _LOCAL, "ISO 7380 button head"),
    "M5x12 button": (3, _E, _LOCAL, "ISO 7380 button head"),
    "M5x14 button": (3, _E, _LOCAL, "ISO 7380 button head"),
    "M5x10 socket": (3, _E, _LOCAL, "ISO 4762 socket head (collar clamp screws)"),
    "M5x16 socket": (3, _E, _LOCAL, "ISO 4762 socket head (clamp screws)"),
    "M5x40 socket": (4, _E, _LOCAL, "ISO 4762 socket head (link pins)"),
    "M5 nyloc": (2.5, _E, _LOCAL, "nyloc nut"),
    "M5 washer": (1, _E, "local hardware", "M5 washer"),
    "M4x8 socket": (2.5, _E, _LOCAL, "ISO 4762 socket head"),
    "M4x14 socket": (2.5, _E, _LOCAL, "ISO 4762 socket head"),
    "M4x25 socket": (3, _E, _LOCAL, "ISO 4762 socket head"),
    "M4x30 socket": (3, _E, _LOCAL, "ISO 4762 socket head"),
    "M4x40 socket": (3, _E, _LOCAL, "ISO 4762 socket head"),
    "M4x60 button": (4, _E, _LOCAL, "ISO 7380 button head (hood screws)"),
    "M4x100 socket": (5, _E, _LOCAL, "ISO 4762 socket head (handle through-bolts)"),
    "M4 nut": (1, _E, _LOCAL, "hex nut"),
    "M4 nyloc": (2, _E, _LOCAL, "nyloc nut"),
    "M8x35 hex": (13, _E, "local hardware", "ISO 4017 hex bolt (arm pivots)"),
    "M8x40 hex": (13, _E, "local hardware", "ISO 4017 hex bolt (drum idler axle)"),
    "M8x70 hex": (16, _E, "local hardware", "ISO 4017 hex bolt (drum drive axle)"),
    "M8x75 hex": (18, _E, "local hardware", "ISO 4017 hex bolt, partly threaded (wheel axles)"),
    "M8 nyloc": (6, _E, "local hardware", "nyloc nut"),
    "M8 washer": (2, _E, "local hardware", "M8 washer"),
    # ---- electronics and sensors
    "bts7960": (300, _L, "Robokits RKI-6606 at 256; others 329-353 (v1 price)", "43 A H-bridge driver: left drive, right drive, drum, lift"),
    "relay": (250, _E, "Amazon.in / local electrical shop", "12 V 40 A automotive relay with socket, fails open"),
    "buck": (250, _E, "Amazon.in / Robu", "5 V 5 A step-down (LM2596/XL4015 class) for the Pi and sensors"),
    "fuse_holder": (100, _E, "Amazon.in / local electrical shop", "inline blade-fuse holder (main and branch)"),
    "pi5": (0, _H, "the team has it", "Raspberry Pi 5 with active cooler (excluded from the total)"),
    "esp32": (500, _E, "Robu / Amazon.in (v1 price)", "ESP32 dev board: motor PWM, encoders, limit switches"),
    "mpu6050": (200, _E, "Robu / Amazon.in (v1 price)", "6-axis IMU, no magnetometer"),
    "battery_3s2p": (2500, _E, "BatteryWorks 3S2P 5200 mAh pack listed at 900; pack with 20 A BMS and charger (v1 price)", "3S2P Li-ion pack, 11.1 V, at least 20 A BMS, plus 12.6 V charger"),
    "estop": (400, _E, "Evelta XB2-BS542 at 198 (head size not in the listing: the genuine XB2-BS542 is 40 mm, check it); Probots ProMax metal at 899", "22 mm panel-mount, twist-release, red mushroom head of at least 40 mm (modelled with 60 mm); any listed head size complies"),
    "estop_body": (0, _H, "with the E-stop", "contact block of the panel-mount E-stop (priced with the head)"),
    "pzem051": (2000, _E, "Robu.in (price not visible on 2026-09-29; Alibaba $8.5 wholesale)", "PZEM-051 DC energy meter with 50 A shunt, wired between battery and E-stop (v1 price, probably lower)"),
    "servo_sg90": (150, _E, "Robu / Amazon.in (v1 price)", "camera pan servo"),
    "webcam": (1000, _E, "Amazon.in (v1 price)", "USB webcam 720p, driving view and AprilTag detection"),
    "tof_vl53": (500, _L, "Robokits 402; KTRON 570 (v1 price)", "VL53L1X ToF sensor: 2 front (wheel tracks) + 1 rear; Class 1 laser (allowed)"),
}

STOCK_PER_M = {"2020 T-slot": (420, _L, "Fastdep 420 incl. GST (heavy); Robu EasyMech 1 m; ~398 from", "2020 T-slot B-type slot 6, 1 m lengths, cut with a hacksaw (+-1 mm is fine) or by the vendor")}

# Lines that are not in the model but belong in the budget (v1 carries the same lines).
EXTRA_LINES = (
    ("Wire, connectors, XT60, ferrules, heat-shrink, cable ties", 1, 1000, _E, "local electrical shop", "the 250 g wiring allowance in the mass budget"),
    ("Practice sand pit + printed AprilTags", 1, 1000, _E, "local", "beach, volleyball or construction sand is fine; for the working-rover video"),
    ("Lift limit switches: 2 micro switches with lever, wire", 1, 100, _E, "Robu / Amazon.in", "not in the model; one at each end of the lift channel"),
    ("Spares (motor, driver, fuses, cells)", 1, 1500, _E, "Robokits / Robu / local", "same allowance as v1"),
)
FILAMENT_PER_KG = (1000, _E, "Amazon.in / local", "PETG 1.75 mm, 1 kg spool; buy the printed total x 1.10 for brims, purge and one reprint")
