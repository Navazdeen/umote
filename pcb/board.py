"""Remote button board: parts, pads and nets.

Coordinates are in mm, viewed from the COMPONENT side, origin at the board's
top-left corner, x to the right, y towards the bottom (towards the remote's
charging end). Copper is on the opposite (bottom) side.
"""
import math

BOARD_W = 43.0
BOARD_H = 112.0

ANT_KEEPOUT = 5.5    # copper-free band at the top edge (ESP32 antenna faces it), bar SW1's pads
TRACE_W = 1.0        # default signal trace
POWER_W = 1.5        # VBAT / IR LED current paths
CLEARANCE = 0.8      # copper-to-copper
EDGE_CLEAR = 1.0     # copper-to-board-edge
JUMPER_PAD = 2.0


class Pad:
    def __init__(self, ref, num, x, y, net, shape="circle", w=2.0, h=2.0, drill=0.8):
        self.ref, self.num, self.x, self.y = ref, str(num), x, y
        self.net, self.shape, self.w, self.h, self.drill = net, shape, w, h, drill

    @property
    def name(self):
        return f"{self.ref}.{self.num}"


class Part:
    def __init__(self, ref, kind, x, y, rot, value, pads, label=None, body=None):
        self.ref, self.kind, self.x, self.y, self.rot = ref, kind, x, y, rot
        self.value, self.pads, self.label = value, pads, label or value
        self.body = body  # (w, h) silkscreen box in local coords


def _xf(x0, y0, rot, dx, dy):
    a = math.radians(rot)
    return (x0 + dx * math.cos(a) - dy * math.sin(a),
            y0 + dx * math.sin(a) + dy * math.cos(a))


def tact6(ref, x, y, sig, label, rot=0):
    """6x6 mm THT tactile switch. Pads in the same row (6.5 mm apart) are
    connected inside the switch; pressing joins the two rows (4.5 mm)."""
    pads = []
    for i, (dx, dy, net) in enumerate([(-3.25, -2.25, "GND"), (3.25, -2.25, "GND"),
                                       (-3.25, 2.25, sig), (3.25, 2.25, sig)], 1):
        px, py = _xf(x, y, rot, dx, dy)
        pads.append(Pad(ref, i, px, py, net, w=2.0, h=2.0, drill=1.0))
    return Part(ref, "SW_6x6", x, y, rot, "6x6 tact", pads, label, body=(6.0, 6.0))


def dip28(ref, x, y, netmap):
    """Horizontal DIP-28: pins 1-14 on the lower row (left->right),
    15-28 on the upper row (right->left). Oval pads so nothing fits
    between pins."""
    pads = []
    x0 = x - 6.5 * 2.54
    for pin in range(1, 29):
        if pin <= 14:
            px, py = x0 + (pin - 1) * 2.54, y + 3.81
        else:
            px, py = x0 + (28 - pin) * 2.54, y - 3.81
        pads.append(Pad(ref, pin, px, py, netmap.get(pin), shape="oval", w=1.6, h=2.4, drill=0.8))
    return Part(ref, "DIP28", x, y, 0, "MCP23017-E/SP", pads, "MCP23017", body=(35.6, 6.0))


def header(ref, x, y, nets, label, pitch=2.54, vertical=False, drill=1.0):
    pads = []
    n = len(nets)
    for i, net in enumerate(nets):
        off = (i - (n - 1) / 2) * pitch
        px, py = (x, y + off) if vertical else (x + off, y)
        w, h = (2.6, 1.7) if vertical else (1.7, 2.6)
        pads.append(Pad(ref, i + 1, px, py, net, shape="oval", w=w, h=h, drill=drill))
    body = (2.54, n * 2.54) if vertical else (n * 2.54, 2.54)
    return Part(ref, f"HDR_1x{n}", x, y, 90 if vertical else 0, label, pads, label, body=body)


def two_pin(ref, kind, x, y, pitch, net1, net2, value, vertical=False, drill=0.8, body=None):
    if vertical:
        p = [(x, y - pitch / 2), (x, y + pitch / 2)]
    else:
        p = [(x - pitch / 2, y), (x + pitch / 2, y)]
    pads = [Pad(ref, 1, p[0][0], p[0][1], net1, drill=drill),
            Pad(ref, 2, p[1][0], p[1][1], net2, drill=drill)]
    return Part(ref, kind, x, y, 90 if vertical else 0, value, pads, value, body=body)


