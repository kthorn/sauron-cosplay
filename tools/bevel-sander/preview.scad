// Preview only: two brackets on a 300 mm strip, finishing a bevel on 10 mm foam.
include <bevel-sander.scad>
build = false;
strip = 300;
view = "3d";  // [3d, end]
foam = 10;
module wood() color("burlywood") translate([0, 0, end_cap]) linear_extrude(strip)
    polygon([at(0, 0), at(wood_width, 0), at(wood_width, wood_thickness), at(0, wood_thickness)]);
module paper() color("dimgray") translate([0, 0, end_cap]) linear_extrude(strip)
    polygon([[0, 0], d * wood_width, o + d * wood_width, o]);
module blade() color("lightgreen") translate([0, 0, -30]) linear_extrude(strip + 60)
    polygon([[-45, 0], [0, 0], [6, -6 * tan(bevel_angle)], [6, -foam], [-45, -foam]]);
module scene() {
    color("orange") bracket();
    color("orange") translate([0, 0, strip + 2 * end_cap]) mirror([0, 0, 1]) bracket();
    wood(); paper(); blade();
}
if (view == "end") scene(); else rotate([90, 0, 0]) scene();
