// Shared helpers for the rover model. `use <lib.scad>`.
include <params.scad>

// Rotate children so local +z points along `z` and local +y along `y`
// (both unit vectors, perpendicular).
module orient(z, y) {
    x = cross(y, z);
    multmatrix([[x[0], y[0], z[0], 0],
                [x[1], y[1], z[1], 0],
                [x[2], y[2], z[2], 0],
                [0, 0, 0, 1]]) children();
}

// 20 × 20 × 1.5 aluminium square tube along +x from x = 0, centred on y and z.
module tube_x(len) {
    color(c_alu) rotate([0, 90, 0]) linear_extrude(len)
        difference() { square(tube, center = true); square(tube - 3, center = true); }
}

// D-shaped shaft profile, flat facing +y.
module d_profile(d, flat) {
    intersection() {
        circle(d = d);
        translate([-d, -d]) square([2 * d, flat + d / 2]);
    }
}

// Johnson side-shaft geared motor. The output shaft lies on the local z axis
// (tip towards +z); the gearbox face is at z = 0 and the gearbox axis sits
// jm_shaft_off along local +y.
module johnson_motor() {
    color(c_motor) {
        translate([0, jm_shaft_off, -jm_gear_len]) cylinder(d = jm_gear_d, h = jm_gear_len);
        translate([0, jm_shaft_off, -jm_gear_len - jm_can_len]) cylinder(d = jm_can_d, h = jm_can_len);
    }
    color("Gainsboro") {
        cylinder(d = 10, h = 2);
        linear_extrude(jm_shaft_len) d_profile(jm_shaft_d, jm_shaft_flat);
    }
}

// Split clamp for a Johnson motor, in the motor's local frame (see above).
// The split plane passes through the gearbox axis: "roof" is the half on the
// +y side (top face at roof_y), "floor" the other half (bottom face at
// floor_y). mount_holes: [[x, z], ...] M4 heat-set insert holes going into
// the face named by `mount` ("roof" or "floor"). `tail` extends the roof as a
// plate past the motor's rear end for an extra mounting bolt.
module motor_clamp(half = "roof", mount_holes = [], tail = 0, wall = 5, mount = "roof") {
    w = jm_gear_d / 2 + 8.5;                 // half width (room for the pinch bolts)
    ga = jm_shaft_off;                        // gearbox axis y
    roof_y = ga + jm_gear_d / 2 + 3;
    floor_y = ga - jm_gear_d / 2 - wall;
    body_z0 = -jm_gear_len - jm_can_len;
    pinch = [[-w + 3.5, -13], [w - 3.5, -13], [-w + 3.5, -48], [w - 3.5, -48]];   // gearbox, can
    difference() {
        union() {
            if (half == "roof") {
                translate([-w, ga, body_z0]) cube([2 * w, roof_y - ga, -body_z0 - 2]);
                if (tail > 0)
                    translate([-w, roof_y - 9, body_z0 - tail]) cube([2 * w, 9, tail + 1]);
            } else {
                translate([-w, floor_y, body_z0]) cube([2 * w, ga - floor_y, -body_z0 - 2]);
            }
        }
        // stepped bore: gearbox, then motor can
        translate([0, ga, -jm_gear_len - 1]) cylinder(d = jm_gear_d + 0.4, h = jm_gear_len + 2);
        translate([0, ga, body_z0 - 1]) cylinder(d = jm_can_d + 0.6, h = jm_can_len + 1.5);
        // M3 pinch bolts (nut traps in the lower half)
        for (p = pinch) translate([p[0], 0, p[1]]) rotate([-90, 0, 0]) {
            translate([0, 0, floor_y - 1]) cylinder(d = m3, h = roof_y - floor_y + 2);
            translate([0, 0, floor_y - 1]) cylinder(d = 6.4, h = 3.5, $fn = 6);
        }
        // M4 heat-set inserts from the mounting face
        for (h = mount_holes)
            if (mount == "roof") translate([h[0], roof_y + 0.01, h[1]]) rotate([90, 0, 0]) cylinder(d = 5.6, h = 8);
            else translate([h[0], floor_y - 0.01, h[1]]) rotate([-90, 0, 0]) cylinder(d = 5.6, h = 7);
    }
}

// 608 bearing (22 × 8 × 7) with its axis on local z.
module bearing608() {
    color("LightSteelBlue") difference() {
        cylinder(d = 22, h = 7);
        translate([0, 0, -1]) cylinder(d = 8, h = 9);
    }
}

// Plain box with a lid lip, for electronics. Open top at z = h.
module open_box(size, wall = 2.4, floor = 2.4, r = 3) {
    difference() {
        rounded_block(size, r);
        translate([wall, wall, floor]) rounded_block([size[0] - 2 * wall, size[1] - 2 * wall, size[2]], max(r - wall, 0.5));
    }
}

module rounded_block(size, r) {
    linear_extrude(size[2]) polygon(convex_hull([for (x = [r, size[0] - r], y = [r, size[1] - r]) each circ([x, y], r, 16)]));
}

// ---------- 2D point helpers ----------
// Shapes are built as explicit polygons rather than hull() so the model also
// imports cleanly into FreeCAD (its OpenSCAD importer can't do 2D hulls).

function circ(c, r, n = 48) = [for (i = [0 : n - 1]) c + r * [cos(360 * i / n), sin(360 * i / n)]];

function _cross(o, a, b) = (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
function _less(a, b) = a[0] < b[0] || (a[0] == b[0] && a[1] < b[1]);
function _sort(v) = len(v) <= 1 ? v : let (p = v[floor(len(v) / 2)])
    concat(_sort([for (x = v) if (_less(x, p)) x]), [p], _sort([for (x = v) if (_less(p, x)) x]));
function _pop(h, p) = len(h) >= 2 && _cross(h[len(h) - 2], h[len(h) - 1], p) <= 0
    ? _pop([for (j = [0 : len(h) - 2]) h[j]], p) : h;
function _chain(pts, i = 0, h = []) = i >= len(pts) ? h : _chain(pts, i + 1, concat(_pop(h, pts[i]), [pts[i]]));

// Convex hull of 2D points (Andrew's monotone chain), counter-clockwise.
function convex_hull(points) = let (
        s = _sort(points),
        lower = _chain(s),
        upper = _chain([for (i = [len(s) - 1 : -1 : 0]) s[i]]))
    concat([for (i = [0 : len(lower) - 2]) lower[i]], [for (i = [0 : len(upper) - 2]) upper[i]]);

// Outline of a thick polyline: path = [[x, y], ...], widths = one per point.
function _unit(v) = v / norm(v);
function _normal(p, i) = let (
        d = i == 0 ? p[1] - p[0] : i == len(p) - 1 ? p[i] - p[i - 1] : _unit(p[i + 1] - p[i]) + _unit(p[i] - p[i - 1]))
    _unit([-d[1], d[0]]);
function polyline_band(path, widths) = concat(
    [for (i = [0 : len(path) - 1]) path[i] + widths[i] / 2 * _normal(path, i)],
    [for (i = [len(path) - 1 : -1 : 0]) path[i] - widths[i] / 2 * _normal(path, i)]);
