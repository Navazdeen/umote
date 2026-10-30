"""Export the routed board: KiCad PCB, Gerbers + drill, plotter SVG, docs."""
import json, os, pickle, sys, uuid
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
import board as B
from route import pad_geom

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)
res = pickle.load(open("best.pkl", "rb"))
parts = B.build(res["assign"], res["j5"], res["j4"])
traces, jumpers = res["traces"], res["jumpers"]
W = B.TRACE_W

nets = sorted({p.net for part in parts for p in part.pads if p.net} | {n for n, _ in traces})
netid = {n: i + 1 for i, n in enumerate(nets)}
U = lambda: str(uuid.uuid4())

# ------------------------------------------------------------------ KiCad
def kpad(p, part):
    dx, dy = round(p.x - part.x, 4), round(p.y - part.y, 4)
    net = f'(net {netid[p.net]} "{p.net}")' if p.net else ""
    if p.drill is None:
        return (f'    (pad "{p.num}" smd rect (at {dx} {dy}) (size {p.w} {p.h}) '
                f'(layers "B.Cu" "B.Mask") {net} (uuid "{U()}"))')
    shape = {"circle": "circle", "oval": "oval", "rect": "rect"}[p.shape]
    return (f'    (pad "{p.num}" thru_hole {shape} (at {dx} {dy}) (size {p.w} {p.h}) (drill {p.drill}) '
            f'(layers "*.Cu" "*.Mask") {net} (uuid "{U()}"))')


def kfoot(part, extra=""):
    pads = "\n".join(kpad(p, part) for p in part.pads)
    body = ""
    if part.body:
        w, h = part.body
        body = (f'    (fp_rect (start {-w/2:.3f} {-h/2:.3f}) (end {w/2:.3f} {h/2:.3f}) '
                f'(stroke (width 0.15) (type solid)) (fill none) (layer "F.SilkS") (uuid "{U()}"))')
    lab = (part.label or part.value).replace('"', "")
    return f'''  (footprint "remote:{part.kind}" (layer "F.Cu") (uuid "{U()}") (at {part.x:.4f} {part.y:.4f})
    (property "Reference" "{part.ref}" (at 0 0 0) (layer "F.SilkS") (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))
    (property "Value" "{lab}" (at 0 1.5 0) (layer "F.Fab") (uuid "{U()}") (effects (font (size 1 1) (thickness 0.15))))
{body}
{pads}{extra}
  )'''


lines = ['(kicad_pcb (version 20240108) (generator "remote-router") (generator_version "8.0")',
         '  (general (thickness 1.6) (legacy_teardrops no))', '  (paper "A4")',
         '  (layers (0 "F.Cu" signal) (31 "B.Cu" signal) (34 "B.Paste" user) (35 "F.Paste" user)',
         '    (36 "B.SilkS" user "B.Silkscreen") (37 "F.SilkS" user "F.Silkscreen") (38 "B.Mask" user)',
         '    (39 "F.Mask" user) (44 "Edge.Cuts" user) (48 "B.Fab" user) (49 "F.Fab" user))',
         '  (setup (pad_to_mask_clearance 0))', '  (net 0 "")']
lines += [f'  (net {i} "{n}")' for n, i in netid.items()]
for part in parts:
    lines.append(kfoot(part))
for k, (net, a, b) in enumerate(jumpers, 1):
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    jp = B.Part(f"W{k}", "WIRE_JUMPER", cx, cy, 0, "wire", [
        B.Pad(f"W{k}", 1, a[0], a[1], net, w=B.JUMPER_PAD, h=B.JUMPER_PAD, drill=0.8),
        B.Pad(f"W{k}", 2, b[0], b[1], net, w=B.JUMPER_PAD, h=B.JUMPER_PAD, drill=0.8)], "wire")
    line = (f'\n    (fp_line (start {a[0]-cx:.3f} {a[1]-cy:.3f}) (end {b[0]-cx:.3f} {b[1]-cy:.3f}) '
            f'(stroke (width 0.3) (type solid)) (layer "F.SilkS") (uuid "{U()}"))')
    lines.append(kfoot(jp, line))
