// Parametric grouser wheel for the CAC 2027 rover (units: mm).
//
// Print with the outer face (z = 0) on the bed: PETG, 3–4 walls,
// 20–25% gyroid infill, no supports.
//
// Render:   openscad --backend=manifold -o wheel.stl wheel.scad
// Variant:  openscad -D grouser_count=16 -D grouser_h=15 -o wheel_g16.stl wheel.scad
//
// The motor's 6 mm D-shaft goes into the hub from the open (inner) side.
// With use_bearing = true, a 608 bearing sits in the outer face and rides on
// an M8 stub axle held by an outer bracket, so the gearbox shaft doesn't
// carry the robot's weight.

/* [Rim] */
rim_d = 150;        // rim outer diameter; grousers add 2 × grouser_h
width = 60;
rim_t = 3;          // rim wall thickness
web_t = 4;          // outer face thickness

/* [Grousers] */
grouser_count = 14;
grouser_h = 12;     // height above the rim
grouser_t = 4;      // keep ≥ 3 so the tips aren't sharp

/* [Hub: Johnson geared motor, 6 mm D-shaft] */
hub_d = 32;
hub_len = 25;       // from the outer face towards the motor
shaft_d = 6.0;
shaft_flat = 5.5;   // across-flats of the D-shaft; measure yours
shaft_depth = 15;
clearance = 0.2;    // fit allowance; tune with a test print
grub_d = 3.2;       // M3 grub screw onto the shaft flat
nut_w = 5.7;        // M3 nut across flats + clearance
nut_t = 2.6;

/* [Outboard 608 bearing] */
use_bearing = true;
bearing_d = 22.2;
bearing_w = 7.2;

/* [Lightening holes in the outer face] */
hole_count = 6;

$fn = 96;

assert(!use_bearing || hub_len - shaft_depth >= bearing_w + 2,
       "Shaft bore and bearing pocket overlap: increase hub_len or reduce shaft_depth");

rim_inner_r = rim_d / 2 - rim_t;
hole_ring_r = (hub_d / 2 + rim_inner_r) / 2;
hole_d = min(0.6 * (rim_inner_r - hub_d / 2),
             0.65 * 2 * PI * hole_ring_r / hole_count);
grub_z = hub_len - shaft_depth / 2;
flat_y = (shaft_flat + clearance) - (shaft_d + clearance) / 2;  // y of the bore's flat
nut_y = (flat_y + hub_d / 2) / 2;                               // halfway to the hub surface

echo(str("Overall diameter: ", rim_d + 2 * grouser_h, " mm, width: ", width, " mm"));

// D-shaped profile: the flat faces +y.
module d_profile(d, flat) {
    intersection() {
        circle(d = d);
        translate([-d, -d]) square([2 * d, flat + d / 2]);
    }
}

module wheel() {
    difference() {
        union() {
            // rim
            difference() {
                cylinder(d = rim_d, h = width);
                translate([0, 0, -1]) cylinder(r = rim_inner_r, h = width + 2);
            }
            // outer face
            cylinder(r = rim_inner_r + 0.5, h = web_t);
            // hub
            cylinder(d = hub_d, h = hub_len);
            // grousers
            for (i = [0 : grouser_count - 1])
                rotate(i * 360 / grouser_count)
                    translate([rim_d / 2 - 1, -grouser_t / 2, 0])
                        cube([grouser_h + 1, grouser_t, width]);
        }

        // lightening holes
        for (i = [0 : hole_count - 1])
            rotate(i * 360 / hole_count + 180 / hole_count)
                translate([hole_ring_r, 0, -1]) cylinder(d = hole_d, h = web_t + 2);

        // D-shaft bore
        translate([0, 0, hub_len - shaft_depth])
            linear_extrude(shaft_depth + 1)
                d_profile(shaft_d + clearance, shaft_flat + clearance);

        // grub screw hole and M3 nut slot (drop the nut in from the top)
        translate([0, 0, grub_z]) rotate([-90, 0, 0]) cylinder(d = grub_d, h = hub_d);
        translate([-nut_w / 2, nut_y - nut_t / 2, grub_z - nut_w / 2])
            cube([nut_w, nut_t, hub_len]);

        // 608 bearing pocket in the outer face
        if (use_bearing)
            translate([0, 0, -1]) cylinder(d = bearing_d, h = bearing_w + 1);
    }
}

wheel();
