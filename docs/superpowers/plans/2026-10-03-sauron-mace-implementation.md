# Sauron Mace Patterns and Adapters Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce editable OpenSCAD geometry, verified foam-blade cutting patterns, and two small printable adapter designs for the approved child-sized Sauron prop.

**Architecture:** `mace.scad` owns every geometric dimension, blade point, and mounting station. `export.py` invokes OpenSCAD, styles and tiles its actual SVG, renders PDFs with existing CairoSVG, and verifies the fabrication outputs. One standard-library test file exercises the same render and verification functions used by the real export command.

**Tech Stack:** OpenSCAD, Python 3, existing CairoSVG, Python's `unittest`/XML/JSON/subprocess libraries, and Poppler's PDF-to-SVG conversion. No web service, application framework, CAD Python stack, or custom PDF parser.

**Spec:** `docs/superpowers/specs/2026-10-03-sauron-mace-design.md`, approved by the user on 2026-10-03 after the Opus 5.5 follow-up returned no supported substantive findings.

## Global Constraints

- Approximately 35 inches overall: **889 mm**, including foam ends; provisional PVC length **839 mm**, not 889 mm.
- Six identical blades; centers spaced **60 degrees**. Default axial bounds **0–295.275 mm**, radial bounds **18.5–65 mm**; outline width **46.5 mm**.
- Nominal ¾-inch US Schedule 40 PVC: initial measured-OD input **26.67 mm**. Bore clearance **+0.50 mm on diameter**; default bore **27.17 mm**.
- Initial foam **10 mm**; slot clearance **+0.50 mm on total width**; default slot **10.5 mm**.
- Adapter OD **60 mm**, height **16 mm**, slot floor radius **18.5 mm**; stations **45 mm** and **225 mm** from the blade base. Print the same adapter twice.
- Mounting lands cover adapter height plus **3 mm at either end**, **22 mm** total. Minimum bore-to-slot wall **3 mm**; cover/cap clearance at least **0.5 mm**.
- Top foam cap: maximum OD **36 mm**, sleeve overlap **15 mm**, soft extension **35 mm**, blunt tip radius **3 mm**. Pommel: OD **40 mm**, length **40 mm**, including **15 mm** solid foam beyond the PVC.
- Caps are assembly/check envelopes, **not printed parts**. Only adapter and approximately **5 mm-high** fit-coupon geometry belongs in fabrication STLs.
- Metadata and the real SVG, not a second coordinate list in Python, supply reference positions. Radial X maps to SVG X; positive axial distance maps to negative SVG Y.
- A4 and US Letter pages: at least **10 mm** margins, **10 mm** overlap, alignment marks and a **100 mm** calibration bar. Print at **100% / Actual Size**.
- Verify the actual outline in final SVG and PDF physical coordinates, within **0.1 mm**; a correct calibration bar alone is insufficient.
- Fail explicitly on invalid dimensions, missing tools, failed rendering, unexpected output, or verification failure. Never create placeholder fabrication files.
- Physical coupon, adhesive, cap-retention, one-blade flop, and child carry checks remain mandatory. Digital checks do not establish impact safety.
- This folder is not a Git repository. Do not initialize Git or create a worktree solely for workflow compliance; commit steps are not applicable unless the owner separately requests Git.

## Review Focus

1. Measured pipe/foam differs from the nominal values: bore and slot must follow the inputs, while geometrically incompatible sizes fail explicitly — Task 1.
2. Blade length changes: station locations rescale, but 22 mm land heights do not; cap/land collisions are rejected — Task 1.
3. SVG/PDF units, reversed Y, and tile origins: the blade itself must retain physical scale, reference alignment, and complete page coverage — Task 2.
4. Missing tools, a nonzero exit, or OpenSCAD `ERROR:` text even with a zero exit: rendering must stop without publishing accepted artifacts — Tasks 1 and 2.
5. Regeneration and paths with spaces: reducing the page count must remove only obsolete generated pages, preserve unrelated files, and work outside the project cwd — Task 2.

## File Map

