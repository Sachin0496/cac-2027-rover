// Bucket drum excavator (RASSOR-style), drum-local frame: axis = z,
// drive end plate at z = 0..plate_t, idler cap at z = drum_len.
//
// Digging: spin in +angle (CCW about +z). Each tooth bites, sand drops into
// the mouth behind it and a spiral baffle carries it inward to the core.
// Dumping: spin the other way and the spirals carry it back out.
// Two rings of 4 scoops, the second ring clocked 45°, so one tooth cuts at a time.
//
// Print drum_body standing on its end plate (no supports), drum_cap and
// drum_drive_hub flat.
include <params.scad>
use <lib.scad>

$fn = 96;

shell_t = 2.4;
plate_t = 4;
r_in = drum_r - shell_t;
scoops = 4;          // per ring
ring_clock = [0, 45];
scoop_w = 30;        // opening angle behind each tooth
scoop_h = 22;        // how far the mouth dives inwards
sweep = 150;         // spiral length, degrees
r_core = 26;         // spiral ends here and releases sand into the core
baffle_t = 2;
tooth_t = 4;         // thicker where it cuts
body_len = drum_len - plate_t;          // body without the cap
ring_z = [plate_t, body_len / 2 + plate_t / 2, body_len];
hub_bolt_r = 18;
hub_bolt_a = [90, 210, 330];
lug_a = [for (k = [0 : scoops - 1]) ring_clock[1] + 30 + k * 360 / scoops];

function pol(p) = [p[0] * cos(p[1]), p[0] * sin(p[1])];

// Baffle centreline [r, angle] for a tooth at angle 0: dives in behind the
// mouth, then spirals to the core.
function baffle_path() = concat(
    [for (i = [0 : 6]) let (t = i / 6) [r_in - scoop_h * sin(90 * t), -scoop_w * t]],
    [for (i = [1 : 24]) let (t = i / 24)
        [r_in - scoop_h - (r_in - scoop_h - r_core) * t, -scoop_w - sweep * t]]);

module baffle() {
    polygon(polyline_band([for (q = baffle_path()) pol(q)], [for (q = baffle_path()) baffle_t]));
    // tooth: raked slightly forward, overlapping the shell and the baffle root
    polygon(polyline_band([pol([drum_tip_r, 4]), pol([r_in - 3, -1])], [tooth_t, tooth_t]));
}

module ring_profile(clock) {
    difference() {
        circle(r = drum_r);
        circle(r = r_in);
        for (k = [0 : scoops - 1]) rotate(clock + k * 360 / scoops)
            polygon([[0, 0], pol([drum_r + 5, -scoop_w]), pol([drum_r + 5, -scoop_w / 2]),
                     pol([drum_r + 5, 0])]);
    }
    for (k = [0 : scoops - 1]) rotate(clock + k * 360 / scoops) baffle();
}

// Cap mounting lug, chamfered underneath so it prints without support.
module lug(a, z_top) {
    ro = drum_r + 8;
    rotate(a) difference() {
        translate([0, 7, 0]) rotate([90, 0, 0]) linear_extrude(14)
            polygon([[r_in, z_top - 22], [r_in + 1, z_top - 22], [ro, z_top - 12], [ro, z_top], [r_in, z_top]]);
        translate([drum_r + 4, 0, z_top - 8]) cylinder(d = 5.6, h = 9, $fn = 24);
    }
}

module drum_body() {
    difference() {
        union() {
            cylinder(r = drum_r, h = plate_t);
            for (i = [0 : 1]) translate([0, 0, ring_z[i]])
                linear_extrude(ring_z[i + 1] - ring_z[i]) ring_profile(ring_clock[i]);
            for (a = hub_bolt_a) translate(pol([hub_bolt_r, a])) cylinder(d = 11, h = plate_t + 8);
            for (a = lug_a) lug(a, body_len);
        }
        translate([0, 0, -1]) cylinder(d = 9, h = plate_t + 2);
        for (a = hub_bolt_a) translate([each pol([hub_bolt_r, a]), -1]) cylinder(d = 5.6, h = 9);
    }
}

module drum_cap() {
    difference() {
        union() {
            cylinder(r = drum_r, h = plate_t);
            for (a = lug_a) rotate(a) translate([r_in, -7, 0]) cube([drum_r + 8 - r_in, 14, plate_t]);
            cylinder(d = 36, h = plate_t + hub_gap - 5);   // idler boss
        }
        translate([0, 0, -1]) cylinder(d = 9, h = 40);
        translate([0, 0, plate_t + hub_gap - 5 - b608_w]) cylinder(d = b608_d, h = b608_w + 1);
        for (a = lug_a) rotate(a) translate([drum_r + 4, 0, -1]) cylinder(d = m4, h = plate_t + 2);
    }
}

module drum_drive_hub() {
    difference() {
        union() {
            cylinder(d = 50, h = 5);
            cylinder(d = 24, h = hub_gap - 1);
        }
        translate([0, 0, -1]) linear_extrude(hub_gap + 1)
            d_profile(jm_shaft_d + 0.2, jm_shaft_flat + 0.2);
        for (a = hub_bolt_a) translate([each pol([hub_bolt_r, a]), -1]) {
            cylinder(d = m4, h = 7);
            translate([0, 0, 5]) cylinder(d = 8.5, h = 10);   // head clearance
        }
        // M3 grub screw onto the shaft flat, nut dropped in from the top
        translate([0, 0, 10]) rotate([-90, 0, 0]) cylinder(d = m3, h = 20);
        translate([-3, 6, 10 - 3]) cube([6, 2.6, 20]);
    }
}

// Whole drum in drum-local coordinates.
module drum_assembly() {
    color(c_print2) drum_body();
    color(c_print2) translate([0, 0, body_len]) drum_cap();
    color(c_print) mirror([0, 0, 1]) drum_drive_hub();
}

core_area = PI * r_in * r_in;
echo(str("Drum: ", drum_len, " mm long, ", 2 * drum_tip_r, " mm over the teeth; gross volume ~",
         round(core_area * (body_len - plate_t) / 1e5) / 10, " L (usable ~40%)"));

drum_assembly();
