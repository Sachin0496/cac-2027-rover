// Chassis: 20 × 20 aluminium tube rectangle, 6 mm plywood deck, four drive
// motors in printed clamps, four grouser wheels.
//
// The clamps hang under the rail/cross-member corners, so each one also ties
// a rail to its cross member (the deck ties the tops).
include <params.scad>
use <lib.scad>
use <wheel.scad>

$fn = 64;

// Clamp tail reaches in under the cross member.
drive_clamp_tail = gear_face_y - jm_gear_len - jm_can_len - (frame_w / 2 - tube - tube);
// M4 inserts: two through the rail, one through the cross member.
drive_clamp_holes = [[-15, rail_y - gear_face_y], [15, rail_y - gear_face_y],
                     [0, frame_w / 2 - tube - tube / 2 - gear_face_y]];

function drive_clamp_tail() = drive_clamp_tail;     // for print.scad
function drive_clamp_holes() = drive_clamp_holes;

module drive_clamp(half) {
    color(c_print) motor_clamp(half, drive_clamp_holes, drive_clamp_tail);
}

// Place children in the frame of the drive motor at axle x = xa on side s
// (s = +1 left, -1 right): shaft on the axle, pointing outwards.
module at_drive_motor(xa, s) {
    translate([xa, s * gear_face_y, axle_z]) orient([0, s, 0], [0, 0, 1]) children();
}

module rails() {
    for (s = [-1, 1]) translate([-rail_len / 2, s * rail_y, rail_z0 + tube / 2]) tube_x(rail_len);
    for (xa = [-axle_x, axle_x])
        translate([xa, -(frame_w / 2 - tube), rail_z0 + tube / 2]) rotate([0, 0, 90])
            tube_x(frame_w - 2 * tube);
}

module deck() {
    color(c_wood) translate([deck_x0, -frame_w / 2, rail_z1])
        cube([deck_x1 - deck_x0, frame_w, deck_t]);
}

module drivetrain(motors = true, clamps = true, wheels = true) {
    for (xa = [-axle_x, axle_x], s = [-1, 1]) {
        if (motors) at_drive_motor(xa, s) johnson_motor();
        if (clamps) at_drive_motor(xa, s) { drive_clamp("roof"); drive_clamp("cap"); }
        if (wheels) translate([xa, s * wheel_out_y, axle_z]) orient([0, -s, 0], [0, 0, 1])
            color(c_print2) wheel();
    }
}

module frame_assembly() {
    rails();
    deck();
    drivetrain();
}

frame_assembly();