| File | Responsibility |
|---|---|
| `mace.scad` | Canonical blade profile, parameters, assertions, slotted ring, foam cap envelopes, assembly preview, metadata |
| `export.py` | OpenSCAD invocation, metadata extraction, styled/tiled SVG/PDF output, STL and final-pattern verification, CLI |
| `test_mace.py` | One `unittest` module covering the model and the actual export gate, including negative probes |
| `README.md` | Tool setup, regeneration, parameter names, printing, PVC layout, dry fitting, assembly, limitations |
| `SOURCES.md` | Existing research ledger; update only when additional verified references are used |
| `patterns/blade.svg` | Full-size annotated pattern; cutting path distinct from references |
| `patterns/blade-a4-NN.svg/.pdf` | Numbered A4 pages |
| `patterns/blade-letter-NN.svg/.pdf` | Numbered US Letter pages |
| `patterns/manifest.json` | Model-derived metadata, source fingerprint, generated filenames, page sizes and common-origin tile offsets |
| `prints/adapter.stl`, `prints/fit-coupon.stl` | Verified fabrication meshes |

The manifest is generated evidence for these exports, not a second configuration or hand-maintained geometry file. No pattern or STL is marked fabrication-ready until the real verification gate has passed.

---

## Prerequisite: Owner-installed tools

OpenSCAD and Poppler are absent. Ubuntu package candidates were confirmed: OpenSCAD `2021.01-6build4`, Poppler `24.02.0-1ubuntu9.9`. Passwordless sudo is unavailable, so the agent cannot perform this installation unattended.

- [ ] **Owner installs the two distro packages**, or supplies equivalent executables:

```bash
sudo apt-get install openscad poppler-utils
```

- [ ] **Verify tools before the feature test cycle:**

```bash
openscad --version
pdftocairo -v
python3 -c 'import cairosvg; print(cairosvg.__version__)'
```

Expected: successful version output and CairoSVG import. If package metadata is stale, the owner may need `sudo apt-get update` first. Do not request the owner's password, invent an installation fallback, or count a missing dependency as the intended TDD failure.

## Task 1: Parametric CAD and Render Contract

**Files:**
- Create: `mace.scad`
- Create: initial `export.py` render/metadata functions
- Create: `test_mace.py`, `TestCad`
- Create: initial `README.md` tool setup and model preview instructions

**Interfaces:**
- Consumes: approved spec and `SOURCES.md` drawing reference; installed OpenSCAD.
- Produces: `run_scad(mode: str, destination: Path, defines: dict[str, float] | None = None) -> None` and `read_model(defines: dict[str, float] | None = None) -> dict` in `export.py`.
- `run_scad` resolves `mace.scad` relative to `export.py`, uses argument arrays without a shell, honors an optional `OPENSCAD` executable override, and treats missing output or any OpenSCAD `ERROR:` as failure regardless of exit status.
- `read_model` parses one tagged `echo()` array beginning with `MACE_META` into a dictionary. Required keys: `parameters`, `blade_points`, `blade_bounds`, `bore_diameter`, `slot_width`, `stations`, `land_bands`, `pipe_span`, `top_cap_start`, `top_cap_radius`, and `svg_axes`. Names and values are echoed by SCAD, not recomputed from Python constants.
- SCAD public numeric names include `overall_length`, `blade_length`, `head_radius`, `pipe_od`, `bore_clearance`, `foam_thickness`, `slot_clearance`, `adapter_od`, `adapter_height`, `slot_root_radius`, `cover_allowance`, and the cap dimensions named in the README. Model modes: `blade_2d`, `metadata`, `adapter`, `fit_coupon`, `assembly`.

- [ ] **Step 1: Write the failing default-contract test** in `TestCad.test_defaults`:

```python
m = read_model()
self.assertEqual(m["blade_bounds"], [18.5, 0, 65, 295.275])
self.assertAlmostEqual(m["bore_diameter"], 27.17, places=3)
self.assertAlmostEqual(m["slot_width"], 10.5, places=3)
self.assertEqual(m["stations"], [45, 225])
self.assertEqual(m["land_bands"], [[34, 56], [214, 236]])
self.assertEqual(m["pipe_span"], [15, 854])
self.assertAlmostEqual(m["top_cap_start"], 245.275, places=3)
self.assertEqual(m["top_cap_radius"], 18)
self.assertEqual(m["svg_axes"], [1, -1])
```

