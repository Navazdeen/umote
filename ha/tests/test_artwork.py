import io

from PIL import Image

from custom_components.umote.artwork import shrink


def img_bytes(w, h, fmt="WEBP"):
    im = Image.new("RGB", (w, h))
    for x in range(0, w, max(1, w // 8)):
        im.paste((x * 255 // w, 80, 160), (x, 0, min(w, x + w // 8 + 1), h))
    buf = io.BytesIO()
    im.save(buf, fmt, progressive=True) if fmt == "JPEG" else im.save(buf, fmt)
    return buf.getvalue()


def check(out):
    im = Image.open(io.BytesIO(out))
    assert im.format == "JPEG" and im.size == (212, 76) and not im.info.get("progressive")
    assert len(out) <= 16384


def test_webp_1920x1080_becomes_212x76_baseline_jpeg():
    check(shrink(img_bytes(1920, 1080)))


def test_progressive_jpeg_becomes_baseline():
    check(shrink(img_bytes(800, 450, "JPEG")))


def test_artwork_handles_portrait_and_tiny():
    check(shrink(img_bytes(300, 900, "PNG")))
    check(shrink(img_bytes(40, 20, "PNG")))


def test_artwork_rejects_garbage():
    assert shrink(b"not an image") is None and shrink(b"") is None
    assert shrink(img_bytes(1920, 1080)[:200]) is None   # truncated
