# PDF/SVG cutting-path probe

## Environment and exact probe

Versions: `python3` with CairoSVG 2.9.0, Pillow 12.2.0, NumPy 1.26.3; `pdftocairo -v` = Poppler 24.02.0; `openscad --version` = OpenSCAD 2021.01. Commands used:

```sh
T=$(mktemp -d)
python3 -c 'import cairosvg; cairosvg.svg2pdf(url="'$T'/probe.svg",write_to="'$T'/probe.pdf")'
pdftocairo -svg "$T/probe.pdf" "$T/out.svg"
```

Throwaway artifacts were `/tmp/tmp.thbozHqaGu/probe.svg`, `probe.pdf`, and `out.svg` (not product files). The source was A4 `width="210mm" height="297mm" viewBox="0 0 210 297"`, with white background, this transformed black cut:

```svg
<g id="cut" transform="translate(100 80) scale(0.9) translate(-20 -12.5)" clip-path="url(#pageclip)">
 <path id="cutpath" d="M 0 0 L 40 0 L 40 25 L 0 25 Z"
       fill="none" stroke="#000" stroke-width="0.3"/>
</g>
<path id="outside" d="M205 290 L220 290 L220 305 L205 305 Z"
      fill="none" stroke="#000" stroke-width="0.3" clip-path="url(#pageclip)"/>
<path id="ref" d="M20 120 H190 V130 H20 Z" fill="none"
      stroke="#0066ff" stroke-width="0.2" stroke-dasharray="2,2"/>
<path id="bar" d="M20 160 H120" fill="none" stroke="#ff0000" stroke-width="0.5"/>
```

## Measured behavior

The A4 round trip emits `width="595.275591" height="841.889764" viewBox="0 0 595.275591 841.889764"` (72 points/inch, 25.4 mm/inch). Letter (`215.9mm x 279.4mm`) emits exactly `612 x 792` points. Use `mm = points * 25.4 / 72`; do not infer scale from arbitrary path coordinates. The emitted SVG uses top-down Y coordinates. CairoSVG/Poppler may add a near-identity page matrix; in this run it was `matrix(0.998785,0,0,0.998785,0,0.456587)`, so apply all matrices before measuring.

The scaled cut centerline in emitted SVG was `M 232.442679 ... L 334.488586 ... L ... 258.658581 ...`, with the matrix above: approximately 101.92 x 63.70 points = **35.97 x 22.47 mm**, as expected for 40 x 25 mm at 0.9 (small rounding/page-matrix differences). The red bar remained approximately 99.9 mm. Thus a 0.9 cut scale with an apparently correct 100 mm calibration bar is detectable by comparing independent known geometry; trusting the bar alone is insufficient. A 0.1 mm acceptance limit requires comparing measured nominal cut dimensions to CAD dimensions in mm, not merely checking page/bar dimensions.

The outside black path remains in the emitted SVG with full coordinates extending beyond page bounds (`x` through approximately 623.6 points), but is enclosed by a clip path whose visible page-edge region is retained. Therefore extraction must honor clip regions; do not assume paths are already clipped.

## Recommended narrow validator

1. Parse only the `pdftocairo -svg` XML and its `<path>` elements (including paths under groups); read root point dimensions and convert points to mm with `25.4/72`.
2. Select explicit cut styling: black stroke (`rgb(0%, 0%, 0%)` or equivalent), `fill="none"`, and expected stroke width. Exclude `<defs>`/glyph definitions and all non-black paths. Better: make every annotation a non-black color in source; PDF->SVG does not preserve source IDs reliably, so black annotations are inherently ambiguous and should reject/flag rather than silently count.
3. Recursively compose every group/path `transform` (matrix, translate, scale, rotate); transform all path geometry and stroke width. Handle at least emitted `M`, `L`, `H`, `V`, `C`, `S`, `Q`, `T`, `A`, and `Z`; curves/arcs need extrema (or a conservative flattening tolerance), not just endpoint bounds. Include stroke half-width in bounds.
4. Intersect bounds with applicable `clipPath` geometry before page/tile bounds. Since full out-of-page paths survive, clipping is mandatory. For tiled validation, transform common tile origin and overlap consistently, then compare each cut component against CAD expected bounds with absolute error <=0.1 mm (and reject scale drift independently using multiple known dimensions, e.g. cut geometry plus 100 mm red bar).

This proves feasibility of measuring vector bounds; it does not claim physical print fit or printer accuracy.