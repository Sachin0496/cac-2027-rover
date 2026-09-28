// Lift actuator on the deck centre line (world coordinates): a Johnson motor
// turns an M8 threaded rod held in two 608 bearings; a carriage with a
// captive M8 nut slides in a printed channel and pushes the lever through two
// pushrod links. M8 thread + ~300 RPM motor ≈ 6 mm/s; the thread is
// self-locking, so the drum holds its height with the motor off.
include <params.scad>
use <lib.scad>

$fn = 48;

ch_x0 = act_rear_x + 6;       // channel runs between the bearing blocks
ch_x1 = act_front_x - 6;
ch_w = 22;
ch_wall = 4;
ch_floor = 3;
ch_h = 24;
gear_face_x = -12;            // actuator motor gearbox face
rod_x0 = 7;                   // M8 rod start (inside the coupler)
rod_x1 = act_front_x + 9;
act_clamp_holes = [[-13, -15], [13, -15], [-13, -45], [13, -45]];

function act_clamp_holes() = act_clamp_holes;       // for print.scad
function ch_floor() = ch_floor;

module act_channel() {
    difference() {
        union() {
            translate([ch_x0, -ch_w / 2 - ch_wall, deck_z]) cube([ch_x1 - ch_x0, ch_w + 2 * ch_wall, ch_h]);
            translate([ch_x0, -ch_w / 2 - ch_wall - 8, deck_z]) cube([ch_x1 - ch_x0, ch_w + 2 * ch_wall + 16, 3]);
        }
        translate([ch_x0 - 1, -ch_w / 2, deck_z + ch_floor]) cube([ch_x1 - ch_x0 + 2, ch_w, ch_h]);
        for (x = [ch_x0 + 12, ch_x1 - 12], y = [-1, 1])
            translate([x, y * (ch_w / 2 + ch_wall + 4), deck_z - 1]) cylinder(d = m4, h = 5);
        // limit-switch lever windows in the left wall at both ends of travel
        for (x = [carriage_x(arm_up) - carriage_len / 2 - 4, carriage_x(arm_press) + carriage_len / 2 + 4])
            translate([x - 3, ch_w / 2 - 1, deck_z + 8]) cube([6, ch_wall + 2, 10]);
    }
}

// facing = +1: bearing pocket opens towards +x; -1: towards -x.
module act_bearing_block(x, facing) {
    difference() {
        union() {
            translate([x - 6, -15, deck_z]) cube([12, 30, 30]);
            translate([x - 6, -24, deck_z]) cube([12, 48, 4]);
        }
        translate([x, 0, screw_z]) rotate([0, 90, 0]) cylinder(d = m8 + 1, h = 20, center = true);
        translate([facing > 0 ? x + 6 - b608_w : x - 7, 0, screw_z]) rotate([0, 90, 0])
            cylinder(d = b608_d, h = b608_w + 1);
        for (y = [-19, 19]) translate([x, y, deck_z - 1]) cylinder(d = m4, h = 6);
    }
}

module act_carriage(xc) {
    difference() {
        union() {
            translate([xc - carriage_len / 2, -ch_w / 2 + 0.3, deck_z + ch_floor + 0.5]) cube([carriage_len, ch_w - 0.6, 17.5]);
            translate([xc, 4, carriage_pin_z]) rotate([90, 0, 0]) linear_extrude(8)
                polygon(convex_hull(concat(circ([0, 0], 7),
                    [for (x = [-10, 10], y = [0, 1]) [x, deck_z + ch_floor + 16 - carriage_pin_z + y]])));
        }
        translate([xc, 0, screw_z]) rotate([0, 90, 0]) cylinder(d = m8 + 0.6, h = 40, center = true);
        translate([xc - m8_nut_t / 2, -m8_nut / 2, screw_z - 7.7]) cube([m8_nut_t, m8_nut, 30]);   // nut drops in
        translate([xc, 0, carriage_pin_z]) rotate([90, 0, 0]) cylinder(d = m5, h = 30, center = true);
    }
}

// Motor clamp halves, in the motor's local frame.
module act_motor_clamp(half) {
    if (half == "roof") motor_clamp("roof", [], 0, 3);
    else motor_clamp("floor", act_clamp_holes, 0, 3, "floor");
}

module at_act_motor() { translate([gear_face_x, 0, screw_z]) orient([1, 0, 0], [0, 0, 1]) children(); }

module actuator_assembly(a, hardware = true) {
    color(c_print) {
        act_channel();
        act_bearing_block(act_rear_x, -1);
        act_bearing_block(act_front_x, 1);
        act_carriage(carriage_x(a));
        at_act_motor() { act_motor_clamp("roof"); act_motor_clamp("floor"); }
    }
    at_act_motor() johnson_motor();
    if (hardware) {
        color("Gainsboro") {
            translate([rod_x0, 0, screw_z]) rotate([0, 90, 0]) cylinder(d = 8, h = rod_x1 - rod_x0);
            translate([gear_face_x + 6, 0, screw_z]) rotate([0, 90, 0]) cylinder(d = 19, h = 25);   // 6→8 mm coupler
        }
        for (x = [act_rear_x - 6 - 1, act_front_x + 6 - b608_w])
            translate([x, 0, screw_z]) rotate([0, 90, 0]) bearing608();
        // limit switches
        color("Black") for (x = [carriage_x(arm_up) - carriage_len / 2 - 4, carriage_x(arm_press) + carriage_len / 2 + 4])
            translate([x - 10, ch_w / 2 + ch_wall, deck_z + 6]) cube([20, 6, 10]);
    }
}

echo(str("Actuator stroke ", round(carriage_x(arm_press) - carriage_x(arm_up)), " mm (arm ",
         arm_press, "° to ", arm_up, "°)"));

actuator_assembly(arm_up);