def smd1206(ref, x, y, net1, net2, value, vertical=False):
    """1206 resistor/capacitor on the copper side (hand-solder pads)."""
    d = 1.6
    if vertical:
        p, (w, h) = [(x, y - d), (x, y + d)], (1.8, 1.4)
    else:
        p, (w, h) = [(x - d, y), (x + d, y)], (1.4, 1.8)
    pads = [Pad(ref, 1, p[0][0], p[0][1], net1, shape="rect", w=w, h=h, drill=None),
            Pad(ref, 2, p[1][0], p[1][1], net2, shape="rect", w=w, h=h, drill=None)]
    kind = "C_1206" if ref.startswith("C") else "R_1206"
    return Part(ref, kind, x, y, 90 if vertical else 0, value, pads, value,
                body=(1.8, 3.4) if vertical else (3.4, 1.8))


def to92(ref, x, y, e, b, c):
    """TO-92 with legs spread to 2.54 mm (E-B-C, flat face towards +y)."""
    pads = [Pad(ref, "E", x - 2.54, y, e, shape="oval", w=1.6, h=2.4),
            Pad(ref, "B", x, y, b, shape="oval", w=1.6, h=2.4),
            Pad(ref, "C", x + 2.54, y, c, shape="oval", w=1.6, h=2.4)]
    return Part(ref, "TO92_wide", x, y, 0, "S8050", pads, "S8050 EBC", body=(5.0, 4.0))


# --------------------------------------------------------------------------
# Switch positions are fixed by the case (remote_case.scad `singles`, `dpad_c`);
# rot 180 puts the signal row towards -y (the chip) for keys below it.
BUTTONS = {
    #  ref       x     y     function  rot
    "SW1":  (7.5,   6.0, "POWER", 0),
    "SW2":  (21.5, 12.5, "UP",    0),
    "SW3":  (8.5,  25.5, "LEFT",  180),   # GND row at the bottom: a straight GND run down to SW7
    "SW4":  (21.5, 25.5, "OK",    0),
    "SW5":  (34.5, 25.5, "RIGHT", 0),
    "SW6":  (21.5, 38.5, "DOWN",  0),
    "SW7":  (8.5,  50.0, "BACK",  0),
    "SW8":  (21.5, 50.0, "HOME",  0),
    "SW9":  (34.5, 50.0, "VOICE", 0),
    "SW10": (8.5,  77.0, "VOL_UP",   180),
    "SW11": (8.5,  90.0, "VOL_DOWN", 180),
    "SW12": (21.5, 83.5, "MUTE",     180),
    "SW13": (34.5, 77.0, "CH_UP",    180),
    "SW14": (34.5, 90.0, "CH_DOWN",  180),
}

# The chip sits a little left of centre: one lane round its left end (POWER).
# The 8 keys above it land on its top row (GPA), the 5 below on its bottom row (GPB1-7).
# At y 65.5 there are three lanes between the BACK/HOME/VOICE row and its top pins.
CHIP_X, CHIP_Y = 20.6, 65.5

# MCP23017 fixed pins. GPA0..7 = pins 21..28, GPB0..7 = pins 1..8.
CHIP_FIXED = {9: "3V3", 10: "GND", 12: "SCL", 13: "SDA",
              15: "GND", 16: "GND", 17: "GND", 18: "3V3", 20: "INT"}

# J5 goes to the display board (ESP32-32E); labels are the ESP32 pins.
J5_LABELS = {"VBAT": "VBAT", "GND": "GND", "IR": "IO27", "3V3": "3V3", "INT": "IO35", "SCL": "IO5", "SDA": "IO1"}


def wirepads(ref, pads, label):
    """Loose wire pads (no header): [(net, x, y), ...]. Wires are soldered on the copper side
    and run beside the battery, so the pads can sit wherever routing wants them."""
    ps = [Pad(ref, i + 1, x, y, net, w=2.2, h=2.2, drill=1.0) for i, (net, x, y) in enumerate(pads)]
    cx = sum(p.x for p in ps) / len(ps); cy = sum(p.y for p in ps) / len(ps)
    return Part(ref, "WIREPADS", cx, cy, 0, label, ps, label)


