"""Every shared dimension for rover v2 (mm, degrees, grams). Spec section 6.

World frame: +X forward, +Y left, +Z up, ground at z = 0, frame centred on x = y = 0.
Change a value here and run `python tasks.py all`; everything regenerates.
"""

# ---------- colours (spec 8.1: colour by function) ----------
COLORS = {
    "yellow": "#FFCD11",     # working parts: drum, arms, hood, tower head
    "graphite": "#2B2E33",   # structure and drive: wheels, mounts, cradles, covers, trays
    "alu": "#C9CDD2",        # 2020 extrusions
    "steel": "#8A8F98",      # bolts, nuts, washers
    "brass": "#B5A642",      # lead-screw nut
    "black": "#1A1A1A",      # boards, motors, servo, camera
    "red": "#D7191C",        # E-stop only
}

# ---------- tolerances (set from the fit-test kit) ----------
TOL_BEARING = 0.2   # added to a 22.0 mm bearing seat (printed seat = 22.2)
TOL_TRAP = 0.4      # added to nut across-flats in printed hex traps
TOL_HOLE = 0.4      # added to bolt diameter in printed clearance holes

# ---------- printing ----------
BED = (210.0, 210.0, 240.0)   # usable volume of a 220 x 220 x 250 printer
PETG = 1.27                   # g/cm3
FILL = 0.75                   # printed mass vs solid (3-4 walls, 25 % gyroid), same as v1
MAX_PRINT_G = 180.0           # no single print above this (A4)
OVERHANG_DEG = 45.0
BRIDGE_MAX = 8.0

# ---------- frame: 2020 T-slot ----------
TUBE = 20.0
RAIL_X0 = -212.0            # 17 mm behind the rear cross member: the outer corner brackets' T-nuts sit in this stub (x = -212..-202)
RAIL_LEN = 402.0           # to x = 190: carries the front pivot-bracket ears (T-nut to x = 184) and the front cradle bolts (x = 182)
RAIL_Y = 140.0                # rail centre line |y|; outer face 150, inner face 130
RAIL_Z0 = 116.0               # rail bottom; top = RAIL_Z0 + 20
CROSS_LEN = 260.0
PIVOT_X = 159.0               # arm pivot (v1: 199)
CROSS_FRONT_X = PIVOT_X - 65.0
CROSS_REAR_X = -185.0

# ---------- wheels and axles ----------
AXLE_X_FRONT = 150.0          # front axle: the arm's low poses need the front cradle where it is
AXLE_X_REAR = -110.0          # rear axle 40 mm further in than v1: wheelbase 260 keeps the front share with a full drum under 75 %
AXLE_Z = 87.0
WHEEL_D = 174.0               # over grouser tips
WHEEL_W = 60.0
WHEEL_IN_Y = 160.0
WHEEL_OUT_Y = 220.0

# ---------- Johnson 12 V side-shaft motor (v1 values, measure-first) ----------
JM_GEAR_D = 37.0
JM_GEAR_LEN = 25.0
JM_CAN_D = 28.5
JM_CAN_LEN = 38.0
JM_SHAFT_D = 6.0
JM_SHAFT_FLAT = 5.5
JM_SHAFT_LEN = 22.0
JM_SHAFT_OFF = 7.5            # gearbox axis above the shaft axis

# ---------- bearings and axle hardware ----------
B608_D = 22.0
B608_W = 7.0
B608_ID = 8.0
M8_BOLT_LEN = 75.0

