// Electronics and sensor mounts (world coordinates).
//   Right side of the deck: sealed box with the Pi 5, ESP32, 5 V buck, relay.
//   Left side: hood over the four BTS7960 motor drivers.
//   Rear: battery tray; mast with E-stop, PZEM-051 energy meter (high and
//   visible, as the rules require) and the camera on a pan servo.
//   Front: two VL53L1X ToF sensors looking down the wheel tracks; one on the
//   mast looking backwards for reversing.
include <params.scad>
use <lib.scad>

$fn = 48;

box = [130, 110, 45];
lid_t = 3;
ebox_at = [-120, -frame_w / 2 + 5, deck_z];
hood = [130, 110, 58];
hood_at = [-120, frame_w / 2 - 5 - hood[1], deck_z];
batt = [65, 57, 38];                       // 3S2P 18650 pack, lying down
tray_at = [-205, -98, deck_z];
rear_tof_z = deck_z + 95;
estop_z = deck_z + 160;
pzem_z = deck_z + 290;
tof_sensor_at = [262, 192, 118];           // front ToF face centre, |y| mirrored
tof_tilt = 35;                             // looks 35° down, ~17 cm ahead of the wheel

// ---------- printed parts ----------
module ebox_base() {
    difference() {
        open_box(box);
        translate([box[0] / 2 - 15, box[1] - 4, box[2] - 14]) cube([30, 6, 15]);   // cable slot, inner side
        for (x = [12, box[0] - 12], y = [12, box[1] - 12]) translate([x, y, -1]) cylinder(d = m4, h = 5);
    }
}

module ebox_lid() {
    rounded_block([box[0], box[1], lid_t], 3);
    translate([2.6, 2.6, -4]) difference() {
        rounded_block([box[0] - 5.2, box[1] - 5.2, 4], 1);
        translate([2, 2, -1]) rounded_block([box[0] - 9.2, box[1] - 9.2, 6], 1);
    }
}

// Printed like a box (closed side on the bed), then flipped over the drivers:
// vents end up low on the outer side, the cable slot low on the inner side.
module driver_hood() {
    difference() {
        open_box(hood);
        for (x = [20 : 18 : hood[0] - 20]) translate([x, -1, hood[2] - 18]) cube([8, 5, 12]);
        translate([hood[0] / 2 - 15, hood[1] - 4, hood[2] - 12]) cube([30, 6, 13]);
    }
}

module battery_tray() {
    difference() {
        open_box([batt[0] + 6, batt[1] + 6, 22]);
        for (x = [15, batt[0] - 9]) translate([x, -1, 10]) cube([10, batt[1] + 8, 4]);   // strap slots
        for (x = [10, batt[0] - 4], y = [10, batt[1] - 4]) translate([x, y, -1]) cylinder(d = m4, h = 5);
    }
}

module mast_base() {
    difference() {
        union() {
            translate([-22, -22, 0]) cube([44, 44, 5]);
            translate([-15, -15, 0]) cube([30, 30, 35]);
        }
        translate([-(tube + 0.5) / 2, -(tube + 0.5) / 2, 5]) cube([tube + 0.5, tube + 0.5, 40]);
        for (y = [-17, 17]) translate([0, y, -1]) cylinder(d = m4, h = 7);
        translate([0, 0, 22]) rotate([0, 90, 0]) cylinder(d = m4, h = 40, center = true);
    }
}

// Square collar that clamps onto the mast, with a plate on the -x side.
module mast_collar(plate = [50, 50]) {
    difference() {
        union() {
            translate([-(tube + 8) / 2, -(tube + 8) / 2, 0]) cube([tube + 8, tube + 8, 20]);
            translate([-(tube + 8) / 2 - 4, -plate[0] / 2, 0]) cube([4, plate[0], plate[1]]);
        }
        translate([-(tube + 0.5) / 2, -(tube + 0.5) / 2, -1]) cube([tube + 0.5, tube + 0.5, 22]);
        translate([0, 0, 10]) rotate([90, 0, 0]) cylinder(d = m4, h = 40, center = true);
    }
}

module estop_box() {   // bolts to its collar plate; 22 mm E-stop on the -x face
    difference() {
        translate([-50, -23, 0]) open_box([46, 46, 50]);
        translate([-51, 0, 25]) rotate([0, 90, 0]) cylinder(d = 22.5, h = 5);
    }
}

module pzem_holder() {   // frame around the 90 × 50 × 25 meter, display facing -x
    difference() {
        translate([-34, -50, 0]) cube([32, 100, 60]);
        translate([-31, -45.2, 5]) cube([26, 90.4, 60]);
        translate([-35, -40, 10]) cube([6, 80, 40]);   // display window
    }
}

module camera_pan_mount() {   // cap on the mast top holding an SG90 servo
    difference() {
        translate([-16, -16, 0]) cube([32, 32, 38]);
        translate([-(tube + 0.5) / 2, -(tube + 0.5) / 2, -1]) cube([tube + 0.5, tube + 0.5, 16]);
        translate([-6.2, -11.8, 20]) cube([12.4, 23.6, 20]);   // SG90 body pocket
    }
}

