"""v6 fit check: components as simple solids, in assembled coordinates, against the assembled case
parts (case/stl_v6/asm_*.stl) and against each other; wire paths; insertion paths.

Every number comes from case/stl_v6/params.json (written by case/v5/export.sh). The head half's
components are built straight and turned by the same bend as head_xf() in profile.scad.
Usage: python3 case/fit_check_v5.py [stl_dir] [grow_mm]      exit 1 on any undesigned collision
"""
import itertools, json, os, sys
import numpy as np
import trimesh

# designed contacts: (component, case part) or (component, component) pairs that touch on purpose
SKIP = {
    ("display PCB", "head body"),                      # sits on its 4 posts
    ("display PCB", "head panel"),                     # clamped by the panel's 4 bosses
    ("button PCB", "key panel"),                        # clipped to the panel
    ("button PCB", "key body"),                          # rests on the prongs' top (0.2 clear) / bottom stops
    ("IR LED L", "head panel"), ("IR LED R", "head panel"),     # in their clips
    ("IR LED L", "head body"), ("IR LED R", "head body"),       # dome against the tip skin
    ("EC11", "frame"), ("EC11 nut", "frame"),            # frame top and nut clamp the bulkhead
    ("EC11", "wheel"),                                   # the shaft in the wheel's D-bore
    ("EC11", "EC11 nut"), ("EC11", "carrier"),           # nut on the bushing; pins through the carrier
    ("battery 46x105", "key body"),                      # on the floor (foam)
    ("carrier", "ridge"), ("carrier", "frame"),          # spans the collar floor to the cap
    ("display PCB", "LCD + touch glass"), ("display PCB", "display back parts"), ("display PCB", "USB-C receptacle"),
    ("display back parts", "USB-C receptacle"), ("USB-C plug overmold", "USB-C receptacle"),
    ("USB-C plug overmold", "USB-C plug metal"), ("button PCB", "copper-side SMDs"),
    ("copper-side SMDs", "battery 46x105"),
    ("wire BAT", "battery 46x105"), ("wire BAT", "display back parts"),
    ("wire roller", "carrier"), ("wire roller", "EC11"), ("wire roller", "MCP23017 DIP-28"),
    ("wire boards", "display back parts"), ("wire boards", "MCP23017 DIP-28"),
}
# spec-maximum sizes already: checked exactly, not grown
EXACT = {"USB-C plug overmold", "USB-C plug metal"}
CASE = {"head body": "asm_head_body", "head panel": "asm_head_panel", "frame": "asm_frame", "ridge": "asm_ridge",
        "key body": "asm_key_body", "key panel": "asm_key_panel", "wheel": "asm_wheel",
        "caps": "caps_asm", "dpad ring": "asm_dpad_ring", "dock": "asm_dock", "grip pad": "asm_grip_pad",
        "pogo plate": "asm_pogo_plate_a", "dock plate": "asm_dock_plate_a"}                      # the remote docked
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
    for m in head.values():
        m.apply_transform(H)
    comp = {**head, **key}
    stl = P["_stl"]
    comp["EC11"] = trimesh.load(f"{stl}/asm_ec11.stl")
    comp["EC11 nut"] = trimesh.load(f"{stl}/asm_nut.stl")
    comp["carrier"] = trimesh.load(f"{stl}/asm_carrier.stl")
    # wires. Through the wheel zone everything runs in the frame's -x channel (x -15.3..-10, beside
    # the wheel), through notches at the bottom of both end walls. The battery pair leaves the
    # battery's end, crosses the 1.5 gap to the channel; in the head it runs under the display's back
    # parts to the BAT socket (+x, y 18). The inter-board set: over the button board's -x edge (as v5),
    # down into the channel, under the display in the head. The roller's three: off the carrier's
    # back (+x), out of the frame's key-end notch, over the button board's +x edge to the MCP23017.
    hp = lambda p: trimesh.transform_points([p], H)[0]
    yh, yk, cyw = P["y_head_end"], P["y_key_start"], P["cy"]
    # all three cross the 7 mm zone under the button board's start (the battery starts after it):
    # BAT at z 3.5, the inter-board set at 6.5 (under the SMDs at 7.5), the roller at 4.5
    comp["wire BAT"] = wire([[18, yk + 6, 3.5], [-11.2, yk + 6, 3.5], [-11.2, yk - 1, 3.5], [-11.2, yh + 3, 3.5],
                             hp([-11.2, yh - 1.5, 3.0]), hp([-11.2, 40, 3.0]), hp([12, 20, 3.0]), hp([18, 18, 3.0])], 1.6)
    comp["wire boards"] = wire([hp([-18, 40, 3.0]), hp([-13.4, 45, 3.0]), hp([-13.4, yh - 1.5, 3.2]), [-13.4, yh + 3, 6.5],
                                [-13.4, yk - 1, 6.5], [-13.4, yk + 3, 6.5], [-22.4, yk + 3, 6.5], [-22.4, P["bb_y0"] + 3, 8.6],
                                [-22.4, P["bb_y0"] + 4, 10.8], [-21.0, P["bb_y0"] + 6, 10.8], [-21.0, P["bb_y0"] + 15.5, 10.8], [-19.7, P["bb_y0"] + 17, 10.8], [-19.7, cyy - 6, 10.7], [-16.5, cyy - 4.6, 10.7]], 1.6)
    xc = P["ec11_xf"] + P["ec11_h"] + P["carrier"][0]
    comp["wire roller"] = wire([[xc + 0.9, cyw + 3, 8.0], [14.4, yk - 1, 4.5], [14.4, yk + 3, 4.5], [22.4, yk + 3, 4.5],
                                [22.4, P["bb_y0"] + 3, 8.6], [22.4, P["bb_y0"] + 4, 10.8], [20.4, P["bb_y0"] + 6, 10.8], [20.2, cyy - 3.8, 10.8]], 1.6)
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
    stl = argv[0] if argv else os.path.join(os.path.dirname(__file__), "stl_v6")
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
        h = hit(ma, mb, 0.0 if a in EXACT else grow)
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
    for n, up in [("button PCB", 20), ("MCP23017 DIP-28", 20), ("battery 46x105", 20)]:   # v6: the battery goes in from the front too
        m = comp[n]; s = trimesh.convex.convex_hull(np.vstack([m.vertices, m.vertices + [0, 0, up]]))
        if "key body" in case and hit(s, case["key body"]) is not None:
            bad.append(f"{n} can't go into the key body")
    # moving parts in their other positions: every cap pressed, the VOL rocker tipped, the roller pressed
    print("Moving parts (pressed / tipped):")
    for label, swap in [("caps pressed", {"caps": "caps_asm_pressed"}), ("rocker tipped", {"caps": "caps_asm_rocker_tilt"})]:
        moved = {k: trimesh.load(f"{stl}/{v}.stl", force="mesh") for k, v in swap.items()}
        for k, mk in moved.items():
            for a, ma in comp.items():
                if (a, k) in SKIP or (a.startswith("stem") and k == "caps"):
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
    # the wheel turns: its full (un-knurled) cylinder must clear the frame and the ridge
    print("Wheel swept:")
    sw = cyl([P["whl_x"] - P["whl_w"] / 2, P["cy"], P["axle_z"]], [P["whl_x"] + P["whl_w"] / 2, P["cy"], P["axle_z"]], P["whl_d"], 96)
    for b in ("frame", "ridge", "key body", "head body"):
        if b in case:
            h = hit(sw, case[b], 0.2)
            if h is not None:
                bad.append(f"wheel swept x {b} {h.volume:.3f} mm3")
    for line in bad:
        print("  " + line)
    print("RESULT:", "no collisions" if not bad else f"{len(bad)} problems")
    return len(bad)


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
