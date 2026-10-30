"""Export the routed board: KiCad PCB, a fab Gerber set (copper, mask, silk, outline, drill) as a
zip, plotter SVGs and docs. Reads best.pkl from build_board.py.

Layers (viewed from the top = component side, as Gerbers are):
  F_Cu   through-hole pad rings only     B_Cu   pads, SMD pads and every trace
  F_Mask / B_Mask   pad openings         F_SilkS part outlines and refs
  B_SilkS  wire-pad names and the two jumper wires (layout "pads"), mirrored to read from below
Jumpers that end on existing pads (layout "pads") are wires, not holes: they appear only as silk."""
import json, os, pickle, sys, uuid, zipfile
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity
import board as B
from route import pad_geom

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)
res = pickle.load(open("best.pkl", "rb"))
parts = B.build(res["assign"], res["layout"])
traces, jumpers = res["traces"], res["jumpers"]
W = B.TRACE_W
MASK_X = 0.05                      # solder-mask expansion round each pad

allpads = [p for part in parts for p in part.pads]
def on_pad(q):
    return any(abs(p.x - q[0]) < 0.05 and abs(p.y - q[1]) < 0.05 for p in allpads)
# jumpers between existing pads are loose wires; others get their own drilled pads
wire_jumpers = [j for j in jumpers if on_pad(j[1]) and on_pad(j[2])]
pad_jumpers = [j for j in jumpers if j not in wire_jumpers]

nets = sorted({p.net for p in allpads if p.net} | {n for n, _ in traces})
netid = {n: i + 1 for i, n in enumerate(nets)}
U = lambda: str(uuid.uuid4())

# pad-row names for the silkscreen and the docs
j5 = next((p for p in parts if p.ref == "J5"), None)
def j5_name(p):
    if p.net in ("K1", "K2"):
        return f"LED{p.net[1]}-"
    if p.net == "VBAT" and [q for q in j5.pads if q.net == "VBAT"][0] is p and \
            sum(q.net == "VBAT" for q in j5.pads) > 1:
        return "LED+"
    return p.net

