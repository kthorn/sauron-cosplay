"""Render and verify the OpenSCAD source; no duplicated blade coordinates."""
import argparse
from collections import defaultdict
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import cairosvg

SOURCE = Path(__file__).resolve().with_name("mace.scad")


def run_scad(mode: str, destination: Path, defines: dict[str, float] | None = None) -> None:
    destination = Path(destination)
    command = [os.environ.get("OPENSCAD", "openscad"), "-o", str(destination), "-D", f'mode="{mode}"']
    if destination.suffix == ".stl":
        command += ["--export-format", "asciistl"]
    for name, value in (defines or {}).items():
        if not re.fullmatch(r"[A-Za-z_]\w*", name) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"Invalid numeric parameter: {name}={value!r}")
        command += ["-D", f"{name}={value!r}"]
    command.append(str(SOURCE))
    environment = {**os.environ, "QT_QPA_PLATFORM": "offscreen"}
    prior_stamp = destination.stat().st_mtime_ns if destination.exists() else None
    try:
        result = subprocess.run(command, capture_output=True, text=True, env=environment, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(f"OpenSCAD could not render {mode}: {error}") from error
    diagnostic = result.stdout + result.stderr
    if destination.suffix == ".echo" and destination.exists():
        diagnostic += destination.read_text()
    if result.returncode or "ERROR:" in diagnostic:
        raise RuntimeError(f"OpenSCAD {mode}: {diagnostic.strip()}")
    if not destination.exists() or not destination.stat().st_size or destination.stat().st_mtime_ns == prior_stamp:
        raise RuntimeError(f"OpenSCAD produced no new {mode} output: {diagnostic.strip()}")


def read_model(defines: dict[str, float] | None = None) -> dict:
    with tempfile.TemporaryDirectory(prefix="mace-metadata-") as directory:
        target = Path(directory) / "model.echo"
        run_scad("metadata", target, defines)
        records = [json.loads(line.removeprefix("ECHO: ")) for line in target.read_text().splitlines() if line.startswith("ECHO: ")]
    tagged = [record for record in records if isinstance(record, list) and record and record[0] == "MACE_META"]
    if len(tagged) != 1:
        raise RuntimeError("OpenSCAD metadata missing or ambiguous")
    metadata = dict(tagged[0][1:])
    metadata["parameters"] = dict(metadata["parameters"])
    unknown = set(defines or {}) - metadata["parameters"].keys()
    if unknown:
        raise ValueError(f"Unknown model parameter(s): {', '.join(sorted(unknown))}")
    return metadata


NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)
PAPERS = {"a4": [210, 297], "letter": [215.9, 279.4]}
MARGIN, TOP, BOTTOM, OVERLAP, TOLERANCE = 10, 25, 30, 10, .1
ANNOTATION_GUTTER = 100  # Full-canvas space after outline, including margins.
NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
IDENTITY = (1, 0, 0, 1, 0, 0)


def _multiply(m, n):
    a, b, c, d, e, f = m
    g, h, i, j, k, l = n
    return (a*g+c*h, b*g+d*h, a*i+c*j, b*i+d*j, a*k+c*l+e, b*k+d*l+f)


def _point(m, p):
    a, b, c, d, e, f = m
    return (a*p[0]+c*p[1]+e, b*p[0]+d*p[1]+f)


def _matrix(text):
    result = IDENTITY
    parts = list(re.finditer(r"([a-zA-Z]+)\s*\(([^)]*)\)", text))
    if re.sub(r"([a-zA-Z]+)\s*\(([^)]*)\)", "", text).strip(" ,\t\n"):
        raise ValueError(f"Unsupported SVG transform: {text}")
    for part in parts:
        name, values = part[1], [float(v) for v in re.findall(NUMBER, part[2])]
        if name == "matrix" and len(values) == 6:
            m = tuple(values)
        elif name == "translate" and len(values) in [1, 2]:
            m = (1, 0, 0, 1, values[0], values[1] if len(values) == 2 else 0)
        elif name == "scale" and len(values) in [1, 2]:
            m = (values[0], 0, 0, values[-1], 0, 0)
        elif name == "rotate" and len(values) in [1, 3]:
            angle = math.radians(values[0])
            m = (math.cos(angle), math.sin(angle), -math.sin(angle), math.cos(angle), 0, 0)
            if len(values) == 3:
                x, y = values[1:]
                m = _multiply((1, 0, 0, 1, x, y), _multiply(m, (1, 0, 0, 1, -x, -y)))
        else:
            raise ValueError(f"Unsupported SVG transform: {text}")
        result = _multiply(result, m)
    return result