// Front ToF mount, left side (s = +1) or right (-1): an 8 mm L-plate bolted on
// top of the rail end, reaching out ahead of the front wheel, with the sensor
// on a face underneath tilted 35° down. Print it upside down (no supports).
module tof_plate(s) {
    // starts just past the deck; both bolts sit behind the arm pivot bolt (x = pivot_x)
    pts = [[179, 131], [240, 131], [240, 178], [262, 178], [262, 206], [226, 206], [226, 149], [179, 149]];
    mirror([0, s > 0 ? 0 : 1, 0]) difference() {
        union() {
            translate([0, 0, rail_z1]) linear_extrude(8) polygon(pts);
            // wedge from the plate down to the tilted sensor face, as an XZ profile
            slab = [for (x = [-4, 0], z = [-9, 9])
                [tof_sensor_at[0] + x * cos(tof_tilt) + z * sin(tof_tilt),
                 tof_sensor_at[2] - x * sin(tof_tilt) + z * cos(tof_tilt)]];
            translate([0, tof_sensor_at[1] + 12, 0]) rotate([90, 0, 0]) linear_extrude(24)
                polygon(convex_hull(concat(slab, [[244, rail_z1 + 1], [262, rail_z1 + 1]])));
        }
        for (x = [184, 191]) translate([x, rail_y, rail_z0 - 5]) cylinder(d = m4, h = 40);   // through the rail
        translate(tof_sensor_at) for (dy = [-7, 7])
            rotate([0, -90 + tof_tilt, 0]) translate([0, dy, -1]) cylinder(d = 2.2, h = 9);   // M2 sensor screws
    }
}

// 40° wedge for the rear ToF sensor; glue/screw it to the mast collar plate.
module tof_wedge() {
    difference() {
        rotate([90, 0, 0]) linear_extrude(20, center = true) polygon([[0, 0], [25, 0], [0, 25 * tan(40)]]);
        translate([6, 0, -1]) cylinder(d = m3, h = 30);
    }
}

// ---------- placement ----------
module electronics_assembly() {
    color(c_print) {
        translate(ebox_at) ebox_base();
        translate(ebox_at + [0, 0, box[2]]) ebox_lid();
        translate(hood_at + [0, hood[1], hood[2]]) rotate([180, 0, 0]) driver_hood();
        translate(tray_at) battery_tray();
        translate([mast_x, 0, deck_z]) mast_base();
        translate([mast_x, 0, estop_z]) { mast_collar(); estop_box(); }
        translate([mast_x, 0, pzem_z]) { mast_collar([100, 60]); pzem_holder(); }
        translate([mast_x, 0, deck_z + mast_h - 15]) camera_pan_mount();
        for (s = [-1, 1]) tof_plate(s);
        translate([mast_x, 0, rear_tof_z]) mast_collar([30, 30]);
        translate([mast_x - (tube + 8) / 2 - 4, 0, rear_tof_z + 25]) mirror([0, 0, 1]) rotate([0, 0, 180]) tof_wedge();
    }
    translate([mast_x, 0, deck_z]) rotate([0, -90, 0]) tube_x(mast_h);
    // components (placeholders)
    color(c_pcb) {
        translate(ebox_at + [8, 8, 3]) cube([85, 56, 18]);                // Raspberry Pi 5
        translate(ebox_at + [8, 72, 3]) cube([52, 28, 12]);               // ESP32
        translate(ebox_at + [98, 8, 3]) cube([23, 48, 15]);               // 5 V buck
        translate(ebox_at + [68, 70, 3]) cube([50, 26, 18]);              // relay
        for (i = [0 : 1], j = [0 : 1]) translate(hood_at + [8 + i * 62, 4 + j * 52, 1]) cube([50, 50, 42]);   // BTS7960 ×4
    }
    color("Gold") translate(tray_at + [3, 3, 3]) cube(batt);
    color("Red") translate([mast_x - 54 - 25, 0, estop_z + 25]) rotate([0, 90, 0]) cylinder(d = 40, h = 25);
    color("Black") translate([mast_x - 34, -45, pzem_z + 5]) cube([26, 90, 50]);
    color("DimGray") {
        translate([mast_x - 6, -11.5, deck_z + mast_h + 5]) cube([12, 23, 29]);        // SG90
        translate([mast_x - 12, -30, deck_z + mast_h + 34]) cube([25, 60, 25]);       // USB camera, facing +x
    }
    color("Purple") {
        for (s = [-1, 1]) translate([tof_sensor_at[0], s * tof_sensor_at[1], tof_sensor_at[2]])
            rotate([0, tof_tilt, 0]) translate([0, -6.5, -12.5]) cube([2, 13, 25]);
        translate([mast_x - (tube + 8) / 2 - 4 - 12.5, -6.5, rear_tof_z + 12]) rotate([0, -50, 0]) cube([2, 13, 25]);   // rear ToF
    }
}

electronics_assembly();
