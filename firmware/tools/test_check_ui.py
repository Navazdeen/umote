import json

from check_ui import check


def obj(name, x, y, w, h, clickable=True, text=None, font_px=None, text_w=None, outline=0, layer="base"):
    return {"screen": "s", "obj": name, "x": x, "y": y, "w": w, "h": h, "clickable": clickable, "hidden": False,
            "text": text, "font_px": font_px, "text_w": text_w, "outline": outline, "layer": layer}


def kinds(objs):
    return {f.split(":", 1)[0] for f in check(objs)}


def test_small_target_fails():
    assert "target" in kinds([obj("btn", 10, 10, 40, 44)])


def test_close_buttons_fail_gap():
    assert "gap" in kinds([obj("a", 10, 10, 44, 44), obj("b", 60, 10, 44, 44)])


def test_outline_counts_toward_gap():
    assert "gap" in kinds([obj("a", 10, 10, 44, 44, outline=5), obj("b", 64, 10, 44, 44)])


def test_clipped_text_fails_unless_trunc():
    assert "clipped" in kinds([obj("lbl", 10, 10, 30, 16, False, "Hello there", 12, 50)])
    assert not check([obj("lbl_trunc", 10, 10, 30, 16, False, "Hello there", 12, 50)])


def test_small_text_fails():
    assert "text" in kinds([obj("lbl", 10, 10, 80, 16, False, "Hi", 11, 10)])


def test_glyph_fails():
    assert "glyph" in kinds([obj("lbl", 10, 10, 80, 16, False, "Done ✓", 12, 40)])
    assert "glyph" in kinds([obj("lbl", 10, 10, 80, 16, False, "Hot \U0001F525", 12, 40)])


def test_offscreen_fails():
    assert "bounds" in kinds([obj("btn", 200, 10, 44, 44)])


def test_stacked_rows_may_touch():
    assert not check([obj("row_a", 0, 40, 240, 48), obj("row_b", 0, 88, 240, 48)])


def test_modal_hides_base_layer():
    base = [obj("a", 10, 10, 44, 44), obj("b", 56, 10, 44, 44)]
    assert not check(base + [obj("m", 10, 100, 100, 44, layer="modal")])


def test_correct_fixture_passes():
    assert not check([obj("a", 10, 10, 44, 44), obj("b", 62, 10, 44, 44),
                      obj("lbl", 10, 70, 100, 16, False, "Living room …", 13, 90)])


def test_cli(tmp_path, capsys):
    from check_ui import main
    p = tmp_path / "d.jsonl"
    p.write_text("\n".join(json.dumps(o) for o in [obj("btn", 10, 10, 40, 44)]))
    assert main([str(p)]) == 1
    assert "target" in capsys.readouterr().out