# ------------------------------------------------------------------ KiCad
def kpad(p, part):
    dx, dy = round(p.x - part.x, 4), round(p.y - part.y, 4)
    net = f'(net {netid[p.net]} "{p.net}")' if p.net else ""
    if p.drill is None:
        shape = "oval" if p.shape == "oval" else "rect"
        return (f'    (pad "{p.num}" smd {shape} (at {dx} {dy}) (size {p.w} {p.h}) '
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
for k, (net, a, b) in enumerate(pad_jumpers, 1):
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    jp = B.Part(f"W{k}", "WIRE_JUMPER", cx, cy, 0, "wire", [
        B.Pad(f"W{k}", 1, a[0], a[1], net, w=B.JUMPER_PAD, h=B.JUMPER_PAD, drill=0.8),
        B.Pad(f"W{k}", 2, b[0], b[1], net, w=B.JUMPER_PAD, h=B.JUMPER_PAD, drill=0.8)], "wire")
    line = (f'\n    (fp_line (start {a[0]-cx:.3f} {a[1]-cy:.3f}) (end {b[0]-cx:.3f} {b[1]-cy:.3f}) '
            f'(stroke (width 0.3) (type solid)) (layer "F.SilkS") (uuid "{U()}"))')
    lines.append(kfoot(jp, line))
for net, a, b in wire_jumpers:
    lines.append(f'  (gr_line (start {a[0]:.4f} {a[1]:.4f}) (end {b[0]:.4f} {b[1]:.4f}) (stroke (width 0.25) '
                 f'(type dash)) (layer "B.SilkS") (uuid "{U()}"))')
for net, pts in traces:
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        lines.append(f'  (segment (start {x1:.4f} {y1:.4f}) (end {x2:.4f} {y2:.4f}) (width {W}) '
                     f'(layer "B.Cu") (net {netid[net]}) (uuid "{U()}"))')
lines.append(f'  (gr_rect (start 0 0) (end {B.BOARD_W} {B.BOARD_H}) (stroke (width 0.1) (type solid)) '
             f'(fill none) (layer "Edge.Cuts") (uuid "{U()}"))')
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
copper = [pad_geom(p) for p in allpads] + [LineString(pts).buffer(W / 2, 16) for _, pts in traces]
jpads = [q for _, a, b in pad_jumpers for q in (a, b)]
copper += [Point(q).buffer(B.JUMPER_PAD / 2, 24) for q in jpads]
cu = unary_union(copper)
holes = [(p.x, p.y, p.drill) for p in allpads if p.drill] + [(q[0], q[1], 0.8) for q in jpads]

# ------------------------------------------------------------------ Gerber helpers (board y runs down)
def gy(y):
    return B.BOARD_H - y


def gnum(v):
    return f"{int(round(v * 1e6))}"


class Gerber:
    def __init__(self, func, comment):
        self.head = [f"G04 remote button board, {comment}*", f"%TF.FileFunction,{func}*%",
                     "%FSLAX46Y46*%", "%MOMM*%", "%LPD*%"]
        self.ap, self.body = {}, []

    def aperture(self, key, spec):
        if key not in self.ap:
            self.ap[key] = (10 + len(self.ap), spec)
        return self.ap[key][0]

    def flash_pad(self, p, grow=0.0):
        w, h = p.w + 2 * grow, p.h + 2 * grow
        if p.shape == "circle":
            d = self.aperture(("C", w), f"C,{w:.4f}")
        elif p.shape == "rect":
            d = self.aperture(("R", w, h), f"R,{w:.4f}X{h:.4f}")
        else:
            d = self.aperture(("O", w, h), f"O,{w:.4f}X{h:.4f}")
        self.body.append(f"D{d}*\nX{gnum(p.x)}Y{gnum(gy(p.y))}D03*")

    def flash_circle(self, q, dia):
        d = self.aperture(("C", dia), f"C,{dia:.4f}")
        self.body.append(f"D{d}*\nX{gnum(q[0])}Y{gnum(gy(q[1]))}D03*")

    def line(self, pts, width):
        d = self.aperture(("C", width), f"C,{width:.4f}")
        self.body.append(f"D{d}*")
        x, y = pts[0]
        self.body.append(f"X{gnum(x)}Y{gnum(gy(y))}D02*")
        for x, y in pts[1:]:
            self.body.append(f"X{gnum(x)}Y{gnum(gy(y))}D01*")

    def region(self, poly):              # filled polygon (silk text); holes drawn clear
        def ring(r, clear):
            c = list(r.coords)
            self.body += (["%LPC*%"] if clear else []) + ["G36*", f"X{gnum(c[0][0])}Y{gnum(gy(c[0][1]))}D02*"] + \
                         [f"X{gnum(x)}Y{gnum(gy(y))}D01*" for x, y in c[1:]] + ["G37*"] + (["%LPD*%"] if clear else [])
        ring(poly.exterior, False)
        for i in poly.interiors:
            ring(i, True)

    def write(self, path):
        head = self.head + [f"%ADD{num}{spec}*%" for num, spec in self.ap.values()]
        open(path, "w").write("\n".join(head + self.body + ["M02*"]) + "\n")


FONT = FontProperties(family="DejaVu Sans", weight="bold")
def text_polys(s, x, y, size, mirror=False, rot=0, anchor="center"):
    """Text as polygons in board coordinates (y down), centred on (x, y)."""
    tp = TextPath((0, 0), s, size=size, prop=FONT)
    polys = []
    for verts in tp.to_polygons():
        if len(verts) >= 3:
            polys.append(Polygon(verts).buffer(0))
    # even-odd: letters with holes come as separate rings; xor builds them
    g = None
    for p in sorted(polys, key=lambda p: -p.area):
        g = p if g is None else g.symmetric_difference(p)
    x0, y0, x1, y1 = g.bounds
    g = affinity.translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2 if anchor == "center" else -y1)
    g = affinity.scale(g, 1, -1, origin=(0, 0))             # font y up -> board y down
    if rot:
        g = affinity.rotate(g, rot, origin=(0, 0))
    if mirror:
        g = affinity.scale(g, -1, 1, origin=(0, 0))
    g = affinity.translate(g, x, y)
    return list(getattr(g, "geoms", [g]))


# --- copper
f_cu, b_cu = Gerber("Copper,L1,Top", "top copper (through-hole rings)"), Gerber("Copper,L2,Bot", "bottom copper")
f_mask, b_mask = Gerber("Soldermask,Top", "top mask"), Gerber("Soldermask,Bot", "bottom mask")
for p in allpads:
    b_cu.flash_pad(p); b_mask.flash_pad(p, MASK_X)
    if p.drill:
        f_cu.flash_pad(p); f_mask.flash_pad(p, MASK_X)
for q in jpads:
    for g in (f_cu, b_cu):
        g.flash_circle(q, B.JUMPER_PAD)
    for g in (f_mask, b_mask):
        g.flash_circle(q, B.JUMPER_PAD + 2 * MASK_X)
for net, pts in traces:
    b_cu.line(pts, W)

# --- silkscreen: keep it off the pads (mask openings + 0.15)
keepout = unary_union([pad_geom(p).buffer(MASK_X + 0.15) for p in allpads])
f_silk, b_silk = Gerber("Legend,Top", "top silkscreen"), Gerber("Legend,Bot", "bottom silkscreen")
def silk_outline(g, geom):
    for seg in getattr(geom, "geoms", [geom]):
        if seg.length > 0.2:
            g.line(list(seg.coords), 0.15)
