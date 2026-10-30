"""Extract launcher icons from the TV's APKs into 44x44 PNGs for the firmware.

usage: python tools/appicons.py --tv 192.168.31.100 --out firmware/assets/apps <package>...
"""
from __future__ import annotations

import argparse
import io
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

ADB = str(Path.home() / "tools/platform-tools/adb")
DPIS = (640, 480, 320, 240, 160)


def compose_adaptive(background: Image.Image, foreground: Image.Image) -> Image.Image:
    """Stack the two 108dp layers and keep the visible centre 72dp."""
    size = max(background.width, foreground.width, 108)
    canvas = background.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    canvas.alpha_composite(foreground.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS))
    m = round(size * 18 / 108)
    return canvas.crop((m, m, size - m, size - m))


def crop_opaque_square(img: Image.Image, alpha_threshold: int = 230) -> Image.Image:
    """Crop to the solid part of the icon, dropping transparent margins and soft shadows."""
    img = img.convert("RGBA")
    mask = img.getchannel("A").point(lambda a: 255 if a >= alpha_threshold else 0)
    box = mask.getbbox()
    if not box:
        return img
    l, t, r, b = box
    side = max(r - l, b - t)
    cx, cy = (l + r) // 2, (t + b) // 2
    l, t = max(0, cx - side // 2), max(0, cy - side // 2)
    return img.crop((l, t, min(img.width, l + side), min(img.height, t + side)))


def finish(img: Image.Image, size: int = 44, radius: int = 12) -> Image.Image:
    img = img.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    k = 4
    mask = Image.new("L", (size * k, size * k), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size * k - 1, size * k - 1), radius * k, fill=255)
    mask = mask.resize((size, size), Image.Resampling.LANCZOS)
    img.putalpha(ImageChops.multiply(img.getchannel("A"), mask))
    return img


def _adb(tv: str, *args: str) -> str:
    return subprocess.run([ADB, "-s", f"{tv}:5555", *args], capture_output=True, text=True, check=True).stdout


def _layer(apk, ref: str | None) -> Image.Image | None:
    """Resolve an adaptive-icon layer reference to an image (raster file or solid colour)."""
    if not ref:
        return None
    arsc = apk.get_android_resources()
    try:
        res_id = int(ref.lstrip("@"), 16)
        configs = arsc.get_resolved_res_configs(res_id)
    except (ValueError, KeyError):
        return None
    best = None
    for cfg, value in configs:
        if isinstance(value, str) and value.endswith((".png", ".webp")):
            dens = cfg.get_density() if hasattr(cfg, "get_density") else 0
            if best is None or dens > best[0]:
                best = (dens, value)
        elif isinstance(value, str) and value.startswith("#"):
            hexv = value.lstrip("#")
            argb = int(hexv, 16)
            a = (argb >> 24) & 0xFF if len(hexv) == 8 else 255
            return Image.new("RGBA", (108, 108), ((argb >> 16) & 0xFF, (argb >> 8) & 0xFF, argb & 0xFF, a))
    return Image.open(io.BytesIO(apk.get_file(best[1]))) if best else None


def icon_from_apk(path: str, splits: tuple[str, ...] = ()) -> Image.Image:
    from loguru import logger
    logger.remove()
    from androguard.core.apk import APK
    from androguard.core.axml import AXMLPrinter

    apk = APK(path)
    files = []
    for dpi in DPIS:
        f = apk.get_app_icon(max_dpi=dpi)
        if f and f not in files:
            files.append(f)
    xml = next((f for f in files if f.endswith(".xml")), None)
    if xml:
        tree = AXMLPrinter(apk.get_file(xml)).get_xml_obj()
        ns = "{http://schemas.android.com/apk/res/android}drawable"
        refs = {child.tag: child.get(ns) for child in tree}
        bg, fg = _layer(apk, refs.get("background")), _layer(apk, refs.get("foreground"))
        if bg is not None and fg is not None:
            return compose_adaptive(bg, fg)
    raster = next((f for f in files if f.endswith((".png", ".webp"))), None)
    if raster is not None:
        return crop_opaque_square(Image.open(io.BytesIO(apk.get_file(raster))))
    # Density-split installs keep the icon bitmaps in split_config.<dpi>.apk under the same id.
    ref = apk.get_attribute_value("application", "icon")
    for split in splits:
        img = _layer(APK(split), ref)
        if img is not None:
            return crop_opaque_square(img)
    raise ValueError(f"no raster icon ({files})")


def main(tv: str, packages: list[str], out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {}
    with tempfile.TemporaryDirectory() as tmp:
        for pkg in packages:
            try:
                paths = [line.split(":", 1)[1] for line in _adb(tv, "shell", "pm", "path", pkg).split()]
                if not paths:
                    raise ValueError("not installed")
                remote = next((p for p in paths if p.endswith("/base.apk")), paths[0])
                local = f"{tmp}/{pkg}.apk"
                _adb(tv, "pull", remote, local)
                splits = []
                for n, sp in enumerate(p for p in paths if "dpi.apk" in p):
                    splits.append(f"{tmp}/{pkg}.split{n}.apk")
                    _adb(tv, "pull", sp, splits[-1])
                finish(icon_from_apk(local, tuple(splits))).save(out_dir / f"{pkg}.png")
                result[pkg] = "ok"
            except Exception as err:  # noqa: BLE001 - report every package, keep going
                result[pkg] = f"missing: {err}"
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tv", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("packages", nargs="+")
    a = ap.parse_args()
    res = main(a.tv, a.packages, a.out)
    for k, v in res.items():
        print(f"{k}: {v}")
    sys.exit(0 if all(v == "ok" for v in res.values()) else 1)
