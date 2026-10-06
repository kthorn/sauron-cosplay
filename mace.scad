// Child-sized Sauron carrying/photo prop. Millimeters; see README.md and SOURCES.md.
// Print holder_lower and holder_upper once each, fit_coupon once.
// Crown is printed to a point, recessed inside separate EVA blades.
// Pommel is FOAM. Legacy rings + foam top cap remain a lighter alternative.
mode = "assembly"; // [assembly,ring_assembly,blade_2d,metadata,adapter,fit_coupon,holder,holder_lower,holder_upper]
overall_length = 889;
blade_length = 295.275;
head_radius = 65;
pipe_od = 26.67;
bore_clearance = 0.5; // Total DIAMETER allowance
foam_thickness = 10;
slot_clearance = 0.3; // Total slot WIDTH allowance
adapter_od = 60;
adapter_height = 16;
slot_root_radius = 18.5;
cover_allowance = 3;
land_allowance = 3;
coupon_height = 5;
tip_od = 36;
tip_overlap = 15;
tip_extension = 35;
tip_end_radius = 4; // Legacy foam top-cap tip radius
crown_recess = 12; // Printed crown ends this far below EVA blade tips
pin_d = 4; // Printed joint alignment pins on the lower section
pin_length = 6;
pin_clearance = 0.4; // Total hole DIAMETER allowance
pommel_od = 40;
pommel_height = 40;
pommel_extension = 15;
$fn = 128;

bore_diameter = pipe_od + bore_clearance;
slot_width = foam_thickness + slot_clearance;
adapter_radius = adapter_od / 2;
land_half = adapter_height / 2 + land_allowance;
axial_scale = blade_length / 295.275;
stations = [45 * axial_scale, 225 * axial_scale];
land_bands = [for (s = stations) [s - land_half, s + land_half]];
blade_base = overall_length - blade_length;
pipe_start = pommel_extension;
pipe_end = overall_length - tip_extension;
top_cap_start = blade_length - tip_extension - tip_overlap;
cover_radius = pipe_od / 2 + cover_allowance;
holder_start = stations[0] - adapter_height/2;
holder_body_end = stations[1] + adapter_height/2;
holder_body_height = holder_body_end - holder_start;
holder_end = blade_length - crown_recess;
holder_height = holder_end - holder_start;
holder_bore_height = pipe_end - blade_base - holder_start + 1; // 1 mm axial PVC slack
crown_stem_z = holder_bore_height + 2; // Protect the pipe wall before the outer cone narrows
holder_split = (holder_start + holder_end)/2;
// Reference spindle (drawing's 380 mm core): base collar, narrow waist, one
// hexagonal swell, then a long taper to the pointed crown. Blades sit at the
// six vertices. Axial positions are fractions of the 196 mm mounting envelope;
// the final taper keeps 3 mm of wall around the PVC end before the tip.
holder_profile = [
    [slot_root_radius+5.5, 0],
    [adapter_radius-3, holder_body_height*8/196],
    [adapter_radius-3, holder_body_height*16/196],
    [slot_root_radius+1, holder_body_height*51/196],
    [adapter_radius, holder_body_height*168/196],
    [slot_root_radius+5, crown_stem_z-14],
    [slot_root_radius+1, crown_stem_z],
    [0, holder_height]
];
function profile_r(z, i=0) = z <= holder_profile[i+1][1]
    ? holder_profile[i][0] + (holder_profile[i+1][0]-holder_profile[i][0])*(z-holder_profile[i][1])/(holder_profile[i+1][1]-holder_profile[i][1])
    : profile_r(z, i+1);
// Pins sit midway between bore and hexagon flats at the joint, on the flat
// directions so they stay clear of the vertex grooves.
pin_circle = (bore_diameter/2 + profile_r(holder_height/2)*cos(30))/2;
function r(f) = slot_root_radius + (head_radius - slot_root_radius) * f;
function z(y) = y * axial_scale;

