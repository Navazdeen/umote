"""Compiled grid A* with optional straight 'jumper' hops over traces."""
import heapq
import numpy as np
from numba import njit

DX = np.array([1, -1, 0, 0, 1, 1, -1, -1], np.int64)
DY = np.array([0, 0, 1, -1, 1, -1, 1, -1], np.int64)
DC = np.array([1.0, 1.0, 1.0, 1.0, 1.414, 1.414, 1.414, 1.414])


@njit(cache=True)
def _h(ix, iy, x0, y0, x1, y1):
    dx = 0 if x0 <= ix <= x1 else (x0 - ix if ix < x0 else ix - x1)
    dy = 0 if y0 <= iy <= y1 else (y0 - iy if iy < y0 else iy - y1)
    m = min(dx, dy); M = max(dx, dy)
    return M + 0.414 * m


@njit(cache=True)
def astar(blocked, hard, padable, src, dst, allow_jump, jmin, jmax, jcost, turn, max_exp):
    NY, NX = blocked.shape
    INF = 1e18
    g = np.full((NY, NX, 9), INF)
    prev = np.full((NY, NX, 9, 3), -1, np.int64)   # px, py, pd
    pjump = np.zeros((NY, NX, 9), np.uint8)
    ys, xs = np.nonzero(dst)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    heap = [(0.0, 0.0, 0, 0, 0)]
    heap.pop()
    sy, sx = np.nonzero(src)
    for i in range(len(sx)):
        g[sy[i], sx[i], 8] = 0.0
        heapq.heappush(heap, (_h(sx[i], sy[i], x0, y0, x1, y1), 0.0, sx[i], sy[i], 8))
    exp = 0
    gx, gy, gd = -1, -1, -1
    while len(heap) > 0:
        f, gc, ix, iy, d = heapq.heappop(heap)
        if gc > g[iy, ix, d] + 1e-9:
            continue
        if dst[iy, ix]:
            gx, gy, gd = ix, iy, d
            break
        exp += 1
        if exp > max_exp:
            break
        for k in range(8):
            nx = ix + DX[k]; ny = iy + DY[k]
            if nx < 0 or ny < 0 or nx >= NX or ny >= NY or blocked[ny, nx]:
                continue
            if k >= 4 and (blocked[iy, nx] or blocked[ny, ix]):
                continue
            c = DC[k]
            if d != 8 and d != k:
                c += turn
            ng = gc + c
            if ng < g[ny, nx, k] - 1e-9:
                g[ny, nx, k] = ng
                prev[ny, nx, k, 0] = ix; prev[ny, nx, k, 1] = iy; prev[ny, nx, k, 2] = d
                pjump[ny, nx, k] = 0
                heapq.heappush(heap, (ng + _h(nx, ny, x0, y0, x1, y1), ng, nx, ny, k))
        if allow_jump and padable[iy, ix]:
            for k in range(4):
                L = 1
                crossed = False
                while L < jmax:
                    tx = ix + DX[k] * L; ty = iy + DY[k] * L
                    if tx < 0 or ty < 0 or tx >= NX or ty >= NY or hard[ty, tx]:
                        break
                    if blocked[ty, tx]:
                        crossed = True
                    elif crossed and padable[ty, tx]:
                        if L >= jmin:
                            ng = gc + jcost + L * 0.5
                            if ng < g[ty, tx, 8] - 1e-9:
                                g[ty, tx, 8] = ng
                                prev[ty, tx, 8, 0] = ix; prev[ty, tx, 8, 1] = iy; prev[ty, tx, 8, 2] = d
                                pjump[ty, tx, 8] = 1
                                heapq.heappush(heap, (ng + _h(tx, ty, x0, y0, x1, y1), ng, tx, ty, 8))
                        break
                    L += 1
    if gx < 0:
        return np.zeros((0, 3), np.int64)
    out = []
    cx, cy, cd = gx, gy, gd
    while cx >= 0:
        out.append((cx, cy, np.int64(pjump[cy, cx, cd])))
        px = prev[cy, cx, cd, 0]; py = prev[cy, cx, cd, 1]; pd = prev[cy, cx, cd, 2]
        cx, cy, cd = px, py, pd
    res = np.zeros((len(out), 3), np.int64)
    for i in range(len(out)):
        res[i, 0] = out[len(out) - 1 - i][0]
        res[i, 1] = out[len(out) - 1 - i][1]
        res[i, 2] = out[len(out) - 1 - i][2]
    return res
