// Variant A, "drawing": close adaptation of the United Cutlery PD4646 blade side view.
// Spear tip, round bite below the upper ring, solid mid-body, opening with an inward
// barb beneath the outer spike, backswept spur at the base. Same rings, stations, caps.
include <../mace.scad>
include <blade_shapes.scad>

function variant_points() = design(concat(
    head(bez([18.5, 0], [34, 2], [54, 13])),
    [[54, 13], [47.5, 31], [55.5, 99], [65, 108], [36, 295.275]],
    tail(bez([36, 295.275], [31, 252], [18.5, 240])),
    arc([18.5, 190], 19, 90, -90, 14),
    bez([18.5, 122], [31, 121], [36, 108]),
    [[32, 99], [39.5, 96.5]],
    tail(bez([39.5, 96.5], [37.5, 80], [37, 72])),
    tail(bez([37, 72], [35, 58], [18.5, 58]))
));
blade_points = variant_points();

assert(land_bands[0][1] < z(58), "variant A: lower root must cover lower band");
assert(land_bands[1][0] > z(209) && land_bands[1][1] < z(240), "variant A: upper root must cover upper band");
