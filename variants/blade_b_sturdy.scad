// Variant B, "sturdy": the drawing's rhythm simplified for 10 mm EVA and a child.
// Smaller bite, one smooth opening without barb, 5 mm blunt tip, shorter spur.
// Foam beside the openings stays at least 18 mm wide (A: 14.5). Same rings, stations, caps.
include <../mace.scad>
include <blade_shapes.scad>

function variant_points() = design(concat(
    head(bez([18.5, 0], [34, 2], [50, 15])),
    [[50, 15], [46, 28], [55.5, 99], [65, 108], [39, 295.275], [34, 295.275]],
    tail(bez([34, 295.275], [29, 252], [18.5, 242])),
    arc([18.5, 192], 16, 90, -90, 12),
    bez([18.5, 118], [30, 116], [33, 100]),
    tail(bez([33, 100], [34, 76], [18.5, 62]))
));
blade_points = variant_points();

assert(land_bands[0][1] < z(62), "variant B: lower root must cover lower band");
assert(land_bands[1][0] > z(208) && land_bands[1][1] < z(242), "variant B: upper root must cover upper band");
