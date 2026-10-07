// End brackets that turn a 1x2 furring strip into a 35-degree bevel sanding block.
//
// End view (looking along the strip):
//
//            ______
//           /     /|   <- back flange, screwed to the back of the strip
//          / wood/ |
//    _____/_____/  |   <- the strip; sandpaper glued on its front face
//   |  foot   V \
//   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾\    <- sanding face, 35 deg below the foot plane
//
// The foot rides flat on the foam's face; the sandpaper meets it at V with a
// 145-degree open angle, so the sanded surface ends up 35 degrees off the face.
// Units: mm. Print one "left" and one "right" (mirror images), end cap down.

/* [Wood strip] */
wood_width = 38.1;      // the face that carries sandpaper (1.5 in)
wood_thickness = 19.05; // (0.75 in)
wood_clearance = 0.6;   // total, added to both pocket dimensions
paper_thickness = 0.6;  // sandpaper (plus glue) on the front face

/* [Geometry] */
bevel_angle = 35;       // between the foam face and the sanded bevel
foot_length = 25;       // contact on the foam face, measured from V
foot_thickness = 4;
wall = 4;               // inner-edge wall and back flange
bracket_length = 25;    // along the strip, from the wood's end
end_cap = 3;            // plate over the wood's end grain; 0 for none
nose_radius = 2;        // round on the foot's trailing edge

/* [Screws] */
screw_d = 3.6;          // clearance for #6 wood screws
head_d = 7.6;           // 82-degree countersink diameter at the surface

side = "left";          // [left, right]
build = true;           // preview.scad turns this off to place its own copies

$fn = 48;

d = [cos(bevel_angle), -sin(bevel_angle)];  // down the sanding face, away from the foot
n = [sin(bevel_angle), cos(bevel_angle)];   // out of the sanding face, into the block
ww = wood_width + wood_clearance;
wt = wood_thickness + wood_clearance;
o = paper_thickness * n;                    // front-inner corner of the wood pocket

function at(u, v) = o + u * d + v * n;      // strip-local coordinates -> profile

// Wood pocket; front face (v < 0) left open past the sanding plane.
module pocket() polygon([at(0, -5), at(ww + 5, -5), at(ww + 5, wt), at(0, wt)]);

module profile() {
    difference() {
        union() {
            // Foot plus the gusset up to the top of the inner-edge wall.
            hull() {
                translate([-foot_length + nose_radius, nose_radius]) circle(nose_radius);
                translate([-foot_length + nose_radius, 0]) square([foot_length - nose_radius, foot_thickness]);
                polygon([[0, 0], at(0, 0), at(0, wt + wall), at(-wall, wt + wall), at(-wall, 0)]);
            }
            // Back flange across the full width of the strip.
            polygon([at(-wall, wt), at(ww, wt), at(ww, wt + wall), at(-wall, wt + wall)]);
        }
        pocket();
    }
}

// Same outline, closed over the pocket: the end cap.
module cap_profile() {
    union() {
        profile();
        polygon([at(0, 0), at(ww, 0), at(ww, wt), at(0, wt)]);
    }
}

module screw_hole(u) {
    // Placed on the flange's outer face, drilled along -n into the wood.
    p = at(u, wt + wall);
    a = atan2(n[1], n[0]);
    translate([p[0], p[1], end_cap + bracket_length / 2])
        rotate([0, 0, a]) rotate([0, -90, 0]) {
            translate([0, 0, -1]) cylinder(d = screw_d, h = wall + 2);
            translate([0, 0, -0.01]) cylinder(d1 = head_d, d2 = 0, h = head_d / 2 / tan(41));
            translate([0, 0, -5]) cylinder(d = head_d, h = 5);
        }
}

module bracket() {
    difference() {
        union() {
            if (end_cap > 0) linear_extrude(end_cap) cap_profile();
            translate([0, 0, end_cap - 0.01]) linear_extrude(bracket_length + 0.01) profile();
        }
        for (u = [ww / 4, 3 * ww / 4]) screw_hole(u);
    }
}

// Printed with the end cap on the bed (Z = 0); Z runs along the strip.
if (build) {
    if (side == "right") mirror([1, 0, 0]) bracket();
    else bracket();
}
