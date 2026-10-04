# Child-sized Sauron mace: blade patterns and adapters

Status: approved by the user on 2026-10-03; implementation plan written, execution-method selection and tool installation pending.

## Purpose and scope

Create editable cutting patterns and printable adapters for an approximately three-quarter-scale Sauron cosplay mace carried by a 4′8″ nine-year-old. Preserve the approved construction: approximately 35 inches overall, nominal ¾-inch PVC, six EVA-foam blades, two small printed adapters, and permanent glued assembly. Keep exposed tips soft and weight low, especially at the head.

Deliver the blade outline, adapter, fit coupon, assembly preview, print-ready patterns, and concise fabrication instructions. This is a carrying/photo prop, not a striking toy. Film-exact engraving, a complete printed handle, armor, removable joints, and load-bearing/impact certification are outside this first build.

## Selected modeling approach

Use **one parametric OpenSCAD file** as the canonical geometric source. It supplies a 2D blade outline and 3D adapter/preview geometry. A small export script invokes OpenSCAD and uses the already-installed CairoSVG package to make printable PDF pages from the exported SVG; it must not contain a second copy of the blade coordinates or mounting dimensions.

A `metadata` mode emits tagged, machine-readable `echo()` data with derived blade bounds, station centers, mounting-band extents, dimensions, and the model-to-SVG axis convention (radial X maps to SVG X; positive axial distance maps to negative SVG Y). `export.py` honors that transform and the native SVG `viewBox`, then adds dashed reference marks, labels, and the calibration bar in the same coordinate space. It must not recalculate station positions from independent constants or fit the outline and marks to separate bounding boxes. This resolves OpenSCAD's unstyled SVG output without duplicating geometric definitions.

Alternatives considered:

- Hand-authored SVG plus separate OpenSCAD adapters: fewer export steps, but duplicates the mounting dimensions and risks a pattern/adapter mismatch.
- CadQuery or another Python solid-modeling stack: capable, but adds a substantial dependency for two simple slotted rings.

OpenSCAD gives native SVG and STL exports and an interactive preview with little project infrastructure. No framework or package scaffolding is needed.

## Initial dimensions and coordinate contract

All CAD dimensions are millimeters. Nominal values are starting points, not verified printer fits.

| Parameter | Initial value / meaning |
|---|---|
| Overall prop length | 889 mm (35 inches), including foam pommel and tip |
| Blade axial length | 295.275 mm, rounded only for display |
| Nominal head diameter | 130 mm across opposed blade radial centerlines; an adjustable project choice, not a verified replica dimension. Foam thickness slightly increases the circumscribed envelope. |
| Pipe OD | 26.67 mm; replace with actual measured OD |
| Pipe bore clearance | +0.50 mm on **diameter**, initially |
| Foam thickness | 10 mm; replace with measured foam thickness |
| Foam slot clearance | +0.50 mm on **total width**, initially |
| Blade count | Six; centers spaced 60 degrees |
| Adapter outside diameter | 60 mm |
| Adapter axial height | 16 mm |
| Slot inner radial coordinate | 18.5 mm from the pipe axis |
| Slot outer opening | Through the adapter's outer perimeter, nominal radius 30 mm |
| Adapter station centers | 45 mm and 225 mm from the blade's lower end |
| Minimum core wall | At least 3 mm from bore surface to any slot |
| Foam tip extension past PVC end | 35 mm |
| Foam beyond PVC at pommel end | 15 mm |
| Shaft foam-covering allowance | 3 mm radially, outside adapter/cap seating areas |
| Blade-to-cover/cap clearance | At least 0.5 mm radially |
| Top foam cap | 36 mm maximum OD; 15 mm sleeve overlap plus 35 mm soft extension; blunt tip radius 3 mm |
| Foam pommel cap | 40 mm OD and 40 mm axial length; 25 mm sleeve overlap plus 15 mm solid foam beyond PVC |

