// Interference check between two part groups at arm angle `a`.
// Run check_interference.py rather than opening this directly.
include <params.scad>
use <lib.scad>
use <frame.scad>
use <arm.scad>
use <actuator.scad>
use <electronics.scad>

pair_a = "lift";
pair_b = "frame";
a = arm_up;

module group(g) {
    if (g == "frame") { rails(); deck(); drivetrain(); }
    else if (g == "lift") lift_assembly(a, hardware = false);
    else if (g == "actuator") actuator_assembly(a, hardware = false);
    else if (g == "electronics") electronics_assembly();
}

intersection() { group(pair_a); group(pair_b); }