Also pin `TestCad.test_measured_sizes`: `pipe_od=27` and `foam_thickness=12` produce a 27.5 mm bore and 12.5 mm slot without changing blade length. Pin `TestCad.test_scaled_stations_fixed_lands`: `blade_length=320` rescales stations by `320/295.275`, keeps both lands 22 mm high, and preserves cap separation. Write the negative and shape tests listed in Step 4 now, before implementing the corresponding guards.

- [ ] **Step 2: Run the red check:**

```bash
python3 -m unittest -v test_mace.TestCad
```

Expected initially: failure because the render/model interface does not exist, not because tool setup was skipped.

- [ ] **Step 3: Implement the canonical SCAD model and metadata/render interface.** Build an original polygon inspired by the reference drawing: elongated silhouette, swept outer lobes, outward inner reliefs, straight required mounting lands, and the approved bounds. No engraving or downloaded-model reuse. Use one blade module for both the cutting outline and centered foam extrusion. A common adapter module accepts height, giving the real ring and thin coupon; fabrication rings sit on Z=0, while assembly placement uses station center minus half ring height. Use one set of derived values for cap envelopes, preview, assertions, and metadata. Default preview is `assembly`.

Include SCAD assertions for positive dimensions, core wall, blade separation, cap/cover clearance, full 22 mm land stock beyond the ring perimeter, and cap/land separation. The radial insertion clearance follows from outward-moving profiles bounded outside the core and aligned slots; do not claim collision checking merely because a pretty preview renders. Python rejects non-finite numbers and unknown override names before accepting a render.

- [ ] **Step 4: Run the complete CAD gate, including its negative and shape checks.**

Names/assertions:
- `test_invalid_fit_rejected`: `pipe_od=34`, `foam_thickness=24`, and negative clearance each raise an explicit error.
- `test_short_blade_rejected`: `blade_length=240` is rejected because the top cap encroaches on the upper mounting region.
- `test_profile`: echoed point list is a single non-self-intersecting polygon with the required bounds and complete stock at both land bands; all point radii are at least 18.5 by default.
- `test_missing_tool`: unavailable `OPENSCAD` path raises an error, not fake metadata or a fake STL.
- `test_zero_exit_error_rejected`: a mocked zero-exit process containing `ERROR:` is rejected by the same `run_scad` used in production.
- `test_assembly_renders`: the actual `assembly` mode produces a nonempty temporary `.csg` file without render errors; it is never put in `prints/`.

Run `python3 -m unittest -v test_mace.TestCad`; expected: all tests pass. Render the actual blade SVG to a temporary PNG with existing CairoSVG and inspect it against the reference. If a display is available, also view the assembly in OpenSCAD; otherwise record that interactive visual check as an owner-side check, not as an action the headless agent performed. Visual inspection supplements, not replaces, geometric assertions.

- [ ] **Step 5: Record the task evidence.** List created files, red/green commands, visual-check result, and any remaining rendering limitations. Commit only if the owner has separately established Git; otherwise leave files in this project folder.

## Task 2: Verified Cutting Pages and Fabrication Exports

**Files:**
- Modify: `export.py`
- Modify: `test_mace.py`, add `TestExports`
- Modify: `README.md`
- Generate: `patterns/` and `prints/` files in the file map

**Interfaces:**
- Consumes: Task 1's `run_scad`, `read_model`, metadata keys, native `blade_2d` SVG, and the real `adapter`/`fit_coupon` modes.
- Produces: `build(output_dir: Path, defines: dict[str, float] | None = None) -> dict` and `validate_exports(output_dir: Path) -> None` in `export.py`. `build` returns the generated manifest and runs the real validator before publishing successful output.
- CLI: `python3 export.py [--out DIR] [--set NAME=NUMBER ...]`; default output root is the project folder, independent of caller cwd. `python3 export.py --check [--out DIR]` validates an existing export tree without regenerating it.
- Manifest supplies `cad` metadata and `pages` entries with format, physical size, SVG/PDF relative filenames, and common-origin offsets. Generated-file ownership is explicit; reject unsafe manifest paths rather than deleting outside `patterns/` or `prints/`.