// Original simplified silhouette, inspired by the United Cutlery drawing.
// Normalized radial fractions make head width independent of pipe/slot dimensions.
// Mounting-band endpoints remain absolute offsets from scaled station centers.
blade_points = [
    [r(0), 0], [r(.397849), z(16)],
    [r(.311828), land_bands[0][0]], [r(.634409), land_bands[0][0]],
    [r(.870968), z(62)], [r(.612903), z(57)],
    [r(1), z(95)], [r(.677419), z(118)], [r(.849462), z(185)],
    [r(.612903), z(203)], [r(.741935), land_bands[1][0]],
    [r(.569892), land_bands[1][1]], [r(.827957), z(250)],
    [r(.419355), z(262)], [r(.376344), blade_length],
    [r(.225806), z(279)], [r(.139785), z(255)],
    [r(0), land_bands[1][1]], [r(0), land_bands[1][0]],
    [r(.161290), z(197)], [r(.268817), z(163)],
    [r(.182795), z(128)], [r(.096774), z(96)],
    [r(0), land_bands[0][1]], [r(0), land_bands[0][0]], [r(.096774), z(18)]
];
// Inner edge, tip to base: its radial shadow is the only groove in the holder.
blade_inner_edge = [for (i = [14:len(blade_points)-1]) blade_points[i], blade_points[0]];
parameters = [
    ["overall_length", overall_length], ["blade_length", blade_length],
    ["head_radius", head_radius], ["pipe_od", pipe_od],
    ["bore_clearance", bore_clearance], ["foam_thickness", foam_thickness],
    ["slot_clearance", slot_clearance], ["adapter_od", adapter_od],
    ["adapter_height", adapter_height], ["slot_root_radius", slot_root_radius],
    ["cover_allowance", cover_allowance], ["land_allowance", land_allowance],
    ["coupon_height", coupon_height], ["tip_od", tip_od],
    ["tip_overlap", tip_overlap], ["tip_extension", tip_extension],
    ["tip_end_radius", tip_end_radius], ["crown_recess", crown_recess], ["pin_d", pin_d], ["pin_length", pin_length],
    ["pin_clearance", pin_clearance], ["pommel_od", pommel_od],
    ["pommel_height", pommel_height], ["pommel_extension", pommel_extension]
];

assert(overall_length > blade_length && blade_length > 0, "overall/blade length");
assert(pipe_od > 0 && foam_thickness > 0 && adapter_height > 0, "positive sizes");
assert(bore_clearance >= 0 && slot_clearance >= 0, "negative clearance");
assert(cover_allowance >= 0 && land_allowance >= 3, "cover/land allowance");
assert(head_radius > adapter_radius && adapter_radius > slot_root_radius, "head/ring/slot radii");
assert(slot_root_radius - bore_diameter / 2 >= 3, "minimum core wall 3 mm");
assert(slot_width < 2 * slot_root_radius * tan(30), "adjacent slot/blade separation");
assert(slot_root_radius >= cover_radius + .5, "covered pipe clearance");
assert(slot_root_radius >= tip_od / 2 + .5, "foam tip clearance");
assert(tip_od > bore_diameter && tip_overlap > 0 && tip_extension > 0, "tip sleeve");
assert(tip_end_radius >= 3 && tip_end_radius <= tip_od / 2, "rounded tip radius at least 3 mm");
assert(pommel_od > bore_diameter && pommel_extension > 0 && pommel_height > pommel_extension, "pommel sleeve");
assert(blade_base > pommel_height, "blade/pommel separation");
assert(coupon_height > 0 && coupon_height <= adapter_height, "coupon height");
assert(land_bands[0][0] > z(18) && land_bands[0][1] < z(57), "lower land stock");
assert(land_bands[1][0] > z(203) && land_bands[1][1] < z(250), "upper land stock");
assert(r(.311828) > adapter_radius && r(.569892) > adapter_radius, "radial land stock");
assert(top_cap_start > land_bands[1][1], "cap/upper land separation");
assert(min([for (p = holder_profile) if (p[1] <= crown_stem_z) p[0]])*cos(30) - bore_diameter/2 >= 3, "minimum hexagonal holder wall 3 mm");
assert(crown_recess > 0 && holder_body_height < crown_stem_z && crown_stem_z < holder_height, "crown/pipe/blade-tip clearance");
assert(max([for (p = holder_profile) p[0]]) <= adapter_radius, "holder shoulders require larger adapter_od");
assert(pin_d >= 3 && pin_length >= 3 && pin_clearance >= 0 && pin_length + 1 < holder_height/2, "joint pin size");
assert(min(pin_circle - bore_diameter/2, profile_r(holder_height/2)*cos(30) - pin_circle) - (pin_d+pin_clearance)/2 >= 1.2, "joint pin wall 1.2 mm");
// Blade inner-edge radius at blade-local z (edge runs tip to base).
function inner_r(z, i=0) = z >= blade_inner_edge[i+1][1]
    ? blade_inner_edge[i+1][0] + (blade_inner_edge[i][0]-blade_inner_edge[i+1][0])*(z-blade_inner_edge[i+1][1])/(blade_inner_edge[i][1]-blade_inner_edge[i+1][1])
    : inner_r(z, i+1);