# ---------- axle stack, left-side module, y measured outward from the frame centre ----------
# (y0, y1) ranges; single numbers are planes.
Y_STACK = {
    "gear_face": 123.4,
    "coupler": (133.6, 158.6),
    "nut": (158.6, 166.6),
    "washer": (166.6, 168.2),
    "spacer_end_in": (168.2, 170.7),
    "bearing_B": (170.7, 177.7),
    "spacer_mid": (177.7, 200.3),
    "bearing_A": (200.3, 207.3),
    "spacer_end_out": (207.3, 209.8),
    "wheel_boss": (209.8, 216.0),
    "wheel_wall": (216.0, 220.0),
    "cap": (220.0, 228.0),
    "bolt_head_underside": 222.5,
    "bolt_tip": 147.5,
}
MOUNT_PLATE_Y = (150.0, 160.0)
HOUSING_Y = (160.0, 207.3)
HOUSING_R = 16.5             # bearing-housing outer radius (bearing seat r = 11.1, wall 5.4)

# ---------- drop 2: excavator (spec 7.3, updated while modelling) ----------
SPINE_X = (-175.0, 84.0)      # centre spine between the rear and front cross members
PIVOT_Z = 148.0               # pivot above the rail top, on brackets that stand on the rails
ARM_LEN = 156.0               # pivot to drum axis (dig pose: tooth tips about 8 mm below grade)
ARM_Y = (106.0, 118.0)        # arm plate |y| (12 mm thick)
POSES = (-28, -25, 0, 20, 35) # press, dig, level, mid, carry/dump
DRUM_LEN = 200.0
DRUM_R = 80.0                 # shell outer radius
DRUM_TIP_R = 90.0             # tooth tips

# ---------- drum drive stack, left side, world y outward (drop 2) ----------
Y_DRUM = {
    "plate_outer": 100.0,                 # drum end plate, outer face
    "spacer_s1": (100.0, 106.2),
    "bearing_1": (106.2, 113.2),
    "spacer_mid": (113.2, 131.8),
    "bearing_2": (131.8, 138.8),
    "spacer_end": (138.8, 141.3),
    "washer": (141.3, 142.9),
    "nut": (142.9, 150.9),
    "coupler": (151.1, 176.1),
    "gear_face": 187.1,                   # shaft points inward (-y)
    "clamp": (187.1, 212.1),
    "bolt_head_underside": 93.5,          # hex head sits in the plate pocket inside the drum
    "bolt_len": 70.0,
}
R_ROOT, R_EAR, R_TIP, R_BOSS = 15.0, 19.0, 24.0, 19.0
PIVOT_WALL_Y = (119.6, 129.6)              # 10 mm bracket wall (bolt bending couple); an M8 washer spaces the arm bearing
LINK_T, LINK_W = 7.0, 14.0                 # link plates (buckling)
EAR_AT = (25.0, 35.0)                     # crossbar centre, arm-local (along, up)
LEVER_PIN_AT = (-10.0, 55.0)              # lever pin, arm-local (short lever: ~60 mm carriage stroke, 150 mm screw)
LINK_LEN = 100.0
CARRIAGE_PIN_Z = 175.0
CROSSBAR_LEN = 212.0                      # 2020, between the arm inner faces
BLOCK_W = 40.0                            # crossbar clamp block outer size (a x u)
BLOCK_HOLE_A = 15.0                       # arm-mounting M4 holes at +-15 from the crossbar axis

# ---------- lift screw drive (world frame; screw axis y = 0, z = 155) ----------
SCREW_Z = 155.0
SCREW_X = (-25.0, 125.0)                  # T8 x 2 lead screw, 150 mm
LIFT = {
    "channel_x": (-14.0, 127.0), "base_z": (136.0, 142.0), "wall_z_top": 166.0, "inner_w": 26.0,
    "block_rear_x": (-12.0, 2.0), "block_front_x": (97.0, 111.0), "block_z": (142.0, 168.0),
    "carriage_len": 24.0, "carriage_z": (143.0, 168.0), "ear_top": 186.0,
    "coupler_x0": -37.5, "motor_gear_face_x": -48.0,
    "cradle_x": (-75.0, -46.0), "cradle_half_w": 31.0,
    "feet": [(20.0, 0.0), (60.0, 0.0), (94.0, -8.0), (94.0, 8.0)],
}
