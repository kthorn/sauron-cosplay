"""Export/verify the alternative blade variants through the unchanged export.py pipeline.

Each variant gets its own output folder (patterns/, prints/) beside this script; the
project's main patterns/ and prints/ are never touched.
"""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import export  # noqa: E402

VARIANTS = {"a-drawing": "blade_a_drawing.scad", "b-sturdy": "blade_b_sturdy.scad",
            "c-hybrid": "blade_c_hybrid.scad", "d-spiked": "blade_d_spiked.scad"}
BEVEL_WIDTH = 6  # mm in from each exposed edge; suits 10 mm foam (about 4 mm removed per face)
BEVEL_COLOR = "#008800"  # not black/blue/red, so export.py's outline verification ignores it
INCLUDED = [HERE.parent / "mace.scad", HERE / "blade_shapes.scad"]


def use(name: str) -> Path:
    """Point export.py at a variant; fingerprint also covers the included SCAD files."""
    source = HERE / VARIANTS[name]
    export.SOURCE = source
    export._fingerprint = lambda: {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                   for path in [source, *INCLUDED, Path(export.__file__).resolve()]}
    return HERE / name


def bevel_lines(defines: dict[str, float] | None, width: float) -> list:
    """Outline inset by `width`, as polylines in native SVG coordinates, minus the root edge.

    The root (mounting) edge sits in the slots and stays square, so inset segments
    running parallel to it are dropped; everything else exposed gets a bevel guide.
    """
    source = export.SOURCE
    with tempfile.TemporaryDirectory(prefix="mace-bevel-") as directory:
        inset = Path(directory) / "bevel.scad"
        inset.write_text(f"include <{source}>\noffset(delta=-{width}) polygon(blade_points);\n")
        target = Path(directory) / "bevel.svg"
        try:
            export.SOURCE = inset  # metadata mode draws nothing itself; only the inset renders
            export.run_scad("metadata", target, defines)
            cad = export.read_model(defines)
        finally:
            export.SOURCE = source
        paths = [path.get("d", "") for path in ET.parse(target).getroot().iter(f"{{{export.NS}}}path")]
    limit = cad["parameters"]["slot_root_radius"] + width + .05
    lines = []
    for segment in (s for d in paths for s in export._segments(d)):
        if max(segment[0][0], segment[1][0]) < limit:
            continue
        if lines and lines[-1][-1] == segment[0]:
            lines[-1].append(segment[1])
        else:
            lines.append(list(segment))
    if not lines:
        raise ValueError("Bevel inset is empty")
    return lines


def add_bevels(lines: list):
    """Wrap export._pattern so every full/tiled SVG (and thus PDF) also carries the bevel guides."""
    original = export._pattern

    def pattern(filename, native_path, view, cad, page=None, all_pages=()):
        result = original(filename, native_path, view, cad, page, all_pages)
        tree = ET.parse(filename)
        root = tree.getroot()
        group = next(g for g in root.iter(f"{{{export.NS}}}g") if any(c.get("id") == "cut" for c in g))
        bevel = export._element(group, "g", id="bevel")
        d = " ".join("M " + " L ".join(f"{x:.4f} {y:.4f}" for x, y in line) for line in lines)
        export._element(bevel, "path", d=d, fill="none", stroke=BEVEL_COLOR, stroke_width=.3, stroke_dasharray="4 1 1 1")
        canvas = [float(v) for v in root.get("viewBox").split()]
        export._text(root, canvas[0]+20, canvas[1]+canvas[3]-6,
                     "GREEN DASH-DOT: bevel guide, NOT a cut (carve both faces).")
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        return result
    export._pattern = pattern
    return original


def preview(name: str) -> None:
    """Assembly PNG beside the variant's patterns (not manifest-owned; regenerated freely)."""
    target = use(name) / "assembly-preview.png"
    command = [os.environ.get("OPENSCAD", "openscad"), "-o", str(target), "-D", 'mode="assembly"',
               "--imgsize=900,1200", "--camera=0,0,0,75,0,30,1000", "--viewall", "--autocenter", "--projection=ortho", "--colorscheme=Tomorrow", str(export.SOURCE)]
    subprocess.run(command, check=True, capture_output=True, env={**os.environ, "QT_QPA_PLATFORM": "offscreen"}, timeout=180)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="*", metavar="NAME", help=f"default: all of {', '.join(VARIANTS)}")
    parser.add_argument("--set", action="append", default=[], metavar="NAME=NUMBER")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--bevel", type=float, default=BEVEL_WIDTH, metavar="MM", help="bevel guide inset (default %(default)s)")
    args = parser.parse_args()
    try:
        defines = {name: float(value) for name, value in (entry.split("=", 1) for entry in args.set)}
        for name in args.names or VARIANTS:
            out = use(name)
            if args.check:
                export.validate_exports(out)
                print(f"Verified {name}: {out}")
            else:
                original = add_bevels(bevel_lines(defines, args.bevel))
                try:
                    manifest = export.build(out, defines)
                finally:
                    export._pattern = original
                preview(name)
                print(f"Verified exports {name}: {out} ({len(manifest['pages'])} PDF pages)")
    except (ValueError, RuntimeError, OSError, ET.ParseError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Variant export/verification failed: {error}\n")


if __name__ == "__main__":
    main()