def _segments(data):
    # Only straight cutting/reference paths are generated. Reject curves rather
    # than silently measuring endpoints or implementing a generic SVG parser.
    tokens = re.findall(r"[A-Za-z]|" + NUMBER, data)
    result, p, start, command, i = [], (0, 0), (0, 0), None, 0
    while i < len(tokens):
        if tokens[i].isalpha():
            command = tokens[i]
            i += 1
        if command is None or command.upper() not in ["M", "L", "H", "V", "Z"]:
            raise ValueError(f"Unsupported cutting/reference path command: {command}")
        kind, relative = command.upper(), command.islower()
        if kind == "Z":
            q = start
            command = None
        else:
            count = 2 if kind in ["M", "L"] else 1
            try:
                values = [float(v) for v in tokens[i:i+count]]
                if len(values) != count:
                    raise ValueError("truncated path")
            except ValueError as error:
                raise ValueError("Malformed straight SVG path") from error
            i += count
            if kind in ["M", "L"]:
                q = tuple(values[k] + (p[k] if relative else 0) for k in [0, 1])
            elif kind == "H":
                q = (values[0] + (p[0] if relative else 0), p[1])
            else:
                q = (p[0], values[0] + (p[1] if relative else 0))
        if kind == "M":
            start = q
            command = "l" if relative else "L"
        elif math.dist(p, q) > 1e-7:
            result.append((p, q))
        p = q
    return result


def _clip(segment, box):
    a, b = segment
    dx, dy = b[0]-a[0], b[1]-a[1]
    low, high = 0., 1.
    for p, q in [(-dx, a[0]-box[0]), (dx, box[2]-a[0]), (-dy, a[1]-box[1]), (dy, box[3]-a[1])]:
        if abs(p) < 1e-12:
            if q < -1e-8:
                return None
        elif p < 0:
            low = max(low, q/p)
        else:
            high = min(high, q/p)
    if high-low <= 1e-8:
        return None
    return ((a[0]+low*dx, a[1]+low*dy), (a[0]+high*dx, a[1]+high*dy))


def _bounds(segments):
    points = [p for segment in segments for p in segment]
    if not points:
        raise ValueError("Missing outline/ink geometry")
    return [min(p[0] for p in points), min(p[1] for p in points), max(p[0] for p in points), max(p[1] for p in points)]


def _color(value):
    value = value.replace(" ", "").lower()
    if value == "black":
        value = "#000000"
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        value = "#" + "".join(c*2 for c in value[1:])
    if re.fullmatch(r"#[0-9a-f]{6}", value):
        rgb = tuple(int(value[i:i+2], 16) for i in [1, 3, 5])
    elif re.fullmatch(r"rgb\([\d.%]+,[\d.%]+,[\d.%]+\)", value):
        # Poppler quantizes PDF colors (e.g. 79.998779%, not literal 80%).
        rgb = tuple(round(float(c.rstrip("%"))*(2.55 if c.endswith("%") else 1)) for c in value[4:-1].split(","))
    else:
        return None
    return {(0, 0, 0): "black", (0, 102, 204): "blue", (204, 0, 0): "red"}.get(rgb)


