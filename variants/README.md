# Blade variant D — "spiked" (chosen design)

The blade design we're building, adapted from the United Cutlery PD4646 drawing
(see [../SOURCES.md](../SOURCES.md)). It lives beside the original blade: the main `mace.scad`,
`patterns/` and `prints/` still hold the original blade and its holder. **Print and cut from `d-spiked/`.**

| | D — `d-spiked` |
|---|---|
| Body | Sturdy body; narrowest foam beside the openings ≥ 16 mm |
| Tip | Spear point |
| Openings | Round bite below the upper ring; opening under the back arm with an inward barb |
| Outer spike | Hooked spike at the widest point, with a deep notch on both sides |
| Base | Crescent horn pointing outward and back |

Features from the drawing's side view of a single blade, top to bottom: the long, straight outer edge running
from the tip to one outward spike roughly a third of the way up; a round bite open to the shaft; a solid body
that touches the shaft; an opening under the back arm, with a small barb; and a swept-back spur over a curved heel.
The drawing's openings show the central holder through them, and D's do too.

## Scale and compatibility

Same ~3/4-scale envelope as the original: **295.275 mm tip-to-base × 46.5 mm radial**
(slot root 18.5 → head radius 65). For comparison, 75% of the drawing's 183.8 mm head is ≈ 69 mm radius;
`--set head_radius=69` widens D to match while the root stays on the bands.

Feature spacing was adapted so that the root edge stays **solid on both mounting bands** (34–56 and 214–236 mm
from the blade base). The rings/holder, stations, caps and assembly steps from the main README are therefore unchanged.
D is just `include <../mace.scad>` plus its own `blade_points` (and `holder_profile`), so it follows any future changes
to the mount (e.g. the holder) automatically. After `mace.scad` or `export.py` changes, regenerate.

D's holder grooves follow its own blade's inner edge, so its holder STLs differ from the main ones.
**D also reshapes the holder spindle** (`holder_profile` in `blade_d_spiked.scad`) to match its blade, as in the drawing:
the collar sits on D's base root, the 19.5 mm waist inside the lower opening, the 60 mm swell over the solid middle root
(118–176 mm from the blade base), and one taper runs through the round bite to the pointed crown. Grooves are cut only at D's
three root contacts: about 37–67, 117–179 and 207–243 mm. The two-piece split and joint pins are unchanged; on D the joint
(160 mm) falls inside the middle groove zone, and the pins sit on the hexagon flats, clear of the grooves.

## Files

- `blade_d_spiked.scad`: D's source; open in OpenSCAD for the assembly view.
- `blade_shapes.scad`: shared Bezier/arc helpers; also points the holder's blade grooves
  (`blade_inner_edge` in `mace.scad`) at D's inner edge.
- `d-spiked/`: generated `patterns/` (full-size SVG, A4 and Letter tiled PDFs, manifest),
  `prints/` (same adapter/coupon as the main ones; holder shaped and grooved for D) and `assembly-preview.png`.
  **Print D's holder from `d-spiked/prints/`**, not the main `prints/`: see above.
- `export_variants.py`, `test_variants.py`.

```bash
cd /home/kurtt/sauron-cosplay
python3 variants/export_variants.py
python3 variants/export_variants.py --check
python3 variants/export_variants.py --set foam_thickness=12
python3 -m unittest variants/test_variants.py
```

`export_variants.py` runs the unchanged `export.py` build and verification steps: printed-scale SVG/PDF
outline checks, calibration bar, band references and STL checks. Print and assembly instructions are the
same as in the main README; the tape-up dimensions are the same 295.275 × 46.5 mm.

## Bevel guides

D's pattern also has a **green dash-dot bevel line**, 6 mm in from each exposed edge (not
along the straight mounting edge, which sits in the slots). It is a marking line, **not a cut**:
1. Cut the blade out square along the black line.
2. Transfer the green line to **both faces** (prick through the paper, or measure 6 mm in).
3. Carve or sand from the line down to the edge on each face, leaving about a 2 mm flat in the middle of the edge.
   With 10 mm foam that removes about 4 mm per face, roughly a 35° bevel.
4. Where the line stops short of a point (tip, spikes, barb, horn), taper the bevel out to the point.

Change the inset with `--bevel MM`, e.g. `--bevel 4` for thinner foam. `export.py` checks only black, blue and red ink,
so the bevel lines are checked by `test_variants.py` instead: present on every sheet, inside the outline, off the root edge.

## Not verified

These are digital checks only. No foam has been cut. Test-cut one blade from scrap EVA and
check flex across the bridges, the barb, the hooked spike and the horn. Round over and bevel every point by hand, as in the main README.
