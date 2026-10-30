"""Parse adb shell output from the TV into inputs and apps. Pure functions."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Input:
    port: int
    passthrough_id: str
    cec_name: str | None
    connected: bool


@dataclass(frozen=True)
class App:
    package: str


_HW_ID = re.compile(r"([a-z0-9_.]+/\.hdmi\.HDMIInputService/HW(\d+))")
_HW_INFO = re.compile(r"TvInputHardwareInfo \{id=(\d+), type=9,.*?hdmi_port=(\d+), cable_connection_status=(\d+)")
_CEC = re.compile(r"CEC:.*?display_name: (.+?) power_status:.*?port_id: (-?\d+)")
_ACTIVE = re.compile(r"mActiveSource: \((0x[0-9a-fA-F]+), (0x[0-9a-fA-F]+)\)")
_PORT_ADDR = re.compile(r"port_id: (\d+), type: HDMI_IN, address: (0x[0-9a-fA-F]+)")
_ACTIVITY = re.compile(r"^\s+([A-Za-z0-9_.]+)/\S+\s*$", re.M)


def _cec_names(hdmi_control: str) -> dict[int, str]:
    names: dict[int, str] = {}
    for name, port in _CEC.findall(hdmi_control):
        if int(port) > 0:
            names.setdefault(int(port), name.strip())
    return names


def parse_inputs(tv_input: str, hdmi_control: str) -> list[Input]:
    ids = {int(n): full for full, n in _HW_ID.findall(tv_input)}
    names = _cec_names(hdmi_control)
    by_port: dict[int, Input] = {}
    for hw, port, status in _HW_INFO.findall(tv_input):
        hw, port = int(hw), int(port)
        if hw in ids and 1 <= port <= 4 and port not in by_port:
            by_port[port] = Input(port, ids[hw], names.get(port), status == "1")
    return [by_port[p] for p in sorted(by_port)]


def parse_current_input(hdmi_control: str) -> int | None:
    m = _ACTIVE.search(hdmi_control)
    if not m:
        return None
    addr = int(m.group(2), 16)
    for port, port_addr in _PORT_ADDR.findall(hdmi_control):
        if int(port_addr, 16) == addr:
            return int(port)
    for name_port in re.findall(rf"physical_address: {m.group(2)} port_id: (\d+)", hdmi_control):
        return int(name_port)
    return None


def parse_apps(packages: str, system: frozenset[str]) -> list[App]:
    found = {p for p in _ACTIVITY.findall(packages) if p not in system}
    return [App(p) for p in sorted(found)]
