// Shared dimensions for the CAC 2027 rover v1 (units: mm, degrees).
// `include <params.scad>` from every part file. No geometry here.
//
// World frame: +X forward (drum end), +Y left, +Z up; ground at z = 0;
// frame centred on x = y = 0.

// ---------- stock and hardware ----------
tube = 20;                 // 20 × 20 mm aluminium square tube, 1.5 mm wall
m3 = 3.4;                  // clearance holes
m4 = 4.4;
m5 = 5.4;
m8 = 8.4;
m4_nut = 7.4;              // across flats + clearance
m8_nut = 13.3;
m8_nut_t = 6.8;
b608_d = 22.2;             // 608 bearing pocket
b608_w = 7.2;

// ---------- Johnson side-shaft geared motor (measure yours!) ----------
jm_gear_d = 37;            // gearbox diameter
jm_gear_len = 25;
jm_can_d = 28.5;           // motor can diameter; gear + can = 63 mm
jm_can_len = 38;
jm_shaft_d = 6;            // D-shaft
jm_shaft_flat = 5.5;       // across the flat
jm_shaft_len = 22;
jm_shaft_off = 7.5;        // output shaft offset from the gearbox axis

// ---------- wheels (geometry lives in wheel.scad) ----------
wheel_d = 174;             // over the grousers
wheel_w = 60;
wheel_hub_len = 25;
axle_z = wheel_d / 2;      // axle height on firm ground

// ---------- frame ----------
rail_len = 420;            // side rails along X
frame_w = 300;             // outside width of the tube rectangle
rail_y = frame_w / 2 - tube / 2;          // rail centre line, |y|
axle_x = 150;                             // axles at ±axle_x
wheel_gap = 10;                           // rail outer face → wheel inner edge
wheel_in_y = frame_w / 2 + wheel_gap;     // 160
wheel_out_y = wheel_in_y + wheel_w;       // 220
gear_face_y = wheel_out_y - wheel_hub_len - 2;   // drive gearbox face, |y|
// Drive motors hang under the rails with the offset shaft pointing down,
// so the gearbox axis sits jm_shaft_off above the axle.
drive_gear_z = axle_z + jm_shaft_off;
rail_z0 = drive_gear_z + jm_gear_d / 2 + 3;      // clamp roof under the rails
rail_z1 = rail_z0 + tube;
deck_t = 6;                                      // plywood
deck_z = rail_z1 + deck_t;                       // deck top
deck_x0 = -rail_len / 2;
deck_x1 = 178;                                   // stops short of the arm roots

// ---------- lift arms and drum ----------
pivot_x = rail_len / 2 - 11;
pivot_z = rail_z0 + tube / 2;
arm_len = 130;             // pivot → drum axis
arm_t = 12;
arm_root_r = 18;
arm_end_r = 36;
drum_len = 200;
drum_r = 80;               // shell outer radius
drum_tip_r = 90;           // scoop tooth tips
hub_gap = 16;              // drum end plate → arm: room for the bolt-on hubs
arm_in_y = drum_len / 2 + hub_gap;
arm_out_y = arm_in_y + arm_t;
crossbar_at = [25, 35];    // arm-local [along, up] of the 20 × 20 crossbar
lever_pin_at = [-10, 80];  // arm-local position of the lever pin
arm_down = -20;            // digging: tooth tips ~8 mm below grade
arm_press = -25;           // lowest: pressing the drum into the sand
arm_up = 35;               // carrying: drum ~110 mm clear of the ground

// ---------- lift actuator (lead screw on the deck, y = 0) ----------
screw_z = deck_z + 14;     // M8 screw axis height
carriage_pin_z = deck_z + 30;
pushrod_len = 85;          // pin centre to pin centre
act_front_x = 171;         // front 608 bearing centre
act_rear_x = 36;           // rear 608 bearing centre
carriage_len = 30;

// ---------- mast ----------
mast_x = -axle_x;          // stands on the rear cross member
mast_h = 380;

// ---------- assembly colours ----------
c_alu = "Silver";
c_print = "SteelBlue";
c_print2 = "DarkOrange";
c_motor = "DimGray";
c_wood = "BurlyWood";
c_pcb = "ForestGreen";

// ---------- helpers ----------
// Arm-local point p = [along, up] → world [x, z] at arm angle a.
function arm_pt(a, p) = [pivot_x + p[0] * cos(a) - p[1] * sin(a),
                         pivot_z + p[0] * sin(a) + p[1] * cos(a)];
// Carriage pin x for a given arm angle (pushrod geometry).
function carriage_x(a) = let (p = arm_pt(a, lever_pin_at))
    p[0] - sqrt(pushrod_len * pushrod_len - pow(p[1] - carriage_pin_z, 2));
