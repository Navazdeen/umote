"""Hand-planned route for the 14-key board (layout "wires"). Every key and the GND network are
laid here as explicit polylines; route.py only finishes the IR driver and any short gaps.

Topology (component-side view, y down):
- Keys above the chip descend through switch interiors / the gaps between columns and fan
  into the top row (GPA): BACK 28, LEFT 27, UP 26, OK 25, DOWN 24, HOME 23, VOICE 22, RIGHT 21.
  VOICE and RIGHT cross over on two lanes just above the pins.
- POWER runs down the left edge into pin 1. Keys below the chip go straight up into GPB:
  VOL_DOWN 3, VOL_UP 4, CH_DOWN 5, MUTE 7, CH_UP 8.
- GND: a spine through the centre column's interiors, row links through the switches'
  internally joined pin pairs, a trunk down the right edge, and the chip's GND pins tied
  under the chip and out to that trunk. 3V3 pin 18 -> pin 9 runs under the chip above it.
"""
import board as B

ASSIGN = {"BACK": 28, "LEFT": 27, "UP": 26, "OK": 25, "DOWN": 24, "HOME": 23, "VOICE": 22, "RIGHT": 21,
          "POWER": 1, "VOL_DOWN": 3, "VOL_UP": 4, "CH_DOWN": 5, "MUTE": 7, "CH_UP": 8}


def px(pin):
    return round(B.CHIP_X - 6.5 * 2.54 + ((pin - 1) if pin <= 14 else (28 - pin)) * 2.54, 3)


UP_Y, LO_Y = B.CHIP_Y - 3.81, B.CHIP_Y + 3.81      # 61.69, 69.31

TRACES = [
    # --- keys above the chip (top row) ---
    ("BTN_BACK",  [(5.25, 52.25), (px(28), 55.0), (px(28), UP_Y)]),
    ("BTN_LEFT",  [(5.25, 23.25), (7.6, 25.6), (7.6, 55.0), (px(27), 56.0), (px(27), UP_Y)]),
    ("BTN_UP",    [(18.25, 14.75), (16.0, 17.0), (9.4, 17.0), (9.4, 57.0), (px(26), 57.23), (px(26), UP_Y)]),
    ("BTN_OK",    [(18.25, 27.75), (14.1, 31.9), (14.1, 53.6), (px(25), 55.99), (px(25), UP_Y)]),
    ("BTN_DOWN",  [(18.25, 40.75), (15.9, 43.1), (15.9, 54.35), (px(24), 56.0), (px(24), UP_Y)]),
    ("BTN_HOME",  [(18.25, 52.25), (18.25, 54.55), (px(23), 56.01), (px(23), UP_Y)]),
    ("BTN_VOICE", [(31.25, 52.25), (31.25, 56.4), (px(22), 56.4), (px(22), UP_Y)]),
    ("BTN_RIGHT", [(31.25, 27.75), (33.6, 30.1), (33.6, 58.2), (px(21), 58.2), (px(21), UP_Y)]),
    ("BTN_POWER", [(4.25, 8.25), (1.6, 10.9), (1.6, 67.0), (px(1), LO_Y)]),
    # --- keys below the chip (bottom row) ---
    ("BTN_VOL_UP",   [(11.75, 74.75), (px(4), LO_Y)]),
    ("BTN_VOL_DOWN", [(11.75, 87.75), (px(3), 85.17), (px(3), LO_Y)]),
    ("BTN_CH_DOWN",  [(31.25, 87.75), (29.9, 89.1), (15.0, 89.1), (15.0, 73.0), (px(5), 72.25), (px(5), LO_Y)]),
    ("BTN_MUTE",     [(18.25, 81.25), (px(7), 80.17), (px(7), LO_Y)]),
    ("BTN_CH_UP",    [(31.25, 74.75), (23.5, 74.75), (px(8), 73.12), (px(8), LO_Y)]),
    # --- GND ---
    ("GND", [(10.75, 3.75), (11.7, 5.6), (16.3, 10.25), (18.25, 10.25)]),              # SW1 -> SW2
    ("GND", [(18.25, 10.25), (21.5, 10.25), (21.5, 47.75), (18.25, 47.75)]),           # centre spine SW2..SW8
    ("GND", [(21.5, 23.25), (18.25, 23.25)]),                                           # spine -> SW4
    ("GND", [(21.5, 36.25), (18.25, 36.25)]),                                           # spine -> SW6
    ("GND", [(11.75, 27.75), (16.25, 23.25), (18.25, 23.25)]),                          # SW3 -> SW4
    ("GND", [(11.75, 27.75), (11.75, 47.75)]),                                          # SW3 -> SW7
    ("GND", [(24.75, 23.25), (31.25, 23.25)]),                                          # SW4 -> SW5
    ("GND", [(37.75, 23.25), (40.6, 26.1), (40.6, 44.9), (37.75, 47.75)]),              # SW5 -> SW9
    ("GND", [(37.75, 47.75), (40.6, 50.6), (40.6, 76.4), (37.75, 79.25)]),              # SW9 -> SW13 trunk
    ("GND", [(40.6, 66.5), (px(10), 66.5), (px(10), LO_Y)]),                            # under the chip -> pin 10
    ("GND", [(px(15), UP_Y), (px(15), 66.5)]),
    ("GND", [(px(16), UP_Y), (px(16), 66.5)]),
    ("GND", [(px(17), UP_Y), (px(17), 66.5)]),
    ("GND", [(px(10), LO_Y), (px(10), 71.2), (28.1, 72.4)]),                            # pin 10 -> C1
    ("GND", [(31.25, 79.25), (24.75, 85.75)]),                                          # SW13 -> MUTE
    ("GND", [(37.75, 79.25), (40.6, 82.1), (40.6, 89.4), (37.75, 92.25)]),              # SW13 -> SW14
    ("GND", [(11.75, 92.25), (13.6, 94.1), (29.4, 94.1), (31.25, 92.25)]),              # SW11 -> SW14
    ("GND", [(5.25, 79.25), (2.1, 82.4), (2.1, 89.1), (5.25, 92.25)]),                  # SW10 -> SW11
    # --- 3V3 ---
    ("3V3", [(px(18), UP_Y), (px(18), 64.3), (px(9), 64.3), (px(9), LO_Y)]),
    ("3V3", [(px(9), LO_Y), (px(9), 71.2), (24.9, 72.4)]),                              # pin 9 -> C1
]


