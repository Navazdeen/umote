"""v5 fit check: components as simple solids, in assembled coordinates, against the assembled case
parts (case/stl_v5/asm_*.stl) and against each other; wire paths; insertion paths.

Every number comes from case/stl_v5/params.json (written by case/v5/export.sh). The head half's
components are built straight and turned by the same bend as head_xf() in profile.scad.
Usage: python3 case/fit_check_v5.py [stl_dir] [grow_mm]      exit 1 on any undesigned collision
"""
import itertools, json, os, sys
import numpy as np
import trimesh

# designed contacts: (component, case part) or (component, component) pairs that touch on purpose
SKIP = {
    ("display PCB", "head body"),                      # sits on its 4 posts
    ("USB-C plug overmold", "head body"),               # stops on the notch floor (v4)
    ("button PCB", "key panel"),                        # clipped to the panel
    ("button PCB", "key body"),                          # rests on the prongs' top (0.2 clear) / bottom stops
    ("IR LED L", "head panel"), ("IR LED R", "head panel"),     # in their clips
    ("IR LED L", "head body"), ("IR LED R", "head body"),       # dome against the tip skin
    ("EC11", "cradle"),                                  # sits on the cradle plate
    ("tact 6x6", "collar"), ("tact 6x6", "cradle"),      # on the collar floor; the arm rests on its plunger
    ("battery 46x105", "key body"),                      # on the floor (foam)
    ("display PCB", "LCD + touch glass"), ("display PCB", "display back parts"), ("display PCB", "USB-C receptacle"),
    ("display back parts", "USB-C receptacle"), ("USB-C plug overmold", "USB-C receptacle"),
    ("USB-C plug overmold", "USB-C plug metal"), ("button PCB", "copper-side SMDs"),
    ("copper-side SMDs", "battery 46x105"),
    ("wire BAT", "battery 46x105"), ("wire BAT", "display back parts"),
    ("wire roller", "EC11"), ("wire roller", "MCP23017 DIP-28"),
}
CASE = {"head body": "asm_head_body", "head panel": "asm_head_panel", "collar": "asm_collar",
        "key body": "asm_key_body", "key panel": "asm_key_panel", "wheel": "asm_wheel", "cradle": "asm_cradle",
        "caps": "caps_asm", "dpad ring": "asm_dpad_ring", "magnet plate": "asm_magnet_plate",
        "dock": "asm_dock"}                      # the remote docked
OPTIONAL = set()


