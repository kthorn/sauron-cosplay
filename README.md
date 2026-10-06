# Child-sized Sauron mace

A **carrying/photo prop, not a striking toy**, sized for a 4′8″ child: **889 mm / 35 inches overall**, six EVA blades, nominal ¾-inch PVC, and a multi-tapered printed blade holder in **two stacked sections**, split **perpendicular to the handle axis**. These dimensions already represent approximately **¾ scale**; do not scale the STLs down again. Original simplified silhouette, not a film-exact tracing. References and fact/design distinctions: [SOURCES.md](file:///home/kurtt/sauron-cosplay/SOURCES.md) (`/home/kurtt/sauron-cosplay/SOURCES.md`).

## Foam helmet paper templates

Original, more movie-like **layered face plates and all six crown spires**, provisionally sized for a **540 mm headband**. These are **paper-fit design drawings, not measured or foam-ready patterns**. No printed helmet shell is needed.

- [US Letter PDF — five pages](file:///home/kurtt/sauron-cosplay/patterns/helmet/helmet-letter.pdf): `/home/kurtt/sauron-cosplay/patterns/helmet/helmet-letter.pdf`
- [A4 PDF — five pages](file:///home/kurtt/sauron-cosplay/patterns/helmet/helmet-a4.pdf): `/home/kurtt/sauron-cosplay/patterns/helmet/helmet-a4.pdf`
- [Preview, cut list, paper assembly, and scaling instructions](file:///home/kurtt/sauron-cosplay/patterns/helmet/README.md): `/home/kurtt/sauron-cosplay/patterns/helmet/README.md`

Print at **Actual Size / 100%** and check each 100 mm ruler. Pages 1–4 are cutting sheets; page 5 is the assembly key, **not a cutting template**. All parts fit on individual sheets at the supplied size. Full-size editable SVG masters are in `patterns/helmet/`. Paper-fit before EVA; eye position needs separate checking, and helmet sizing does not use the mace's 75% scale. Mace files and regeneration commands below remain separate and unchanged by this drawing set.

## Files

All files are under `/home/kurtt/sauron-cosplay`:

| File | Use |
|---|---|
| `mace.scad` | Editable canonical geometry; default view is assembly |
| `patterns/blade.svg` | Full-size editable pattern, 150 × 351 mm canvas; use tiled PDFs for home printing |
| `patterns/blade-a4-01.pdf`, `blade-a4-02.pdf` | **Two A4 sheets**, 210 × 297 mm each |
| `patterns/blade-letter-01.pdf`, `blade-letter-02.pdf` | **Two US Letter sheets**, 215.9 × 279.4 mm each |
| Matching numbered `.svg` files | Editable versions of the tiled sheets |
| `prints/fit-coupon.stl` | Print **one first** to test real pipe/foam fit |
| `prints/holder-lower.stl` | Print **one**, upright: lower hexagonal holder section, approximately 123 mm tall plus three 6 mm alignment pins on top |
| `prints/holder-upper.stl` | Print **one**, upright: upper hexagonal section with integrated pointed cone and three matching pin holes in its bed face, approximately 123 mm tall |
| `prints/holder.stl` | Complete approximately 246 mm holder for reference/larger printers; **too tall upright for the A1 mini** |
| `prints/adapter.stl` | Optional original ring; print two **instead of** the tapered holder |
| `patterns/manifest.json` | Parameters, holder profile/split, source fingerprints, common tile origins and owned generated files |
| `export.py`, `test_mace.py` | Regeneration and executable verification |

## Tools and regeneration

Verified here with **OpenSCAD 2021.01, Poppler 24.02.0, CairoSVG 2.9.0**. Use the Python interpreter that has CairoSVG installed (here `/home/kurtt/miniforge3/bin/python3`).

```bash
sudo apt-get install openscad poppler-utils
python3 -c 'import cairosvg'
cd /home/kurtt/sauron-cosplay
python3 export.py
python3 export.py --check
python3 -m unittest -v
openscad mace.scad
```

Measure your actual pipe OD and foam thickness before fitting. Example:

```bash
python3 export.py --set pipe_od=27 --set foam_thickness=12
python3 export.py --out "/path/with spaces"
```

`--set` overrides apply to that export, not to the saved SCAD defaults. For a matching interactive preview, set the same values in OpenSCAD's Customizer or edit `mace.scad`; edit SCAD for persistent changes. Commands can also use the script's absolute path from another cwd; default output remains this project folder. `OPENSCAD` and `PDFTOCAIRO` may select alternate executable paths. `--check` checks saved outputs without regenerating them; source edits require regeneration. Invalid sizes, missing tools and failed verification stop publication. Regeneration removes only obsolete manifest-owned files and refuses unowned filename collisions or unsafe/symlink paths.

Public millimeter parameters: `overall_length`, `blade_length`, `head_radius`, `pipe_od`, `bore_clearance`, `foam_thickness`, `slot_clearance`, `adapter_od`, `adapter_height`, `slot_root_radius`, `cover_allowance`, `land_allowance`, `coupon_height`, `tip_od`, `tip_overlap`, `tip_extension`, `tip_end_radius`, `crown_recess`, `pin_d`, `pin_length`, `pin_clearance`, `pommel_od`, `pommel_height`, `pommel_extension`. Bore clearance is on **diameter**; slot clearance is on **total width**, not per side. Changing blade length scales stations but keeps land height independent of that scale. `crown_recess` defaults to 12 mm below the EVA blade tips; `tip_end_radius` defaults to 4 mm. `tip_extension` retains the 35 mm PVC-to-blade-tip setback. `tip_od` and `tip_overlap` describe only the optional legacy foam top cap (`ring_assembly` preview). Other dimensions can require more pages; use the whole numbered set, including the caption gutter on wide heads. Incompatible core, cap, covering or neighboring-blade sizes are rejected.

## Print and tape the blade pattern

1. Choose **either the two A4 PDFs or the two Letter PDFs**, not a mixture. Print at **100% / Actual Size**, with Fit/Shrink disabled.
2. Measure the red **100 mm bar** on both sheets before trimming. Black solid lines are cuts; dashed blue lines/boxes are mounting references **not cuts**; gray crosses are alignment marks. These line styles remain distinguishable in grayscale.
3. Trim the **bottom 30 mm from page 1** and the **top 25 mm from page 2**. Align both gray crosses in the **10 mm overlap**, then tape. Do not simply butt whole page edges together. Discard the trimmed headers/footers only after the ruler check.
4. Check the assembled black outline: **295.275 mm tip-to-base × 46.5 mm radial width**. Cut on the black line's center. Transfer **six identical blades** onto measured 10 mm EVA; round/bevel the outer points and exposed foam edges. No rigid blade reinforcements.

## Print and fit the tapered holder

The **hexagonal spindle** follows the drawing's 380 mm core: a flared base collar, a narrow waist, one widest swell, then a long taper to the crown. Blades sit at its **six vertices**, but it is grooved **only where a blade meets the core**: around the lower collar (about 37–80 mm from the blade base) and the upper swell (about 183–250 mm). Each groove floor follows the blade's inner edge; between the grooves the hexagon is solid. The upper section includes a **printed cone ending in a hexagonal point** (no ball tip), ending approximately **12 mm below the protruding EVA blade tips**. This is a simplified interpretation of the drawing, not a precision replica. The existing **295.275 mm blades, 180 mm station spacing, and PVC cut length are unchanged**. The complete holder is approximately **246 mm tall**, split perpendicular to the handle axis into **two approximately 123 mm sections**, joined end-to-end around the PVC. Three printed **4 mm alignment pins** on the lower section's top face (6 mm long, on the hexagon-flat directions clear of the grooves) drop into **4.4 mm blind holes** in the upper section's bed face; no screws or other hardware.

Default dimensions: pipe OD **26.67**, bore **27.17** (+0.50 diameter); foam **10**, slot **10.3** (+0.30 total width), slot roots **18.5 mm from the axis**. The swell reaches **60 mm nominal diameter** (collar 54 mm); grooves remove those vertices, so do not rescale the meshes to force a 60 mm bounding box. The waist leaves approximately **3.30 mm minimum wall** outside the cylindrical bore. The upper bore stops above the PVC end with 1 mm axial slack, then closes with a **45° internal conical ceiling**; the pointed crown above it is solid. Both sections fit well within the A1 mini's **180 × 180 × 180 mm** volume, with room for a brim.

1. Print the existing **5 mm fit coupon first**, upright. Test the real bare PVC and foam; adjust `pipe_od`, `bore_clearance`, `foam_thickness`, and `slot_clearance` rather than forcing a fit.
2. Print **one lower and one upper section**, separately or side-by-side. Import at **100% scale**, with the bore vertical and the exported Z=0 face on the bed. Keep their exported orientation; the sections are **not identical**.
3. Defaults use ascending tapers and the internal bore ceiling no steeper than approximately 45°: **no supports are intended**. The lower bore goes through; the upper bore opens only at the bottom. Inspect Bambu Studio's layer preview before printing, especially if dimensions change. PLA or PETG, 0.2 mm layers, 3–4 perimeters, 15–20% infill, and a small brim are starting settings, not strength certification.
4. Dry-fit both pieces end-to-end on the PVC, **lower first**, with all six grooves aligned and the three pins seated in the upper section's holes. If the pins bind, trim them lightly or regenerate with a larger `pin_clearance`; do not force the joint. Install **both as printed, with their bed faces toward the pommel**: the upper section's bed face is the joint, and its cone points toward the blade tips. Their flat transverse joint is located at **160.138 mm from the blade base**. The collar sits at the original 45 mm station; the 60 mm swell lies just below the 225 mm station. The PVC aligns the bores; the alignment pins establish rotation. Do not twist or force the pieces with blades fitted.
5. Bond the sections to the PVC and to each other only after checking adhesive compatibility on scraps. The butt joint is not a load-rated connection. Pad exposed hard surfaces after fitting without narrowing the grooves.

The original `adapter.stl` remains an optional lighter two-ring alternative. Do not install those rings inside the new holder. The full `holder.stl` is one connected piece but is **not the A1 mini print file**. The new holder adds plastic compared with the rings; weigh the finished mockup and check carrying comfort.

## PVC layout and assembly (defaults)

The **provisional PVC cut is 839 mm**, not 889. Dry-fit before the final cut/glue. Layout includes 15 mm solid foam below the lower pipe end. The EVA blades extend 35 mm above the upper pipe end; the pointed printed cone ends about 12 mm below those blade tips. The EVA surround is **not an impact-protection guarantee**. The top is open approximately **60 mm across**: a finger, nose or eye can reach the hard crown **without touching or deforming the foam**. Keep the head away from faces; do not let children look into or poke the crown.

| Feature | From the prop's lowest foam extremity | From the lower PVC cut end |
|---|---:|---:|
| PVC lower/upper ends | 15 / 854 mm | 0 / 839 mm |
| Blade base | 593.725 mm | 578.725 mm |
| Lower holder bottom | 630.725 mm | **615.725 mm** |
| Lower blade station center | 638.725 mm | 623.725 mm |
| Holder section joint | 753.863 mm | **738.863 mm** |
| Upper blade station center | 818.725 mm | 803.725 mm |
| Rounded printed crown tip (nominal) | 877 mm | **862 mm** |
| EVA blade tips | 889 mm | 874 mm |

If length/cap settings change, use the new manifest's `pipe_span`, `blade_base`, `stations` and parameters instead of these default marks.

1. Have an adult cut/deburr the PVC. Mark the holder's lower bottom and section joint using the table. Slip the lower and upper sections onto **bare PVC**, **bed faces toward the pommel and cone toward the blade tips**, seating the three pins in their holes, which aligns the six grooves, and closing the transverse joint.
2. Dry-fit one blade radially into the aligned grooves. Its root stops at 18.5 mm radius. Existing mounting bands remain **34–56 and 214–236 mm** from the blade base; station centers remain **45 and 225 mm**. Grooves are cut wherever the blade's inner edge would otherwise enter the spindle, so the relieved edge between the bands clears it. Check flop and clearance before cutting/gluing the other five. Thicker foam is a tuning option; regenerate the slots and recheck weight/fit.
3. Fit all six, then glue permanently using manufacturer-compatible adhesives **tested on scraps** for EVA, PVC and the chosen print plastic. Plumbing PVC solvent cement is **not assumed to bond PLA/PETG**. Follow adhesive ventilation, curing and handling directions; keep coating off bond surfaces until joined.
4. The printed crown is already part of the upper section; **do not fit the old foam top cap over it**. Check that the pipe seats without force and that the crown stays approximately 12 mm below the EVA tips along the handle axis. This axial recess does not enclose the tip or prevent direct contact through the open head. For the optional two-ring alternative only, use `ring_assembly` to preview the original foam top-cap envelope: 36 mm OD, 15 mm sleeve overlap and 35 mm solid foam above the PVC, with a blunt 4 mm-radius tip.
5. Make the **pommel cap from EVA**, 40 mm OD × 40 mm long. Its cavity opens from above, is 25 mm deep, and leaves **15 mm solid foam beneath the PVC**. Round the outside without adding to overall length.
6. Bond the foam pommel only after an adhesion/retention trial. Wrap the shaft with approximately **3 mm radial foam**, **not beneath the holder bore or pommel sleeve**; the first 25 mm of PVC seats in the pommel. Leave the PVC bare from the holder's lower bottom through the upper pipe end. Pad exposed holder edges without obstructing blade grooves; the pointed crown intentionally remains printed plastic; lightly sand the point blunt if wanted. Check blade retention and spacing so it stays recessed. Foam blades can bend or tear and must not be relied on to make a hard crown safe to strike with.

## What was verified / what was not

Digital checks: actual SVG outline **295.275 × 46.5 mm**; A4 PDF reconstruction approximately **295.27538 × 46.49914 mm**, Letter **295.27431 × 46.49914 mm** (all within 0.1 mm). The original ring and coupon remain closed connected meshes with correct 16/5 mm height, through-bore and six open slots. The whole tapered holder and both upright sections are also checked for closure/connectivity, correct cylindrical bore and conical ceiling, six vertex grooves whose floors follow the blade inner edge, with solid hexagon vertices outside the contact regions (including width checks on both sides at the blade stations and widest swell; unverifiable groove widths are rejected), the hexagonal spindle profile, pointed crown, and approximately 246/123/123 mm heights. Section bounding boxes are checked against a **175 mm** envelope, reserving 5 mm total for a brim on the 180 mm printer. An actual CAD intersection checks the foam against the new holder, excluding nominal root-face contact. Reference centers **and band boundaries** are checked in SVG/PDF physical coordinates. The real CLI rejects 90%-scaled cut outlines while their calibration bars remain unchanged, then passes after restoration. Model/assembly and both paper-format previews were inspected; no interactive GUI editing or physical fabrication was performed.

Radial/sector/land assertions bound the entire blade foam outside the covered core/cap and within non-overlapping 60° sectors. Radial insertion keeps these clearances; seated roots pass through wider open slots. This is geometric clearance, **not** a load, cushioning, adhesive or impact test.

**Before the child uses it:** test coupon fit and compatible adhesives; assemble one blade to check flop; check holder-joint, blade and pommel retention, crown recession, and that all other hard endpoints/fittings are covered; weigh the completed mockup and check the child's carrying comfort. Check the venue's rigid-core prop rules. Adult supervision for cutting, printing, glue, heat and paint. **Do not swing or strike with this prop.** Foam dimensions are provisional, not an impact-protection rating.
