"""v7 fit check: the bought parts as simple solids (the same models as v6, taken from
fit_check_v6.components with the bend at 0) against the three printed parts and each other; wire
paths; every part going in from the back; the back plates going on and coming off; moving parts.

Usage: python3 case/fit_check_v7.py [--module] [stl_dir] [grow_mm]      exit 1 on any undesigned collision
  --module: the printed carrier (pcb/make_carrier_stl.py) with the CJMCU-2317 MCP23017 module in
            its window, instead of the etched board's DIP-28
"""
import itertools, json, os, sys
import numpy as np
import trimesh
import fit_check_v6 as v6
from fit_check_v6 import hit, cyl, wire

# designed contacts
SKIP = {
    ("display PCB", "shell"), ("display PCB", "head back"),        # clamped between the face bosses and the plate's posts
    ("button PCB", "shell"),                                         # in its 4 clips, against the end stops
    ("IR LED L", "shell"), ("IR LED R", "shell"),                    # dome in the tip wall, body in its saddle
    ("EC11", "shell"), ("EC11 nut", "shell"),                        # bushing in the bulkhead's U-slot, nut against it
    ("EC11", "wheel"), ("EC11", "EC11 nut"), ("EC11", "carrier"),
    ("battery 46x105", "key back"),                                  # on the plate's flat deck (0.2 tape)
    ("display PCB", "LCD + touch glass"), ("display PCB", "display back parts"), ("display PCB", "USB-C receptacle"),
    ("display back parts", "USB-C receptacle"), ("USB-C plug overmold", "USB-C receptacle"),
    ("USB-C plug overmold", "USB-C plug metal"), ("button PCB", "copper-side SMDs"),
    ("copper-side SMDs", "battery 46x105"),
    ("wire BAT", "battery 46x105"), ("wire BAT", "display back parts"),
    ("wire roller", "carrier"), ("wire roller", "EC11"), ("wire roller", "MCP23017 DIP-28"),
    ("wire boards", "display back parts"), ("wire boards", "MCP23017 DIP-28"),
    ("wire roller", "MCP23017 module"), ("wire boards", "MCP23017 module"),   # the wires end on it
    ("button PCB", "MCP23017 module"),                                        # it sits in the carrier's window
    ("button PCB", "carrier spacers"),                                        # v7.2: printed on the carrier
    ("carrier spacers", "shell"), ("carrier spacers", "dpad ring"),          # v7.2: they stop 0.1 under the face (and a ring tab in it)
}
MODULE = (26.0, 21.0, 0.6)     # CJMCU-2317: length (x) and width (y), and the carrier's lip under it
EXACT = {"USB-C plug overmold", "USB-C plug metal"}
CASE = {"shell": "asm_shell", "head back": "asm_head_back", "key back": "asm_key_back", "wheel": "asm_wheel",
        "caps": "caps_asm", "dpad ring": "asm_dpad_ring", "dock": "asm_dock",
        "pogo plate": "asm_pogo_plate_a", "dock plate": "asm_dock_plate_a"}                      # the remote docked


