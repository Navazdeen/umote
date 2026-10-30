"""Assembly and wire guide for the printed board, seen from the copper side (as printed, ridges
up), so it's mirrored left-right from board.py's component-side view. Reads best.pkl."""
import pickle, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import board as B
from route import pad_geom

OUT = sys.argv[1] if len(sys.argv) > 1 else "stl/button_board_copper_guide.png"
res = pickle.load(open("best.pkl", "rb"))
parts = B.build(res["assign"], res["layout"])
m = lambda x: B.BOARD_W - x                   # copper-side view
CU, PAD, TXT, WIRE = "#c47a30", "#c47a30", "#22408f", "#1a7a1a"

fig, ax = plt.subplots(figsize=(7, 13))
ax.add_patch(plt.Rectangle((0, 0), B.BOARD_W, B.BOARD_H, color="#ebe5d8", zorder=0))
for net, pts in res["traces"]:
    g = LineString([(m(x), y) for x, y in pts]).buffer(B.TRACE_W / 2, 8)
    ax.fill(*g.exterior.xy, color=CU, lw=0, zorder=1)
for part in parts:
    for p in part.pads:
        q = B.Pad(p.ref, p.num, m(p.x), p.y, p.net, p.shape, p.w, p.h, p.drill)
        ax.fill(*pad_geom(q).exterior.xy, color=PAD, lw=0, zorder=2)
        if p.drill:
            ax.add_patch(plt.Circle((q.x, q.y), p.drill / 2, color="w", zorder=3))
    if part.ref.startswith("SW"):
        ax.text(m(part.x), part.y + 1.0, part.label, fontsize=7, ha="center", color=TXT, weight="bold", zorder=5)
    elif part.ref != "J5":
        ax.text(m(part.x), part.y + (2.4 if part.ref == "U1" else 0), part.ref, fontsize=6.5, ha="center", va="center",
                color=TXT, weight="bold", zorder=5)
u1 = next(p for p in parts if p.ref == "U1")
pin1 = next(p for p in u1.pads if p.num == "1")
ax.annotate("pin 1", (m(pin1.x), pin1.y + 1.3), (m(pin1.x), pin1.y + 4), color="#b00", fontsize=7, ha="center",
            arrowprops=dict(arrowstyle="->", color="#b00", lw=0.8), zorder=6)
# the row of wire pads: names under each pad, display pin in brackets
j5 = next(p for p in parts if p.ref == "J5")
vb = [p.num for p in j5.pads if p.net == "VBAT"]
NAMES = {("K1", p.num): "LED1 - (cathode)" for p in j5.pads} | {("K2", p.num): "LED2 - (cathode)" for p in j5.pads}
if len(vb) > 1:
    NAMES[("VBAT", vb[0])] = "LED + (anodes)"
for p in j5.pads:
    lab = NAMES.get((p.net, p.num), p.net + ("" if B.J5_LABELS.get(p.net, p.net) == p.net else f" ({B.J5_LABELS[p.net]})"))
    ax.text(m(p.x), B.BOARD_H + 0.6, lab, fontsize=7, ha="center", va="top", color=WIRE, weight="bold", rotation=90)
ax.text(m(j5.x), B.BOARD_H + 17, "all wires: display board (ESP32 pin) and IR LEDs", fontsize=7, ha="center", va="top", color=WIRE)
# jumper wires (insulated, soldered pad to pad on this side)
for net, a, b in res["jumpers"]:
    ax.plot([m(a[0]), m(b[0])], [a[1], b[1]], color="#d00", lw=1.6, ls=(0, (4, 2)), zorder=7)
ax.set_xlim(-14, B.BOARD_W + 13); ax.set_ylim(B.BOARD_H + 20, -2); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("COPPER SIDE (as printed, ridges up)  -  top edge faces the display\n"
             "red dashed = insulated jumper wires: chip pin 20 -> INT pad, chip pin 9 -> 3V3 pad", fontsize=9)
fig.savefig(OUT, dpi=110, bbox_inches="tight"); plt.close(fig)
print("wrote", OUT)