The blade's 2D coordinates are **radial distance from the pipe axis** and **axial distance from the blade's lower end**. The 3D adapter's bore runs along the assembly axis. Preview extrusion of each blade is centered on its radial plane, so a 10 mm blade fits a 10.5 mm slot.

For the default length layout: blade lower end is at 593.725 mm from the pommel extremity, blade tip at 889 mm, PVC starts at 15 mm and ends at 854 mm. The corresponding provisional PVC cut length is **839 mm**, not 889 mm. Dry-fit first; optional pommel decoration must stay inside the chosen overall envelope or explicitly update it.

Changing blade length rescales its axial features, including the two mounting stations. Changing pipe OD or foam thickness does **not** uniformly rescale the prop. Derived geometry must preserve the mounting contract or reject an incompatible configuration clearly.

## Blade and adapter interface

Create a recognizable, simplified Sauron blade silhouette using the United Cutlery drawing linked in `SOURCES.md`. It is an original approximation, not a precision tracing of the low-resolution reference. Prioritize the elongated profile, swept outer lobes, and relieved inner edge over engraving. Use six identical blades; do not cut sharp rigid reinforcements into their outer points.

At each adapter station, the inner blade edge includes a **straight mounting land at radial coordinate 18.5 mm**. Each land spans the full adapter height plus 3 mm at either end: 22 mm total. Throughout that band, the blade extends radially beyond the adapter perimeter. Neither an inner-edge relief nor an outer notch may cut into this required material. Show the bands and adapter-center marks on the printed pattern as reference marks, **not additional cut lines**.

Keep the **entire blade outline at or outside the slot's inner radial coordinate**, not just the mounting lands. Inner-edge reliefs move away from the axis; no blade tip curls inward. The default minimum radius is therefore 18.5 mm and the maximum is 65 mm, giving a 46.5 mm radial outline width. Also require clearance from the covered pipe and the top foam-cap envelope along their full axial spans. Reject pipe, covering, cap, or blade configurations that overlap or leave less than the stated 0.5 mm clearance; a radial insertion path from outside must remain clear except for intended contact inside the slots.

The same adapter STL is printed twice. It is a cylindrical ring with a continuous bore wall and six straight radial slots open to the outside, extending through the adapter height. The foam roots slide inward into these slots and stop at the inner radial coordinate. No dovetails, clips, fasteners, or inaccessible internal cavities are needed.

Dry-fit both rings on the PVC, aligned at the same angular orientation and correct station spacing. Insert all six blades radially before permanent gluing. Cover visible plastic after fitting; foam covering must not occupy the bore or blade slots and invalidate their measured fit.

Print rings with the bore axis vertical, flat on the bed. Through-slots and the vertical bore should require no supports. Use a thin, approximately 5 mm-high version of the same ring as the fit coupon; it exercises both the real bore and the real six-slot geometry.

## Foam end-cap envelopes

Represent both end caps in the OpenSCAD assembly and clearance checks, **not as printed parts**. Their dimensions are provisional project choices, not verified impact-protection requirements. Make them from stacked EVA and hand-shape them; exact decorative cap patterns are unnecessary for this first build.

- **Top cap:** a 36 mm-OD cylindrical foam sleeve overlaps the bare pipe by 15 mm, ending at the PVC endpoint. Above it, 35 mm of solid foam tapers to a blunt 3 mm-radius tip. The sleeve's nominal cavity uses the same 27.17 mm fit diameter, giving approximately 4.4 mm of side foam. In blade-local coordinates the cap occupies 245.275–295.275 mm; only its first 15 mm has a pipe cavity. Its maximum radius is 18 mm, leaving 0.5 mm to the blade roots. The cap starts 9.275 mm above the upper mounting band's end, so it does not intrude into the adapter or land. Changed configurations must preserve this separation or fail explicitly.
- **Pommel cap:** a simple 40 mm-OD, 40 mm-long foam envelope occupies global axial coordinates 0–40 mm. Its cavity opens at the upper end and stops at 15 mm, so the PVC begins at 15 mm and the lowest 15 mm remains solid foam. It is well below the blade region. Round its outside during finishing without extending past the specified axial extremity.