def components(P, module=False):
    comp, head, key = v6.components(P)
    yh, yk, cyw, by = P["y_head_end"], P["y_key_start"], P["cy"], P["bb_y0"]
    cx, cyy = P["bb_w"] / 2 - 20.6, by + 63.5
    if module:
        # module PCB on the carrier's 0.6 lips (0.5 of through-hole solder under and over it), and
        # the SSOP-28 (10.5 x 8.0 with leads, 2.0 tall) on top. Window centre: board (21.5, 63.5).
        L, W, lip = MODULE
        mx, mz = P["bb_w"] / 2 - 21.5, P["bb_z0"] + lip
        del comp["MCP23017 DIP-28"]
        comp["MCP23017 module"] = trimesh.util.concatenate([
            v6.box(mx - L / 2, mx + L / 2, cyy - W / 2, cyy + W / 2, mz - 0.5, mz + 1.6 + 0.5),
            v6.box(mx - 5.25, mx + 5.25, cyy - 4.0, cyy + 4.0, mz + 1.6, mz + 1.6 + 2.0)])
        # v7.2: the carrier's spacer posts (pcb/make_carrier_stl.py), board top to 0.1 under the face
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pcb"))
        import make_carrier_stl as C
        comp["carrier spacers"] = trimesh.util.concatenate([
            cyl([P["bb_w"] / 2 - x, P["bb_y0"] + y, P["bb_top"]], [P["bb_w"] / 2 - x, P["bb_y0"] + y, P["bb_top"] + C.SPACER_H], C.SPACER_D)
            for x, y in C.SPACERS])
    # wires, all laid in from the back. Through the wheel zone they run in the -x notches of both
    # cross walls (x -15.3..-10, beside the wheel). The battery pair leaves the battery's top end,
    # crosses low under the board's start, and runs under the display's back parts to the BAT socket.
    comp["wire BAT"] = wire([[18, yk + 5.6, 3.2], [18, yk + 1.5, 2.5], [-11.2, yk + 1.5, 2.5], [-11.2, yk - 1, 3.5], [-11.2, yh + 3, 3.5],
                             [-11.2, yh - 1.5, 3.2], [-11.2, 40, 3.2], [12, 20, 3.4], [18, 18, 3.4]], 1.6)
    comp["wire boards"] = wire([[-18, 40, 3.0], [-12.9, 45, 3.0], [-12.9, yh - 1.5, 3.2], [-13.4, yh + 3, 6.5],
                                [-13.4, yk - 1, 6.5], [-13.4, yk + 3, 6.5], [-22.4, yk + 3, 6.5], [-22.4, by + 3, 8.6],
                                [-22.4, by + 4, 10.8], [-21.0, by + 6, 10.8], [-21.0, by + 15.5, 10.8], [-19.7, by + 17, 10.8], [-19.7, cyy - 6, 10.7], [-16.5, cyy - 4.6, 10.7]], 1.6)
    xc = P["ec11_xf"] + P["ec11_h"] + P["carrier"][0]
    comp["wire roller"] = wire([[xc + 0.9, cyw + 3, 8.0], [14.4, yk - 1, 4.5], [14.4, yk + 3, 4.5], [22.4, yk + 3, 4.5],
                                [22.4, by + 3, 8.6], [22.4, by + 4, 10.8], [20.4, by + 6, 10.8], [20.2, cyy - 3.8, 10.8]], 1.6)
    return comp


def sweep(m, v):
    return trimesh.convex.convex_hull(np.vstack([m.vertices, m.vertices + np.asarray(v, float)]))


def moved(m, v):
    c = m.copy(); c.apply_translation(v); return c


def fmt(h):
    lo, hi = np.round(h.bounds, 2)
    return f"{h.volume:.3f} mm3 x[{lo[0]},{hi[0]}] y[{lo[1]},{hi[1]}] z[{lo[2]},{hi[2]}]"