def _geometry(filename, pdf=False):
    root = ET.parse(filename).getroot()
    def mm(value):
        match = re.fullmatch(f"({NUMBER})(mm|pt)?", value)
        if not match:
            raise ValueError(f"Unsupported SVG physical unit: {value}")
        factor = 1 if match[2] == "mm" else 25.4/72 if pdf or match[2] == "pt" else 25.4/96
        return float(match[1]) * factor
    size = [mm(root.get(key, "")) for key in ["width", "height"]]
    view = [float(v) for v in root.get("viewBox", "").split()]
    if len(view) != 4 or min(size + view[2:]) <= 0:
        raise ValueError("Invalid SVG canvas")
    sx, sy = size[0]/view[2], size[1]/view[3]
    if abs(sx-sy) > 1e-7:
        raise ValueError("SVG outline canvas aspect/scale mismatch")
    matrix = (sx, 0, 0, sy, -view[0]*sx, -view[1]*sy)
    clips = {e.get("id"): e for e in root.iter() if e.tag == f"{{{NS}}}clipPath"}
    ink = {color: [] for color in ["black", "blue", "red"]}

    def walk(element, parent_matrix, box, inherited):
        tag = element.tag.rsplit("}", 1)[-1]
        if tag in ["defs", "clipPath"]:
            return
        style = {**inherited, **element.attrib}
        style.update(dict(item.split(":", 1) for item in element.get("style", "").split(";") if ":" in item))
        style = {k.strip(): v.strip() for k, v in style.items()}
        if style.get("display") == "none" or style.get("visibility") == "hidden" or float(style.get("opacity", "1")) == 0:
            return
        m = _multiply(parent_matrix, _matrix(element.get("transform", "")))
        clip = element.get("clip-path", "")
        if clip:
            match = re.fullmatch(r"url\(#([^)]*)\)", clip)
            if not match or match[1] not in clips:
                raise ValueError("Unsupported SVG clip reference")
            points = []
            for shape in clips[match[1]]:
                sm = _multiply(m, _matrix(shape.get("transform", "")))
                if shape.tag.endswith("}rect"):
                    x, y = float(shape.get("x", "0")), float(shape.get("y", "0"))
                    w, h = float(shape.get("width")), float(shape.get("height"))
                    points += [_point(sm, p) for p in [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]]
                elif shape.tag.endswith("}path"):
                    points += [_point(sm, p) for s in _segments(shape.get("d", "")) for p in s]
                else:
                    raise ValueError("Unsupported SVG clipping shape")
            if not points:
                raise ValueError("Empty SVG clip")
            bounds = [min(p[0] for p in points), min(p[1] for p in points), max(p[0] for p in points), max(p[1] for p in points)]
            if any(min(abs(p[0]-bounds[0]), abs(p[0]-bounds[2])) > .01 or min(abs(p[1]-bounds[1]), abs(p[1]-bounds[3])) > .01 for p in points):
                raise ValueError("Only rectangular generated SVG clips are supported")
            box = [max(box[0], bounds[0]), max(box[1], bounds[1]), min(box[2], bounds[2]), min(box[3], bounds[3])]
        color = _color(style.get("stroke", "none"))
        if tag == "path" and color and style.get("fill", "black") == "none" and float(style.get("stroke-opacity", "1")) > 0:
            for segment in _segments(element.get("d", "")):
                clipped = _clip(tuple(_point(m, p) for p in segment), box)
                if clipped:
                    ink[color].append(clipped)
        for child in element:
            walk(child, m, box, style)
    walk(root, matrix, [0, 0, *size], {})
    return size, ink


def _same_segments(actual, expected):
    remaining = list(expected)
    for a, b in actual:
        match = next((i for i, (c, d) in enumerate(remaining)
                      if (math.dist(a, c) <= TOLERANCE and math.dist(b, d) <= TOLERANCE)
                      or (math.dist(a, d) <= TOLERANCE and math.dist(b, c) <= TOLERANCE)), None)
        if match is None:
            return False
        remaining.pop(match)
    return not remaining


def _full_width(view):
    return max(150, view[2]+ANNOTATION_GUTTER)


def _pages(view):
    pages = []
    for name, size in PAPERS.items():
        width, height = size[0]-2*MARGIN, size[1]-TOP-BOTTOM
        cols = max(1, math.ceil((_full_width(view)-2*MARGIN-width)/(width-OVERLAP))+1)
        rows = max(1, math.ceil((view[3]-height)/(height-OVERLAP))+1)
        for row in range(rows):
            for col in range(cols):
                number = row*cols+col+1
                prefix = f"patterns/blade-{name}-{number:02d}"
                pages.append({"format": name, "size_mm": size, "origin": [view[0]+col*(width-OVERLAP), view[1]+row*(height-OVERLAP)],
                              "row": row, "column": col, "number": number, "count": rows*cols,
                              "svg": prefix+".svg", "pdf": prefix+".pdf"})
    return pages


def _element(parent, tag, **attributes):
    return ET.SubElement(parent, f"{{{NS}}}{tag}", {key.replace("_", "-"): str(value) for key, value in attributes.items()})


def _text(parent, x, y, text):
    element = _element(parent, "text", x=x, y=y, fill="#666666", font_size=3.2, font_family="sans-serif")
    element.text = text


def _references(parent, cad):
    p, axes = cad["parameters"], cad["svg_axes"]
    left, right = p["slot_root_radius"]*axes[0], (p["head_radius"]+2)*axes[0]
    for station, band in zip(cad["stations"], cad["land_bands"]):
        y = station*axes[1]
        line = _element(parent, "path", d=f"M {left} {y} L {right} {y}", fill="none", stroke="#0066cc", stroke_width=.25, stroke_dasharray="2 2")
        line.set("data-station", str(station))
        _text(parent, right+2, y-1, f"Adapter center: {station:g} mm")
        a, b, edge = band[0]*axes[1], band[1]*axes[1], cad["adapter_radius"]*axes[0]
        _element(parent, "path", d=f"M {left} {a} L {edge} {a} L {edge} {b} L {left} {b} Z", fill="none", stroke="#0066cc", stroke_width=.25, stroke_dasharray="2 2")
    _text(parent, right+2, cad["stations"][0]*axes[1]+5, "Dashed boxes: seating bands; DO NOT CUT")


