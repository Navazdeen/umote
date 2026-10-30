"""Background routing search with move-to-front net ordering and random
connector pin orders. Keeps the best result in best.pkl / best.png."""
import pickle, random, sys, time
import route as R
import board as B
from check import render, drc

rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
LIMIT = float(sys.argv[2]) if len(sys.argv) > 2 else 1500
assigns = list(R.assignments())
best = None
t0 = time.time()
log = open("route_log.txt", "w")


def score(r):
    return len(r.fail) * 1000 + len(r.jumpers) * 60 + r.length() / 10


it = 0
while time.time() - t0 < LIMIT:
    it += 1
    if best is None or rng.random() < 0.35:
        gpb, assign = rng.choice(assigns)
        j5 = B.J1_NETS[:] if best is None else rng.sample(B.J1_NETS, len(B.J1_NETS))
        j4 = rng.sample(B.JMIC_NETS, len(B.JMIC_NETS))
    else:
        assign, j5, j4 = best[1], best[2][:], best[3][:]
        if rng.random() < 0.3:      # small mutation of a connector order
            L = rng.choice([j5, j4]); i, k = rng.sample(range(len(L)), 2); L[i], L[k] = L[k], L[i]
    nets = list(R.nets_of(B.build(assign, j5, j4)).keys())
    order = nets[:]; rng.shuffle(order)
    local = None
    for rnd in range(12):                 # move-to-front on failures
        r, parts = R.attempt(assign, order, j5=j5, j4=j4)
        sc = score(r)
        if local is None or sc < local[0]:
            local = (sc, r, parts, order[:])
        if not r.fail:
            break
        order = r.fail + [n for n in order if n not in r.fail]
    sc, r, parts, order = local
    if best is None or sc < best[0]:
        v = drc(r.copper)
        best = (sc, assign, j5, j4, order)
        pickle.dump({"assign": assign, "j5": j5, "j4": j4, "order": order, "traces": r.traces,
                     "jumpers": r.jumpers, "fail": r.fail, "drc": v}, open("best.pkl", "wb"))
        render(parts, r.traces, r.jumpers, "best.png", f"fail={r.fail} jumpers={len(r.jumpers)} drc={len(v)}")
        log.write(f"{time.time()-t0:6.0f}s it={it} NEW BEST fail={r.fail} jumpers={len(r.jumpers)} len={r.length():.0f} drc={len(v)}\n")
        log.flush()
log.write(f"DONE after {it} iterations\n")