Glue compatible foam caps to the bare pipe only after a scrap adhesion test. Cut the actual foam cavities to suit the measured pipe; modeled clearances do not establish adhesion or cushioning performance. Shaft wrapping stops before the cap sleeves and adapter bores; do not layer wrapping under a part designed to fit bare PVC. Cover the adapters' exposed surfaces after blade seating, without blocking slots. Verify cap retention, no exposed hard endpoints, and carrying comfort in the physical mockup. If adequate padding requires larger envelopes, update the model and recheck blade clearance rather than squeezing an oversized cap into the existing head.

## Files and outputs

- `mace.scad`: source model with selectable `blade_2d`, `metadata`, `adapter`, `fit_coupon`, and `assembly` modes, including parameterized foam-cap envelopes in the assembly; assembly is the normal preview, never the fabrication STL.
- `export.py`: a small export entry point; uses an available OpenSCAD executable and CairoSVG. Missing tools or failed renders are explicit errors, not placeholder output.
- `patterns/`: one full-size SVG and tiled printable SVG/PDF pages for **A4 and US Letter**. Individual numbered PDF pages are acceptable; no PDF-merging dependency is necessary.
- `prints/`: separate adapter and fit-coupon STLs, only after successful OpenSCAD rendering and checks.
- `README.md`: dimensions, adjustable parameters, regeneration command, print settings, fit-check sequence, provisional pipe cut layout, assembly, and practical limitations.
- `SOURCES.md`: URLs, verified dimensions, indexed-only leads, and the distinction between sourced facts and our choices.
- One small executable check for the geometry and export contract; use existing tools or standard-library checks, not a new test framework.

Tile at actual physical scale with at least 10 mm printer margins and 10 mm overlap. Pages need format/page identification, alignment marks, clear cut versus mounting-reference line styles, and a **100 mm calibration bar** on a page where it fits. Numbered pages must use a common coordinate origin so taping them together does not shift the blade outline. Print at 100% / Actual Size; verify the bar with a ruler before cutting foam. Parameter changes that require more pages must produce more pages, not clip or shrink the pattern.

## Verification and physical acceptance

Digital checks must establish:

1. Default blade bounds are axial 0–295.275 mm and radial 18.5–65 mm; the outline is a valid, non-self-intersecting single region. The full foam volume and its radial insertion path clear the pipe, wrapping, and cap envelopes; adjacent blades do not intersect. Ignore only the intended seated blade/slot contacts.
2. All six slot positions and both blade mounting lands agree in the assembly coordinate system. Lands encompass the full station height, including the stated allowance. Exported metadata and reference marks use these same model coordinates.
3. Default bore is 27.17 mm and default slot width is 10.5 mm; at least 3 mm of core wall remains. Covered-pipe and cap clearance is at least 0.5 mm; the top cap does not overlap either adapter or mounting band. A changed pipe OD, foam thickness, covering, or cap envelope either works coherently or fails explicitly. Mounting lands retain their required absolute height when blade length changes; reject a blade too short to accommodate the lands and caps.
4. The two fabrication STL modes render as nonempty single connected solids with a through-bore and open slots; assembly-only geometry, including foam caps, cannot enter their files.
5. Tiled page dimensions, overlap, complete outline coverage, and the 100 mm bar are preserved in SVG and PDF exports. A4 and Letter dimensions are not interchangeable. **Measure the exported blade path itself**, excluding reference marks: default physical bounding-box size must be 295.275 mm axial by 46.5 mm radial, within 0.1 mm. Measure this in final SVG physical units and final PDF page/path coordinates; for tiles, reconstruct bounds using the recorded common-origin offsets. Compare against model-derived bounds for nondefault configurations. A correctly sized script-drawn bar alone does not verify outline scale.
6. The check demonstrably fails on an intentionally invalid configuration or broken expectation, then passes after restoration. Include a deliberate outline-unit/scale corruption with the calibration bar unchanged, proving the exported-outline measurement binds.

