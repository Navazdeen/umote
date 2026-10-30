from PIL import Image, ImageDraw

from appicons import compose_adaptive, crop_opaque_square, finish


def test_adaptive_composite_keeps_centre():
    bg = Image.new("RGBA", (108, 108), (0, 0, 255, 255))
    ImageDraw.Draw(bg).rectangle((18, 18, 89, 89), fill=(255, 0, 0, 255))
    fg = Image.new("RGBA", (108, 108), (0, 0, 0, 0))
    out = compose_adaptive(bg, fg)
    for xy in ((0, 0), (out.width - 1, 0), (0, out.height - 1), (out.width - 1, out.height - 1)):
        assert out.getpixel(xy)[:3] == (255, 0, 0)


def test_crop_removes_transparent_margin_and_shadow():
    im = Image.new("RGBA", (192, 192), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((20, 20, 175, 175), fill=(0, 0, 0, 90))          # soft drop shadow
    d.rectangle((20, 20, 171, 171), fill=(0, 168, 225, 255))     # opaque 152x152 icon
    assert crop_opaque_square(im).size == (152, 152)


def test_finish_is_44_rgba_with_transparent_corners():
    out = finish(Image.new("RGB", (152, 152), (229, 9, 20)))
    assert out.size == (44, 44) and out.mode == "RGBA"
    assert out.getpixel((0, 0))[3] == 0 and out.getpixel((22, 22))[3] == 255
