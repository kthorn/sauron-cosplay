"""Profile and export checks for the alternative blade variants (main tests: ../test_mace.py)."""
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import export_variants  # noqa: E402
from test_mace import inside, intersections  # noqa: E402

ORIGINAL = export_variants.export.SOURCE, export_variants.export._fingerprint

# Openings' axial spans (default mm) and the minimum horizontal foam width beside them.
OPENINGS = {"a-drawing": ([(171, 209), (58, 122)], 14.5), "b-sturdy": ([(176, 208), (62, 118)], 18.5),
            "c-hybrid": ([(176, 208), (62, 118)], 17),
            "d-spiked": ([(176, 208), (62, 118)], 16)}


def widths(points, y):
    xs = sorted(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
                for a, b in zip(points, points[1:] + points[:1]) if (a[1] > y) != (b[1] > y))
    return [xs[i + 1] - xs[i] for i in range(0, len(xs), 2)]


class TestVariants(unittest.TestCase):
    def tearDown(self):
        # use() repoints the shared export module; restore it for ../test_mace.py.
        export_variants.export.SOURCE, export_variants.export._fingerprint = ORIGINAL

    def test_profiles(self):
        for name in export_variants.VARIANTS:
            with self.subTest(name=name):
                export_variants.use(name)
                points = export_variants.export.read_model()["blade_points"]
                self.assertEqual(min(p[0] for p in points), 18.5)
                self.assertEqual(max(p[0] for p in points), 65)
                self.assertEqual(min(p[1] for p in points), 0)
                self.assertAlmostEqual(max(p[1] for p in points), 295.275, places=6)
                self.assertEqual(intersections(points), [])
                for y in [34.1, 45, 55.9, 214.1, 225, 235.9]:
                    for x in [18.6, 25, 30.5]:
                        self.assertTrue(inside((x, y), points), (x, y))
                spans, minimum = OPENINGS[name]
                for low, high in spans:
                    self.assertFalse(inside((19, (low + high) / 2), points), "opening reaches the root")
                    for tenth in range(low * 10 + 5, high * 10 - 4):
                        self.assertGreaterEqual(min(widths(points, tenth / 10)), minimum, (name, tenth / 10))

    def test_saved_exports(self):
        for name in export_variants.VARIANTS:
            with self.subTest(name=name):
                export_variants.export.validate_exports(export_variants.use(name))

    def test_bevel_guides(self):
        """Every pattern sheet carries bevel lines, inset inside the blade and off the root edge."""
        ns = {"svg": export_variants.export.NS}
        for name in export_variants.VARIANTS:
            with self.subTest(name=name):
                out = export_variants.use(name)
                points = export_variants.export.read_model()["blade_points"]
                native = [(x, -y) for x, y in points]
                sheets = sorted((out / "patterns").glob("blade*.svg"))
                self.assertEqual(len(sheets), 5)
                for sheet in sheets:
                    paths = ET.parse(sheet).getroot().findall(".//svg:g[@id='bevel']/svg:path", ns)
                    self.assertEqual(len(paths), 1, sheet.name)
                    self.assertEqual(paths[0].get("stroke"), export_variants.BEVEL_COLOR)
                segments = export_variants.export._segments(paths[0].get("d"))
                self.assertGreater(len(segments), 20)
                for segment in segments:
                    for x, y in segment:
                        self.assertTrue(inside((x, y), native), (name, x, y))
                        self.assertGreater(x, 18.5 + export_variants.BEVEL_WIDTH - .01)

    def test_d_holder_follows_its_blade(self):
        """D's spindle swells over its solid middle root and narrows through the bite."""
        import math
        import tempfile
        export = export_variants.export
        export_variants.use("d-spiked")
        start = export.read_model()["holder_span"][0]
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "holder.stl"
            export.run_scad("holder", target)
            _, contains = export._mesh_geometry(target)
        for i in range(6):
            flat, vertex = math.radians(30 + i*60), math.radians(i*60)
            # Hexagon face distances: 30 mm swell at 150 mm, narrower beside the bite at 205 mm.
            for angle, radius, blade_z, expected in [
                    (flat, 25.7, 150, True), (flat, 26.2, 150, False),
                    (flat, 21.2, 205, True), (flat, 22.0, 205, False),
                    (vertex, 18.3, 150, True), (vertex, 18.7, 150, False),  # middle-root groove
                    (vertex, 25.0, 192, True),  # solid core seen through the bite
                    (vertex, 21.0, 90, False)]:  # 19.5 mm waist inside the lower opening
                point = (radius*math.cos(angle), radius*math.sin(angle), blade_z - start)
                self.assertEqual(contains(point), expected, (i, radius, blade_z))

    def test_blades_clear_their_holder(self):
        """Each variant's foam blades miss its grooved holder (root-face contact excluded)."""
        import os
        import subprocess
        import tempfile
        for name, source in export_variants.VARIANTS.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                scad = Path(directory) / "collision.scad"
                scad.write_text(f'include <{HERE / source}>\nmode="metadata";\nintersection() {{\n'
                                'translate([0,0,holder_start]) holder();\n'
                                'for(i=[0:5]) rotate([0,0,i*60]) translate([.01,0,0]) foam_blade();\n}\n')
                result = subprocess.run([os.environ.get("OPENSCAD", "openscad"), "-o", str(Path(directory) / "c.stl"), str(scad)],
                                        capture_output=True, text=True, timeout=300)
                self.assertIn("empty", result.stderr.lower(), result.stderr)

    def test_scaled_overrides_keep_root_on_bands(self):
        export_variants.use("a-drawing")
        with self.assertRaises(RuntimeError):
            export_variants.export.read_model({"blade_length": 200})
        model = export_variants.export.read_model({"pipe_od": 27, "foam_thickness": 12, "head_radius": 69})
        self.assertEqual(max(p[0] for p in model["blade_points"]), 69)


if __name__ == "__main__":
    unittest.main()
