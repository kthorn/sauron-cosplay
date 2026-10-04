# Tapered blade holder

- [x] Explore existing OpenSCAD model, build instructions, and reference drawing.
- [x] Confirm printer envelope and required blade compatibility: Bambu A1 mini, 180 mm cube; preserve existing approximately 3/4-scale prop and blade geometry.
- [x] Present short in-chat design, including print orientation and verification.
- [x] Obtain approval; user corrected split direction to perpendicular to the handle axis: two stacked sections, printed upright and aligned by the PVC. Subsequent explicit requirements: hexagonal cross section with blades at vertices, integrated rounded printed crown below the protruding EVA tips. Extended sections are now approximately 123 mm each.
- [x] Implement minimal geometry and regression checks: shared slots and mesh inspection, plus three holder modes.
- [x] Render/export and verify each part is a closed connected mesh; document upright print settings and physical-fit limitations.
- [x] Complete independent Anthropic review of the first holder revision and dispose substantive findings: explicit assembly orientation, channel-width gate, corrected wall description.
- [x] Implement requested hexagonal body and integrated rounded printed cone, with unchanged EVA outline / PVC cut and no overlapping legacy foam cap.
- [ ] Complete focused independent review of the final hexagon/crown revision.
- [x] Reshape holder to the drawing's 380 mm core spindle (collar, waist, single 60 mm swell, long taper) and replace full-length vertex channels with grooves cut only where each blade's inner edge meets the core (blade-local ~37–80 and ~183–250 mm). Profile/groove test watched fail first; validator now probes solid vertices outside grooves and groove floors on the blade inner edge, and rejects a full-channel mesh.
- [x] Removed the 4 mm crown ball per user; the cone now ends in a hexagonal point at the same 12 mm recess. Still exported as two upright ~123 mm sections.
- [x] Added joint alignment: three 4 × 6 mm printed pins on the lower section top face (hexagon-flat directions, clear of grooves) and 4.4 mm blind holes in the upper bed face; still two upright prints, no supports intended. Pin test watched fail first; validator checks pins/holes and lower height +6 mm.
- [x] Variant D holder: D-specific `holder_profile` override in variants/blade_d_spiked.scad (collar on base root, waist in lower opening, 60 mm swell over the 118–176 mm middle root, taper through the bite); grooves at D's contacts ~37–67/117–179/207–243 mm. Added mace.scad assert that joint pins clear the vertex grooves. Test watched fail first.
- [ ] Independent review of the spindle/contact-groove revision.

Intent: model the reference's multi-tapered central blade holder for the existing approximately 3/4-scale child-sized carrying/photo prop. Prefer one piece; user authorizes two stacked pieces split perpendicular to the handle axis if necessary for the A1 mini. Retain separate soft EVA blades and pommel, existing blade dimensions/mount spacing/PVC cut, an adjustable PVC bore, and fit clearances. Crown is printed with a 4 mm-radius rounded tip, recessed 12 mm below the EVA blade tips; guarding is geometry, not impact certification. Do not apply another 0.75 scaling factor: the current 295.275 mm blades already use that scale. The original two-ring print remains available as a lighter alternative; the default assembly now uses the tapered holder.

Context: existing mounting centers are 180 mm apart, each original ring is 16 mm high, making their combined axial envelope 196 mm. Repository has no Git metadata, so Git history/diff/commit workflows are unavailable.

## Verification and review

- Original blade outline, 295.275 mm length, 45/225 mm stations, 34–56/214–236 mm bands, and PVC layout compared against pre-task OpenSCAD metadata: unchanged.
- Final measured STL bounds: lower 53.9378 × 51.9616 × 123.137 mm; upper 53.9378 × 51.9616 × 123.129 mm. Complete holder is 246.266 mm tall (nominal 246.275; rounded-tip tessellation). Bore diameter 27.17 mm; full-depth pipe cavity has 1 mm axial slack then a 45° ceiling. Split is transverse at blade-local 160.1375 mm; nominal crown tip 283.275, EVA tip 295.275.
- Actual foam/holder CAD intersection is empty with a 0.01 mm radial offset to exclude intended root-face contact (CGAL otherwise keeps zero-volume contact sheets).
- Final gate: `export.py --check` and all 30 unittests pass (217.162 seconds); log `/tmp/sauron-hex-crown-final-gates.Cami3M.log`. New hexagon/crown and wrong-width checks were watched fail before their fixes. Initial full run exposed a false-positive width probe where a stretched hexagon lacked wall stock; corrected the stock condition, then reran the complete suite green.
- Independent reviewer: Paseo `6db5858f-d7a3-4bfe-a894-d1bd5f879ac8`, verified `claude-opus-5-5`, `max`, Plan Mode. First snapshot `/tmp/sauron-holder-review.OtkZR3` completed; accepted findings: F1 orientation instructions, F2 width validation, F3 wall wording. Reviewer's private plan-file/ExitPlanMode attempt reconciled by sending read-only final-text instruction; terminal status idle with no permissions. No project/snapshot edits occurred.
- Focused final re-review uses the same model/effort/run and pins `/tmp/sauron-hex-crown-review.aWhLY2`; pending, not yet a clean final verdict. Runner inherits live CWD; reviewer explicitly scoped to each absolute snapshot.
- No slicer trial or physical print, fit, weight, glue-retention or carrying test performed.

## Separate follow-ups

- Earlier approved spec/plan/progress documents still carry stale execution status; baseline owner/reviewer informed. Baseline was independently reviewed clean before this holder change.
- Other session reports an unanswered packed single-sheet split-blade-template request; that is separate from this task, which intentionally leaves blade/pattern geometry unchanged.
- Earlier reviewer also found the legacy ring/coupon `_mesh` gate can accept narrower-than-metadata slots because it lacks an inside-edge probe. The new holder gate now checks both sides and rejects wrong widths; legacy ring/coupon strengthening remains a separate follow-up. Always physically test real foam and pipe in the coupon.