def _pattern(filename, native_path, view, cad, page=None, all_pages=()):
    if page:
        width, height = page["size_mm"]
        origin = page["origin"]
        canvas = [0, 0, width, height]
    else:
        width, height = _full_width(view), view[3]+TOP+BOTTOM
        canvas = [view[0]-MARGIN, view[1]-TOP, width, height]
        origin = view[:2]
    root = ET.Element(f"{{{NS}}}svg", {"width": f"{width}mm", "height": f"{height}mm", "viewBox": " ".join(map(str, canvas))})
    if page:
        defs = _element(root, "defs")
        clip = _element(defs, "clipPath", id="tile-clip", clipPathUnits="userSpaceOnUse")
        _element(clip, "rect", x=origin[0], y=origin[1], width=width-2*MARGIN, height=height-TOP-BOTTOM)
        pattern = _element(root, "g", transform=f"translate({MARGIN-origin[0]} {TOP-origin[1]})", clip_path="url(#tile-clip)")
    else:
        pattern = _element(root, "g")
    _references(pattern, cad)
    if page:
        # Two common-coordinate crosses on each shared overlap: same positions
        # appear on both sheets, so taping cannot introduce a separate origin.
        same = [p for p in all_pages if p["format"] == page["format"]]
        for other in same:
            if other["row"] > 0:
                y = other["origin"][1]+OVERLAP/2
                for x in [other["origin"][0]+(width-2*MARGIN)/3, other["origin"][0]+2*(width-2*MARGIN)/3]:
                    _element(pattern, "path", d=f"M {x-2} {y} L {x+2} {y} M {x} {y-2} L {x} {y+2}", fill="none", stroke="#666666", stroke_width=.25)
            if other["column"] > 0:
                x = other["origin"][0]+OVERLAP/2
                for y in [other["origin"][1]+(height-TOP-BOTTOM)/3, other["origin"][1]+2*(height-TOP-BOTTOM)/3]:
                    _element(pattern, "path", d=f"M {x-2} {y} L {x+2} {y} M {x} {y-2} L {x} {y+2}", fill="none", stroke="#666666", stroke_width=.25)
    cut = _element(pattern, "g", id="cut")
    path = copy.deepcopy(native_path)
    path.attrib.update({"fill": "none", "stroke": "#000000", "stroke-width": ".35", "stroke-linejoin": "round"})
    cut.append(path)
    x, y = canvas[0]+MARGIN, canvas[1]+13
    title = f"Sauron blade | {page['format'].upper()} {page['number']}/{page['count']} | Actual Size / 100%" if page else "Sauron blade | FULL SIZE | Cut 6 in EVA"
    _text(root, x, y, title)
    _text(root, x, y+6, "SOLID BLACK: cut. DASHED BLUE: mount references, not cuts. GRAY: alignment.")
    bx, by = canvas[0]+20, canvas[1]+height-18
    _element(root, "path", id="calibration", d=f"M {bx} {by} L {bx+100} {by} M {bx} {by-2} L {bx} {by+2} M {bx+100} {by-2} L {bx+100} {by+2}", fill="none", stroke="#cc0000", stroke_width=.4)
    _text(root, bx, by+7, "100 mm: check with ruler. NO Fit / Shrink to page.")
    ET.ElementTree(root).write(filename, encoding="utf-8", xml_declaration=True)
    return {"size_mm": [width, height], "origin": canvas[:2]}


def _fingerprint():
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in [SOURCE, Path(__file__).resolve()]}


def _owned_path(root, name):
    if not isinstance(name, str) or not re.fullmatch(r"patterns/(?:blade\.svg|manifest\.json|blade-(?:a4|letter)-\d{2,}\.(?:svg|pdf))|prints/(?:adapter|fit-coupon|holder|holder-lower|holder-upper)\.stl", name):
        raise ValueError(f"Unsafe artifact path: {name!r}")
    target = root / name
    if any(p.is_symlink() for p in [target, target.parent]) or not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Unsafe symlink artifact path: {name}")
    return target


