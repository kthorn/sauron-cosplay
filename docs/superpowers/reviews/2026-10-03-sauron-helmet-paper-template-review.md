# Sauron paper templates — revision 2 review and verification

2026-10-03. Subject: original provisional paper-fit design drawings, not fitted foam fabrication or protective headgear. Parent authored/refined the documents and drawings; independent reviewer was read-only. No permanent product code or generator was added. SVGs are the retained masters.

## Review routing and scope

- Requester: OpenAI (`PI_PROVIDER=openai-codex`, `PI_MODEL=gpt-6.1-sol`). Required opposite family: Anthropic.
- Paseo agent: `0411aa0d-d3f7-4eac-b6c3-b96a4f0939dc`, cwd `/home/kurtt/sauron-cosplay`; no Git branch/ref/worktree.
- Canonical selection: `claude/claude-opus-5-5`, thinking `medium`, Plan Mode; actual model/effort/mode verified with `paseo inspect`.
- Evidence supplied: exact spec and pattern README, artifact hashes, rendered four-sheet contact image, assembly preview, production-helmet photograph, and parent physical-export verification results. Reviewer used no tools and did not independently open PDFs or confirm hashes.
- Three scrutiny areas: drawing/assembly contracts, child wearability boundaries, and printing/scaling correctness.
- Initial review plus one focused follow-up, same model/effort. First 120-second wait window elapsed while agent remained running with no error or permission request; subsequent waits returned `idle` and actual final responses were consumed. No route substitution.

Initial spec SHA256: `0b8590c9d465c1dcdfc26b38b476de809d3f1a52b45f2434a83e2522084808ef`.
Corrected reviewed spec SHA256: `514c7fe111a717fdbd355d4d9e93409dcb61457c50be77aea3933cac9e3b7f02`.
Corrected reviewed pattern README SHA256: `f367e110d07bfcda0d924104291474c485026230c0f6c42f4f85d6ebf64b5609`.

## Findings and dispositions

1. **L temple-tab placement unspecified — accepted.** A's two blue side boxes now explicitly say “L behind”; sheet 1 specifies a quarter-turn and sheet 5 names those support zones. Both documents state that a rotated 25 × 20 mm half matches the 20 × 25 mm box, attaches directly behind A, and folds toward the band. Fit L before decorative D and keep D off the fold/free band connection. Do not make D the sole support connection. Follow-up: resolved.
2. **G forehead accent slightly covered inner eye corners — verified and fixed.** Parent exact polygon check reproduced the original overlap, then checked the corrected nominal flat placement. Moved G corners `(11,35)` and `(29,35)` inward to `(14,35)` and `(26,35)`, leaving its 40 × 47 mm bounds and anchor unchanged. Both eye polygons now clear it; curved/worn clearance remains unverified. Follow-up: resolved for the drawing, with only about 1 mm nominal inner-corner margin.
3. **Forehead/nose stand-off under-specified — accepted as a practical documentation gap, not proof of physical failure.** Added K's center forming guide and face/band half labels, and B's below-eye forming guide. Documents now instruct adjustable forehead stand-off, upper-only B attachment, free lower B angled forward, physical clearance checks, and retesting tipping when the gap changes. No fixed spacer depth or guaranteed wearability was invented. Follow-up: resolved as a wording issue.

Optional footer concern addressed: caption moved from y=273 to y=269 mm, leaving at least 10.4 mm below its baseline on Letter; ruler unchanged. Other optional refinements were not blockers and did not warrant extra machinery or review rounds.

Terminal reviewer verdict: **“No supported substantive findings.”** Stop the refinement pass. Subsequent status/link/checklist additions are administrative, not changed fabrication geometry.

## Parent executable and visual verification

One-off document verification reused the existing `export.py` `_geometry`, `_segments`, `_bounds`, and `_same_segments` helpers; no parallel permanent SVG/PDF parser was created.

- All 14 distinct pieces matched independently specified flat bounding dimensions. Spire quantities total six; H quantity is six.
- Every cutting path was inside both paper formats: x ≥ 10, x ≤ 200, 30 ≤ y ≤ 253 mm.
- `pdfinfo` confirmed two five-page packs: Letter 215.9 × 279.4 mm and A4 210 × 297 mm.
- Each page of the final merged PDFs was converted with `pdftocairo -svg -f N -l N -noshrink -nocenter`; actual black cutting paths, blue placement paths, green forming guides (normalized into the existing verifier's reference channel), and red calibration paths matched the SVG masters within 0.1 mm. Page dimensions matched within 0.01 mm.
- Every actual PDF ruler measured 100 mm; `pdftotext -layout` confirmed five provisional warnings and five ruler captions in each pack.
- An intentionally copied 90%-scale A outline failed the physical cutting-path comparison while its 100 mm ruler remained unchanged. Original masters/PDFs were not mutated by the probe.
- Separate eye-overlay regression reproduced the old G/eye intersection and confirmed its absence after the inward-corner correction, at nominal flat placement only.
- Masters, both paper-format PDF examples, and assembly preview were rendered and visually inspected; revised support labels/forming guides checked after corrections.
- Final geometry checks and local Markdown link-target checks were rerun after corrections. Mace source/generated files were outside this session's changes; another session independently owns them.

## Reviewed final artifact hashes

| File under `patterns/helmet/` | SHA256 |
|---|---|
| `01-frame.svg` | `af767f6572b9c0734890af57feba7dbcecb2cd3ec6c8a10f723a10159c24d267` |
| `02-face.svg` | `3382725252666c72c9f201cab9dcb63478ff3045fbe153ee0186c93ea1d81522` |
| `03-center-spires.svg` | `dbb1086b69499819ac96594434a216da752934dc15a610ade25f1d5ef8df858a` |
| `04-paired-spires.svg` | `50a0ab4562e5bcb87f186713d14b202100e7bd1f8ca970972d0763f88d0cbb6c` |
| `05-assembly.svg` | `e8821adcfc7a0130f1c3a7f7496c50643de46906950a3c01eefae62f4a33a28b` |
| `helmet-a4.pdf` | `816ec15260dfc9612cf15b0aa74d6644776d33525473bf8debeb7226a0268954` |
| `helmet-letter.pdf` | `7b51f6a6edb09eb445059b762a55add4034b21f2655fb927945136eabe70dca1` |
| `preview.png` | `f3e375338d18b0d90b044d5efdacd2b230ce3d6e872816292a54d29f6426f05b` |

## Remaining limitations

User silhouette approval and paper fitting are pending. Nominal 540 mm circumference and 60 mm eye spacing are not child measurements. Tight nominal overlay clearance, folded support geometry, six-spire balance, and actual nose/shoulder/door clearance require the physical trial. Paper success does not establish EVA stiffness, forming, bond retention, finished weight, heat comfort, or safe impact performance. Do not go straight from this document review to foam construction without those fit checks.
