// Simulator only: dump the visible LVGL tree as JSON lines for tools/check_ui.py.
#pragma once

#include <cstdio>
#include <map>
#include <string>
#include "lvgl.h"
#include "ui_lv.h"

inline std::map<const lv_obj_t *, std::string> &sim_name_map() { return ui::names(); }
inline std::map<const lv_font_t *, int> &sim_font_map() {
  static std::map<const lv_font_t *, int> m;
  if (m.empty()) {
    const ui::Res &r = ui::R;
    m = {{r.f12, 12}, {r.f13, 13}, {r.f14, 14}, {r.f15, 15}, {r.f17, 17}, {r.f20, 20}, {r.f13b, 13},
         {r.f15b, 15}, {r.f17b, 17}, {r.f20b, 20}, {r.f12s, 12}, {r.f14s, 14}};
  }
  return m;
}

inline bool sim_is_modal(const std::string &n) {
  auto ends = [&](const char *s) { size_t l = strlen(s); return n.size() >= l && n.compare(n.size() - l, l, s) == 0; };
  return ends("_sheet") || ends("_dialog") || n == "page_picker" || n == "kb_pick";
}

inline std::string sim_json_escape(const char *s) {
  std::string o;
  for (; s && *s; s++) {
    if (*s == '"' || *s == '\\') o += '\\';
    if ((unsigned char) *s < 0x20) continue;
    o += *s;
  }
  return o;
}

// clip = visible area of the ancestors; objects entirely outside it count as hidden.
inline void sim_dump_obj(FILE *f, const char *screen, lv_obj_t *obj, lv_area_t clip, bool hidden, bool modal,
                         bool peek) {
  auto &names = sim_name_map();
  auto it = names.find(obj);
  std::string name = it != names.end() ? it->second : "";
  modal = modal || sim_is_modal(name);
  peek = peek || (name.size() > 5 && name.compare(name.size() - 5, 5, "_peek") == 0);
  hidden = hidden || lv_obj_has_flag(obj, LV_OBJ_FLAG_HIDDEN);
  lv_area_t a;
  lv_obj_get_coords(obj, &a);
  lv_area_t vis;
  vis.x1 = LV_MAX(a.x1, clip.x1);
  vis.y1 = LV_MAX(a.y1, clip.y1);
  vis.x2 = LV_MIN(a.x2, clip.x2);
  vis.y2 = LV_MIN(a.y2, clip.y2);
  bool on = vis.x1 <= vis.x2 && vis.y1 <= vis.y2;
  bool gone = hidden || !on;
  if (name.empty()) name = std::string("anon@") + std::to_string(a.x1) + "," + std::to_string(a.y1);
  const char *text = nullptr;
  int font_px = -1, text_w = -1;
  if (lv_obj_check_type(obj, &lv_label_class)) {
    text = lv_label_get_text(obj);
    const lv_font_t *font = lv_obj_get_style_text_font(obj, LV_PART_MAIN);
    auto fit = sim_font_map().find(font);
    font_px = fit != sim_font_map().end() ? fit->second : 0;
    lv_point_t sz;
    lv_text_get_size(&sz, text, font, lv_obj_get_style_text_letter_space(obj, LV_PART_MAIN), 0, LV_COORD_MAX,
                     LV_TEXT_FLAG_NONE);
    lv_label_long_mode_t lm = lv_label_get_long_mode(obj);
    text_w = lm == LV_LABEL_LONG_WRAP || lm == LV_LABEL_LONG_DOT ? 0 : sz.x;
  }
  int outline = lv_obj_get_style_outline_width(obj, LV_PART_MAIN) + lv_obj_get_style_outline_pad(obj, LV_PART_MAIN);
  // LVGL marks every object clickable; a real target also has an event handler.
  bool clickable = lv_obj_has_flag(obj, LV_OBJ_FLAG_CLICKABLE) && lv_obj_get_event_count(obj) > 0 &&
                   !lv_obj_check_type(obj, &lv_label_class);
  if (!gone && !peek) {
    fprintf(f,
            "{\"screen\":\"%s\",\"obj\":\"%s\",\"x\":%d,\"y\":%d,\"w\":%d,\"h\":%d,\"clickable\":%s,\"hidden\":false,"
            "\"text\":%s%s%s,\"font_px\":%d,\"text_w\":%d,\"outline\":%d,\"layer\":\"%s\"}\n",
            screen, name.c_str(), (int) a.x1, (int) a.y1, (int) lv_area_get_width(&a), (int) lv_area_get_height(&a),
            clickable ? "true" : "false", text ? "\"" : "", text ? sim_json_escape(text).c_str() : "null",
            text ? "\"" : "", font_px, text_w, outline, modal ? "modal" : "base");
  }
  if (gone) return;
  for (uint32_t i = 0; i < lv_obj_get_child_count(obj); i++)
    sim_dump_obj(f, screen, lv_obj_get_child(obj, i), vis, hidden, modal, peek);
}

inline void sim_dump(const char *path, const char *screen) {
  FILE *f = fopen(path, "a");
  if (!f) return;
  lv_area_t full = {0, 0, 239, 319};
  sim_dump_obj(f, screen, lv_screen_active(), full, false, false, false);
  sim_dump_obj(f, screen, lv_layer_top(), full, false, false, false);
  fclose(f);
}