for net, pts in traces:
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        lines.append(f'  (segment (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (width {W}) '
                     f'(layer "B.Cu") (net {netid[net]}) (uuid "{U()}"))')
lines.append(f'  (gr_rect (start 0 0) (end {B.BOARD_W} {B.BOARD_H}) (stroke (width 0.1) (type solid)) '
             f'(fill none) (layer "Edge.Cuts") (uuid "{U()}"))')
lines.append(f'  (gr_text "COPPER SIDE" (at {B.BOARD_W/2} 2.2 0) (layer "B.Cu") (uuid "{U()}") '
             f'(effects (font (size 1.2 1.2) (thickness 0.3)) (justify mirror)))')
lines.append(")")
open(f"{OUT}/remote_buttons.kicad_pcb", "w").write("\n".join(lines) + "\n")

# project file carrying the design rules
pro = {"board": {"design_settings": {"rules": {
    "min_clearance": B.CLEARANCE, "min_copper_edge_clearance": B.EDGE_CLEAR,
    "min_track_width": 0.6, "min_through_hole_diameter": 0.8},
    "defaults": {"board_outline_line_width": 0.1}},
    "net_settings": {"classes": [{"name": "Default", "clearance": B.CLEARANCE, "track_width": W}]}},
    "meta": {"filename": "remote_buttons.kicad_pro", "version": 1}}
json.dump(pro, open(f"{OUT}/remote_buttons.kicad_pro", "w"), indent=2)

# ------------------------------------------------------------------ copper geometry
copper = []
for part in parts:
    for p in part.pads:
        copper.append(pad_geom(p))
for net, pts in traces:
    copper.append(LineString(pts).buffer(W / 2, 16))
jpads = []
for net, a, b in jumpers:
    for q in (a, b):
        jpads.append(q)
        copper.append(Point(q).buffer(B.JUMPER_PAD / 2, 24))
cu = unary_union(copper)
holes = [(p.x, p.y, p.drill) for part in parts for p in part.pads if p.drill] + \
        [(q[0], q[1], 0.8) for q in jpads]

# ------------------------------------------------------------------ Gerber (bottom copper, viewed from top)
def gy(y):
    return B.BOARD_H - y


def gnum(v):
    return f"{int(round(v * 1e6))}"


def gerber_copper(path):
    ap = {}
    body = []
    def aperture(key, spec):
        if key not in ap:
            ap[key] = (10 + len(ap), spec)
        return ap[key][0]
    for part in parts:
        for p in part.pads:
            if p.shape == "circle":
                d = aperture(("C", p.w), f"C,{p.w:.4f}")
            elif p.shape == "rect":
                d = aperture(("R", p.w, p.h), f"R,{p.w:.4f}X{p.h:.4f}")
            else:
                d = aperture(("O", p.w, p.h), f"O,{p.w:.4f}X{p.h:.4f}")
            body.append(f"D{d}*\nX{gnum(p.x)}Y{gnum(gy(p.y))}D03*")
    dj = aperture(("C", B.JUMPER_PAD), f"C,{B.JUMPER_PAD:.4f}")
    for q in jpads:
        body.append(f"D{dj}*\nX{gnum(q[0])}Y{gnum(gy(q[1]))}D03*")
    dt = aperture(("C", W), f"C,{W:.4f}")
    body.append(f"D{dt}*")
    for net, pts in traces:
        x, y = pts[0]
        body.append(f"X{gnum(x)}Y{gnum(gy(y))}D02*")
        for x, y in pts[1:]:
            body.append(f"X{gnum(x)}Y{gnum(gy(y))}D01*")
    head = ["G04 remote button board, bottom copper*", "%TF.FileFunction,Copper,L2,Bot*%",
            "%FSLAX46Y46*%", "%MOMM*%", "%LPD*%"]
    for key, (num, spec) in ap.items():
        head.append(f"%ADD{num}{spec}*%")
    open(path, "w").write("\n".join(head + body + ["M02*"]) + "\n")


