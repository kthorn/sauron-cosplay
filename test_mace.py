"""Tests of the actual CAD/render and fabrication-export contracts."""
import importlib.util
import json
import math
import os
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

MODEL_AVAILABLE = importlib.util.find_spec("export") is not None
if MODEL_AVAILABLE:
    import export as model


def inside(point, polygon):
    """Independent ray-crossing check for the foam stock at mounting bands."""
    x, y = point
    hit = False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        if (a[1] > y) != (b[1] > y):
            crossing = a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x < crossing:
                hit = not hit
    return hit


def intersections(points):
    """Non-adjacent crossings/touches, independent of the CAD renderer."""
    def cross(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    edges = list(zip(points, points[1:] + points[:1]))
    found = []
    for i, (a, b) in enumerate(edges):
        for j in range(i + 2, len(edges)):
            if i == 0 and j == len(edges) - 1:
                continue
            c, d = edges[j]
            overlap = all(max(min(a[k], b[k]), min(c[k], d[k])) <= min(max(a[k], b[k]), max(c[k], d[k])) for k in [0, 1])
            if overlap and cross(a, b, c) * cross(a, b, d) <= 0 and cross(c, d, a) * cross(c, d, b) <= 0:
                found.append((i, j))
    return found


class TestCad(unittest.TestCase):
    def setUp(self):
        self.assertTrue(MODEL_AVAILABLE, "CAD/render interface has not been implemented")

    def test_defaults(self):
        m = model.read_model()
        self.assertEqual(m["blade_bounds"], [18.5, 0, 65, 295.275])
        self.assertAlmostEqual(m["bore_diameter"], 27.17, places=3)
        self.assertAlmostEqual(m["slot_width"], 10.5, places=3)
        self.assertEqual(m["stations"], [45, 225])
        self.assertEqual(m["land_bands"], [[34, 56], [214, 236]])
        self.assertEqual(m["pipe_span"], [15, 854])
        self.assertAlmostEqual(m["top_cap_start"], 245.275, places=3)
        self.assertEqual(m["top_cap_radius"], 18)
        self.assertEqual(m["svg_axes"], [1, -1])

    def test_measured_sizes(self):
        m = model.read_model({"pipe_od": 27, "foam_thickness": 12})
        self.assertAlmostEqual(m["bore_diameter"], 27.5, places=3)
        self.assertAlmostEqual(m["slot_width"], 12.5, places=3)
        self.assertAlmostEqual(m["blade_bounds"][3], 295.275, places=3)

    def test_scaled_stations_fixed_lands(self):
        m = model.read_model({"blade_length": 320})
        self.assertAlmostEqual(m["stations"][0], 48.7681, places=3)
        self.assertAlmostEqual(m["stations"][1], 243.8405, places=3)
        for low, high in m["land_bands"]:
            self.assertAlmostEqual(high - low, 22, places=3)
        self.assertGreater(m["top_cap_start"], m["land_bands"][1][1])

    def test_invalid_fit_rejected(self):
        for overrides in [{"pipe_od": 34}, {"foam_thickness": 24}, {"bore_clearance": -.1}]:
            with self.subTest(overrides=overrides):
                with self.assertRaisesRegex(RuntimeError, "Assertion"):
                    model.read_model(overrides)

    def test_short_blade_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "Assertion"):
            model.read_model({"blade_length": 240})

    def test_unknown_and_nonfinite_overrides(self):
        for overrides in [{"piple_od": 27}, {"pipe_od": math.nan}, {"pipe_od": math.inf}]:
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    model.read_model(overrides)

    def test_profile(self):
        points = model.read_model()["blade_points"]
        self.assertGreater(len(points), 8)
        self.assertEqual(min(p[0] for p in points), 18.5)
        self.assertEqual(max(p[0] for p in points), 65)
        self.assertEqual(min(p[1] for p in points), 0)
        self.assertEqual(max(p[1] for p in points), 295.275)
        self.assertEqual(intersections(points), [])
        for y in [34.1, 45, 55.9, 214.1, 225, 235.9]:
            for x in [18.6, 25, 30.5]:
                self.assertTrue(inside((x, y), points), (x, y))
        # Real 2D render catches invalid polygon output, not just echoed data.
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "blade.svg"
            model.run_scad("blade_2d", target)
            self.assertIn("<svg", target.read_text())

    def test_missing_tool(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(os.environ, {"OPENSCAD": str(Path(directory) / "absent")}):
                with self.assertRaisesRegex(RuntimeError, "OpenSCAD"):
                    model.run_scad("metadata", Path(directory) / "m.echo")

    def test_zero_exit_error_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "m.echo"
            target.write_text("not valid model data")
            result = subprocess.CompletedProcess([], 0, "", "ERROR: Assertion failed: probe")
            with patch("export.subprocess.run", return_value=result):
                with self.assertRaisesRegex(RuntimeError, "ERROR: Assertion"):
                    model.run_scad("metadata", target)

    def test_stale_output_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "old.svg"
            target.write_text("old render, not newly produced")
            result = subprocess.CompletedProcess([], 0, "", "")
            with patch("export.subprocess.run", return_value=result):
                with self.assertRaisesRegex(RuntimeError, "no.*output"):
                    model.run_scad("blade_2d", target)

    def test_tapered_holder_sections_keep_scale_and_fit_mini(self):
        # Catches double-scaling, a longitudinal split, missing tapers or bore,
        # and export of assembly coordinates instead of bed coordinates.
        cad = model.read_model()
        self.assertEqual(cad["blade_bounds"], [18.5, 0, 65, 295.275])
        self.assertEqual(cad["stations"], [45, 225])
        self.assertEqual(cad["holder_span"], [37, 283.275])
        self.assertAlmostEqual(cad["holder_split"], 160.1375, delta=.001)
        with tempfile.TemporaryDirectory() as directory:
            for part in ["lower", "upper"]:
                target = Path(directory) / f"holder-{part}.stl"
                model.run_scad(f"holder_{part}", target)
                vertices = [tuple(map(float, v)) for v in re.findall(
                    r"vertex\s+([-+\d.eE]+)\s+([-+\d.eE]+)\s+([-+\d.eE]+)", target.read_text())]
                self.assertTrue(vertices)
                bounds = [max(v[i] for v in vertices)-min(v[i] for v in vertices) for i in range(3)]
                self.assertAlmostEqual(bounds[2], 123.1375 + (6 if part == "lower" else 0), delta=.01)  # lower pins
                self.assertLessEqual(max(bounds), 175)  # room for a brim on 180 mm bed
                self.assertAlmostEqual(min(v[2] for v in vertices), 0, places=3)
                bore_vertices = [v for v in vertices if v[2] < 90]
                self.assertAlmostEqual(min(math.hypot(v[0], v[1]) for v in bore_vertices), 13.585, places=3)
                _, contains = model._mesh_geometry(target)
                self.assertEqual(contains((0, 0, bounds[2]-1)), part == "upper")
                model._holder_mesh(target, cad, part)
            whole = Path(directory) / "holder.stl"
            model.run_scad("holder", whole)
            model._holder_mesh(whole, cad, "whole")
            # Test the full foam insertion path, excluding nominal root-face
            # contact: CGAL retains zero-volume sheets at exactly 18.5 mm.
            collision = Path(directory) / "collision.stl"
            source = Path(directory) / "collision.scad"
            source.write_text(f'use <{model.SOURCE}>\nintersection() {{\n'
                              'translate([0,0,37]) holder();\n'
                              'for(i=[0:5]) rotate([0,0,i*60]) translate([.01,0,0]) foam_blade();\n}\n')
            result = subprocess.run([os.environ.get("OPENSCAD", "openscad"), "-o", str(collision), str(source)],
                                    capture_output=True, text=True, timeout=120)
            self.assertIn("empty", result.stderr.lower(), result.stderr)
            self.assertFalse(collision.exists())

    def test_holder_sections_have_alignment_pins(self):
        # Lower top face carries three printed pins; upper bed face has
        # matching clearance holes. Both print upright without supports.
        cad = model.read_model()
        circle, diameter, length, clearance = cad["holder_pins"]
        half = (cad["holder_span"][1]-cad["holder_span"][0])/2
        with tempfile.TemporaryDirectory() as directory:
            for part in ["lower", "upper"]:
                target = Path(directory) / f"holder-{part}.stl"
                model.run_scad(f"holder_{part}", target)
                _, contains = model._mesh_geometry(target)
                for i in range(3):
                    angle = math.radians(30+i*120)  # hexagon flats, clear of vertex grooves
                    def at(radius, z):
                        return contains((radius*math.cos(angle), radius*math.sin(angle), z))
                    if part == "lower":
                        self.assertTrue(at(circle, half+length/2))
                        self.assertFalse(at(circle+diameter/2+.3, half+length/2))
                    else:
                        self.assertFalse(at(circle+diameter/2+clearance/2-.1, length/2))
                        self.assertTrue(at(circle+diameter/2+clearance/2+.3, length/2))
                        self.assertTrue(at(circle, length+1))  # blind hole
                model._holder_mesh(target, cad, part)

    def test_holder_wrong_channel_width_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "holder-lower.stl"
            for height in [16, 6]:  # thin mounting band cannot supply a width probe
                cad = model.read_model({"adapter_height": height})
                for thickness in [8.5, 12]:  # actual widths 9.0 and 12.5 vs required 10.5
                    with self.subTest(height=height, thickness=thickness):
                        model.run_scad("holder_lower", target, {"adapter_height": height, "foam_thickness": thickness})
                        with self.assertRaisesRegex(ValueError, "slot|channel"):
                            model._holder_mesh(target, cad, "lower")

    def test_holder_unverifiable_width_rejected(self):
        settings = {"adapter_od": 48.4, "foam_thickness": 20, "pin_d": 3, "pin_clearance": .2}
        cad = model.read_model(settings)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "holder-lower.stl"
            model.run_scad("holder_lower", target, settings)
            with self.assertRaisesRegex(ValueError, "verify channel width"):
                model._holder_mesh(target, cad, "lower")

    def test_hexagon_vertices_and_guarded_round_crown(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "holder.stl"
            model.run_scad("holder", target)
            vertices, contains = model._mesh_geometry(target)
            # Reference spindle: one 30 mm hexagonal swell (face 25.981 mm from
            # axis; a dodecagon would be 30 mm) above a 19.5 mm waist.
            for i in range(6):
                angle = math.radians(30+i*60)
                for radius, z, expected in [(25.7, 168, True), (26.2, 168, False),
                                            (16.6, 51, True), (17.2, 51, False)]:
                    self.assertEqual(contains((radius*math.cos(angle), radius*math.sin(angle), z)), expected)
                angle -= math.pi/6
                # Grooves follow each blade's inner edge, only where it meets
                # the core: lower land, upper swell, and solid in between.
                for radius, z, expected in [(18.3, 8, True), (18.7, 8, False),
                                            (22.0, 168, True), (23.0, 168, False),
                                            (22.5, 95, True)]:
                    self.assertEqual(contains((radius*math.cos(angle), radius*math.sin(angle), z)), expected, (radius, z))
            # Full print starts 37 mm above blade base. The pointed tip ends
            # 12 mm short of the 295.275 mm EVA tips; no PVC cut changes.
            self.assertAlmostEqual(max(v[2] for v in vertices), 246.275, delta=.01)
            self.assertTrue(contains((0, 0, 245.9)))
            self.assertFalse(contains((0, 0, 246.5)))
            self.assertFalse(contains((0, 0, 223)))  # PVC endpoint inside bore
            self.assertFalse(contains((0, 0, 225)))  # 45-degree internal ceiling, not a flat bridge
            self.assertFalse(contains((0, 0, 234)))
            self.assertTrue(contains((4, 0, 234)))
            self.assertTrue(contains((0, 0, 239)))  # solid above the ceiling apex
            # Pointed hexagonal apex, no ball: 1.95 mm vertex radius 2 mm below it.
            self.assertTrue(contains((1.5, 0, 244.275)))
            self.assertFalse(contains((2.2, 0, 244.275)))

    def test_assembly_renders(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "assembly.csg"
            model.run_scad("assembly", target)
            self.assertGreater(target.stat().st_size, 100)


class TestExports(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not hasattr(model, "build") or not hasattr(model, "validate_exports"):
            return
        cls.template = tempfile.TemporaryDirectory(prefix="mace-test-template-")
        cls.addClassCleanup(cls.template.cleanup)
        cls.manifest = model.build(Path(cls.template.name))

    def setUp(self):
        self.assertTrue(hasattr(model, "build") and hasattr(model, "validate_exports"),
                        "Export build/verification interface has not been implemented")
        directory = tempfile.TemporaryDirectory(prefix="mace-test-")
        self.addCleanup(directory.cleanup)
        self.parent = Path(directory.name)
        self.root = self.parent / "outputs with spaces"
        shutil.copytree(self.template.name, self.root)

    def shrink_cut(self, filename):
        tree = ET.parse(filename)
        cut = tree.find(".//*[@id='cut']")
        self.assertIsNotNone(cut)
        cut.set("transform", "scale(0.9)")
        tree.write(filename, encoding="unicode")

    def test_default_exports(self):
        result = model.build(self.root)
        model.validate_exports(self.root)
        self.assertEqual(result["cad"]["blade_bounds"], [18.5, 0, 65, 295.275])
        for filename in ["patterns/blade.svg", "prints/adapter.stl", "prints/fit-coupon.stl"]:
            self.assertTrue((self.root / filename).is_file())
        self.assertEqual({p["format"] for p in result["pages"]}, {"a4", "letter"})
        for page in result["pages"]:
            self.assertEqual(page["size_mm"], {"a4": [210, 297], "letter": [215.9, 279.4]}[page["format"]])
        self.assertEqual(len(result["pages"]), 4)

    def test_holder_exports_and_corruption(self):
        for part in ["lower", "upper"]:
            self.assertTrue((self.root / f"prints/holder-{part}.stl").is_file())
        # Catches a rescaled mesh via the bore/envelope checks.
        target = self.root / "prints/holder-lower.stl"
        target.write_text(re.sub(r"vertex\s+([-+\d.eE]+)\s+([-+\d.eE]+)\s+([-+\d.eE]+)",
                                lambda m: f"vertex {float(m[1])*1.1} {float(m[2])*1.1} {m[3]}",
                                target.read_text()))
        with self.assertRaisesRegex(ValueError, "STL|holder"):
            model.validate_exports(self.root)

    def test_svg_scale_corruption(self):
        filename = self.root / "patterns/blade.svg"
        before = ET.parse(filename).find(".//*[@id='calibration']").attrib.copy()
        self.shrink_cut(filename)
        after = ET.parse(filename).find(".//*[@id='calibration']").attrib
        self.assertEqual(after, before)  # bar is untouched, outline alone is wrong
        with self.assertRaisesRegex(ValueError, "SVG.*outline"):
            model.validate_exports(self.root)

    def test_pdf_scale_corruption(self):
        import cairosvg
        page = self.manifest["pages"][0]
        alternate = self.parent / "changed-outline.svg"
        shutil.copyfile(self.root / page["svg"], alternate)
        self.shrink_cut(alternate)
        cairosvg.svg2pdf(url=str(alternate), write_to=str(self.root / page["pdf"]))
        with self.assertRaisesRegex(ValueError, "PDF.*outline"):
            model.validate_exports(self.root)

    def test_missing_pdf_tool(self):
        previous = {name: (self.root / name).read_bytes() for name in self.manifest["owned"]}
        with patch.dict(os.environ, {"PDFTOCAIRO": str(self.parent / "absent tool")}):
            with self.assertRaisesRegex(RuntimeError, "pdftocairo"):
                model.build(self.root, {"pipe_od": 27})
        self.assertEqual(previous, {name: (self.root / name).read_bytes() for name in previous})
        fresh = self.parent / "fresh"
        with patch.dict(os.environ, {"PDFTOCAIRO": str(self.parent / "absent tool")}):
            with self.assertRaises(RuntimeError):
                model.build(fresh)
        self.assertFalse((fresh / "patterns/manifest.json").exists())

    def test_stl_contamination(self):
        mesh = self.root / "prints/adapter.stl"
        original = mesh.read_bytes()
        mesh.unlink()
        with self.assertRaisesRegex(ValueError, "missing|Missing"):
            model.validate_exports(self.root)
        mesh.write_bytes(original)
        # Closed, disconnected tetrahedron: genuine triangles, not an empty marker.
        points = [(80, 0, 0), (81, 0, 0), (80, 1, 0), (80, 0, 1)]
        extra = "\nsolid contaminant\n"
        for face in [(0, 2, 1), (0, 1, 3), (1, 2, 3), (2, 0, 3)]:
            extra += "facet normal 0 0 0\nouter loop\n"
            extra += "".join("vertex %s %s %s\n" % points[i] for i in face)
            extra += "endloop\nendfacet\n"
        mesh.write_text(original.decode() + extra + "endsolid contaminant\n")
        with self.assertRaisesRegex(ValueError, "mesh|STL"):
            model.validate_exports(self.root)
        # Real assembly must never be accepted as an adapter mesh.
        model.run_scad("assembly", mesh)
        with self.assertRaisesRegex(ValueError, "mesh|STL"):
            model.validate_exports(self.root)

    def test_bore_size_corruption(self):
        mesh = self.root / "prints/adapter.stl"
        def widen(match):
            x, y, z = map(float, match.groups())
            radius = math.hypot(x, y)
            if 0 < radius < 15:
                x, y = x*(radius+.1)/radius, y*(radius+.1)/radius
            return f"vertex {x} {y} {z}"
        mesh.write_text(re.sub(r"vertex\s+([-+\d.eE]+)\s+([-+\d.eE]+)\s+([-+\d.eE]+)", widen, mesh.read_text()))
        with self.assertRaisesRegex(ValueError, "STL.*bore"):
            model.validate_exports(self.root)

    def test_calibration_bar_shape_corruption(self):
        filename = self.root / "patterns/blade.svg"
        tree = ET.parse(filename)
        # Same 100 mm X span, but a diagonal is not a 100 mm ruler bar.
        tree.find(".//*[@id='calibration']").set("d", "M 28 12 L 128 22")
        tree.write(filename, encoding="unicode")
        with self.assertRaisesRegex(ValueError, "calibration bar"):
            model.validate_exports(self.root)

    def test_band_reference_corruption(self):
        filename = self.root / "patterns/blade.svg"
        tree = ET.parse(filename)
        band = next(e for e in tree.findall(".//*[@stroke='#0066cc']") if e.get("d", "").strip().endswith("Z"))
        band.set("transform", "translate(0 1)")
        tree.write(filename, encoding="unicode")
        with self.assertRaisesRegex(ValueError, "mounting reference"):
            model.validate_exports(self.root)

    def test_stations_on_pages(self):
        seen = set()
        for page in self.manifest["pages"]:
            tree = ET.parse(self.root / page["svg"])
            for line in tree.findall(".//*[@data-station]"):
                station = float(line.get("data-station"))
                self.assertIn("stroke-dasharray", line.attrib)
                self.assertNotEqual(line.get("stroke"), "#000000")
                numbers = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", line.get("d"))]
                self.assertEqual(numbers[1], -station)
                y_on_page = numbers[1] - page["origin"][1] + 25
                if 25 <= y_on_page <= page["size_mm"][1] - 30:
                    seen.add((page["format"], station))
        self.assertEqual(seen, {("a4", 45), ("a4", 225), ("letter", 45), ("letter", 225)})
        model.validate_exports(self.root)  # real SVG AND PDF reference placement

    def test_wide_head_labels_fit(self):
        import io
        import cairosvg
        from PIL import Image
        result = model.build(self.root, {"head_radius": 185})
        # Rasterize real text: a label cropped at the right edge leaves ink in
        # this 5 mm border. Expectations do not reuse exporter text metrics.
        image = Image.open(io.BytesIO(cairosvg.svg2png(url=str(self.root / "patterns/blade.svg"), background_color="white"))).convert("RGB")
        border = image.crop((image.width-19, 0, image.width, image.height))
        pixels = border.load()
        self.assertFalse(any(min(pixels[x, y]) < 240 for y in range(border.height) for x in range(border.width)), "full SVG clips right-side labels")
        right = result["full_svg"]["origin"][0]+result["full_svg"]["size_mm"][0]-10
        for paper in ["a4", "letter"]:
            coverage = max(p["origin"][0]+p["size_mm"][0]-20 for p in result["pages"] if p["format"] == paper)
            self.assertGreaterEqual(coverage, right)

    def test_page_count_changes(self):
        long = model.build(self.root, {"head_radius": 185})
        self.assertGreater(len(long["pages"]), 4)
        note = self.root / "patterns/my-notes.txt"
        note.write_text("keep me")
        short = model.build(self.root)
        self.assertEqual(len(short["pages"]), 4)
        for name in set(long["owned"]) - set(short["owned"]):
            self.assertFalse((self.root / name).exists(), name)
        self.assertEqual(note.read_text(), "keep me")
        model.validate_exports(self.root)

    def test_oversize_holder_rejected_before_publication(self):
        previous = {name: (self.root / name).read_bytes() for name in self.manifest["owned"]}
        with self.assertRaisesRegex(ValueError, "A1 mini"):
            model.build(self.root, {"blade_length": 700})
        self.assertEqual(previous, {name: (self.root / name).read_bytes() for name in previous})

    def test_paths_and_cwd(self):
        elsewhere = self.parent / "different cwd"
        elsewhere.mkdir()
        result = subprocess.run([sys.executable, str(Path(model.__file__).resolve()),
                                 "--out", str(self.root), "--set", "pipe_od=27", "--set", "foam_thickness=12"],
                                cwd=elsewhere, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, str(Path(model.__file__).resolve()), "--check", "--out", str(self.root)],
                                cwd=elsewhere, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(elsewhere.iterdir()), [])
        cad = json.loads((self.root / "patterns/manifest.json").read_text())["cad"]
        self.assertEqual(cad["bore_diameter"], 27.5)
        self.assertEqual(cad["slot_width"], 12.5)

    def test_unsafe_manifest_paths(self):
        victim = self.parent / "keep-me.txt"
        victim.write_text("untouched")
        manifest_path = self.root / "patterns/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["owned"].append("../keep-me.txt")
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "path|Path"):
            model.build(self.root)
        self.assertEqual(victim.read_text(), "untouched")

    def test_unowned_collision_not_overwritten(self):
        fresh = self.parent / "unowned"
        (fresh / "patterns").mkdir(parents=True)
        target = fresh / "patterns/blade.svg"
        target.write_text("my hand-made pattern")
        with self.assertRaisesRegex(ValueError, "unowned|overwrite"):
            model.build(fresh)
        self.assertEqual(target.read_text(), "my hand-made pattern")


if __name__ == "__main__":
    unittest.main(verbosity=2)