def _mesh_geometry(filename):
    text = filename.read_text()
    vertices = [tuple(round(float(v), 5) for v in match) for match in re.findall(r"vertex\s+("+NUMBER+r")\s+("+NUMBER+r")\s+("+NUMBER+r")", text)]
    if not vertices or len(vertices) % 3 or len(vertices)//3 != text.count("endfacet"):
        raise ValueError(f"STL mesh has no valid triangles: {filename}")
    triangles = [vertices[i:i+3] for i in range(0, len(vertices), 3)]
    edges = defaultdict(list)
    for i, triangle in enumerate(triangles):
        if len(set(triangle)) != 3:
            raise ValueError("STL mesh degenerate triangle")
        for a, b in zip(triangle, triangle[1:]+triangle[:1]):
            edges[tuple(sorted([a, b]))].append(i)
    if any(len(faces) != 2 for faces in edges.values()):
        raise ValueError("STL mesh is not closed/manifold")
    neighbors = defaultdict(set)
    for a, b in edges.values():
        neighbors[a].add(b)
        neighbors[b].add(a)
    seen, stack = set(), [0]
    while stack:
        i = stack.pop()
        if i not in seen:
            seen.add(i)
            stack.extend(neighbors[i]-seen)
    if len(seen) != len(triangles):
        raise ValueError("STL mesh contains disconnected solids")

    def cross(a, b):
        return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    def dot(a, b):
        return sum(x*y for x, y in zip(a, b))
    def subtract(a, b):
        return tuple(x-y for x, y in zip(a, b))
    ray = (1, .137, .071)
    rays = []
    for a, b, c in triangles:
        e1, e2 = subtract(b, a), subtract(c, a)
        if dot(cross(e1, e2), cross(e1, e2)) < 1e-16:
            raise ValueError("STL mesh zero-area triangle")
        h = cross(ray, e2)
        determinant = dot(e1, h)
        if abs(determinant) > 1e-10:
            rays.append((a, e1, e2, h, 1/determinant))
    def contains(point):
        hits = set()
        for a, e1, e2, h, inverse in rays:
            s = subtract(point, a)
            u = inverse*dot(s, h)
            q = cross(s, e1)
            v = inverse*dot(ray, q)
            t = inverse*dot(e2, q)
            if -.0000001 <= u <= 1.0000001 and v >= -.0000001 and u+v <= 1.0000001 and t > 1e-7:
                hits.add(round(t, 6))
        return len(hits) % 2 == 1
    return vertices, contains


def _mesh(filename, cad, height):
    vertices, contains = _mesh_geometry(filename)
    if abs(min(math.hypot(v[0], v[1]) for v in vertices)-cad["bore_diameter"]/2) > .01:
        raise ValueError("STL mesh bore diameter mismatch")
    if abs(min(v[2] for v in vertices)) > .01 or abs(max(v[2] for v in vertices)-height) > .01 or any(math.hypot(v[0], v[1]) > cad["adapter_radius"]+.01 for v in vertices):
        raise ValueError(f"STL mesh envelope/height contamination: {filename}")
    p = cad["parameters"]
    bore, root, radius = cad["bore_diameter"]/2, p["slot_root_radius"], cad["adapter_radius"]
    for level in [height*.25, height*.75]:
        for i in range(12):
            angle = math.radians(i*30)
            for distance, expected in [(0, False), (bore-.2, False), (bore+.2, True)]:
                point = (distance*math.cos(angle), distance*math.sin(angle), level)
                if contains(point) != expected:
                    raise ValueError("STL mesh through-bore/wall mismatch")
        for i in range(6):
            angle = math.radians(i*60)
            for x, y, expected in [(root-.2, 0, True), (root+.2, 0, False), (radius-.2, 0, False),
                                   (root+1, cad["slot_width"]/2+.2, True), (root+1, -cad["slot_width"]/2-.2, True)]:
                point = (x*math.cos(angle)-y*math.sin(angle), x*math.sin(angle)+y*math.cos(angle), level)
                if contains(point) != expected:
                    raise ValueError("STL mesh six open slots/width mismatch")
            angle += math.pi/6
            if not contains(((radius-.2)*math.cos(angle), (radius-.2)*math.sin(angle), level)):
                raise ValueError("STL mesh missing outer ring stock")


def _groove_floor(cad, z):
    """Blade inner-edge radius at holder-local z: the floor of its groove."""
    z += cad["holder_span"][0]
    edge = cad["blade_inner_edge"]
    return next(ra+(rb-ra)*(z-za)/(zb-za) for (ra, za), (rb, zb) in zip(edge, edge[1:]) if zb <= z <= za)


