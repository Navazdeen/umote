"""Grid A* router for a one-sided board, with optional wire jumpers.

Rules come from board.py: 1.0 mm traces, 0.8 mm clearance, 1.0 mm edge
clearance. Traces never pass between DIP pins because the inflated
keep-out of neighbouring pads closes that gap.
"""
import heapq, itertools, json, math, random, sys
import numpy as np
import shapely
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union

import board as B

G = 0.254                      # routing grid (mm)
MARGIN = 0.12                  # raster safety margin (mm)
W = B.TRACE_W
NX = int(round(B.BOARD_W / G)) + 1
NY = int(round(B.BOARD_H / G)) + 1
XS = np.arange(NX) * G
YS = np.arange(NY) * G
GX, GY = np.meshgrid(XS, YS)   # [iy, ix]


def pad_geom(p):
    if p.shape == "circle":
        return Point(p.x, p.y).buffer(p.w / 2, 24)
    if p.shape == "rect":
        return box(p.x - p.w / 2, p.y - p.h / 2, p.x + p.w / 2, p.y + p.h / 2)
    # oval (stadium)
    r = min(p.w, p.h) / 2
    if p.w >= p.h:
        seg = LineString([(p.x - p.w / 2 + r, p.y), (p.x + p.w / 2 - r, p.y)])
    else:
        seg = LineString([(p.x, p.y - p.h / 2 + r), (p.x, p.y + p.h / 2 - r)])
    return seg.buffer(r, 24)


def mask_of(geom):
    if geom is None or geom.is_empty:
        return np.zeros((NY, NX), bool)
    shapely.prepare(geom)
    return shapely.contains_xy(geom, GX, GY)


from astar import astar

KEEP = B.CLEARANCE + W / 2 + MARGIN                 # trace centre keep-out
PADZ = B.JUMPER_PAD / 2 + B.CLEARANCE + MARGIN      # jumper pad keep-out


def window_mask(geom):
    """Mask of grid cells inside geom, computed only over its bounding box."""
    x0, y0, x1, y1 = geom.bounds
    i0 = max(0, int(x0 / G) - 1); i1 = min(NX, int(x1 / G) + 2)
    j0 = max(0, int(y0 / G) - 1); j1 = min(NY, int(y1 / G) + 2)
    shapely.prepare(geom)
    m = shapely.contains_xy(geom, GX[j0:j1, i0:i1], GY[j0:j1, i0:i1])
    return (j0, j1, i0, i1), m


class Layer:
    """Per-net accumulated keep-out counts so 'blocked for net N' is cheap."""
    def __init__(self):
        self.all = np.zeros((NY, NX), np.int32)
        self.net = {}

    def add(self, net, geom):
        (j0, j1, i0, i1), m = window_mask(geom)
        self.all[j0:j1, i0:i1] += m
        self.net.setdefault(net, np.zeros((NY, NX), np.int32))[j0:j1, i0:i1] += m

    def other(self, net):
        own = self.net.get(net)
        return (self.all - own) > 0 if own is not None else self.all > 0