assert(profile_r(holder_height/2) <= inner_r(holder_split) || pin_circle*sin(30) - (pin_d+pin_clearance)/2 >= slot_width/2 + .5,
    "joint pins clear of vertex grooves");
assert(holder_start >= 0 && holder_body_end < top_cap_start, "holder/legacy foam cap separation");
assert(mode == "assembly" || mode == "ring_assembly" || mode == "blade_2d" || mode == "metadata" || mode == "adapter" || mode == "fit_coupon" || mode == "holder" || mode == "holder_lower" || mode == "holder_upper", "unknown mode");

module blade_2d() { polygon(blade_points); }
module foam_blade() {
    rotate([90, 0, 0]) linear_extrude(foam_thickness, center=true) blade_2d();
}
module core_cutouts(height) {
    translate([0, 0, -1]) cylinder(d=bore_diameter, h=height+2);
    for (i = [0:5]) rotate([0, 0, i*60])
        translate([slot_root_radius, -slot_width/2, -1])
            cube([adapter_radius-slot_root_radius+1, slot_width, height+2]);
}
// Grooves exist only where a blade meets the core: each is the radial shadow of
// the blade's inner edge, so blades still insert radially and seat on the lands.
module blade_grooves() {
    for (i = [0:5]) rotate([0, 0, i*60]) translate([0, 0, -holder_start])
        rotate([90, 0, 0]) linear_extrude(slot_width, center=true)
            polygon(concat([[head_radius+1, -1], [head_radius+1, blade_length+1],
                            [blade_inner_edge[0][0], blade_length+1]],
                           blade_inner_edge, [[slot_root_radius, -1]]));
}
module adapter(height=adapter_height) {
    difference() {
        cylinder(d=adapter_od, h=height);
        core_cutouts(height);
    }
}
module holder() {
    difference() {
        rotate_extrude($fn=6) polygon(concat([[0, 0]], holder_profile));
        translate([0, 0, -1]) cylinder(d=bore_diameter, h=holder_bore_height+1);
        // Blind crown bore closes with a 45-degree ceiling, not a 27 mm bridge.
        translate([0, 0, holder_bore_height])
            cylinder(r1=bore_diameter/2, r2=0, h=bore_diameter/2);
        blade_grooves();
    }
}
module holder_section(upper=false) {
    bottom = upper ? holder_height/2 : 0;
    // Transverse butt joint: the PVC aligns the bores, pins set rotation.
    // Each exported section has its own bottom at Z=0 for upright printing.
    // Lower top face carries pins; upper bed face has matching blind holes.
    difference() {
        union() {
            translate([0, 0, -bottom]) intersection() {
                holder();
                translate([-adapter_radius-1, -adapter_radius-1, bottom])
                    cube([adapter_od+2, adapter_od+2, holder_height/2]);
            }
            if (!upper) for (i = [0:2]) rotate([0, 0, 30+i*120])
                translate([pin_circle, 0, holder_height/2]) {
                    translate([0, 0, -.5]) cylinder(d=pin_d, h=pin_length-.1, $fn=32);
                    translate([0, 0, pin_length-.6]) cylinder(d1=pin_d, d2=pin_d-1.2, h=.6, $fn=32);
                }
        }
        if (upper) for (i = [0:2]) rotate([0, 0, 30+i*120])
            translate([pin_circle, 0, -1]) cylinder(d=pin_d+pin_clearance, h=pin_length+1.5, $fn=32);
    }
}
module tip_cap() {
    difference() {
        cylinder(d=tip_od, h=tip_overlap);
        translate([0, 0, -1]) cylinder(d=bore_diameter, h=tip_overlap+1);
    }
    translate([0, 0, tip_overlap])
        cylinder(r1=tip_od/2, r2=tip_end_radius, h=tip_extension);
}
module pommel_cap() {
    difference() {
        cylinder(d=pommel_od, h=pommel_height);
        translate([0, 0, pommel_extension])
            cylinder(d=bore_diameter, h=pommel_height-pommel_extension+1);
    }
}
module assembly(legacy_rings=false) {
    color("silver") translate([0, 0, pipe_start])
        cylinder(d=pipe_od, h=pipe_end-pipe_start);
    color([.2, .23, .25]) difference() {
        translate([0, 0, pommel_height]) difference() {
            cylinder(r=cover_radius, h=pipe_end-tip_overlap-pommel_height);
            translate([0, 0, -1]) cylinder(d=pipe_od, h=pipe_end-tip_overlap-pommel_height+2);
        }
        if (legacy_rings) {
            for (s = stations) translate([0, 0, blade_base+s-adapter_height/2-.1])
                cylinder(r=cover_radius+1, h=adapter_height+.2);
        } else translate([0, 0, blade_base+holder_start-.1])
            cylinder(r=cover_radius+1, h=holder_height+.2);
    }
    for (i = [0:5]) color([.28, .3, .32])
        translate([0, 0, blade_base]) rotate([0, 0, i*60]) foam_blade();
    if (legacy_rings) {
        for (s = stations) color("darkorange")
            translate([0, 0, blade_base+s-adapter_height/2]) adapter();
        color([.25, .27, .29]) translate([0, 0, pipe_end-tip_overlap]) tip_cap();
    } else color("darkorange") translate([0, 0, blade_base+holder_start]) holder();
    color([.25, .27, .29]) pommel_cap();
}
module metadata() {
    echo(["MACE_META",
        ["parameters", parameters], ["blade_points", blade_points],
        ["blade_bounds", [slot_root_radius, 0, head_radius, blade_length]],
        ["bore_diameter", bore_diameter], ["slot_width", slot_width],
        ["stations", stations], ["land_bands", land_bands],
        ["pipe_span", [pipe_start, pipe_end]], ["blade_base", blade_base],
        ["top_cap_start", top_cap_start], ["top_cap_radius", tip_od/2],
        ["adapter_radius", adapter_radius], ["adapter_height", adapter_height],
        ["coupon_height", coupon_height], ["cover_radius", cover_radius],
        ["holder_span", [holder_start, holder_end]], ["holder_split", holder_split],
        ["holder_profile", holder_profile], ["blade_inner_edge", blade_inner_edge], ["holder_bore_height", holder_bore_height],
        ["holder_body_span", [holder_start, holder_body_end]],
        ["holder_pins", [pin_circle, pin_d, pin_length, pin_clearance]],
        ["svg_axes", [1, -1]]
    ]);
}
if (mode == "blade_2d") blade_2d();
else if (mode == "metadata") metadata();
else if (mode == "adapter") adapter();
else if (mode == "fit_coupon") adapter(coupon_height);
else if (mode == "holder") holder();
else if (mode == "holder_lower") holder_section();
else if (mode == "holder_upper") holder_section(true);
else if (mode == "ring_assembly") assembly(true);
else assembly();