- [ ] **Step 1: Write the failing export tests.** Write the corruption/failure probes listed in Step 4 before implementing the corresponding validator. `TestExports.test_default_exports` builds into a `TemporaryDirectory` and requires:

```python
result = build(output_dir)
validate_exports(output_dir)
self.assertEqual(result["cad"]["blade_bounds"], [18.5, 0, 65, 295.275])
self.assertTrue((output_dir / "patterns/blade.svg").is_file())
self.assertTrue((output_dir / "prints/adapter.stl").is_file())
self.assertTrue((output_dir / "prints/fit-coupon.stl").is_file())
self.assertEqual({p["format"] for p in result["pages"]}, {"a4", "letter"})
```

Require A4 page size `[210, 297]` mm and Letter `[215.9, 279.4]` mm, complete coverage with at least 10 mm margins and 10 mm overlap, and an exactly 100 mm calibration bar. Default blade paths reconstruct to 295.275 × 46.5 mm within 0.1 mm in final SVG **and PDF** coordinates. Dashed mounting marks must correspond to the echoed stations and bands after the declared X/Y transform.

- [ ] **Step 2: Run the red check:**

```bash
python3 -m unittest -v test_mace.TestExports
```

Expected initially: failure because `build` and `validate_exports` are not implemented.

- [ ] **Step 3: Implement actual exports and their validator.** Use the real SCAD-exported SVG path and its viewBox. Add references solely from metadata. Give the cutting outline black styling, mounting references blue/dashed, labels and alignment marks gray, and the calibration bar red; the grayscale legend must still distinguish cut from reference lines. Keeping only cutting geometry black also lets PDF inspection identify the actual outline rather than annotation glyphs.

Tile the common physical coordinate space without scaling it to page width. Use explicit millimeter page sizes and store each tile origin in the manifest. CairoSVG converts each numbered SVG into its numbered PDF; no PDF merger. Render both STLs from their own modes, explicitly requesting ASCII STL for the small standard-library mesh check if supported by the verified OpenSCAD version.

For PDF measurement, invoke **`pdftocairo -svg`** on the actual PDF and measure its black cutting paths after SVG group transforms and physical-unit conversion. Reconstruct tile bounds using recorded origins. Parse the straight-line path output needed here; fail on unexpected unsupported commands instead of writing a generic PDF parser or assuming scale. PDF inspection and publication require Poppler, not just CairoSVG.

Verify the real mesh triangles: nonempty, one connected closed component, correct height (16 mm or 5 mm), no pipe/cap/other assembly geometry, centered open bore, and six open radial slots. Use welded vertex/edge checks and representative interior/exterior probes; do not assume nominal 60 mm OD implies a 60 mm X bounding box after the radial slots remove its extremes.

Generate in a unique temporary staging directory, run the same `validate_exports` there, then publish the known artifact set. On regeneration, remove only obsolete files recorded as owned by the prior manifest; preserve unrelated files. No generic deployment/transaction framework.

- [ ] **Step 4: Run the real-gate failure probes and prove they bind.**

Names/assertions:
- `test_svg_scale_corruption`: modify only the exported cut-outline transform to 90% scale, leaving the calibration bar unchanged; `validate_exports` raises an error.
- `test_pdf_scale_corruption`: produce a PDF from a 90%-scaled cut layer while leaving the corresponding canonical SVG, metadata, and bar unchanged; PDF inspection makes `validate_exports` fail.
- `test_missing_pdf_tool`: unavailable `pdftocairo` produces a clear verification error and no successful publication.
- `test_stl_contamination`: a missing mesh, disconnected extra solid, or cap/pipe-sized contaminating mesh is rejected rather than treated as a valid ring.
- `test_stations_on_pages`: reference positions survive negative-Y mapping and tile translation and remain non-cut markings.
- `test_page_count_changes`: use a valid long `blade_length=700`, then regenerate defaults; page counts change, stale owned numbered pages disappear, and an unrelated note remains.
- `test_paths_and_cwd`: build and validate a directory containing spaces while running from another cwd; no shell interpretation or accidental writes there.