class Router:
    def __init__(self, parts):
        self.parts = parts
        self.copper = []
        self.traces, self.jumpers, self.fail = [], [], []
        self.keep, self.hard, self.padz = Layer(), Layer(), Layer()
        e = B.EDGE_CLEAR + W / 2 + MARGIN
        self.edge_block = ~((GX >= e) & (GX <= B.BOARD_W - e) & (GY >= e) & (GY <= B.BOARD_H - e))
        # antenna keep-out band along the top edge; SW1's pads sit in it and may be left downwards
        band = GY < B.ANT_KEEPOUT
        for part in parts:
            if part.ref == "SW1":
                for p in part.pads:
                    band &= (GX - p.x) ** 2 + (GY - p.y) ** 2 > 1.6 ** 2
        self.edge_block |= band
        for part in parts:
            for p in part.pads:
                # switch and 1206 pads get a wider berth so traces don't seal them off
                self._add(p.net, pad_geom(p), "pad", roomy=p.shape in ("circle", "rect"))
            # reserve a short escape lane out of every DIP / header / TO-92 pin so
            # other nets can't hug the row and wall the pins in
            for p in part.pads:
                d = None
                if part.kind == "DIP28":
                    d = (0, -1) if p.y < part.y else (0, 1)
                elif part.kind.startswith("HDR"):
                    if part.rot == 90:
                        d = (1, 0) if part.x < B.BOARD_W / 2 else (-1, 0)
                    else:
                        d = (0, -1)
                elif part.kind == "TO92_wide":
                    d = (0, 1)
                if d and p.net:
                    lane = LineString([(p.x, p.y), (p.x + d[0] * 3.2, p.y + d[1] * 3.2)]).buffer(0.45, 8)
                    self.keep.add(p.net, lane)

    def _add(self, net, geom, kind, roomy=False):
        self.copper.append((net, geom, kind))
        # foreign pads get a wider berth so traces don't seal off pad access
        self.keep.add(net, geom.buffer(KEEP + (0.5 if roomy else 0.0), 12))
        self.padz.add(net, geom.buffer(PADZ, 12))
        if kind in ("pad", "jpad"):
            self.hard.add(net, geom.buffer(KEEP, 12))

    def groups(self, net):
        items = [g for n, g, k in self.copper if n == net]
        for part in self.parts:
            if part.kind == "SW_6x6":
                for a, b in ((0, 1), (2, 3)):
                    pa, pb = part.pads[a], part.pads[b]
                    if pa.net == net:
                        items.append(LineString([(pa.x, pa.y), (pb.x, pb.y)]).buffer(0.01))
        # wire jumpers join their two pads electrically
        for jn, a, b in self.jumpers:
            if jn == net:
                items.append(LineString([a, b]).buffer(0.01))
        comps = []
        for g in items:
            hit = [c for c in comps if c.intersects(g)]
            merged = unary_union([g] + hit)
            comps = [c for c in comps if not any(c is h for h in hit)] + [merged]
        return comps

    def route_pair(self, net, sg, dg, allow_jump=True):
        blocked = self.keep.other(net) | self.edge_block
        hard = self.hard.other(net) | self.edge_block
        padable = ~(self.padz.other(net) | self.edge_block)
        src = mask_of(sg.buffer(-0.05)) & ~blocked
        dst = mask_of(dg.buffer(-0.05)) & ~blocked
        if not src.any() or not dst.any():
            return None
        res = astar(blocked.astype(np.uint8), hard.astype(np.uint8), padable.astype(np.uint8),
                    src, dst, allow_jump, int(3.0 / G), int(30 / G), 25.0, 0.6, 600_000)
        return res if len(res) else None

    def commit(self, net, res):
        seg = [(res[0, 0] * G, res[0, 1] * G)]
        for x, y, j in res[1:]:
            p = (x * G, y * G)
            if j:
                a = seg[-1]
                self._add_trace(net, seg)
                self.jumpers.append((net, a, p))
                for q in (a, p):
                    self._add(net, Point(q).buffer(B.JUMPER_PAD / 2, 24), "jpad")
                seg = [p]
            else:
                seg.append(p)
        self._add_trace(net, seg)

    def _add_trace(self, net, pts):
        if len(pts) < 2:
            return
        simp = [pts[0]]
        for i in range(1, len(pts) - 1):
            a, b, c = simp[-1], pts[i], pts[i + 1]
            if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) > 1e-9:
                simp.append(b)
        simp.append(pts[-1])
        self.traces.append((net, simp))
        self._add(net, LineString(simp).buffer(W / 2, 12), "trace")

    def route_net(self, net, allow_jump=True):
        while True:
            comps = self.groups(net)
            if len(comps) <= 1:
                return True
            pairs = sorted(itertools.combinations(range(len(comps)), 2),
                           key=lambda ab: comps[ab[0]].distance(comps[ab[1]]))
            for a, b in pairs[:2]:
                r = self.route_pair(net, comps[a], comps[b], allow_jump)
                if r is not None:
                    self.commit(net, r)
                    break
            else:
                self.fail.append(net)
                return False

    def length(self):
        return sum(LineString(p).length for _, p in self.traces)


def nets_of(parts):
    ns = {}
    for part in parts:
        for p in part.pads:
            if p.net:
                ns.setdefault(p.net, []).append(p)
    return {n: v for n, v in ns.items() if len(v) > 1 or n.startswith("BTN")}