def gerber_edge(path):
    pts = [(0, 0), (B.BOARD_W, 0), (B.BOARD_W, B.BOARD_H), (0, B.BOARD_H), (0, 0)]
    s = ["G04 board outline*", "%TF.FileFunction,Profile,NP*%", "%FSLAX46Y46*%", "%MOMM*%",
         "%ADD10C,0.1000*%", "D10*", f"X{gnum(0)}Y{gnum(0)}D02*"]
    for x, y in pts[1:]:
        s.append(f"X{gnum(x)}Y{gnum(y)}D01*")
    open(path, "w").write("\n".join(s + ["M02*"]) + "\n")


def excellon(path):
    tools = sorted({d for _, _, d in holes})
    s = ["M48", "METRIC,TZ"] + [f"T{i+1}C{d:.3f}" for i, d in enumerate(tools)] + ["%", "G90", "G05"]
    for i, d in enumerate(tools):
        s.append(f"T{i+1}")
        for x, y, dd in holes:
            if dd == d:
                s.append(f"X{x:.3f}Y{gy(y):.3f}")
    open(path, "w").write("\n".join(s + ["M30"]) + "\n")


gerber_copper(f"{OUT}/remote_buttons-B_Cu.gbr")
gerber_edge(f"{OUT}/remote_buttons-Edge_Cuts.gbr")
excellon(f"{OUT}/remote_buttons.drl")

# ------------------------------------------------------------------ plotter SVG
def svg(path, mirror, title):
    g = cu
    if mirror:   # seen from the copper side
        g = affinity.scale(g, xfact=-1, origin=(B.BOARD_W / 2, B.BOARD_H / 2))
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    def ring(r):
        return "M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in r.coords) + " Z"
    paths = []
    for p in polys:
        d = ring(p.exterior) + " " + " ".join(ring(i) for i in p.interiors)
        paths.append(f'<path d="{d}" fill="black" fill-rule="evenodd"/>')
    # small unfilled dot at each hole centre: etches a pit that centres the drill
    dots = []
    for x, y, d in holes:
        xx = B.BOARD_W - x if mirror else x
        dots.append(f'<circle cx="{xx:.3f}" cy="{y:.3f}" r="0.25" fill="white"/>')
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{B.BOARD_W}mm" height="{B.BOARD_H}mm" '
         f'viewBox="0 0 {B.BOARD_W} {B.BOARD_H}">\n<title>{title}</title>\n'
         f'<rect x="0" y="0" width="{B.BOARD_W}" height="{B.BOARD_H}" fill="none" stroke="#999" stroke-width="0.1"/>\n'
         + "\n".join(paths + dots) + "\n</svg>\n")
    open(path, "w").write(s)


svg(f"{OUT}/plot_copper_side_MIRRORED.svg", True, "Copper pattern as seen from the copper side - plot this")
svg(f"{OUT}/copper_top_view.svg", False, "Copper pattern seen through the board from the component side")

# ------------------------------------------------------------------ docs
pin_of = {v: k for k, v in res["assign"].items()}
bit = {}
for fn, pin in res["assign"].items():
    bit[fn] = (pin - 21) if 21 <= pin <= 28 else 8 + (pin - 1)
json.dump({"mcp23017_pin": res["assign"], "esphome_number": bit,
           "J5_to_display": dict(zip(range(1, 12), res["j5"])),
           "J4_mic": dict(zip(range(1, 6), res["j4"])),
           "jumpers": [{"net": n, "from": a, "to": b} for n, a, b in jumpers],
           "unrouted": res["fail"]}, open(f"{OUT}/pinmap.json", "w"), indent=1)
print("nets", len(nets), "traces", len(traces), "jumpers", len(jumpers), "unrouted", res["fail"])
print("files:", sorted(os.listdir(OUT)))