def _holder_mesh(filename, cad, part):
    vertices, contains = _mesh_geometry(filename)
    height = cad["holder_span"][1]-cad["holder_span"][0]
    offset = height/2 if part == "upper" else 0
    length = height if part == "whole" else height/2
    bounds = [max(v[i] for v in vertices)-min(v[i] for v in vertices) for i in range(3)]
    pin_circle, pin_d, pin_length, pin_clearance = cad["holder_pins"]
    pins = pin_length if part == "lower" else 0
    bore = cad["bore_diameter"]/2
    bore_height = cad["holder_bore_height"]
    bore_vertices = [v for v in vertices if v[2]+offset < bore_height-.01]
    if (not bore_vertices or abs(min(v[2] for v in vertices)) > .01 or abs(bounds[2]-length-pins) > .01
            or abs(min(math.hypot(v[0], v[1]) for v in bore_vertices)-bore) > .01
            or any(math.hypot(v[0], v[1]) > cad["adapter_radius"]+.01 for v in vertices)):
        raise ValueError("STL holder bore/envelope mismatch")
    if part != "whole" and max(bounds) > 175:
        raise ValueError("STL holder exceeds A1 mini envelope with 5 mm total brim allowance")
    for (ra, za), (rb, zb) in zip(cad["holder_profile"], cad["holder_profile"][1:]):
        for fraction in [.25, .75]:
            z = za+(zb-za)*fraction
            if not offset < z < offset+length:
                continue
            radius = ra+(rb-ra)*fraction
            for i in range(6):
                angle = math.radians(i*60)
                # Hexagon flats, vertex channels and the blind bore / solid crown.
                flat = radius*math.cos(math.pi/6)
                inner_radius = max(0, bore-max(0, z-bore_height))  # 45-degree bore ceiling
                probes = [(0, 0, inner_radius == 0), (flat-.2, math.pi/6, True),
                          (flat+.2, math.pi/6, False)]
                if inner_radius > .2:
                    probes += [(inner_radius-.2, 0, False), (inner_radius+.2, 0, True)]
                # Vertex grooves only where the blade meets the core; solid elsewhere.
                floor = _groove_floor(cad, z)
                if min(radius, floor)-.3 > inner_radius+.2:
                    probes += [(min(radius, floor)-.3, 0, True)]
                if radius > floor+.3:
                    probes += [(floor+.2, 0, False)]
                for distance, extra_angle, expected in probes:
                    point = (distance*math.cos(angle+extra_angle), distance*math.sin(angle+extra_angle), z-offset)
                    if contains(point) != expected:
                        raise ValueError("STL holder bore/slots/hexagonal taper mismatch")
    # Verify width at mounting stations AND the widest shoulders; thin mounting
    # bands can sit below the flare, where there is no wall to probe.
    widest = max(p[0] for p in cad["holder_profile"])
    levels = {s-cad["holder_span"][0] for s in cad["stations"]}
    levels.update(z for r, z in cad["holder_profile"] if r == widest)
    width_probes = 0
    for z in sorted(levels):
        if not offset < z < offset+length:
            continue
        radius = next(ra+(rb-ra)*(z-za)/(zb-za)
                      for (ra, za), (rb, zb) in zip(cad["holder_profile"], cad["holder_profile"][1:])
                      if za <= z <= zb)
        for i in range(6):
            angle = math.radians(i*60)
            for sign in [-1, 1]:
                for extra, expected in [(-.2, False), (.2, True)]:
                    x, y = _groove_floor(cad, z)+1, sign*(cad["slot_width"]/2+extra)
                    if radius-abs(y)/math.sqrt(3) <= x+.2:
                        continue  # Thin hexagon corners cannot supply an outer-wall probe.
                    point = (x*math.cos(angle)-y*math.sin(angle), x*math.sin(angle)+y*math.cos(angle), z-offset)
                    width_probes += 1
                    if contains(point) != expected:
                        raise ValueError("STL holder channel width mismatch")
    if not width_probes:
        raise ValueError("STL holder lacks shoulder stock to verify channel width; increase adapter_od")
    # Joint alignment: pins on the lower top face, blind holes in the upper bed face.
    for i in range(3):
        angle = math.radians(30+i*120)
        hole = (pin_d+pin_clearance)/2
        probes = {"lower": [(pin_circle, length+pin_length/2, True), (pin_circle+pin_d/2+.3, length+pin_length/2, False)],
                  "upper": [(pin_circle+hole-.1, pin_length/2, False), (pin_circle+hole+.3, pin_length/2, True)]}.get(part, [])
        for distance, z, expected in probes:
            if contains((distance*math.cos(angle), distance*math.sin(angle), z)) != expected:
                raise ValueError("STL holder joint pin/hole mismatch")
    if offset < height-.3 < offset+length and not contains((0, 0, height-.3-offset)):
        raise ValueError("STL holder pointed crown mismatch")