# Layout "pads": the bottom area, hand-laid. J5 is one row of hole-less pads at y 108.8,
# x 14.76 .. 37.62: GND K1 K2 IR LED+ VBAT 3V3 INT SCL SDA (LED+ is VBAT too). The only way past
# the bottom keys' GND line is through SW13/SW14. QB loops over Q1; the row's GND comes via Q1 E.
PADS_TRACES = [
    ("SCL",  [(px(12), LO_Y), (px(12), 71.5), (33.55, 73.1), (33.55, 104.5), (35.08, 106.03), (35.08, 108.8)]),
    ("SDA",  [(px(13), LO_Y), (px(13), 71.0), (35.4, 71.8), (35.4, 101.0), (37.62, 103.22), (37.62, 108.8)]),
    ("GND",  [(9.96, 99.3), (9.96, 94.5), (11.75, 92.25)]),                    # Q1 E -> SW11
    ("GND",  [(9.96, 99.3), (8.4, 102.0)]),                                    # Q1 E -> R5
    ("GND",  [(8.4, 102.0), (8.4, 108.8), (14.76, 108.8)]),                    # R5 -> J5 GND
    ("QB",   [(12.5, 99.3), (12.5, 101.2), (11.6, 102.0)]),                    # Q1 B -> R5
    ("QB",   [(12.5, 99.3), (12.5, 96.0), (23.2, 96.0), (23.2, 102.0)]),       # Q1 B -> R4, over Q1
    ("QC",   [(15.04, 99.3), (15.04, 100.64), (17.0, 102.6), (20.1, 102.6)]),  # Q1 C -> R6, R7
    ("K1",   [(17.0, 105.8), (17.3, 106.6), (17.3, 108.8)]),                   # R6 -> J5 LED1-
    ("K2",   [(20.1, 105.8), (19.84, 106.6), (19.84, 108.8)]),                 # R7 -> J5 LED2-
    ("IR",   [(23.2, 105.2), (22.38, 106.4), (22.38, 108.8)]),                 # R4 -> J5 IR
    ("GND",  [(30.4, 99.5), (30.4, 95.1), (29.4, 94.1)]),                      # C2 -> GND line
    ("VBAT", [(27.2, 99.5), (27.2, 105.8), (27.46, 106.06), (27.46, 108.8)]),  # C2 -> J5 VBAT
    ("VBAT", [(24.92, 108.8), (27.46, 108.8)]),                                # J5 LED+ -> VBAT
]
# insulated wires soldered pad to pad on the copper side: (net, from, to J5 pad)
PADS_JUMPERS = [("INT", (px(20), UP_Y), (32.54, 108.8)), ("3V3", (px(9), LO_Y), (30.0, 108.8))]


def seed(r, layout="wires"):
    for net, pts in TRACES + (PADS_TRACES if layout == "pads" else []):
        r._add_trace(net, pts)
    if layout == "pads":
        r.jumpers += PADS_JUMPERS
