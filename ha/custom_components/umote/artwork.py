"""Shrink Cast artwork to what the remote can decode. Pure function."""
from __future__ import annotations

import io

from PIL import Image, ImageOps

SIZE = (212, 76)
MAX_BYTES = 16384
MAX_PIXELS = 40_000_000


def shrink(data: bytes) -> bytes | None:
    """212x76 baseline JPEG <= 16 KB, cover-cropped and centred; None if unusable."""
    if not data:
        return None
    try:
        with Image.open(io.BytesIO(data)) as im:
            if im.width * im.height > MAX_PIXELS:
                return None
            im = ImageOps.fit(im.convert("RGB"), SIZE, Image.Resampling.LANCZOS)
    except (OSError, ValueError, Image.DecompressionBombError):
        return None
    for quality in range(85, 0, -10):
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=quality, progressive=False, optimize=True)
        if buf.tell() <= MAX_BYTES:
            return buf.getvalue()
    return None