def validate_exports(output_dir: Path) -> None:
    root = Path(output_dir).resolve()
    manifest = json.loads(_owned_path(root, "patterns/manifest.json").read_text())
    paths = [_owned_path(root, name) for name in manifest["owned"]]
    if any(not path.is_file() for path in paths):
        raise ValueError("Missing generated artifact/mesh")
    if manifest["source_fingerprint"] != _fingerprint():
        raise ValueError("Source changed: regenerate exports")
    cad = read_model(manifest["cad"]["parameters"])
    if cad != manifest["cad"] or manifest["pages"] != _pages(manifest["native_viewbox"]):
        raise ValueError("Manifest metadata/page origins disagree with source")
    owned = {"patterns/blade.svg", "patterns/manifest.json", "prints/adapter.stl", "prints/fit-coupon.stl",
             "prints/holder.stl", "prints/holder-lower.stl", "prints/holder-upper.stl"}
    owned.update(page[k] for page in manifest["pages"] for k in ["svg", "pdf"])
    if set(manifest["owned"]) != owned:
        raise ValueError("Manifest owned artifact set mismatch")
    points = [tuple(value*axis for value, axis in zip(point, cad["svg_axes"])) for point in cad["blade_points"]]
    expected = list(zip(points, points[1:]+points[:1]))
    all_ink = {name: [] for name in PAPERS}
    full = manifest["full_svg"]

    def check(filename, origin, expected_size, clip_box=None, pdf=False):
        label = "PDF" if pdf else "SVG"
        size, ink = _geometry(filename, pdf)
        if any(abs(a-b) > .01 for a, b in zip(size, expected_size)):
            raise ValueError(f"{label} page size mismatch: {filename}")
        actual = [tuple((p[0]+origin[0], p[1]+origin[1]) for p in segment) for segment in ink["black"]]
        target = [s for segment in expected if (s := _clip(segment, clip_box))] if clip_box else expected
        if not _same_segments(actual, target):
            raise ValueError(f"{label} outline geometry/scale mismatch: {filename}")
        by = expected_size[1]-18
        bar = [((20, by), (120, by)), ((20, by-2), (20, by+2)), ((120, by-2), (120, by+2))]
        if not _same_segments(ink["red"], bar):
            raise ValueError(f"{label} 100 mm calibration bar mismatch")
        references = []
        left = cad["parameters"]["slot_root_radius"]*cad["svg_axes"][0]
        for station, band in zip(cad["stations"], cad["land_bands"]):
            y = station*cad["svg_axes"][1]
            right = (cad["parameters"]["head_radius"]+2)*cad["svg_axes"][0]
            references.append(((left, y), (right, y)))
            a, b = (v*cad["svg_axes"][1] for v in band)
            edge = cad["adapter_radius"]*cad["svg_axes"][0]
            corners = [(left, a), (edge, a), (edge, b), (left, b)]
            references.extend(zip(corners, corners[1:]+corners[:1]))
        if clip_box:
            references = [s for segment in references if (s := _clip(segment, clip_box))]
        blue = [tuple((p[0]+origin[0], p[1]+origin[1]) for p in s) for s in ink["blue"]]
        if not _same_segments(blue, references):
            raise ValueError(f"{label} mounting references misaligned: {filename}")
        return actual
    check(root/"patterns/blade.svg", full["origin"], full["size_mm"])
    with tempfile.TemporaryDirectory(prefix="mace-pdf-check-") as directory:
        for page in manifest["pages"]:
            width, height = page["size_mm"]
            x, y = page["origin"]
            box = [x, y, x+width-2*MARGIN, y+height-TOP-BOTTOM]
            origin = [x-MARGIN, y-TOP]
            check(root/page["svg"], origin, page["size_mm"], box)
            svg = Path(directory) / "page.svg"
            command = [os.environ.get("PDFTOCAIRO", "pdftocairo"), "-svg", "-noshrink", "-nocenter", str(root/page["pdf"]), str(svg)]
            try:
                result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            except (OSError, subprocess.TimeoutExpired) as error:
                raise RuntimeError(f"pdftocairo verification unavailable: {error}") from error
            if result.returncode or not svg.is_file():
                raise RuntimeError(f"pdftocairo verification failed: {result.stderr}")
            all_ink[page["format"]].extend(check(svg, origin, page["size_mm"], box, pdf=True))
    target_bounds = _bounds(expected)
    for name, segments in all_ink.items():
        if any(abs(a-b) > TOLERANCE for a, b in zip(_bounds(segments), target_bounds)):
            raise ValueError(f"PDF {name} reconstructed outline scale/coverage mismatch")
    _mesh(root/"prints/adapter.stl", cad, cad["adapter_height"])
    _mesh(root/"prints/fit-coupon.stl", cad, cad["coupon_height"])
    for part in ["whole", "lower", "upper"]:
        filename = "holder.stl" if part == "whole" else f"holder-{part}.stl"
        _holder_mesh(root/"prints"/filename, cad, part)