used = []                         # silk already placed, so labels don't pile up
if j5:
    for p in j5.pads:   # names running up from each wire pad, read from the copper side
        polys = text_polys(j5_name(p), p.x, 0, 0.9, mirror=True, rot=90)
        top = max(q.bounds[3] for q in polys)
        for poly in polys:
            q = affinity.translate(poly, 0, p.y - p.h / 2 - 0.5 - top)
            b_silk.region(q); used.append(q.buffer(0.2))
for part in parts:
    if part.ref == "J5":
        continue
    smd = all(p.drill is None for p in part.pads)       # SMDs sit on the copper side
    g = b_silk if smd else f_silk
    if part.body:
        w, h = part.body
        r = box(part.x - w / 2, part.y - h / 2, part.x + w / 2, part.y + h / 2).exterior.difference(keepout)
        silk_outline(g, r)
    lab = part.label if part.ref.startswith("SW") else ("MCP23017" if part.ref == "U1" else part.ref)
    size = 1.0 if part.ref.startswith("SW") or part.ref == "U1" else 0.8
    bh = part.body[1] / 2 if part.body else 1.0
    bw = part.body[0] / 2 if part.body else 1.0
    for dx, dy in ((0, 0), (0, bh + 0.9), (0, -bh - 0.9), (bw + 1.3, 0), (-bw - 1.3, 0)):
        polys = text_polys(lab, part.x + dx, part.y + dy, size, mirror=smd)
        u = unary_union(polys)
        if not u.intersects(keepout) and not any(u.intersects(o) for o in used) and \
                box(0.3, 0.3, B.BOARD_W - 0.3, B.BOARD_H - 0.3).contains(u):
            for poly in polys:
                g.region(poly)
            used.append(u.buffer(0.2))
            break
for net, a, b in wire_jumpers:   # dashed line along each loose jumper wire (pad names say which)
    ln = LineString([a, b]); L = ln.length; k = 0.0
    while k < L:
        seg = LineString([ln.interpolate(k).coords[0], ln.interpolate(min(k + 1.2, L)).coords[0]]).difference(keepout)
        silk_outline(b_silk, seg); k += 2.0
for poly in text_polys("COPPER SIDE", B.BOARD_W / 2, 2.6, 1.2, mirror=True):
    b_silk.region(poly)

edge = Gerber("Profile,NP", "board outline")
edge.line([(0, 0), (B.BOARD_W, 0), (B.BOARD_W, B.BOARD_H), (0, B.BOARD_H), (0, 0)], 0.1)


def excellon(path):
    tools = sorted({d for _, _, d in holes})
    s = ["M48", "; plated through holes", "METRIC,TZ"] + [f"T{i+1}C{d:.3f}" for i, d in enumerate(tools)] + ["%", "G90", "G05"]
    for i, d in enumerate(tools):
        s.append(f"T{i+1}")
        for x, y, dd in holes:
            if dd == d:
                s.append(f"X{x:.3f}Y{gy(y):.3f}")
    open(path, "w").write("\n".join(s + ["M30"]) + "\n")


GB = {"F_Cu.gtl": f_cu, "B_Cu.gbl": b_cu, "F_Mask.gts": f_mask, "B_Mask.gbs": b_mask,
      "F_SilkS.gto": f_silk, "B_SilkS.gbo": b_silk, "Edge_Cuts.gm1": edge}
for name, g in GB.items():
    g.write(f"{OUT}/remote_buttons-{name}")
excellon(f"{OUT}/remote_buttons-PTH.drl")
with zipfile.ZipFile(f"{OUT}/remote_buttons_gerbers.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for name in list(GB) + ["PTH.drl"]:
        z.write(f"{OUT}/remote_buttons-{name}", f"remote_buttons-{name}")

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
bit = {fn: (pin - 21) if 21 <= pin <= 28 else 8 + (pin - 1) for fn, pin in res["assign"].items()}
json.dump({"mcp23017_pin": res["assign"], "esphome_number": bit,
           "J5_wire_pads": [{"pad": p.num, "name": j5_name(p), "net": p.net, "display_pin": B.J5_LABELS.get(p.net)}
                            for p in j5.pads] if j5 else [],
           "wire_jumpers": [{"net": n, "from": a, "to": b} for n, a, b in wire_jumpers],
           "unrouted": res["fail"]}, open(f"{OUT}/pinmap.json", "w"), indent=1)
print("nets", len(nets), "traces", len(traces), "wire jumpers", len(wire_jumpers), "pad jumpers", len(pad_jumpers),
      "holes", len(holes), "unrouted", res["fail"])
print("files:", sorted(os.listdir(OUT)))
