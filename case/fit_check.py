"""Fit check: components as simple solids in the case's model coordinates, intersected
with the exported shell and back plate (and with each other).

Model coords (as in remote_case.scad): x across (+x = user's left, face up), y from the tip,
z from the back edge plane up to the front face. Run after exporting stl_v4/shell.stl and
stl_v4/back.stl. Every number below mirrors a value in remote_case.scad or board.py.
"""
import itertools, sys
import numpy as np
import trimesh

STL = sys.argv[1] if len(sys.argv) > 1 else "stl_v4"
GAP = float(sys.argv[2]) if len(sys.argv) > 2 else 0.15         # components are grown by this much, so near-misses show up too

# ---- values from remote_case.scad
T, top_t, plate_t, wall = 15.8, 1.6, 1.6, 2.2
front_in = T - top_t
db_w, db_l, db_pcb, db_front, db_back = 42.89, 74.33, 1.6, 3.84, 4.63
usb_in, usb_x, usb_body_h, clr = 1.0, 1.22, 3.2, 0.3
lcd_from_ant, bl_w, bl_l = 6.34, 42.6, 60.0
bb_w, bb_l, bb_pcb = 43.0, 112.0, 1.6
sw_body, sw_total, smd_h, top_parts = 3.5, 7.0, 0.8, 4.4
batt = (34, 50, 5); foam = 0.5; board_gap = 6.0
ir_x = 12; ir_z = front_in - 1.9

db_y0 = wall + clr
db_top = front_in - 0.3 - db_front; db_z0 = db_top - db_pcb
bb_y0 = db_y0 + db_l + board_gap
batt_z0 = plate_t + foam
bb_z0 = batt_z0 + batt[2] + smd_h; bb_top = bb_z0 + bb_pcb