Run the full `python3 -m unittest -v`; expected: all tests pass. Also run the actual CLI gate, `python3 export.py --check --out PROBE_DIR`, on the deliberately scale-corrupted temporary SVG/PDF trees: require a nonzero exit identifying outline scale, then restore and require a zero exit. Each corruption is isolated in a temporary copy and restored/rebuilt; never leave a deliberate probe in the user's fabrication outputs.

- [ ] **Step 5: Generate and inspect the actual deliverables.**

```bash
python3 export.py
python3 export.py --check
python3 -m unittest -v
```

Expected: verified blade SVG, A4/Letter PDF pages, manifest, adapter STL and coupon STL; all tests pass. Render and inspect at least one page from each paper format and the full blade to catch inverted marks, clipped labels, or poor silhouette. Inspect the assembly in OpenSCAD when a display is available; otherwise deliver the tested assembly preview source and explicitly leave its interactive visual check to the owner. Measure the path, not a screenshot, for acceptance. Record each output's actual dimensions and page counts instead of predicting them in the README.

- [ ] **Step 6: Finish the fabrication instructions in `README.md`.** Explain `OPENSCAD`, numeric `--set` overrides, regeneration/check commands, actual output filenames/page counts, Actual Size printing and ruler calibration, printing one coupon first, two identical adapters, and the 839 mm provisional PVC layout. Document the foam cap cavities and bare-pipe seating, glue compatibility/scrap tests, one-blade mockup, cap retention, child carry check, and venue rules. Do not imply measured physical comfort or joint strength from digital passing checks.

- [ ] **Step 7: Record task evidence and preserve the known limitations.** Include real red/green and corruption-probe results, outputs generated, tool versions, inspections, and residual physical checks. Commit only if Git has been separately authorized.

## Final Independent Review and Handoff

- [ ] Re-run the exact final commands above and collect their output before requesting review.
- [ ] For recommended native execution, use **one fresh Opus 5.5 reviewer at the operator's selected medium effort**, in a read-only shell-capable route. Proposed route: a Paseo Claude agent in Plan Mode, in the verified local workspace for `/home/kurtt/sauron-cosplay`. Execution approval must include this route; do not silently replace the governed runner or select a different model.
- [ ] Verify the agent's actual model and workspace with `paseo inspect`; give it the approved spec, four product source files, generated manifest and output paths, and gate evidence. Allow only read-only inspection and the verification commands; no edits, publication, or nested delegation. Since no Git branch exists, review the complete product-file/output set rather than inventing a branch diff.
- [ ] Treat only an actual completed verdict as review completion. A `paseo wait` status other than `idle`, a runner failure, or an unanswered permission request is a blocker, not a clean review. Verify supported findings and fix in the primary session, then rerun affected gates. Do not automatically review this implementation-plan document.
- [ ] Deliver the CAD source, blade SVG/PDF links, two STL links, sources ledger, verified dimensions, and a short list of physical checks still required. Do not claim the prop has been printed or physically tested.

## Plan Self-Review

- [x] Spec coverage: CAD/interface and caps in Task 1; marking, tiling, both physical-scale checks and meshes in Task 2; physical fabrication sequence in README.
- [x] Interfaces: render/metadata functions belong to Task 1; build/validation/CLI consume them in Task 2; metadata names agree across the tasks.
- [x] Review Focus: all five listed input/failure classes have named tests in their owning tasks.
- [x] Proportion: two coupled implementation tasks, four product source files, native tools for PDF inspection, no added framework or wholesale copied implementation.
- [x] Environment: package candidates checked; installation requires the owner; no installation, product code, or fabricated exports performed during planning.
- [ ] User reviews the written plan and selects native or subagent-driven execution.
