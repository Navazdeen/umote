"""Remote button board: parts, pads and nets.

Coordinates are in mm, viewed from the COMPONENT side, origin at the board's
top-left corner, x to the right, y towards the bottom (towards the remote's
charging end). Copper is on the opposite (bottom) side.
"""
import math

BOARD_W = 43.0
BOARD_H = 96.0

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


def header(ref, x, y, nets, label, pitch=2.54, vertical=False):
    pads = []
    n = len(nets)
    for i, net in enumerate(nets):
        off = (i - (n - 1) / 2) * pitch
        px, py = (x, y + off) if vertical else (x + off, y)
        w, h = (2.6, 1.7) if vertical else (1.7, 2.6)
        pads.append(Pad(ref, i + 1, px, py, net, shape="oval", w=w, h=h, drill=1.0))
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
# Button signal nets are named by function; which MCP23017 pin each one lands
# on is chosen by the router script (so traces don't cross) and written to
# pinmap.json for the firmware.
BUTTONS = {
    #  ref       x     y     function
    "SW1": (7.5, 6.0, "POWER"),
    "SW2": (21.5, 12.5, "UP"),
    "SW3": (8.5, 25.5, "LEFT"),
    "SW4": (21.5, 25.5, "OK"),
    "SW5": (34.5, 25.5, "RIGHT"),
    "SW6": (21.5, 38.5, "DOWN"),
    "SW7": (8.5, 50.0, "BACK"),
    "SW8": (21.5, 50.0, "HOME"),
    "SW9": (34.5, 50.0, "VOICE"),
}

# chip sits a little left of centre: one lane round its left end (POWER),
# two lanes round its right end (INT and RESET's 3V3)
CHIP_X, CHIP_Y = 20.6, 63.5

# MCP23017 fixed pins. GPA0..7 = pins 21..28, GPB0..7 = pins 1..8.
CHIP_FIXED = {9: "3V3", 10: "GND", 12: "SCL", 13: "SDA",
              15: "GND", 16: "GND", 17: "GND", 18: "3V3", 20: "INT"}

# J1 goes to the display board (ESP32-32E). Order chosen to suit routing.
J1_NETS = ["VBAT", "GND", "IR", "3V3", "INT", "SCL", "SDA"]
J1_LABELS = ["VBAT", "GND", "IO27", "3V3", "IO35", "IO5", "IO1"]
# The INMP441 module sits at the top of this board, right under the screen,
# but is wired straight to the display board (5 short wires): its pads carry
# no traces here. Order follows the common round INMP441 breakout [CHECK].
JMIC_NETS = ["M_SCK", "M_WS", "M_LR", "M_SD", "M_VDD", "M_GND"]
JMIC_LABELS = ["SCK", "WS", "L/R", "SD", "VDD", "GND"]


def build(button_pins, j5=None, j4=None):
    """button_pins: dict function -> MCP23017 pin number."""
    parts = []
    for ref, (x, y, fn) in BUTTONS.items():
        parts.append(tact6(ref, x, y, "BTN_" + fn, fn))
    netmap = dict(CHIP_FIXED)
    for fn, pin in button_pins.items():
        netmap[pin] = "BTN_" + fn
    parts.append(dip28("U1", CHIP_X, CHIP_Y, netmap))

    for p in bottom_parts(j5 or J1_NETS, j4 or JMIC_NETS):
        parts.append(p)
    return parts


# Bottom-zone parts; positions are tuned by layout iterations.
BOTTOM = {
    "C1": (25.7, 71.8, False), "R1": (35.5, 73.5, False), "R2": (35.5, 77.5, False),
    "R3": (39.0, 84.5, True), "Q1": (6.5, 74.0), "R5": (11.5, 78.0, True),
    "R4": (6.0, 80.5, False), "R6": (15.5, 80.0, True), "R7": (19.5, 80.0, True),
    "C2": (28.5, 86.0, False), "J3": (3.0, 87.0), "J4": (32.4, 4.0), "J5": (21.5, 93.0),
}


def bottom_parts(j5, j4):
    b = BOTTOM
    def s(ref, n1, n2, val):
        x, y, v = b[ref]
        return smd1206(ref, x, y, n1, n2, val, vertical=v)
    return [
        s("C1", "3V3", "GND", "100nF"),
        s("R1", "3V3", "SDA", "4.7k"),
        s("R2", "3V3", "SCL", "4.7k"),
        s("R3", "3V3", "INT", "10k"),
        # IR driver: low-side NPN; the two IR LEDs sit at the remote's tip (J3)
        to92("Q1", *b["Q1"], "GND", "QB", "QC"),
        s("R5", "QB", "GND", "10k"),
        s("R4", "IR", "QB", "1k"),
        s("R6", "QC", "K1", "15R"),
        s("R7", "QC", "K2", "15R"),
        s("C2", "VBAT", "GND", "47uF"),
        header("J3", *b["J3"], ["VBAT", "K1", "K2"], "IR LED", vertical=True),
        header("J4", *b["J4"], j4, "INMP441"),
        header("J5", *b["J5"], j5, "TO DISPLAY"),
    ]


if __name__ == "__main__":
    ps = build({})
    print(len(ps), "parts", sum(len(p.pads) for p in ps), "pads")