def box(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return b


def rbox(x0, x1, y0, y1, z0, z1, r):
    """box with its vertical edges rounded (r)"""
    from shapely.geometry import box as sbox
    p = sbox(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, 16)
    m = trimesh.creation.extrude_polygon(p, z1 - z0); m.apply_translation([0, 0, z0])
    return m


def rbox_y(x0, x1, y0, y1, z0, z1, r):
    """box running along y with its edges parallel to y rounded (r)"""
    m = rbox(x0, x1, z0, z1, y0, y1, r)               # built in x-z, extruded along "z"
    m.apply_transform([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])   # swap y and z
    return m


def cyl_y(x, y0, y1, z, d):
    c = trimesh.creation.cylinder(radius=d / 2, height=y1 - y0, sections=48)
    c.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    c.apply_translation([x, (y0 + y1) / 2, z])
    return c


def cyl_z(x, y, z0, z1, d):
    c = trimesh.creation.cylinder(radius=d / 2, height=z1 - z0, sections=48)
    c.apply_translation([x, y, (z0 + z1) / 2])
    return c


def bpos(bx, by):            # button-board coords -> model
    return bb_w / 2 - bx, bb_y0 + by


hw = db_w / 2
comp = {}
# display board
comp["display PCB"] = rbox(-hw, hw, db_y0, db_y0 + db_l, db_z0, db_z0 + db_pcb, 4.0)   # 4 mm corners (drawing)
ant = db_y0 + db_l                                  # antenna end (USB end faces the tip)
comp["LCD + touch glass"] = box(-bl_w / 2, bl_w / 2, ant - lcd_from_ant - bl_l, ant - lcd_from_ant, db_top, db_top + db_front)
comp["display back parts"] = box(-hw + 0.5, hw - 0.5, db_y0 + 1, ant - 1, db_z0 - db_back, db_z0)
# USB-C shell is a stadium (fully rounded ends), 8.94 x 3.2, face usb_in behind the PCB edge
usb_c, ur, uy0 = db_z0 - usb_body_h / 2, usb_body_h / 2, db_y0 + usb_in
comp["USB-C receptacle"] = trimesh.util.concatenate([
    box(usb_x - 4.47 + ur, usb_x + 4.47 - ur, uy0, uy0 + 7.35, usb_c - ur, usb_c + ur),
    cyl_y(usb_x - 4.47 + ur, uy0, uy0 + 7.35, usb_c, usb_body_h),
    cyl_y(usb_x + 4.47 - ur, uy0, uy0 + 7.35, usb_c, usb_body_h)])
# a USB-C plug fully inserted: spec-max overmold 12.35 x 6.5 from the receptacle face outwards
# it stops on the notch floor (usb_floor from the tip); its metal shell (8.34 x 2.56 stadium)
# passes the floor's hole and reaches the receptacle face
usb_floor = 1.85
comp["USB-C plug overmold"] = rbox_y(usb_x - 6.175, usb_x + 6.175, -10, usb_floor - 0.05, usb_c - 3.25, usb_c + 3.25, 2.0)
comp["USB-C plug metal"] = rbox_y(usb_x - 4.17, usb_x + 4.17, -10, uy0 - 0.01, usb_c - 1.28, usb_c + 1.28, 1.27)
# IR LEDs: 3 mm body, 3.8 mm flange behind the clip (y 7.15+), tip ~5.4 mm ahead of the flange
for sx in (-1, 1):
    comp[f"IR LED {'L' if sx > 0 else 'R'}"] = trimesh.util.concatenate([
        cyl_y(sx * ir_x, 7.2 - 5.4, 7.2, ir_z, 3.0), cyl_y(sx * ir_x, 7.2, 8.2, ir_z, 3.8)])
# button board
comp["button PCB"] = box(-bb_w / 2, bb_w / 2, bb_y0, bb_y0 + bb_l, bb_z0, bb_top)
SW = {"POWER": (7.5, 6.0), "UP": (21.5, 12.5), "LEFT": (8.5, 25.5), "OK": (21.5, 25.5), "RIGHT": (34.5, 25.5),
      "DOWN": (21.5, 38.5), "BACK": (8.5, 50.0), "HOME": (21.5, 50.0), "VOICE": (34.5, 50.0),
      "VOL+": (8.5, 77.0), "VOL-": (8.5, 90.0), "MUTE": (21.5, 83.5), "CH+": (34.5, 77.0), "CH-": (34.5, 90.0)}
for n, (bx, by) in SW.items():
    x, y = bpos(bx, by)
    comp[f"switch {n}"] = box(x - 3, x + 3, y - 3, y + 3, bb_top, bb_top + sw_body)
    comp[f"stem {n}"] = cyl_z(x, y, bb_top + sw_body, bb_top + sw_total, 3.5)
cx, cy = bpos(20.6, 63.5)
comp["MCP23017 DIP-28"] = box(cx - 18.0, cx + 18.0, cy - 4.6, cy + 4.6, bb_top, bb_top + top_parts)
qx, qy = bpos(12.5, 99.3)            # Q1 TO-92 (layout "pads"), legs spread; mounted to top_parts high
comp["Q1 TO-92"] = box(qx - 2.6, qx + 2.6, qy - 2.0, qy + 2.0, bb_top, bb_top + top_parts)
comp["copper-side SMDs"] = box(-bb_w / 2 + 1, bb_w / 2 - 1, bb_y0 + 1, bb_y0 + bb_l - 1, bb_z0 - smd_h, bb_z0)
mx, my = bpos(34.0, 7.0)
comp["INMP441 module"] = cyl_z(mx, my, bb_top + 0.05, bb_top + 0.05 + 2.6, 15.0)   # 2.1 measured + 0.5 solder
comp["battery 503450"] = box(-batt[0] / 2, batt[0] / 2, bb_y0 + 1, bb_y0 + 1 + batt[1], batt_z0, batt_z0 + batt[2])   # under the top half: the area under the chip is left for wires

# case, assembled
sh = trimesh.load(f"{STL}/shell.stl"); sh.apply_transform(np.diag([1, 1, -1, 1])); sh.apply_translation([0, 0, T])
bk = trimesh.load(f"{STL}/back.stl"); bk.apply_transform(np.diag([1, 1, -1, 1])); bk.apply_translation([0, 0, plate_t])
case = {"shell": sh, "back plate": bk}
for press in (0, 0.3):            # caps at rest and fully pressed
    cp = trimesh.load(f"{STL}/caps_asm{'' if not press else '_pressed'}.stl")
    comp[f"caps{' (pressed)' if press else ''}"] = cp

bad = 0
def report(a, b, ma, mb, grow):
    global bad
    g = ma.copy()
    if grow:
        # grow by GAP: cheap Minkowski for boxes/cylinders via scaling about the centre
        ext = g.bounds[1] - g.bounds[0]
        g.apply_translation(-g.centroid); g.apply_scale((ext + 2 * GAP) / ext); g.apply_translation(ma.centroid)
    try:
        hit = trimesh.boolean.intersection([g, mb], engine="manifold")
    except Exception as e:
        print(f"  ?? {a} vs {b}: {e}"); return
    if hit.is_empty or hit.volume < 1e-3:
        return
    bad += 1
    lo, hi = np.round(hit.bounds, 2)
    print(f"  {a:22s} x {b:12s} {hit.volume:8.3f} mm3   x[{lo[0]},{hi[0]}] y[{lo[1]},{hi[1]}] z[{lo[2]},{hi[2]}]")

print(f"Components vs case (grown {GAP} mm):")
for a, ma in comp.items():
    for b, mb in case.items():
        report(a, b, ma, mb, True)
print("Components vs each other (exact):")
skip = {("display PCB", "LCD + touch glass"), ("display PCB", "display back parts"), ("display PCB", "USB-C receptacle"),
        ("display back parts", "USB-C receptacle"), ("USB-C plug overmold", "USB-C receptacle"), ("USB-C plug overmold", "USB-C plug metal"), ("button PCB", "copper-side SMDs"), ("copper-side SMDs", "battery 503450")}
for (a, ma), (b, mb) in itertools.combinations(comp.items(), 2):
    # a pressed cap pushes its stem down, which these solids don't model; caps vs caps is the same parts
    if {a, b} & {"caps (pressed)"} and (a.startswith("stem") or b.startswith("stem") or {a, b} == {"caps", "caps (pressed)"}):
        continue
    # the caps' grip ribs press onto the stems by design (0.05 a side)
    if "caps" in (a, b) and (a.startswith("stem") or b.startswith("stem")):
        continue
    if (a, b) in skip or a.startswith("switch") and b.startswith("stem") or a.startswith("stem") and b.startswith("switch"):
        continue
    if ma.bounds[0][0] > mb.bounds[1][0] or mb.bounds[0][0] > ma.bounds[1][0]:
        continue
    report(a, b, ma, mb, False)
# Assembly path: boards and parts go in from the open back, straight up. Sweep each (convex)
# part from 20 mm below its place to its place and check the sweep against the shell.
print("Insertion from the back (swept, exact):")
for n in ["display PCB", "LCD + touch glass", "display back parts", "USB-C receptacle", "button PCB",
          "MCP23017 DIP-28", "Q1 TO-92", "INMP441 module", "battery 503450"] + [k for k in comp if k.startswith("switch")]:
    m = comp[n]
    sweep = trimesh.convex.convex_hull(np.vstack([m.vertices, m.vertices - [0, 0, 20]]))
    report(n + " (sweep)", "shell", sweep, case["shell"], False)
print("RESULT:", "no collisions" if not bad else f"{bad} collisions")
