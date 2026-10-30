"""Rebuild both viewers from case/stl_v4: the claude.ai page (scratchpad) and the local
viewer.html with download links."""
import base64, json, os, trimesh, numpy as np
SP = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(SP, "..", "stl_v4")   # page template lives beside this script
T, plate_t = 15.8, 1.6
b64 = lambda m: base64.b64encode(m.export(file_type="stl")).decode()
L = lambda f: trimesh.load(os.path.join(STL, f))
out = {f: b64(L(f + ".stl")) for f in ["shell", "back", "caps", "ir_test", "usb_test", "cap_fit_test"]}
# printable button board (made by pcb/make_stl.py, copper side up, mirrored)
BOARD = os.path.join(SP, "..", "..", "pcb", "stl", "button_board_print.stl")
bd = trimesh.load(BOARD); out["board"] = b64(bd)
# ...and in the case: component side up at bb_top, copper side down (a 180 deg turn about x)
bb_y0, bb_top, bb_l = 2.5 + 74.33 + 6.0, 9.5, 112.0
ba = bd.copy(); ba.apply_transform(np.diag([1, -1, -1, 1])); ba.apply_translation([-21.5, bb_y0 + bb_l, bb_top])
sh = L("shell.stl"); sh.apply_transform(np.diag([1, 1, -1, 1])); sh.apply_translation([0, 0, T])
bk = L("back.stl"); bk.apply_transform(np.diag([1, 1, -1, 1])); bk.apply_translation([0, 0, plate_t])
out["asm_shell"], out["asm_back"], out["asm_caps"], out["asm_board"] = b64(sh), b64(bk), b64(L("caps_asm.stl")), b64(ba)
meshes = "<script>const MESHES=" + json.dumps(out) + ";</script>\n"
head, tail = open(f"{SP}/viewer_head.html").read(), open(f"{SP}/viewer_tail.html").read()
open(f"{SP}/umote_case_v4.html", "w").write(head + meshes + tail)

files = [("shell.stl", "Shell", "front face down, no supports"), ("back.stl", "Back plate", "inner face down"),
         ("caps.stl", "Caps + 2 spacers", "flange down"), ("ir_test.stl", "IR test coupon", "as exported"),
         ("usb_test.stl", "USB-C test plate", "flat; 0.65 mm"),
         ("cap_fit_test.stl", "Cap fit test plate", "face down; holes 9.2 to 9.8"),
         ("button_board_print.stl", "Button board (print)", "copper side up; PETG/ASA")]
rows = "".join(f'<li><a href="{f}" download>{n}</a><span>{os.path.getsize(os.path.join(STL, f))/1e6:.1f} MB · {o}</span></li>' for f, n, o in files)
block = ('<div>\n      <div class="label">Download for slicing</div>\n      <ul class="dl">' + rows +
         '</ul>\n      <div class="sub">Already in print orientation: import into OrcaSlicer as-is.</div>\n    </div>\n    ')
anchor = '<div>\n      <div class="label">Show</div>'
css = (".dl { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }\n"
       ".dl li { display: flex; flex-direction: column; gap: 1px; }\n"
       ".dl a { color: var(--accent); font-weight: 500; text-decoration: none; font-size: 13.5px; }\n"
       ".dl a:hover, .dl a:focus-visible { text-decoration: underline; }\n"
       ".dl span { color: var(--muted); font-size: 12px; font-family: var(--mono); }\n</style>")
lh = head.replace(anchor, block + anchor, 1).replace("</style>", css, 1)
open(f"{STL}/viewer.html", "w").write('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
     '<meta name="viewport" content="width=device-width, initial-scale=1">\n' + lh + meshes + tail + "</html>\n")
print("built", os.path.getsize(f"{SP}/umote_case_v4.html"), os.path.getsize(f"{STL}/viewer.html"))
