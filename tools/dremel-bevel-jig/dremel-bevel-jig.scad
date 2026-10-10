// Dremel jig for sanding a 35-degree bevel with a 1/2 in sanding drum.
//
// Side view (looking along the foam edge):
//
//                 ___
//      Dremel    /  /  collar, screwed on in place of the nose cap
//        \\     /__/
//         \\   / \_ collet and mandrel
//    ______\\_/___\___
//   |  foot (forked)  V\ drum         V: where the sole meets the bevel plane;
//   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\             it lands on the green line.
//          foam          \ 35 deg
//
// The drum's axis lies in the bevel plane, pointing straight across the edge, so
// its side sands a flat bevel as the jig slides along. The sole rides flat on the
// foam face, straddling the drum. Units: mm. Print collar-down, no supports.

/* [Bevel] */
bevel_angle = 35;       // between the foam face and the sanded bevel

/* [Drum] */
drum_d = 12.7;          // Dremel 407: 1/2 in
drum_clearance = 1.5;   // radial, around the drum in the fork

/* [Dremel nose] */
thread_d = 19.05;       // 3/4 in nose thread, as on the 3000/4000/4300/8220
thread_pitch = 25.4 / 12;
thread_clearance = 0.5; // on diameter; raise if the test ring is tight
thread_length = 12;
thread_chamfer = 0.8;   // 45-degree lead-in at the thread's entry (the bed face)
shoulder_to_drum = 30;  // nose shoulder (where the cap seats) to the drum's top end
collet_d = 18;          // clear bore in front of the thread

/* [Jig] */
collar_od = 28;
foot_width = 44;        // across the edge direction, both tines together
foot_length = 30;       // inboard from V
foot_thickness = 4;
cheek = 4.5;            // side plates from the foot up to the collar

part = "jig";           // [jig, thread-test]
build = true;           // preview.scad turns this off to place its own copies

$fn = 72;

a = [0, cos(bevel_angle), -sin(bevel_angle)]; // tool axis, toward the drum's free end
n = [0, sin(bevel_angle), cos(bevel_angle)];  // out of the bevel plane, toward the axis
r = drum_d / 2;
o = r * n;                                    // axis point straight above V
t_top = -foot_thickness / 2 / sin(bevel_angle); // nominal drum top: halfway up the foot
t_shoulder = t_top - shoulder_to_drum;

// Children built along +Z are placed on the tool axis, Z = t.
module on_axis(t = 0)
    multmatrix([[1, 0, 0, o[0]], [0, -n[1], a[1], o[1]], [0, -n[2], a[2], o[2]], [0, 0, 0, 1]])
        translate([0, 0, t]) children();

// 60-degree thread form (ISO basic profile), right-hand, along +Z.
module thread_rod(d, p, length) {
    H = sqrt(3) / 2 * p;
    R = d / 2;
    Rr = R - 5 / 8 * H;
    flank = 5 / 16 * p;
    function f(u) = let (v = u - floor(u / p) * p)
        v < p / 16 ? R
        : v < p / 16 + flank ? R - (v - p / 16) / flank * (R - Rr)
        : v < p / 16 + flank + p / 4 ? Rr
        : v < p - p / 16 ? Rr + (v - p / 16 - flank - p / 4) / flank * (R - Rr)
        : R;
    section = [for (k = [0 : $fn - 1]) f(-p * k / $fn) * [cos(360 * k / $fn), sin(360 * k / $fn)]];
    linear_extrude(height = length, twist = -360 * length / p, slices = ceil(length / p * $fn))
        polygon(section);
}

// 45-degree lead-in cone, from past the thread crest down to its root.
module lead_in()
    translate([0, 0, -0.01]) cylinder(r1 = (thread_d + thread_clearance) / 2 + thread_chamfer,
        r2 = (thread_d + thread_clearance) / 2 - 5 / 8 * sqrt(3) / 2 * thread_pitch,
        h = thread_chamfer + 5 / 8 * sqrt(3) / 2 * thread_pitch);

module collar() on_axis(t_shoulder) cylinder(d = collar_od, h = thread_length);

// Back end runs parallel to the tool axis so it prints as a vertical wall.
module foot_slab(x0, x1)
    translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(x1 - x0)
        polygon([[-foot_length, 0], [0, 0], [0, foot_thickness],
                 [-foot_length - foot_thickness / tan(bevel_angle), foot_thickness]]);

module cheeks() {
    for (s = [-1, 1]) hull() {
        intersection() {
            collar();
            translate([s > 0 ? collar_od / 2 - cheek : -collar_od / 2, -100, -100]) cube([cheek, 200, 200]);
        }
        foot_slab(s > 0 ? collar_od / 2 - cheek : -collar_od / 2,
                  s > 0 ? collar_od / 2 : -collar_od / 2 + cheek);
    }
}

// The 145-degree open wedge the foam occupies: below the sole and below the bevel.
module foam_side()
    rotate([90, 0, 90]) linear_extrude(400, center = true)
        polygon([[-200, 0], [0, 0], [200, -200 * tan(bevel_angle)], [200, -300], [-200, -300]]);

module jig() {
    difference() {
        union() {
            collar();
            cheeks();
            foot_slab(-foot_width / 2, foot_width / 2);
        }
        on_axis(t_shoulder - 1) thread_rod(thread_d + thread_clearance, thread_pitch, thread_length + 2);
        on_axis(t_shoulder) lead_in();
        on_axis(t_shoulder + thread_length - 0.01) cylinder(d = collet_d, h = shoulder_to_drum - thread_length - 2);
        on_axis(t_top - 12) cylinder(r = r + drum_clearance, h = 100);
        foam_side();
    }
}

// Short ring with the same thread: print first to check the fit on the Dremel.
module thread_test() {
    difference() {
        cylinder(d = collar_od, h = 6, $fn = 6);
        translate([0, 0, -0.5]) thread_rod(thread_d + thread_clearance, thread_pitch, 7);
        lead_in();
    }
}

// Jig is printed collar-down: rotate the tool axis to +Z, collar face on Z = 0.
module jig_print()
    translate([0, 0, -t_shoulder])
        multmatrix([[1, 0, 0, 0], [0, -n[1], -n[2], 0], [0, a[1], a[2], 0], [0, 0, 0, 1]])
            translate(-o) jig();

if (build) {
    if (part == "thread-test") thread_test();
    else jig_print();
}
