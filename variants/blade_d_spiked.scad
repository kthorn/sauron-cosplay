// Variant D, "spiked": C (B's sturdy body with A's tip and inner barb) plus the
// drawing's external spikes: a hooked spike at the widest point with a deeper notch
// behind it, and a crescent base horn pointing outward and back. Same rings, stations, caps.
include <../mace.scad>
include <blade_shapes.scad>

function variant_points() = design(concat(
    head(bez([18.5, 0], [40, 9], [58, 3])),
    head(bez([58, 3], [50, 12], [47, 27])),
    [[47, 27], [51.5, 99], [65, 101], [57, 116], [61.5, 125], [36, 295.275]],
    tail(bez([36, 295.275], [31, 252], [18.5, 240])),
    arc([18.5, 192], 16, 90, -90, 12),
    bez([18.5, 118], [29, 117], [34, 106]),
    [[29.5, 100], [35, 97]],
    tail(bez([35, 97], [35, 76], [18.5, 62]))
));
blade_points = variant_points();
// Holder spindle placed for D's root: collar on the base root, 19.5 mm waist inside
// the lower opening, the 60 mm swell over the solid middle root (118-176 mm), then one
// taper through the round bite to the crown stem. Grooves still follow blade_inner_edge.
holder_profile = [
    [slot_root_radius+5.5, 0],
    [adapter_radius-3, z(45)-holder_start],
    [adapter_radius-3, z(53)-holder_start],
    [slot_root_radius+1, z(88)-holder_start],
    [adapter_radius, z(150)-holder_start],
    [slot_root_radius+1, crown_stem_z],
    [0, holder_height]
];

assert(land_bands[0][1] < z(62), "variant D: lower root must cover lower band");
assert(land_bands[1][0] > z(208) && land_bands[1][1] < z(240), "variant D: upper root must cover upper band");
