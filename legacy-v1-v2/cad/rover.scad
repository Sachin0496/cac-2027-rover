// CAC 2027 rover v1 — full assembly. Open this file in OpenSCAD.
//
//   lift = arm angle: arm_press (-25) pressing the drum in, arm_down (-20)
//   digging, arm_up (35) carrying / stowed. e.g. openscad -D lift=-20 rover.scad
//   show_envelope = true draws the rulebook's 1.5 × 0.75 × 0.75 m stowed box.
//
// The console prints the overall size, estimated mass and centre of gravity.
include <params.scad>
use <lib.scad>
use <frame.scad>
use <arm.scad>
use <actuator.scad>
use <electronics.scad>

lift = arm_up;
show_envelope = false;

frame_assembly();
lift_assembly(lift);
actuator_assembly(lift);
electronics_assembly();

if (show_envelope)
    %translate([-750 + 80, -375, 0]) cube([1500, 750, 750]);

// ---------- size check ----------
drum_c = arm_pt(lift, [arm_len, 0]);
x_min = -axle_x - wheel_d / 2;
x_max = max(drum_c[0] + drum_tip_r, 266);
z_max = max(deck_z + mast_h + 59, drum_c[1] + drum_tip_r);
size = [x_max - x_min, 2 * wheel_out_y, z_max];
echo(str("Overall size at lift ", lift, "°: ", round(size[0]), " × ", round(size[1]), " × ",
         round(size[2]), " mm (limit 1500 × 750 × 750 stowed): ",
         size[0] <= 1500 && size[1] <= 750 && size[2] <= 750 ? "OK" : "TOO BIG"));
echo(str("Drum: centre ", round(drum_c[0]), " mm ahead of the frame centre, tooth tips ",
         round(drum_c[1] - drum_tip_r), " mm above ground"));

// ---------- mass and centre of gravity (estimates, grams) ----------
arm_mid = arm_pt(lift, [55, 15]);
parts = [
    ["tube frame (1.36 m)", 408, [0, 0, 126]],
    ["plywood deck", 384, [(deck_x0 + deck_x1) / 2, 0, rail_z1 + 3]],
    ["wheels ×4 (PETG)", 4 * 230, [0, 0, axle_z]],
    ["drive motors ×4", 4 * 280, [0, 0, axle_z + 7]],
    ["drive clamps ×4", 4 * 90, [0, 0, axle_z + 12]],
    ["drum body + cap + hub", 720, [drum_c[0], 0, drum_c[1]]],
    ["drum motor", 280, [drum_c[0], 148, drum_c[1] + 7]],
    ["arms, lever, crossbar, links", 370, [arm_mid[0], 0, arm_mid[1]]],
    ["actuator motor + clamp", 360, [-43, 0, screw_z + 7]],
    ["actuator rod, channel, blocks", 300, [95, 0, screw_z]],
    ["electronics box (Pi 5, ESP32, buck, relay)", 275, [-55, -90, deck_z + 22]],
    ["motor drivers ×4 + hood", 390, [-55, 90, deck_z + 28]],
    ["battery 3S2P + tray", 340, [-172, -69, deck_z + 20]],
    ["mast, E-stop, PZEM, camera", 610, [mast_x - 15, 0, deck_z + 250]],
    ["ToF sensors + brackets", 60, [200, 0, 170]],
    ["wiring", 250, [-40, 0, deck_z + 15]],
    ["fasteners, inserts, bearings", 330, [30, 0, 120]]
];
sand_g = 2100;   // ~1.4 L of dry sand in the drum

function total(p, i = 0) = i >= len(p) ? 0 : p[i][1] + total(p, i + 1);
function moment(p, i = 0) = i >= len(p) ? [0, 0, 0] : p[i][1] * p[i][2] + moment(p, i + 1);

m = total(parts);
cg = moment(parts) / m;
cg_l = (moment(parts) + sand_g * [drum_c[0], 0, drum_c[1]]) / (m + sand_g);
front_share = function (c) (c[0] + axle_x) / (2 * axle_x);
echo(str("Mass ~", round(m / 100) / 10, " kg empty, ~", round((m + sand_g) / 100) / 10, " kg with sand"));
echo(str("CG empty x=", round(cg[0]), " z=", round(cg[2]), " mm → ", round(100 * front_share(cg)), "% on the front axle"));
echo(str("CG loaded x=", round(cg_l[0]), " z=", round(cg_l[2]), " mm → ", round(100 * front_share(cg_l)), "% on the front axle"));
