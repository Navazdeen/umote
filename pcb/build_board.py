"""Build the 14-key button board: the hand route (hand_route.py) plus the router for whatever is
left (the IR driver), then DRC. Writes best.pkl (for export.py / make_stl.py) and board.png."""
import pickle, sys
import board as B, route as R, hand_route as H
from check import drc, render

LAYOUT = "pads"
parts = B.build(H.ASSIGN, LAYOUT)
r = R.Router(parts)
H.seed(r, LAYOUT)
left = [n for n in R.nets_of(parts) if len(r.groups(n)) > 1]
print("left for the router:", left)
order = sorted(left, key=lambda n: (n == "GND", n))
for n in order:
    ok = r.route_net(n, allow_jump=True)
    print(f"  {n}: {'ok' if ok else 'FAILED'}")
v = drc(r.copper)
for x in v: print("DRC", x)
print(f"fail={r.fail} jumpers={len(r.jumpers)} drc={len(v)} traces={len(r.traces)}")
render(parts, r.traces, r.jumpers, "board.png", f"14-key board: fail={r.fail} jumpers={len(r.jumpers)} drc={len(v)}")
pickle.dump({"assign": H.ASSIGN, "layout": LAYOUT, "traces": r.traces, "jumpers": r.jumpers,
             "fail": r.fail, "drc": v}, open("best.pkl", "wb"))
