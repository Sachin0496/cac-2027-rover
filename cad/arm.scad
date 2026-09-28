// Lift arms, crossbar, lever, pushrods and the drum with its drive motor.
//
// Parts are modelled in the "arm frame": origin on the pivot axis, +x along
// the arm towards the drum, +z "up" in the arm, y = world y. arm_frame(a)
// places that frame at arm angle a (degrees, positive = drum up).
include <params.scad>
use <lib.scad>
use <drum.scad>

$fn = 64;

module arm_frame(a) { translate([pivot_x, 0, pivot_z]) rotate([0, -a, 0]) children(); }

module arm_profile() {
    polygon(convex_hull(concat(circ([0, 0], arm_root_r), circ([arm_len, 0], arm_end_r),
                               [for (dx = [-16, 16], dy = [-16, 16]) crossbar_at + [dx, dy]])));
}

// side = +1: left arm, clamps the drum motor; side = -1: right arm, idler.
module arm(side) {
    y_in = side * arm_in_y;
    y_out = side * arm_out_y;
    y_mid = (y_in + y_out) / 2;
    difference() {
        translate([0, max(y_in, y_out), 0]) rotate([90, 0, 0]) linear_extrude(arm_t) arm_profile();
        // pivot: M8 through, 608 bearing pressed into the outer face
        rotate([90, 0, 0]) cylinder(d = m8, h = 400, center = true);
        translate([0, side > 0 ? y_out - b608_w : y_out - 1, 0]) rotate([-90, 0, 0])
            cylinder(d = b608_d, h = b608_w + 1);
        // crossbar socket + M4 cross bolt
        translate([crossbar_at[0], y_mid, crossbar_at[1]]) cube([tube + 0.5, arm_t + 2, tube + 0.5], center = true);
        translate([crossbar_at[0], y_mid, crossbar_at[1]]) cylinder(d = m4, h = 60, center = true);
        // lightening holes
        for (p = [[62, 4, 22], [90, 0, 14]])
            translate([p[0], y_mid, p[1]]) rotate([90, 0, 0]) cylinder(d = p[2], h = arm_t + 2, center = true);
        if (side > 0) {
            // gearbox clamp: bore, slit to the end of the arm, M4 pinch bolt + nut trap
            translate([arm_len, y_mid, jm_shaft_off]) rotate([90, 0, 0])
                cylinder(d = jm_gear_d + 0.6, h = arm_t + 2, center = true);
            translate([arm_len, y_mid - arm_t, jm_shaft_off - 1]) cube([arm_end_r + 10, 2 * arm_t, 2]);
            translate([arm_len + 27, y_mid, 0]) cylinder(d = m4, h = 80, center = true);
            translate([arm_len + 27, y_mid, -arm_end_r]) cylinder(d = m4_nut / cos(30), h = arm_end_r - 18, $fn = 6);
        } else {
            translate([arm_len, y_mid, 0]) rotate([90, 0, 0]) cylinder(d = m8, h = arm_t + 2, center = true);
        }
    }
}

// One 8 mm plate (prints flat): a square collar on the crossbar and a tongue
// to the pin. The tongue leaves from the top of the collar so it clears the
// actuator's front bearing block when the drum is fully up.
module lever() {
    sq = tube + 10.5;
    difference() {
        translate([0, 4, 0]) rotate([90, 0, 0]) linear_extrude(8) {
            translate(crossbar_at) square(sq, center = true);
            polygon(convex_hull(concat(circ(crossbar_at + [0, 12], 9), circ(lever_pin_at, 8))));
        }
        translate([crossbar_at[0], 0, crossbar_at[1]]) cube([tube + 0.5, 30, tube + 0.5], center = true);
        translate([crossbar_at[0], 0, crossbar_at[1]]) cylinder(d = m4, h = 60, center = true);
        translate([lever_pin_at[0], 0, lever_pin_at[1]]) rotate([90, 0, 0]) cylinder(d = m5, h = 30, center = true);
    }
}

// Flat link, pins at x = 0 and x = pushrod_len, 6 mm thick along -y from y = 0.
module pushrod_link() {
    rotate([90, 0, 0]) linear_extrude(6) difference() {
        polygon(convex_hull(concat(circ([0, 0], 7), circ([pushrod_len, 0], 7))));
        circle(d = m5);
        translate([pushrod_len, 0]) circle(d = m5);
    }
}

// Printed spacer between the idler arm and the drum cap's bearing.
module idler_spacer() {
    difference() { cylinder(d = 14, h = hub_gap - 11); translate([0, 0, -1]) cylinder(d = m8, h = 20); }
}

module crossbar() {
    translate([crossbar_at[0], -arm_out_y, crossbar_at[1]]) rotate([0, 0, 90]) tube_x(2 * arm_out_y);
}

module lift_assembly(a, hardware = true) {
    arm_frame(a) {
        color(c_print) { arm(1); arm(-1); lever(); }
        crossbar();
        // drum (spins about its own axis, which is along y at x = arm_len)
        translate([arm_len, drum_len / 2, 0]) orient([0, -1, 0], [0, 0, 1]) drum_assembly();
        translate([arm_len, drum_len / 2 + hub_gap + 0.5, 0]) orient([0, -1, 0], [0, 0, 1]) johnson_motor();
        color(c_print) translate([arm_len, -drum_len / 2 - 11, 0]) rotate([90, 0, 0]) idler_spacer();
        if (hardware) {   // pivot and idler M8 bolts, pivot bearings
            color("Gainsboro") {
                for (s = [-1, 1]) translate([0, s * (frame_w / 2 + 8), 0]) rotate([s * 90, 0, 0]) cylinder(d = 8, h = frame_w / 2 + 8 - arm_in_y + 6);
                translate([arm_len, -arm_out_y - 8, 0]) rotate([-90, 0, 0]) cylinder(d = 8, h = arm_out_y + 8 - drum_len / 2 - 4);
            }
            for (s = [-1, 1]) translate([0, s > 0 ? arm_out_y - 7 : -arm_out_y, 0]) rotate([-90, 0, 0]) bearing608();
        }
    }
    pushrods(a);
}

module pushrods(a) {
    p2 = arm_pt(a, lever_pin_at);
    p1 = [carriage_x(a), carriage_pin_z];
    ang = atan2(p2[1] - p1[1], p2[0] - p1[0]);
    color(c_print) for (y0 = [10, -4]) translate([p1[0], y0, p1[1]]) rotate([0, -ang, 0]) pushrod_link();
}

lift_assembly(arm_up);