def build(output_dir: Path, defines: dict[str, float] | None = None) -> dict:
    root = Path(output_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    old_manifest = _owned_path(root, "patterns/manifest.json")
    previous = json.loads(old_manifest.read_text())["owned"] if old_manifest.exists() else []
    for name in previous:
        _owned_path(root, name)
    cad = read_model(defines)
    with tempfile.TemporaryDirectory(prefix=".mace-stage-", dir=root.parent) as directory:
        stage = Path(directory)
        (stage/"patterns").mkdir()
        (stage/"prints").mkdir()
        native = stage/"native.svg"
        run_scad("blade_2d", native, defines)
        svg = ET.parse(native).getroot()
        view = [float(value) for value in svg.get("viewBox").split()]
        paths = list(svg.iter(f"{{{NS}}}path"))
        if len(paths) != 1:
            raise ValueError("Expected one native blade polygon")
        pages = _pages(view)
        full = _pattern(stage/"patterns/blade.svg", paths[0], view, cad)
        for page in pages:
            _pattern(stage/page["svg"], paths[0], view, cad, page, pages)
            cairosvg.svg2pdf(url=str(stage/page["svg"]), write_to=str(stage/page["pdf"]))
        run_scad("adapter", stage/"prints/adapter.stl", defines)
        run_scad("fit_coupon", stage/"prints/fit-coupon.stl", defines)
        for part in ["whole", "lower", "upper"]:
            mode = "holder" if part == "whole" else f"holder_{part}"
            filename = "holder.stl" if part == "whole" else f"holder-{part}.stl"
            run_scad(mode, stage/"prints"/filename, defines)
        owned = ["patterns/blade.svg", "prints/adapter.stl", "prints/fit-coupon.stl",
                 "prints/holder.stl", "prints/holder-lower.stl", "prints/holder-upper.stl"] + [page[k] for page in pages for k in ["svg", "pdf"]] + ["patterns/manifest.json"]
        manifest = {"cad": cad, "native_viewbox": view, "full_svg": full, "pages": pages, "owned": owned, "source_fingerprint": _fingerprint(),
                    "margin_mm": MARGIN, "overlap_mm": OVERLAP, "outline_tolerance_mm": TOLERANCE}
        (stage/"patterns/manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
        validate_exports(stage)
        for name in owned:
            target = _owned_path(root, name)
            if target.exists() and name not in previous:
                raise ValueError(f"Refusing to overwrite unowned artifact: {name}")
        # Per-file atomic publication, manifest last. No unverified render is
        # published; interrupted publication cannot claim a new accepted set.
        for name in owned[:-1]:
            target = _owned_path(root, name)
            target.parent.mkdir(exist_ok=True)
            os.replace(stage/name, target)
        for name in set(previous)-set(owned):
            _owned_path(root, name).unlink(missing_ok=True)
        old_manifest.parent.mkdir(exist_ok=True)
        os.replace(stage/"patterns/manifest.json", old_manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=SOURCE.parent)
    parser.add_argument("--set", action="append", default=[], metavar="NAME=NUMBER")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        defines = {}
        for entry in args.set:
            name, value = entry.split("=", 1)
            defines[name] = float(value)
        if args.check:
            if defines:
                raise ValueError("--check uses the saved manifest; do not supply --set")
            validate_exports(args.out)
            print(f"Verified actual SVG/PDF outlines and all STL meshes: {args.out.resolve()}")
        else:
            manifest = build(args.out, defines)
            print(f"Verified exports: {args.out.resolve()} ({len(manifest['pages'])} PDF pages, holder sections, adapter and coupon)")
    except (ValueError, RuntimeError, OSError, ET.ParseError, KeyError) as error:
        parser.exit(1, f"Export/verification failed: {error}\n")


if __name__ == "__main__":
    main()
