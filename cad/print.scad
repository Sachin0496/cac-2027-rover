// Every printed part in its print orientation, sitting on the bed at z = 0.
// Pick one with `part`, e.g.
//   openscad -D 'part="drum_body"' -o drum_body.stl print.scad
// export.sh exports them all. Quantities are in the parts table below.
include <params.scad>
use <lib.scad>
use <wheel.scad>
use <frame.scad>
use <drum.scad>
use <arm.scad>
use <actuator.scad>
use <electronics.scad>

$fn = 96;
part = "drum_body";

// [id, quantity]
parts = [
    ["wheel", 4], ["drive_clamp_roof", 4], ["drive_clamp_cap", 4],
    ["drum_body", 1], ["drum_cap", 1], ["drum_drive_hub", 1],
    ["arm_drive", 1], ["arm_idler", 1], ["lever", 1], ["pushrod_link", 2], ["idler_spacer", 1],
    ["act_channel", 1], ["act_bearing_block", 2], ["act_carriage", 1],
    ["act_clamp_roof", 1], ["act_clamp_floor", 1],
    ["ebox_base", 1], ["ebox_lid", 1], ["driver_hood", 1], ["battery_tray", 1],
    ["mast_base", 1], ["mast_collar_estop", 1], ["mast_collar_pzem", 1], ["mast_collar_tof", 1],
    ["estop_box", 1], ["pzem_holder", 1], ["camera_pan_mount", 1],
    ["tof_plate_left", 1], ["tof_plate_right", 1], ["tof_wedge", 1]
];

// A clamp half lying on the face that bolts to the robot.
module clamp_on_face(half, holes, tail, wall, mount) {
    ga = jm_shaft_off;
    if (half == "roof")
        translate([0, 0, ga + jm_gear_d / 2 + 3]) rotate([-90, 0, 0]) motor_clamp("roof", holes, tail, wall, mount);
    else
        translate([0, 0, -(ga - jm_gear_d / 2 - wall)]) rotate([90, 0, 0]) motor_clamp("floor", holes, tail, wall, mount);
}

module print_part(p) {
    if (p == "wheel") wheel();
    else if (p == "drive_clamp_roof") clamp_on_face("roof", drive_clamp_holes(), drive_clamp_tail(), 5, "roof");
    else if (p == "drive_clamp_cap") clamp_on_face("cap", [], 0, 5, "roof");
    else if (p == "drum_body") drum_body();
    else if (p == "drum_cap") drum_cap();
    else if (p == "drum_drive_hub") drum_drive_hub();
    else if (p == "arm_drive") rotate([90, 0, 0]) translate([0, -arm_in_y, 0]) arm(1);
    else if (p == "arm_idler") rotate([-90, 0, 0]) translate([0, arm_in_y, 0]) arm(-1);
    else if (p == "lever") rotate([90, 0, 0]) translate([0, 4, 0]) lever();
    else if (p == "pushrod_link") rotate([-90, 0, 0]) pushrod_link();
    else if (p == "idler_spacer") idler_spacer();
    else if (p == "act_channel") translate([0, 0, -deck_z]) act_channel();
    else if (p == "act_bearing_block") translate([0, 0, -deck_z]) act_bearing_block(0, 1);
    else if (p == "act_carriage") translate([0, 0, -(deck_z + ch_floor() + 0.5)]) act_carriage(0);
    else if (p == "act_clamp_roof") clamp_on_face("roof", [], 0, 3, "roof");
    else if (p == "act_clamp_floor") clamp_on_face("cap", act_clamp_holes(), 0, 3, "floor");
    else if (p == "ebox_base") ebox_base();
    else if (p == "ebox_lid") translate([0, 0, 3]) rotate([180, 0, 0]) ebox_lid();
    else if (p == "driver_hood") driver_hood();
    else if (p == "battery_tray") battery_tray();
    else if (p == "mast_base") mast_base();
    else if (p == "mast_collar_estop") mast_collar();
    else if (p == "mast_collar_pzem") mast_collar([100, 60]);
    else if (p == "mast_collar_tof") mast_collar([30, 30]);
    else if (p == "estop_box") translate([0, 0, 50]) rotate([0, -90, 0]) estop_box();       // button face down
    else if (p == "pzem_holder") translate([0, 0, 34]) rotate([0, -90, 0]) pzem_holder();   // window face down
    else if (p == "camera_pan_mount") camera_pan_mount();
    else if (p == "tof_plate_left") translate([0, 0, rail_z1 + 8]) rotate([180, 0, 0]) tof_plate(1);
    else if (p == "tof_plate_right") translate([0, 0, rail_z1 + 8]) rotate([180, 0, 0]) tof_plate(-1);
    else if (p == "tof_wedge") tof_wedge();
    else assert(false, str("unknown part: ", p));
}

print_part(part);