def main(argv):
    module = "--module" in argv
    argv = [a for a in argv if a != "--module"]
    stl = argv[0] if argv else os.path.join(os.path.dirname(__file__), "stl_v7")
    grow = float(argv[1]) if len(argv) > 1 else 0.15
    P = json.load(open(f"{stl}/params.json")); P["_stl"] = stl
    bad = []
    case = {n: trimesh.load(f"{stl}/{f}.stl", force="mesh") for n, f in CASE.items()}
    comp = components(P, module)
    print(f"Components vs case (grown {grow} mm):")
    for (a, ma), (b, mb) in itertools.product(comp.items(), case.items()):
        if (a, b) in SKIP or (a.startswith("stem") and b == "caps") or (a.startswith("switch") and b == "shell"):
            continue
        h = hit(ma, mb, 0.0 if a in EXACT else grow)
        if h is not None:
            bad.append(f"{a} x {b} {fmt(h)}")
    print("Components vs each other (exact):")
    for (a, ma), (b, mb) in itertools.combinations(comp.items(), 2):
        if (a, b) in SKIP or (b, a) in SKIP or {a.split()[0], b.split()[0]} == {"switch", "stem"}:
            continue
        h = hit(ma, mb)
        if h is not None:
            bad.append(f"{a} x {b} {fmt(h)}")
    print("Case parts vs each other (exact):")
    for (a, ma), (b, mb) in itertools.combinations(case.items(), 2):
        h = hit(ma, mb, tol=0.1)          # facet slivers where two printed parts' surfaces coincide
        if h is not None:
            bad.append(f"{a} x {b} {fmt(h)}")
    # everything goes into the shell from the back: sweep it 25 mm towards -z and check the sweep
    print("Insertion from the back (swept):")
    shell = case["shell"]
    board = comp["button PCB"].copy()      # the 4 clips flex 0.6 each as the board snaps past their hooks
    board.apply_transform(np.diag([(P["bb_w"] - 1.3) / P["bb_w"], 1, 1, 1]))
    chip = "MCP23017 module" if module else "MCP23017 DIP-28"
    roller = trimesh.util.concatenate([comp["EC11"], comp["EC11 nut"], comp["carrier"], case["wheel"]])
    for n, m in [("display PCB", comp["display PCB"]), ("LCD + touch glass", comp["LCD + touch glass"]), ("USB-C receptacle", comp["USB-C receptacle"]),
                 ("button PCB", board), (chip, comp[chip]), ("INMP441 module", comp["INMP441 module"]),
                 ("battery 46x105", comp["battery 46x105"])]:
        h = hit(sweep(m, [0, 0, -25]), shell, tol=0.05)
        if h is not None:
            bad.append(f"{n} can't go into the shell from the back: {fmt(h)}")
    for t in (1, 3, 6, 10, 14, 20):       # the contact plate isn't convex (T-rib): step it out instead of sweeping a hull
        h = hit(moved(case["pogo plate"], [0, 0, -t]), shell, tol=0.05)
        if h is not None:
            bad.append(f"pogo plate can't go into the shell from the back ({t} mm out): {fmt(h)}")
    for n in ("EC11", "EC11 nut", "carrier"):
        h = hit(sweep(comp[n], [0, 0, -25]), shell, tol=0.05)
        if h is not None and n != "EC11":
            bad.append(f"{n} can't go into the shell from the back: {fmt(h)}")
    # the EC11's bushing rides down the U-slot (designed contact with the bulkhead); its body and pins must clear
    body = v6.box(P["ec11_xf"] + 0.05, P["ec11_xf"] + P["ec11_h"] + P["carrier"][0] + 1.0, P["cy"] - P["ec11_d"] / 2, P["cy"] + P["ec11_d"] / 2,
                  P["axle_z"] - P["ec11_w"] / 2, P["axle_z"] + P["ec11_w"] / 2)
    h = hit(sweep(body, [0, 0, -25]), shell, tol=0.05)
    if h is not None:
        bad.append(f"EC11 body can't go into the shell from the back: {fmt(h)}")
    h = hit(sweep(cyl([P["whl_x"] - P["whl_w"] / 2, P["cy"], P["axle_z"]], [P["whl_x"] + P["whl_w"] / 2, P["cy"], P["axle_z"]], P["whl_d"], 96), [0, 0, -25]), shell, tol=0.05)
    if h is not None:
        bad.append(f"wheel can't go into the shell from the back: {fmt(h)}")
    # back plates. The head plate lifts straight off the shell. The key plate (battery door) goes on
    # and off along the 45 deg line of its tongues, past the head plate's bevel and the battery.
    print("Back plates on and off:")
    for t in (0.5, 1, 2, 4, 8, 20):
        h = hit(moved(case["head back"], [0, 0, -t]), shell, tol=0.05)
        if h is not None:
            bad.append(f"head plate jams {t} mm off: {fmt(h)}")
    for t in (0.3, 0.6, 1, 1.5, 2, 3, 4, 6):
        k = moved(case["key back"], [0, t, -t])
        for n, other in (("shell", shell), ("head back", case["head back"]), ("battery", comp["battery 46x105"]), ("pogo plate", case["pogo plate"])):
            h = hit(k, other, tol=0.05)
            if h is not None:
                bad.append(f"key plate jams on the {n}, {t} mm along its 45 deg line: {fmt(h)}")
    if hit(moved(case["key back"], [0, 0, -1.5]), shell, tol=0.05) is None:
        bad.append("key plate lifts straight off: the tongues don't hold it")
    print("Moving parts (pressed / tipped):")
    for label, swap in [("caps pressed", {"caps": "caps_asm_pressed"}), ("rocker tipped", {"caps": "caps_asm_rocker_tilt"})]:
        mv = {k: trimesh.load(f"{stl}/{v}.stl", force="mesh") for k, v in swap.items()}
        for k, mk in mv.items():
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
    print("Wheel swept:")
    sw = cyl([P["whl_x"] - P["whl_w"] / 2, P["cy"], P["axle_z"]], [P["whl_x"] + P["whl_w"] / 2, P["cy"], P["axle_z"]], P["whl_d"], 96)
    for b in ("shell", "head back", "key back"):
        h = hit(sw, case[b], 0.2)
        if h is not None:
            bad.append(f"wheel swept x {b} {fmt(h)}")
    for line in bad:
        print("  " + line)
    print("RESULT:", "no collisions" if not bad else f"{len(bad)} problems")
    return len(bad)


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
