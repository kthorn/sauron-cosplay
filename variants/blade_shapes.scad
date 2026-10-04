// Shared outline helpers for the alternative blade variants. Include AFTER ../mace.scad.
// Design coordinates are default-size millimeters: x = radius from the shaft axis
// (18.5 slot root .. 65 head radius), y = distance from blade base (0 .. 295.275 tip).
// design() maps them through mace.scad's r()/z(), so --set head_radius, blade_length
// and slot_root_radius stretch the outline like the original blade.

function design(points) = [for (p = points) [r((p[0] - 18.5) / 46.5), z(p[1])]];
// Quadratic Bezier, n segments, endpoints included.
function bez(p0, c, p1, n=8) = [for (i = [0:n]) let(t = i / n) (1-t)*(1-t)*p0 + 2*(1-t)*t*c + t*t*p1];
// Circular arc from angle a0 to a1 (degrees), endpoints included.
function arc(center, radius, a0, a1, n=12) = [for (i = [0:n]) let(a = a0 + (a1 - a0) * i / n) center + radius * [cos(a), sin(a)]];
function head(v) = [for (i = [0:len(v)-2]) v[i]];
function tail(v) = [for (i = [1:len(v)-1]) v[i]];

// mace.scad's holder grooves follow the blade's inner edge, tip to base. Its default
// index assumes the original outline; variants list the outline base -> outer edge ->
// tip -> inner edge, so take everything from the tip onward.
function tip_index(points) = let(top = max([for (p = points) p[1]]))
    [for (i = [0:len(points)-1]) if (points[i][1] == top) i][0];
function inner_edge(points) = [for (i = [tip_index(points):len(points)-1]) points[i], points[0]];
blade_inner_edge = inner_edge(blade_points);