def box(x0, x1, y0, y1, z0, z1):
    b = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    b.apply_translation([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return b


def cyl(p0, p1, d, sections=32):
    return trimesh.creation.cylinder(radius=d / 2, segment=[p0, p1], sections=sections)


def rbox_y(x0, x1, y0, y1, z0, z1, r):
    from shapely.geometry import box as sbox
    p = sbox(x0 + r, z0 + r, x1 - r, z1 - r).buffer(r, 16)
    m = trimesh.creation.extrude_polygon(p, y1 - y0)
    m.apply_transform([[1, 0, 0, 0], [0, 0, 1, y0], [0, 1, 0, 0], [0, 0, 0, 1]])
    return m


def wire(points, d):
    """a wire bundle: capsules along a polyline"""
    parts = [cyl(a, b, d, 16) for a, b in zip(points[:-1], points[1:])]
    parts += [trimesh.creation.icosphere(subdivisions=1, radius=d / 2).apply_translation(p) for p in points[1:-1]]
    return trimesh.boolean.union(parts, engine="manifold")


def head_matrix(P):
    a = -np.radians(P["theta"])
    T = np.eye(4); T[:3, 3] = [0, P["y_head_end"], P["T"]]
    R = trimesh.transformations.rotation_matrix(a, [1, 0, 0])
    Ti = np.eye(4); Ti[:3, 3] = [0, -P["y_head_end"], -P["T"]]
    return T @ R @ Ti


def components(P):
    H = head_matrix(P)
    head, key = {}, {}
    hw = P["db_w"] / 2; ant = P["db_end"]; db_z0, db_top = P["db_z0"], P["db_top"]
    head["display PCB"] = box(-hw, hw, P["db_y0"], ant, db_z0, db_z0 + P["db_pcb"])
    head["LCD + touch glass"] = box(-21.3, 21.3, ant - P["lcd_from_ant"] - P["lcd_l"], ant - P["lcd_from_ant"], db_top, db_top + P["db_front"])
    back = box(-hw + 0.5, hw - 0.5, P["db_y0"] + 1, ant - 1, db_z0 - P["db_back"], db_z0)
    # the board's back is clear round its four corner holes (reference/board_back.jpg)
    for sx in (-1, 1):
        for y in (P["db_y0"] + 4, ant - 4):
            back = trimesh.boolean.difference([back, cyl([sx * (hw - 4), y, db_z0 - 6], [sx * (hw - 4), y, db_z0 + 1], 6.0)], engine="manifold")
    head["display back parts"] = back
    uc, ur, uy0, ux = db_z0 - P["usb_body_h"] / 2, P["usb_body_h"] / 2, P["db_y0"] + P["usb_in"], P["usb_x"]
    head["USB-C receptacle"] = trimesh.boolean.union([box(ux - 4.47 + ur, ux + 4.47 - ur, uy0, uy0 + 7.35, uc - ur, uc + ur),
        cyl([ux - 4.47 + ur, uy0, uc], [ux - 4.47 + ur, uy0 + 7.35, uc], P["usb_body_h"]),
        cyl([ux + 4.47 - ur, uy0, uc], [ux + 4.47 - ur, uy0 + 7.35, uc], P["usb_body_h"])], engine="manifold")
    head["USB-C plug overmold"] = rbox_y(ux - 6.175, ux + 6.175, -10, P["usb_floor"] - 0.05, uc - 3.25, uc + 3.25, 2.0)
    head["USB-C plug metal"] = rbox_y(ux - 4.17, ux + 4.17, -10, uy0 - 0.01, uc - 1.28, uc + 1.28, 1.27)
    # IR LEDs, tilted theta down at the tip about the tip wall's inner face (as ir_xf())
    tw, a = P["tip_wall"], np.radians(P["theta"])
    d = np.array([0, np.cos(a), np.sin(a)])
    for sx, n in ((1, "IR LED L"), (-1, "IR LED R")):
        o = np.array([sx * P["ir_x"], tw, P["ir_z"]])
        f = lambda t: o + d * (t - tw)
        head[n] = trimesh.boolean.union([cyl(f(7.2 - 5.4), f(7.2), 3.0), cyl(f(7.2), f(8.2), 3.8)], engine="manifold")
    bp = lambda bx, by: (P["bb_w"] / 2 - bx, P["bb_y0"] + by)
    bb_z0, bb_top = P["bb_z0"], P["bb_top"]
    key["button PCB"] = box(-P["bb_w"] / 2, P["bb_w"] / 2, P["bb_y0"], P["bb_y0"] + P["bb_l"], bb_z0, bb_top)
    SW = {"POWER": (7.5, 6.0), "UP": (21.5, 12.5), "LEFT": (8.5, 25.5), "OK": (21.5, 25.5), "RIGHT": (34.5, 25.5),
          "DOWN": (21.5, 38.5), "BACK": (8.5, 50.0), "HOME": (21.5, 50.0), "VOICE": (34.5, 50.0),
          "VOL+": (8.5, 77.0), "VOL-": (8.5, 90.0), "MUTE": (21.5, 83.5), "CH+": (34.5, 77.0), "CH-": (34.5, 90.0)}
    for n, (bx, by) in SW.items():
        x, y = bp(bx, by)
        key[f"switch {n}"] = box(x - 3, x + 3, y - 3, y + 3, bb_top, bb_top + P["sw_body"])
        key[f"stem {n}"] = cyl([x, y, bb_top + P["sw_body"]], [x, y, bb_top + P["sw_total"]], 3.5)
    cx, cyy = bp(20.6, 63.5)
    key["MCP23017 DIP-28"] = box(cx - 18.0, cx + 18.0, cyy - 4.6, cyy + 4.6, bb_top, bb_top + P["top_parts"])
    qx, qy = bp(12.5, 99.3)
    key["Q1 TO-92"] = box(qx - 2.6, qx + 2.6, qy - 2.0, qy + 2.0, bb_top, bb_top + P["top_parts"])
    key["copper-side SMDs"] = box(-P["bb_w"] / 2 + 1, P["bb_w"] / 2 - 1, P["bb_y0"] + 1, P["bb_y0"] + P["bb_l"] - 1, bb_z0 - P["smd_h"], bb_z0)
    mx, my = bp(34.0, 7.0)
    key["INMP441 module"] = cyl([mx, my, bb_top + 0.05], [mx, my, bb_top + 2.65], 15.0)
    b = P["batt"]
    key["battery 46x105"] = box(-b[0] / 2, b[0] / 2, P["batt_y0"], P["batt_y0"] + b[1], P["batt_z0"], P["batt_z0"] + b[2])
    tc, tk = P["tact_c"], P["tact"]
    key["tact 6x6"] = box(tc[0] - tk[0] / 2, tc[0] + tk[0] / 2, tc[1] - tk[1] / 2, tc[1] + tk[1] / 2, P["floor_t"], P["floor_t"] + tk[2])
    for m in head.values():
        m.apply_transform(H)
    comp = {**head, **key}
    stl = P["_stl"]
    comp["EC11"] = trimesh.load(f"{stl}/asm_ec11.stl")
    # wires: the battery pair beside the boards' +x edges, under the display PCB's level in the head;
    # the roller's three over the button board's +x edge to the MCP23017's pins 2 and 6
    hp = lambda p: trimesh.transform_points([p], H)[0]
    comp["wire BAT"] = wire([[20, P["batt_y0"] - 0.4, 5.0], [22.6, P["batt_y0"] - 2.0, 6.2], [22.6, P["bb_y0"] + 1.7, 8.8],
                             [22.6, P["y_head_end"] + 2, 8.8], hp([22.6, P["y_head_end"] - 1.5, 8.8]), hp([22.6, 70, 6.0]),
                             hp([22.6, 20, 6.0]), hp([18, 18, 6.0])], 1.6)
    comp["wire roller"] = wire([[13.5, P["cy"], 6.0], [20.4, P["cy"] + 4, 10.5], [20.4, P["bb_y0"] + 2, 10.8],
                                [20.2, cyy - 3.8, 10.8]], 1.6)
    return comp, set(head), set(key)


def hit(a, b, grow=0.0, tol=1e-3):
    if grow:
        a = a.copy(); ext = a.bounds[1] - a.bounds[0]; c = a.centroid
        a.apply_translation(-c); a.apply_scale((ext + 2 * grow) / np.maximum(ext, 1e-6)); a.apply_translation(c)
    if np.any(a.bounds[0] > b.bounds[1]) or np.any(b.bounds[0] > a.bounds[1]):
        return None
    h = trimesh.boolean.intersection([a, b], engine="manifold")
    return None if h.is_empty or h.volume < tol else h


def main(argv):
    stl = argv[0] if argv else os.path.join(os.path.dirname(__file__), "stl_v5")
    grow = float(argv[1]) if len(argv) > 1 else 0.15
    P = json.load(open(f"{stl}/params.json")); P["_stl"] = stl
    bad = []
    case = {}
    for n, f in CASE.items():
        if os.path.exists(f"{stl}/{f}.stl"):
            case[n] = trimesh.load(f"{stl}/{f}.stl", force="mesh")
        elif n not in OPTIONAL:
            bad.append(f"missing case part {f}.stl")
    comp, head, key = components(P)
    print(f"Components vs case (grown {grow} mm):")
    for (a, ma), (b, mb) in itertools.product(comp.items(), case.items()):
        if (a, b) in SKIP or (a.startswith("stem") and b == "caps") or (a.startswith("switch") and b == "key panel"):
            continue
        h = hit(ma, mb, grow)
        if h is not None:
            lo, hi = np.round(h.bounds, 2); bad.append(f"{a} x {b} {h.volume:.3f} mm3 x[{lo[0]},{hi[0]}] y[{lo[1]},{hi[1]}] z[{lo[2]},{hi[2]}]")
    print("Components vs each other (exact):")
    for (a, ma), (b, mb) in itertools.combinations(comp.items(), 2):
        if (a, b) in SKIP or (b, a) in SKIP or {a.split()[0], b.split()[0]} == {"switch", "stem"}:
            continue
        h = hit(ma, mb)
        if h is not None:
            lo, hi = np.round(h.bounds, 2); bad.append(f"{a} x {b} {h.volume:.3f} mm3 x[{lo[0]},{hi[0]}] y[{lo[1]},{hi[1]}] z[{lo[2]},{hi[2]}]")
    print("Case parts vs each other (exact):")
    for (a, ma), (b, mb) in itertools.combinations(case.items(), 2):
        h = hit(ma, mb, tol=0.1)          # facet slivers where two printed parts' surfaces coincide
        if h is not None:
            lo, hi = np.round(h.bounds, 2); bad.append(f"{a} x {b} {h.volume:.3f} mm3 x[{lo[0]},{hi[0]}] y[{lo[1]},{hi[1]}] z[{lo[2]},{hi[2]}]")
    # insertion: everything goes into its body from the face side; sweep it 20 mm up (along the
    # half's own z for the head) and check the sweep against that body
    print("Insertion from the face (swept):")
    # the display board goes in tip first: down 20 mm with 1.5 mm to spare at the tip, then slid under the tip rim
    Hd = lambda v: trimesh.transform_points([v], head_matrix(P))[0] - trimesh.transform_points([[0, 0, 0]], head_matrix(P))[0]
    # (not "display back parts": that box is a conservative stand-in; the real parts clear the posts)
    for n in ["display PCB", "LCD + touch glass", "USB-C receptacle"]:
        m = comp[n]; a, b = Hd([0, 1.5, 20]), Hd([0, 1.5, 0])
        s1 = trimesh.convex.convex_hull(np.vstack([m.vertices + a, m.vertices + b]))
        s2 = trimesh.convex.convex_hull(np.vstack([m.vertices + b, m.vertices]))
        if "head body" in case and (hit(s1, case["head body"]) is not None or hit(s2, case["head body"]) is not None):
            bad.append(f"{n} can't go into the head body")
    for n, up in [("button PCB", 20), ("MCP23017 DIP-28", 20), ("battery 46x105", -20)]:   # the battery goes in from the back
        m = comp[n]; s = trimesh.convex.convex_hull(np.vstack([m.vertices, m.vertices + [0, 0, up]]))
        if "key body" in case and hit(s, case["key body"]) is not None:
            bad.append(f"{n} can't go into the key body")
    # moving parts in their other positions: every cap pressed, the VOL rocker tipped, the roller pressed
    print("Moving parts (pressed / tipped):")
    for label, swap in [("caps pressed", {"caps": "caps_asm_pressed"}), ("rocker tipped", {"caps": "caps_asm_rocker_tilt"}),
                        ("roller pressed", {"cradle": "asm_cradle_pressed", "wheel": "asm_wheel_pressed"})]:
        moved = {k: trimesh.load(f"{stl}/{v}.stl", force="mesh") for k, v in swap.items()}
        for k, mk in moved.items():
            for a, ma in comp.items():
                if (a, k) in SKIP or (a.startswith("stem") and k == "caps") or (a in ("EC11", "tact 6x6") and k == "cradle"):
                    continue
                h = hit(ma, mk)
                if h is not None:
                    bad.append(f"{label}: {a} x {k} {h.volume:.3f} mm3")
            for b, mb in case.items():
                if b in swap:
                    continue
                h = hit(mk, mb, tol=0.1)
                if h is not None:
                    bad.append(f"{label}: {k} x {b} {h.volume:.3f} mm3")
    for line in bad:
        print("  " + line)
    print("RESULT:", "no collisions" if not bad else f"{len(bad)} problems")
    return len(bad)


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
