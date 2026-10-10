// Preview only: jig on a stand-in Dremel nose with a 1/2 in drum, on beveled 10 mm foam.
include <dremel-bevel-jig.scad>
build = false;
foam = 10;
inset = 6;    // green bevel line, in from the edge
module dremel() color("dimgray") {
    on_axis(t_shoulder - 90) cylinder(d = 42, h = 70);
    on_axis(t_shoulder - 20) cylinder(d1 = 42, d2 = 26, h = 20);
    on_axis(t_shoulder) cylinder(d = thread_d - 1, h = 10);
    on_axis(t_shoulder + 10) cylinder(d = 11, h = 8);           // collet nut
    on_axis(t_shoulder + 18) cylinder(d = 3.2, h = 30);         // mandrel
}
module drum() color("saddlebrown") on_axis(t_top) cylinder(d = drum_d, h = 12.7);
module blade() color("lightgreen") translate([-60, 0, 0]) rotate([90, 0, 90]) linear_extrude(120)
    polygon([[-45, 0], [0, 0], [inset, -inset * tan(bevel_angle)], [inset, -foam], [-45, -foam]]);
module scene() { color("orange") jig(); dremel(); drum(); blade(); }
scene();
