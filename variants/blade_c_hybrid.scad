// Variant C, "hybrid": B's sturdy body, bite and spur, with A's spear tip and the
// inward barb from A's opening. Same rings, stations, caps.
include <../mace.scad>
include <blade_shapes.scad>

function variant_points() = design(concat(
    head(bez([18.5, 0], [34, 2], [50, 15])),
    [[50, 15], [46, 28], [55.5, 99], [65, 108], [36, 295.275]],
    tail(bez([36, 295.275], [31, 252], [18.5, 240])),
    arc([18.5, 192], 16, 90, -90, 12),
    bez([18.5, 118], [29, 117], [34, 106]),
    [[29.5, 100], [35, 97]],
    tail(bez([35, 97], [35, 76], [18.5, 62]))
));
blade_points = variant_points();

assert(land_bands[0][1] < z(62), "variant C: lower root must cover lower band");
assert(land_bands[1][0] > z(208) && land_bands[1][1] < z(240), "variant C: upper root must cover upper band");
