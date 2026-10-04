# Sauron Mace Spec Review (Opus 5.5, read-only)

**Subject:** `docs/superpowers/specs/2026-10-03-sauron-mace-design.md` (SHA256 `1d7ebf40…9b50`), reviewed from the supplied text only. No tools were run. This is not physical validation.

**Default geometry checked by hand:**
- **Bore-to-slot wall:** bore radius 13.585 against slot floor 18.5 gives a minimum wall of 4.915, which meets the ≥3 requirement.
- **Wall between slots:** at r = 18.5, each 10.5 slot subtends about 33° of the 60° pitch, leaving about 8.7 mm of arc between slots.
- **Slot engagement:** 11.5 radial (18.5 to 30).
- **Adapter positions:** both adapters sit fully on the PVC. The upper adapter top is at about 826.7 and the PVC ends at 854.
- **Scale arithmetic:** 0.75 × 46.375 in = 883.44 mm, and 0.75 × 15.5 in = 295.275 mm. The 889 total and the 839 pipe length (15 to 854) are internally consistent.

## Findings

**1. No minimum inner-radius (clearance) rule for the blade profile.**
- **Evidence:** The spec requires a "relieved inner edge", and the land is at radial 18.5. Acceptance 1 bounds only "max 65 radial". Blades "slide inward radially".
- **Consequence:** Nothing stops the outline, outside the lands, from going inside the PVC radius (13.335) or the covering/tip cap. That blade could not be inserted radially. Above the pipe end (854 to 889), inward-swept tips could also collide with each other or with the tip cap. The "no intersecting adjacent blades" check does not catch blade-to-pipe or blade-to-cap intrusion.
- **Smallest fix:** Add a profile constraint and check. Inner edge radius must be ≥ 18.5 within the adapter axial spans. Elsewhere along the pipe it must be ≥ pipe OD/2 plus a covering allowance. Above the PVC it must be ≥ the tip-cap radius. Out-of-range values are rejected.

**2. Tip extension and pommel are load-bearing in the layout but have no defined geometry.**
- **Evidence:** "Overall 889 incl foam pommel/tip", "Foam tip extends 35 beyond PVC", and "soft 35mm tip extension". The outputs list contains no cap or pommel part, and the blade tips also end at 889.
- **Consequence:** The child-safety soft end and the overall length rely on an unspecified part. That part must fit inside the six blade inner edges, a gap of less than about 18.5 radius. That leaves at most about 5 mm of cap wall over a 13.3 mm pipe radius, which may not be a usable soft cap.
- **Smallest fix:** Specify the cap and pommel envelope (OD, length, material, attachment) as parameters in `mace.scad`. Include them in the clearance check from finding 1 and in the README fit sequence. They do not need patterns.

**3. Reference marks cannot leave OpenSCAD with distinct styles without duplicating coordinates.**
- **Evidence:** The script "NEVER duplicates blade coordinates", yet the patterns need "distinct cut/reference styles" with bands and station centers as "REFERENCE marks". OpenSCAD SVG export produces unstyled geometry from a single 2D mode.
- **Consequence:** The implementer will either recompute station and land positions in Python, breaking the single-source rule, or ship patterns without distinguishable reference marks.
- **Smallest fix:** Define a separate SCAD 2D mode, such as `blade_marks`, exported as its own SVG. Alternatively, have the script parse `echo()`'d derived values. `export.py` then only applies styles and tiles the pages.

**4. Scale checks don't measure the exported outline itself.**
- **Evidence:** Acceptance 1 checks the blade's dimensions. Acceptance 5 checks page dimensions, overlap, coverage, and the 100 mm bar.
- **Consequence:** The calibration bar is drawn by the export script, so it can be correct while the imported SCAD outline is mis-scaled. A px-vs-mm or 96-DPI CairoSVG unit error would pass every check and produce wrong-size foam cuts.
- **Smallest fix:** In the final SVG and PDF coordinates, assert that the outline bounding box equals 295.275 axial by 46.5 radial (18.5 to 65), within about 0.1 mm. Assert the bar is exactly 100 mm in the same space. Make the deliberate-failure check (acceptance 6) include a unit or scale corruption.

## Residual risks (not findings)
- **Untested physical fit:** EVA thickness variation, print tolerance, and PLA/PETG–EVA adhesion are unproven until the coupon and scrap tests are done, as the spec already acknowledges.
- **Blade flop:** about 158 mm of unsupported blade between the lands may flop. The one-blade test covers this.
- **Unverified tooling:** OpenSCAD is absent, so no STL or SVG behavior has been verified.

## Substantive findings
1. Blade inner-edge minimum radius and clearance against the pipe, cover and tip cap is unconstrained and unchecked.
2. Tip and pommel caps are undefined despite fixing the overall length and soft-end safety, and their fit inside the blade ring is unchecked.
3. Reference-mark export conflicts with the no-duplication rule under OpenSCAD's unstyled SVG output.
4. The exported outline scale is not discriminatingly verified; only the script-drawn calibration bar is checked.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Concise review with four evidence-backed findings (blade inner clearance, undefined tip/pommel cap, reference-mark export vs single-source rule, exported-outline scale check), hand-checked default geometry, and residual risks"
    }
  ],
  "changedFiles": [],
  "testsAddedOrUpdated": [],
  "commandsRun": [],
  "validationOutput": [
    "Hand-checked: core wall 4.915>=3; inter-slot arc ~8.7mm at r18.5; engagement 11.5mm; upper adapter top ~826.7 < PVC end 854; 75% scale values match SOURCES"
  ],
  "residualRisks": [
    "Physical fit/adhesion/flop unverified until coupon and one-blade tests",
    "OpenSCAD not installed; no STL/SVG behavior verified",
    "Review based solely on supplied spec text; SOURCES.md not independently inspected"
  ],
  "noStagedFiles": true,
  "diffSummary": "No files changed; review text returned for host persistence to docs/superpowers/reviews/2026-10-03-sauron-mace-spec-review-opus-5-5.md",
  "reviewFindings": [
    "major: spec Acceptance 1 / Interface - no minimum blade inner-radius clearance vs PVC/cover/tip cap",
    "major: spec Dimensions/layout - 35mm tip and 15mm pommel caps undefined yet set overall length and safety",
    "major: spec Approach/Patterns - reference-mark styling vs no-duplicated-coordinates rule unresolved",
    "major: spec Acceptance 5 - exported outline scale not verified in final SVG/PDF coordinates"
  ],
  "manualNotes": "No-tools read-only run; plan-mode tool workflow not invoked per runner instructions. Final answer is the review artifact."
}
```