def seed(r, layout):
    """Hand-placed structural traces, laid before the router so random net order can't waste
    the lanes they need. Coordinates: DIP pins are at x = 4.09 + 2.54 * k, rows at 59.69 / 67.31."""
    px = lambda pin: B.CHIP_X - 6.5 * 2.54 + ((pin - 1) if pin <= 14 else (28 - pin)) * 2.54
    up, lo = B.CHIP_Y - 3.81, B.CHIP_Y + 3.81
    # under the chip: 3V3 pin 18 -> pin 9 on the upper lane, GND pins 15-17 -> pin 10 on the lower
    r._add_trace("3V3", [(px(18), up), (px(18), 62.3), (px(9), 62.3), (px(9), lo)])
    r._add_trace("GND", [(px(15), up), (px(15), 64.5), (px(10), 64.5), (px(10), lo)])
    r._add_trace("GND", [(px(16), up), (px(16), 64.5)])
    r._add_trace("GND", [(px(17), up), (px(17), 64.5)])
    # POWER: SW1 down the left edge, round the chip's left end into pin 1
    r._add_trace("BTN_POWER", [(4.25, 8.25), (1.6, 10.9), (1.6, lo), (px(1), lo)])
    for net, pts in SEEDS.get(layout, []):
        r._add_trace(net, pts)


# per-layout extra seeds
SEEDS = {
    # INT round the chip's right end and down the right edge towards J5/R3
    "right": [("INT", [(B.CHIP_X - 6.5 * 2.54 + 8 * 2.54, B.CHIP_Y - 3.81), (B.CHIP_X - 6.5 * 2.54 + 8 * 2.54, 55.2), (40.6, 55.2)]),
              ("GND", [(B.CHIP_X + 6.5 * 2.54, B.CHIP_Y - 3.81), (40.6, 60.4)])],
    "bottom": [("INT", [(B.CHIP_X - 6.5 * 2.54 + 8 * 2.54, B.CHIP_Y - 3.81), (B.CHIP_X - 6.5 * 2.54 + 8 * 2.54, 55.6),
                        (40.6, 55.6), (40.6, 94.0)])],
}


def attempt(assign, order, allow_jump=True, log=None, layout="bottom", seeds=True):
    import time
    parts = B.build(assign, layout)
    r = Router(parts)
    if seeds:
        seed(r, layout)
    for n in order:
        t = time.time()
        ok = r.route_net(n, allow_jump)
        if log:
            log.write(f"    {n}: {'ok' if ok else 'FAIL'} {time.time()-t:.1f}s\n"); log.flush()
    return r, parts


# Top keys on GPA in left-to-right order (pin 28 is leftmost), POWER on GPB0 via the left edge.
TOP = {"BACK": 28, "LEFT": 27, "UP": 26, "OK": 25, "DOWN": 24, "RIGHT": 23, "HOME": 22, "VOICE": 21, "POWER": 1}
NEW = ["VOL_DOWN", "VOL_UP", "MUTE", "CH_DOWN", "CH_UP"]


def assignments():
    """Candidate pin maps: the 5 keys below the chip on GPB1-7 (pins 2-8), in an order that
    follows their left-to-right arrival under the chip."""
    import itertools
    seen = set()
    for pins in itertools.combinations(range(2, 9), 5):
        for order in (NEW, ["VOL_UP", "VOL_DOWN", "MUTE", "CH_DOWN", "CH_UP"],
                      ["VOL_DOWN", "VOL_UP", "MUTE", "CH_UP", "CH_DOWN"], ["VOL_UP", "VOL_DOWN", "MUTE", "CH_UP", "CH_DOWN"]):
            a = dict(TOP); a.update(dict(zip(order, pins)))
            k = tuple(sorted(a.items()))
            if k not in seen:
                seen.add(k); yield a


if __name__ == "__main__":
    layout = sys.argv[1] if len(sys.argv) > 1 else "bottom"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    rng = random.Random(1)
    best = None
    for assign in list(assignments())[:n]:
        nets = list(nets_of(B.build(assign, layout)).keys())
        for t in range(3):
            order = nets[:]
            order.sort(key=lambda q: (q in ("GND", "3V3"), q)) if t == 0 else rng.shuffle(order)
            r, parts = attempt(assign, order, layout=layout)
            sc = (len(r.fail), len(r.jumpers), r.length())
            print({k: v for k, v in assign.items() if k in NEW}, t, "fail", r.fail, "jumpers", len(r.jumpers), flush=True)
            if best is None or sc < best[0]:
                best = (sc, assign, order)
    print("BEST", best[0], best[1])
