"""Design-rule check and preview rendering."""
import itertools, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import box
import board as B
from route import pad_geom


def drc(copper, tol=0.03):
    """copper: list of (net, geom, kind). Returns list of violations."""
    bad = []
    outline = box(0, 0, B.BOARD_W, B.BOARD_H)
    inner = outline.buffer(-B.EDGE_CLEAR)
    for (n1, g1, k1), (n2, g2, k2) in itertools.combinations(copper, 2):
        if n1 == n2 and n1:
            continue
        d = g1.distance(g2)
        if d < B.CLEARANCE - tol:
            bad.append((round(d, 2), n1, k1, n2, k2, tuple(round(v, 1) for v in g1.centroid.coords[0])))
    for n, g, k in copper:
        if not inner.contains(g):
            bad.append(("edge", n, k, tuple(round(v, 1) for v in g.centroid.coords[0])))
    return bad


def render(parts, traces, jumpers, path, title=""):
    fig, ax = plt.subplots(figsize=(5, 11))
    ax.add_patch(plt.Rectangle((0, 0), B.BOARD_W, B.BOARD_H, fill=False, ec="k"))
    for net, pts in traces:
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color="#b87333", lw=B.TRACE_W * 72 / 25.4 * 11 / B.BOARD_H * 9.6, solid_capstyle="round", zorder=1)
    for part in parts:
        for p in part.pads:
            g = pad_geom(p)
            xs, ys = g.exterior.xy
            ax.fill(xs, ys, color="#d08a3a", zorder=2)
            if p.drill:
                ax.add_patch(plt.Circle((p.x, p.y), p.drill / 2, color="w", zorder=3))
        if part.body:
            w, h = part.body
            ax.add_patch(plt.Rectangle((part.x - w / 2, part.y - h / 2), w, h, fill=False, ec="#3355aa", lw=0.6, zorder=4))
        ax.text(part.x, part.y, part.ref, fontsize=5, ha="center", va="center", color="#3355aa", zorder=5)
    for net, a, b in jumpers:
        ax.plot([a[0], b[0]], [a[1], b[1]], color="red", lw=1.5, zorder=6)
    ax.set_xlim(-1, B.BOARD_W + 1); ax.set_ylim(B.BOARD_H + 1, -1)
    ax.set_aspect("equal"); ax.set_title(title, fontsize=8)
    fig.savefig(path, dpi=160, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    parts = B.build({})
    cu = [(p.net, pad_geom(p), "pad") for part in parts for p in part.pads]
    v = drc(cu)
    for x in v:
        print(x)
    print(len(v), "violations")
    render(parts, [], [], "/tmp/claude-0/pads.png", "pads only")