# Parts below/around the keys. Each layout is a candidate for the router to try.
LAYOUTS = {
    # No connector: the display wires (copper side, beside the battery) solder straight onto
    # existing pads: INT pin 20, SCL pin 12, SDA pin 13, 3V3 pin 9, GND pin 10, VBAT C2,
    # IR R4, IR LED cathodes R6/R7 (anodes to VBAT). I2C pull-ups live on the display board.
    "wires": {
        "C1": (26.5, 72.4, False),
        "Q1": (21.5, 99.5),
        "R5": (21.5, 105.0, True), "R4": (16.6, 103.6, False),
        "R6": (27.6, 103.0, True), "R7": (31.4, 103.0, True),
        "C2": (36.6, 103.0, True),
    },
    # "wires" plus one row of 10 hole-less copper pads (J5) along the bottom edge where every
    # wire lands: the display's 7 and the IR LEDs' 3 (K1/K2 cathodes, LED+ = VBAT). The IR
    # driver moves to the bottom-left. SCL/SDA come down through SW13/SW14; INT and 3V3 can't get
    # out of the chip, so they reach the row on two insulated jumper wires (hand_route.PADS_JUMPERS).
    "pads": {
        "C1": (26.5, 72.4, False),
        "Q1": (12.5, 99.3),                 # clear of the VOL- cap's collar
        "R4": (23.2, 103.6, True, True), "R5": (10.0, 102.0, False, True),
        "R6": (17.0, 104.2, True), "R7": (20.1, 104.2, True),
        "C2": (28.8, 99.5, False),
        "J5": ("header", 26.19, 108.8, ["GND", "K1", "K2", "IR", "VBAT", "VBAT", "3V3", "INT", "SCL", "SDA"], None),
    },
    # J5 as a header along the bottom edge; IR driver bottom-left, pull-ups bottom-right
    "bottom": {
        "C1": (25.7, 71.4, False),
        "R1": (39.2, 99.0, True), "R2": (35.6, 99.0, True), "R3": (32.0, 99.0, True),
        "Q1": (10.0, 97.6),
        "R5": (16.4, 98.4, True), "R4": (13.6, 104.0, False),
        "R6": (8.2, 103.0, False), "R7": (8.2, 107.0, False),
        "C2": (19.6, 104.0, True),
        "J3": (2.9, 101.5),
        "J5": ("header", 25.0, 108.6, ["VBAT", "GND", "IR", "3V3", "INT", "SCL", "SDA"]),
    },
    # Logic wires leave from pads on the right edge level with the chip pins that need them;
    # power and IR from pads at the bottom by the IR driver. No INT pull-up: the MCP23017's INT
    # is set push-pull (IO35 has no internal pull-up).
    "right": {
        "C1": (24.9, 71.4, False),
        "R1": (31.0, 71.2, False), "R2": (36.5, 71.2, False),
        "Q1": (10.0, 97.6),
        "R5": (16.4, 98.4, True), "R4": (13.6, 104.0, False),
        "R6": (8.2, 103.0, False), "R7": (8.2, 107.0, False),
        "C2": (19.6, 104.0, True),
        "J3": (2.9, 101.5),
        "J5": ("pads", [("INT", 40.6, 55.2), ("GND", 40.6, 60.4), ("3V3", 40.6, 64.2), ("SDA", 40.6, 69.4), ("SCL", 40.6, 73.0)]),
        "J6": ("pads", [("IR", 23.0, 109.0), ("VBAT", 27.0, 109.0), ("GND", 31.0, 109.0)]),
    },
}


def build(button_pins, layout="bottom"):
    """button_pins: dict function -> MCP23017 pin number."""
    parts = []
    for ref, (x, y, fn, rot) in BUTTONS.items():
        parts.append(tact6(ref, x, y, "BTN_" + fn, fn, rot=rot))
    netmap = dict(CHIP_FIXED)
    for fn, pin in button_pins.items():
        assert pin not in CHIP_FIXED, f"{fn} on fixed pin {pin}"
        netmap[pin] = "BTN_" + fn
    parts.append(dip28("U1", CHIP_X, CHIP_Y, netmap))
    parts += other_parts(LAYOUTS[layout] if isinstance(layout, str) else layout)
    return parts


def other_parts(b):
    def s(ref, n1, n2, val):
        x, y, v, *flip = b[ref]                 # optional 4th item True: swap the two ends
        if flip and flip[0]:
            n1, n2 = n2, n1
        return smd1206(ref, x, y, n1, n2, val, vertical=v)
    ps = [s("C1", "3V3", "GND", "100nF")] + [s(r, "3V3", n, v) for r, n, v in
          (("R1", "SDA", "4.7k"), ("R2", "SCL", "4.7k"), ("R3", "INT", "10k")) if r in b] + [
        # IR driver: low-side NPN; the two IR LEDs sit at the remote's tip (J3)
        to92("Q1", *b["Q1"], "GND", "QB", "QC"),
        s("R5", "QB", "GND", "10k"),
        s("R4", "IR", "QB", "1k"),
        s("R6", "QC", "K1", "15R"),
        s("R7", "QC", "K2", "15R"),
        s("C2", "VBAT", "GND", "47uF"),
    ] + ([header("J3", *b["J3"], ["VBAT", "K1", "K2"], "IR LED", vertical=True)] if "J3" in b else [])
    for ref in ("J5", "J6"):
        if ref not in b:
            continue
        j = b[ref]
        if j[0] == "header":
            ps.append(header(ref, j[1], j[2], j[3], "TO DISPLAY", drill=j[4] if len(j) > 4 else 1.0))
        else:
            ps.append(wirepads(ref, j[1], "TO DISPLAY"))
    return ps


if __name__ == "__main__":
    ps = build({})
    print(len(ps), "parts", sum(len(p.pads) for p in ps), "pads")