Physical acceptance remains separate: print the coupon, check the actual PVC and foam, assemble one blade temporarily, check flop and adhesive compatibility, then let the child try carrying the mockup. Weigh the finished prop. Adjust clearance and foam thickness before committing to all six blades. Neither a rendered STL nor a passing geometric check proves carrying comfort or joint strength.

Printed adapters are not PVC fittings: do not assume plumbing PVC solvent cement bonds PLA or PETG. Select adhesive by its manufacturer's material compatibility, test on scraps, and have an adult handle cutting, printing, adhesives, heat, and finishing. Pad/cap both pipe ends, maintain the soft tip extension, cover visible hard edges, and check the venue's rigid-core prop rules.

## Current environment and approval boundary

The project folder began empty and is **not a Git repository**, so no design commit is possible without separately initializing one. Do not initialize Git merely to satisfy a workflow checkbox.

Python, Pillow, and CairoSVG are available; **OpenSCAD is not installed**. Source creation does not justify claiming STL verification. The implementation plan must establish how to run OpenSCAD (approved installation or an operator-provided executable) before fabrication exports can be accepted.

### Review disposition

Opus 5.5's first completed text-only review covered spec SHA256 `1d7ebf4087739624462369d118f5dede5788ff52c5037f5f0b580f015c449b50`. The parent verified the dimensional arithmetic and accepted the four practical gaps:

1. **Inner clearance:** bound the complete profile outside the slot roots and explicitly check pipe, covering, cap, and insertion-path clearance.
2. **Unspecified end caps:** define adjustable foam-only envelopes and their seating/padding layout. The earlier spec already required padded endpoints; this clarifies them without adding printed cap parts. These are not proven safety dimensions.
3. **Reference export:** explicitly use OpenSCAD-derived metadata for styled reference marks. Distinct styling was possible, but its single-source mechanism had not been specified.
4. **Export scale:** measure the actual final blade path, not merely the separate calibration bar; include a scale-corruption negative check. The default 46.5 mm width follows the newly explicit radial bounds, not a replica measurement.

Numerical check: bore 27.17 mm; bore-to-slot wall 4.915 mm; top cap sleeve wall approximately 4.415 mm; cap-to-blade radial clearance 0.5 mm; cap begins 9.275 mm beyond the upper land. CAD rendering and physical suitability remain unverified.

The focused follow-up reviewed the corrected contract at spec SHA256 `c048bce92aa7e4a3f95775044a6f5e4299d1ce62e22a682293e7fb55ad193551` and returned **“No supported substantive findings.”** Run `0fdb18da-ab39-4821-a7e7-fe98632839d7` completed using verified `claude-opus-5-5`, requested medium effort, read-only Plan Mode with no tools. The review was of the supplied corrected-spec packet, not executable CAD or physical fit. Remaining cap tolerance, retention, and tooling uncertainties are covered by the implementation and mockup checks above. This record and the checklist update are administrative changes after that reviewed version; the geometric contract is unchanged. Stop the refinement pass and request user approval.

### Process checklist

- [x] Capture approved physical intent and permanent assembly decision.
- [x] Inspect the project folder, tools, and dimensional sources.
- [x] Compare modeling approaches and write the geometric interface contract.
- [x] Record sources and distinguish project choices from verified dimensions.
- [x] Self-review dimensions, fit-clearance definitions, coordinate agreement, and approval boundaries.
- [x] Receive the first completed independent spec review and verify/dispose its findings.
- [x] Recheck the substantive corrections with Opus 5.5 at medium effort: no supported substantive findings.
- [x] Obtain user approval of this written spec on 2026-10-03.
- [x] Write and self-review `docs/superpowers/plans/2026-10-03-sauron-mace-implementation.md`.
- [ ] Obtain user review of the plan and execution-method selection.
- [ ] Implement, verify exports, and document physical checks.
