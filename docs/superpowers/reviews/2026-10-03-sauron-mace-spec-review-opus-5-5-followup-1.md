# Sauron Mace Spec: Focused Follow-up Review (Opus 5.5)

**Subject:** `docs/superpowers/specs/2026-10-03-sauron-mace-design.md`, SHA256 `c048bce9…1551`, checked against the supplied packet. This was a text-only review. I used no tools and wrote no file, so the host should save this answer to the configured output path.

## Geometry and caps (prior gaps 1 and 2)

**Gap 1 (blade inner radius) is resolved.** The whole outline is now required to stay at radius 18.5 or more. Reliefs must move away from the axis, and inward-curled tips are banned. The arithmetic is consistent:
- Bore radius is 27.17 / 2 = 13.585, so the wall is 18.5 − 13.585 = 4.915. That meets the ≥3 requirement.
- Covered pipe radius is 13.335 + 3 = 16.335. Adding the 0.5 gap gives 16.835, which is below 18.5.
- Cap radius is 18, which leaves exactly 0.5 to the blade root.

The whole foam volume and the radial insertion path are now checked against the pipe, wrapping and caps. Adjacent blades are checked against each other, and intended contact inside the slots is allowed.

**Gap 2 (cap geometry) is resolved, and the numbers close:**
- **Top cap:** 245.275 + 15 = 260.275. That matches the local PVC end, since 854 − 593.725 = 260.275. Then 260.275 + 35 = 295.275, which is the global tip at 889.
- **Upper adapter:** the station center is 225, so the adapter spans 217–233 and the land spans 214–236. The cap starts 9.275 above the land, so they do not overlap.
- **Pommel:** 15 + 25 = 40. The PVC runs from 15 to 854, a cut length of 839. The lowest blade point (593.725) is far above the pommel.
- **Top-cap side foam:** 18 − 13.585 = 4.415, as stated.

Both caps are labeled assembly/check envelopes and are excluded from the STLs. Too-small padding is to be handled by changing the geometry and rechecking, not by squeezing larger caps in. I found no contradiction with the lands, the adapters or the cover allowance.

## Metadata and export validation (prior gaps 3 and 4)

**Gap 3 (reference styling under the no-duplicate-coordinates rule) is resolved.**
- SCAD `metadata` mode echoes the derived bounds, station centers, land extents and the axis convention.
- The exporter applies that transform and the native viewBox to dashed DO-NOT-CUT marks.
- Python is explicitly barred from holding its own station constants, outline bounds or mount dimensions.
- The native SVG remains the cut outline.

**Gap 4 (independent scale check) is resolved.**
- The check measures the blade path itself, excluding reference marks, in both the final SVG physical units and the final PDF page coordinates.
- Tolerance is 0.1 mm against 295.275 × 46.5. The 46.5 equals 65 − 18.5.
- Tiled pages are reconstructed from common-origin offsets.
- The required fail-then-pass test corrupts the outline scale while leaving the 100 mm bar unchanged, which proves the check depends on the path and not on the script-drawn bar.

## Residual (non-blocking, already covered by the spec's physical-test gates)

- The cap-to-blade-root clearance is exactly at the 0.5 minimum. Hand-shaped foam could fall short of it; the physical mockup gate covers this.
- The top cap overlaps the pipe by 15 mm versus 25 mm for the pommel, so its retention is less proven. The cap-retention test covers this.
- Neither OpenSCAD's real echo/SVG output nor the PDF path extraction has been run yet; that waits on the implementation plan.

**No supported substantive findings.**

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Concise verdict: all four prior gaps checked against the revised packet text with the arithmetic recomputed (wall 4.915; cover 16.835<18.5; cap 18 vs 18.5; top cap 245.275+15=260.275=854-593.725, +35=295.275; land 214..236 vs cap 245.275; pommel 15+25=40; PVC 839; outline 46.5). No contradictions found; residual risks listed."
    }
  ],
  "changedFiles": [],
  "testsAddedOrUpdated": [],
  "commandsRun": [],
  "validationOutput": [
    "Text-only arithmetic recheck of the packet; all stated dimensions are internally consistent"
  ],
  "residualRisks": [
    "Cap-to-blade-root clearance is exactly the 0.5 minimum; hand-shaped foam tolerance is unverified until the mockup",
    "Top-cap 15mm overlap retention is unproven until the physical test",
    "OpenSCAD echo/SVG behavior and PDF path extraction are not executed; deferred to the implementation plan"
  ],
  "noStagedFiles": true,
  "diffSummary": "No edits; review artifact returned for host persistence at docs/superpowers/reviews/2026-10-03-sauron-mace-spec-review-opus-5-5-followup-1.md",
  "reviewFindings": [
    "No supported substantive findings; prior gaps 1-4 resolved without new contradiction"
  ],
  "manualNotes": "No-tools mode: output file not written directly; host persists this answer. Review is limited to the packet text, not the full spec file or any physical validation."
}
```