// umote LVGL user interface, built in C++ so the data-driven parts (sources, tiles, keypad) stay short.
// Shared by remote.yaml (device) and sim.yaml (SDL). Pixel positions follow
// docs/superpowers/specs/2026-10-30-remote-ui-assets/all-screens-v5.html (240x320).
// The YAML side fills ui::R (fonts, images) and the ui::hooks, then calls ui::build().
#pragma once

#include <ArduinoJson.h>
#include <array>
#include <cstdio>
#include <functional>
#include <map>
#include <string>
#include <vector>
#include "lvgl.h"
#include "logic.h"

namespace ui {

// ---- resources and names -------------------------------------------------------------------------
struct Res {
  const lv_font_t *f12, *f13, *f14, *f15, *f17, *f20, *f13b, *f15b, *f17b, *f20b, *f12s, *f14s;
  std::map<std::string, const lv_image_dsc_t *> img;
  const lv_image_dsc_t *get(const std::string &n) const {
    auto it = img.find(n);
    return it == img.end() ? nullptr : it->second;
  }
};
inline Res R;

// Widget names, used by the simulator's layout dump (tools/check_ui.py rules key off them).
inline std::map<const lv_obj_t *, std::string> &names() {
  static std::map<const lv_obj_t *, std::string> m;
  return m;
}
inline lv_obj_t *nm(lv_obj_t *o, const std::string &n) {
#ifdef USE_HOST
  names()[o] = n;
#endif
  return o;
}

// ---- hooks the YAML side provides -----------------------------------------------------------------
struct Hooks {
  std::function<void(const std::string &)> launch;             // source id
  std::function<void()> power;                                  // TV power key / TV-off power button
  std::function<void(const char *)> tv_key;                     // "MEDIA_PLAY_PAUSE", ...
  std::function<void(float)> seek;                              // seconds
  std::function<void(int, const std::string &, bool)> name_source;  // port, name, switch to it
  std::function<void(int)> page_shown;                          // page index
  std::function<void(const std::string &)> log;
};
inline Hooks hooks;

// ---- colours ---------------------------------------------------------------------------------------
constexpr uint32_t BG = 0x0B0B0C, SHEET = 0x1C1C1E, CARD = 0x2C2C2E, GREY = 0x3A3A3C, BLUE = 0x0A84FF,
                   LINK = 0x64A8FF, YELLOW = 0xFFD60A, WHITE = 0xFFFFFF;

inline uint32_t parse_hex(const char *s, uint32_t dflt) {
  if (!s || *s != '#') return dflt;
  return (uint32_t) strtoul(s + 1, nullptr, 16);
}

// ---- widget helpers --------------------------------------------------------------------------------
inline lv_obj_t *box(lv_obj_t *parent, int x, int y, int w, int h, uint32_t bg, lv_opa_t opa = LV_OPA_COVER,
                     int radius = 0) {
  lv_obj_t *o = lv_obj_create(parent);
  lv_obj_remove_style_all(o);
  lv_obj_set_pos(o, x, y);
  lv_obj_set_size(o, w, h);
  lv_obj_set_style_bg_color(o, lv_color_hex(bg), 0);
  lv_obj_set_style_bg_opa(o, opa, 0);
  lv_obj_set_style_radius(o, radius, 0);
  lv_obj_remove_flag(o, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_remove_flag(o, LV_OBJ_FLAG_CLICKABLE);
  return o;
}

inline lv_obj_t *text(lv_obj_t *parent, int x, int y, int w, const lv_font_t *font, uint32_t color, const char *t,
                      lv_text_align_t align = LV_TEXT_ALIGN_LEFT, lv_opa_t opa = LV_OPA_COVER) {
  lv_obj_t *l = lv_label_create(parent);
  lv_obj_set_style_text_font(l, font, 0);
  lv_obj_set_style_text_color(l, lv_color_hex(color), 0);
  lv_obj_set_style_text_opa(l, opa, 0);
  lv_obj_set_style_text_align(l, align, 0);
  lv_label_set_text(l, t);
  lv_obj_set_pos(l, x, y);
  if (w > 0) {   // one line, ellipsis when too long
    lv_obj_set_size(l, w, lv_font_get_line_height(font));
    lv_label_set_long_mode(l, LV_LABEL_LONG_DOT);
  }
  return l;
}

inline lv_obj_t *icon(lv_obj_t *parent, const std::string &name, int px, int x, int y, uint32_t color,
                      lv_opa_t opa = LV_OPA_COVER) {
  lv_obj_t *im = lv_image_create(parent);
  const lv_image_dsc_t *d = R.get("ic_" + name + "_" + std::to_string(px));
  if (d) lv_image_set_src(im, d);
  lv_obj_set_pos(im, x, y);
  lv_obj_set_size(im, px, px);
  lv_obj_set_style_image_recolor(im, lv_color_hex(color), 0);
  lv_obj_set_style_image_recolor_opa(im, LV_OPA_COVER, 0);
  lv_obj_set_style_image_opa(im, opa, 0);
  lv_obj_remove_flag(im, LV_OBJ_FLAG_CLICKABLE);
  return im;
}

inline void set_icon(lv_obj_t *im, const std::string &name, int px) {
  const lv_image_dsc_t *d = R.get("ic_" + name + "_" + std::to_string(px));
  if (d) lv_image_set_src(im, d);
}

using Tap = std::function<void()>;
inline void on_tap(lv_obj_t *o, Tap fn) {
  lv_obj_add_flag(o, LV_OBJ_FLAG_CLICKABLE);
  auto *heap = new Tap(std::move(fn));
  lv_obj_add_event_cb(o, [](lv_event_t *e) { (*static_cast<Tap *>(lv_event_get_user_data(e)))(); },
                      LV_EVENT_CLICKED, heap);
  lv_obj_add_event_cb(o, [](lv_event_t *e) { delete static_cast<Tap *>(lv_event_get_user_data(e)); },
                      LV_EVENT_DELETE, heap);
}

// Rounded button; pressed state dims it. Returns the button.
inline lv_obj_t *button(lv_obj_t *parent, int x, int y, int w, int h, uint32_t bg, lv_opa_t opa, int radius,
                        Tap fn) {
  lv_obj_t *b = box(parent, x, y, w, h, bg, opa, radius);
  lv_obj_set_style_bg_opa(b, opa > LV_OPA_50 ? LV_OPA_70 : (lv_opa_t) (opa + 30), LV_STATE_PRESSED);
  on_tap(b, std::move(fn));
  return b;
}

inline lv_obj_t *text_button(lv_obj_t *parent, int x, int y, int w, int h, const char *t, uint32_t bg,
                             lv_opa_t opa, int radius, uint32_t fg, Tap fn) {
  lv_obj_t *b = button(parent, x, y, w, h, bg, opa, radius, std::move(fn));
  lv_obj_t *l = text(b, 0, 0, 0, R.f14s, fg, t);
  lv_obj_center(l);
  return b;
}

inline void show(lv_obj_t *o, bool on) {
  if (on) lv_obj_remove_flag(o, LV_OBJ_FLAG_HIDDEN);
  else lv_obj_add_flag(o, LV_OBJ_FLAG_HIDDEN);
}

// ---- data from Home Assistant ------------------------------------------------------------------------
struct Source {
  std::string id, kind, name, icon;
  int port = 0;
  uint32_t color = GREY;
  bool unnamed() const { return kind == "input" && name.rfind("HDMI ", 0) == 0; }
};

struct TvData {
  std::vector<Source> sources;
  std::vector<std::string> quick, more;
  std::string current, cast_state, title, app_name, activity;
  bool tv_on = false, has_art = false, playing = false, seekable = true;
  float duration = 0, position = 0;
  int64_t position_ms = 0;   // millis() when position was received
  int64_t updated_ms = 0;    // millis() of the last HA update
};
inline TvData tv;

inline void parse_sources(const std::string &json) {
  JsonDocument doc;
  if (deserializeJson(doc, json)) return;
  tv.sources.clear();
  for (JsonObject s : doc.as<JsonArray>()) {
    Source src;
    src.id = s["id"] | "";
    src.kind = s["kind"] | "";
    src.name = umote::sanitize(s["name"] | "", src.id);
    src.icon = s["icon"] | "";
    src.port = s["port"] | 0;
    src.color = parse_hex(s["color"] | "", GREY);
    tv.sources.push_back(src);
  }
}

inline std::vector<std::string> parse_ids(const std::string &json) {
  std::vector<std::string> out;
  JsonDocument doc;
  if (deserializeJson(doc, json)) return out;
  for (JsonVariant v : doc.as<JsonArray>()) out.push_back(v.as<std::string>());
  return out;
}

// Labels under 44 px tiles: "PS5" rather than "PlayStation 5".
inline std::string short_name(const Source &s) { return s.icon == "ps5" ? "PS5" : s.name; }

inline const Source *find_source(const std::string &id) {
  for (auto &s : tv.sources)
    if (s.id == id) return &s;
  return nullptr;
}

// ---- shared chrome -----------------------------------------------------------------------------------
struct Chrome {
  lv_obj_t *wifi, *batt;
};
inline Chrome chrome;

inline void build_status() {
  lv_obj_t *top = lv_layer_top();
  chrome.wifi = icon(top, "wifi", 16, 156, 9, WHITE, 217);
  chrome.batt = text(top, 176, 9, 50, R.f12s, WHITE, "", LV_TEXT_ALIGN_RIGHT, 217);
  lv_label_set_long_mode(chrome.batt, LV_LABEL_LONG_CLIP);
}

inline lv_obj_t *banner, *banner_text, *toast_box, *toast_text;
inline lv_timer_t *toast_timer;

// Battery / button-board warning replaces the status icons; empty text hides it.
inline void set_status(int batt_pct, bool wifi_up, const char *warning, uint32_t warn_color) {
  lv_label_set_text_fmt(chrome.batt, "%d%%", batt_pct);
  bool warn = warning && *warning;
  show(chrome.wifi, wifi_up && !warn);
  show(chrome.batt, !warn);
  show(banner, warn);
  if (warn) {
    lv_label_set_text(banner_text, warning);
    lv_obj_set_style_bg_color(banner, lv_color_hex(warn_color), 0);
  }
}

inline void build_overlays() {
  banner = nm(box(lv_layer_top(), 136, 10, 100, 22, 0xE5484D, LV_OPA_COVER, 11), "banner");
  banner_text = text(banner, 0, 3, 100, R.f12s, WHITE, "", LV_TEXT_ALIGN_CENTER);
  show(banner, false);
  toast_box = nm(box(lv_layer_top(), 20, 132, 200, 44, CARD, 235, 12), "toast");
  toast_text = text(toast_box, 8, 13, 184, R.f14s, WHITE, "", LV_TEXT_ALIGN_CENTER);
  show(toast_box, false);
}

inline void toast(const std::string &t) {
  lv_label_set_text(toast_text, t.c_str());
  show(toast_box, true);
  lv_obj_move_foreground(toast_box);
  if (toast_timer) lv_timer_delete(toast_timer);
  toast_timer = lv_timer_create([](lv_timer_t *) {
    show(toast_box, false);
    lv_timer_delete(toast_timer);
    toast_timer = nullptr;
  }, 1400, nullptr);
}

// Page title "TV ⌄" style: tapping opens the page picker.
inline std::function<void()> open_picker = [] {};
inline lv_obj_t *page_title(lv_obj_t *page, const char *t, const std::string &id) {
  lv_obj_t *hit = nm(button(page, 4, 0, 130, 44, WHITE, LV_OPA_TRANSP, 9, [] { open_picker(); }), id);
  lv_obj_t *l = text(hit, 10, 10, 0, R.f17b, WHITE, t);
  lv_obj_update_layout(l);
  icon(hit, "chev_down", 16, 10 + lv_obj_get_width(l) + 5, 13, WHITE, 204);
  return hit;
}

// Source tile: app icon, coloured text tile ("PS5", "HDMI") or icon tile (Live TV).
inline lv_obj_t *source_tile(lv_obj_t *parent, const Source &s, int x, int y, int size) {
  std::string app = "app_" + s.id;
  for (auto &c : app)
    if (c == '.') c = '_';
  const lv_image_dsc_t *d = s.kind == "app" ? R.get(app) : nullptr;
  int radius = size * 12 / 44;
  lv_obj_t *t = box(parent, x, y, size, size, d ? BG : s.color, d ? LV_OPA_TRANSP : LV_OPA_COVER, radius);
  lv_obj_set_style_clip_corner(t, true, 0);
  if (d) {
    lv_obj_t *im = lv_image_create(t);
    lv_image_set_src(im, d);
    if (size != 44) lv_image_set_scale(im, 256 * size / 44);
    lv_obj_center(im);
    lv_obj_remove_flag(im, LV_OBJ_FLAG_CLICKABLE);
  } else if (s.icon == "tv") {
    icon(t, "tv", size >= 60 ? 34 : 20, 0, 0, WHITE);
    lv_obj_center(lv_obj_get_child(t, 0));
  } else {
    const char *label = s.icon == "ps5" ? "PS5" : s.kind == "input" ? "HDMI" : nullptr;
    std::string letter = label ? label : s.name.substr(0, 1);
    lv_obj_t *l = text(t, 0, 0, 0, size >= 60 ? R.f20b : R.f13b, WHITE, letter.c_str());
    lv_obj_center(l);
  }
  return t;
}

inline void open_sources();

// ---- TV page -------------------------------------------------------------------------------------------
struct TvPage {
  lv_obj_t *root, *np, *noart, *off, *quick;
  lv_obj_t *art, *title, *app, *sub, *scrub, *track, *fill, *knob, *pos, *rem, *play, *play_icon, *back10, *fwd10;
  lv_obj_t *na_tile_holder, *na_name, *na_sub;
  lv_obj_t *off_power;
  int64_t scrub_start_x = -1;
  bool scrubbing = false;
  float scrub_fraction = 0;
};
inline TvPage tvp;

inline void set_progress_bar(float f) {
  int w = (int) (212 * f);
  lv_obj_set_width(tvp.fill, w < 1 ? 1 : w);
  lv_obj_set_x(tvp.knob, w - 8 < 0 ? 0 : w - 8 > 196 ? 196 : w - 8);
}

inline void scrub_event(lv_event_t *e) {
  lv_event_code_t code = lv_event_get_code(e);
  lv_point_t p;
  lv_indev_get_point(lv_indev_active(), &p);
  int x = p.x - 14;
  if (code == LV_EVENT_PRESSED) {
    tvp.scrub_start_x = p.x;
    tvp.scrubbing = false;
  } else if (code == LV_EVENT_PRESSING) {
    if (!tvp.scrubbing && std::abs((int) (p.x - tvp.scrub_start_x)) >= 8) tvp.scrubbing = true;  // drag threshold
    if (tvp.scrubbing) {
      tvp.scrub_fraction = x < 0 ? 0 : x > 212 ? 1 : x / 212.0f;
      set_progress_bar(tvp.scrub_fraction);
    }
  } else if (code == LV_EVENT_RELEASED || code == LV_EVENT_PRESS_LOST) {
    if (tvp.scrubbing && hooks.seek && tv.duration > 0) hooks.seek(tvp.scrub_fraction * tv.duration);
    tvp.scrubbing = false;
  }
}

inline lv_obj_t *build_quick_row(lv_obj_t *page) {
  box(page, 0, 240, 240, 1, WHITE, 26);
  lv_obj_t *row = nm(box(page, 0, 244, 240, 76, WHITE, LV_OPA_TRANSP), "quick_row");
  lv_obj_add_flag(row, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_scroll_dir(row, LV_DIR_HOR);
  lv_obj_set_scrollbar_mode(row, LV_SCROLLBAR_MODE_OFF);
  lv_obj_remove_flag(row, LV_OBJ_FLAG_SCROLL_CHAIN_HOR);   // a swipe here scrolls the row, not the page
  return row;
}

inline void build_tv(lv_obj_t *page) {
  tvp.root = nm(page, "tv_root");
  page_title(page, "TV", "tv_title");

  // Now Playing (artwork or not)
  tvp.np = box(page, 0, 0, 240, 240, WHITE, LV_OPA_TRANSP);
  tvp.art = nm(lv_image_create(tvp.np), "np_art");
  lv_obj_set_pos(tvp.art, 14, 36);
  lv_obj_set_size(tvp.art, 212, 76);
  lv_obj_set_style_radius(tvp.art, 10, 0);
  lv_obj_set_style_clip_corner(tvp.art, true, 0);
  lv_obj_set_style_bg_color(tvp.art, lv_color_hex(CARD), 0);
  lv_obj_set_style_bg_opa(tvp.art, LV_OPA_COVER, 0);
  tvp.title = nm(text(tvp.np, 14, 115, 212, R.f20b, WHITE, ""), "np_title");
  tvp.app = nm(text(tvp.np, 14, 141, 0, R.f13b, 0xFF8FA6, ""), "np_app");
  tvp.sub = nm(text(tvp.np, 70, 141, 156, R.f13, WHITE, "", LV_TEXT_ALIGN_LEFT, 199), "np_sub");

  tvp.scrub = nm(box(tvp.np, 14, 146, 212, 44, WHITE, LV_OPA_TRANSP), "np_scrub");
  lv_obj_add_flag(tvp.scrub, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_remove_flag(tvp.scrub, LV_OBJ_FLAG_SCROLL_CHAIN);   // drags here never change the page
  lv_obj_remove_flag(tvp.scrub, LV_OBJ_FLAG_GESTURE_BUBBLE);
  for (auto c : {LV_EVENT_PRESSED, LV_EVENT_PRESSING, LV_EVENT_RELEASED, LV_EVENT_PRESS_LOST})
    lv_obj_add_event_cb(tvp.scrub, scrub_event, c, nullptr);
  tvp.track = box(tvp.scrub, 0, 20, 212, 5, WHITE, 71, 2);
  tvp.fill = box(tvp.track, 0, 0, 1, 5, WHITE, LV_OPA_COVER, 2);
  tvp.knob = box(tvp.scrub, 0, 14, 16, 16, WHITE, LV_OPA_COVER, 8);
  tvp.pos = nm(text(tvp.np, 14, 176, 0, R.f12, WHITE, "", LV_TEXT_ALIGN_LEFT, 199), "np_pos");
  tvp.rem = nm(text(tvp.np, 150, 176, 76, R.f12, WHITE, "", LV_TEXT_ALIGN_RIGHT, 199), "np_rem");

  tvp.back10 = nm(button(tvp.np, 14, 200, 56, 44, WHITE, 26, 12, [] {
                    if (hooks.seek) hooks.seek(std::max(0.0f, tv.position - 10));
                  }), "np_back10");
  icon(tvp.back10, "back10", 20, 7, 12, WHITE);
  text(tvp.back10, 32, 14, 0, R.f12s, WHITE, "10");
  tvp.play = nm(button(tvp.np, 88, 200, 64, 44, WHITE, LV_OPA_COVER, 22, [] {
                  if (hooks.tv_key) hooks.tv_key("MEDIA_PLAY_PAUSE");
                }), "np_play");
  tvp.play_icon = icon(tvp.play, "pause", 22, 21, 11, 0x000000);
  tvp.fwd10 = nm(button(tvp.np, 170, 200, 56, 44, WHITE, 26, 12, [] {
                   if (hooks.seek) hooks.seek(tv.position + 10);
                 }), "np_fwd10");
  text(tvp.fwd10, 7, 14, 0, R.f12s, WHITE, "10");
  icon(tvp.fwd10, "fwd10", 20, 29, 12, WHITE);

  // Input / app in front, or playing without artwork
  tvp.noart = box(page, 0, 0, 240, 240, WHITE, LV_OPA_TRANSP);
  tvp.na_tile_holder = box(tvp.noart, 86, 40, 68, 68, WHITE, LV_OPA_TRANSP);
  tvp.na_name = nm(text(tvp.noart, 14, 115, 212, R.f20b, WHITE, "", LV_TEXT_ALIGN_CENTER), "na_name");
  tvp.na_sub = nm(text(tvp.noart, 14, 141, 212, R.f13, WHITE, "", LV_TEXT_ALIGN_CENTER, 199), "na_sub");
  nm(text_button(tvp.noart, 14, 168, 102, 44, "Back to TV", WHITE, 31, 12, WHITE,
                 [] { if (hooks.launch) hooks.launch("tuner"); }), "na_back");
  nm(text_button(tvp.noart, 124, 168, 102, 44, "Sources", WHITE, 31, 12, WHITE, [] { open_sources(); }),
     "na_sources");

  // TV off
  tvp.off = box(page, 0, 0, 240, 240, WHITE, LV_OPA_TRANSP);
  text(tvp.off, 14, 84, 212, R.f15, WHITE, "TV is off", LV_TEXT_ALIGN_CENTER, 199);
  tvp.off_power = nm(button(tvp.off, 60, 120, 120, 56, WHITE, LV_OPA_COVER, 28, [] {
                       if (hooks.power) hooks.power();
                     }), "tv_off_power");
  icon(tvp.off_power, "power", 34, 43, 11, 0x000000);

  tvp.quick = build_quick_row(page);
}

inline void render_quick() {
  lv_obj_clean(tvp.quick);
  int i = 0;
  std::vector<std::string> ids = tv.quick;
  for (auto &s : tv.sources)   // the fifth tile peeks to show the row scrolls
    if (ids.size() < 6 && std::find(ids.begin(), ids.end(), s.id) == ids.end()) ids.push_back(s.id);
  for (auto &id : ids) {
    const Source *s = find_source(id);
    if (!s) continue;
    int x = 13 + 58 * i;
    lv_obj_t *t = source_tile(tvp.quick, *s, x, 12, 44);
    std::string sid = s->id;
    nm(t, i < 4 ? "quick_" + std::to_string(i) : "quick_peek");
    on_tap(t, [sid] { if (hooks.launch) hooks.launch(sid); });
    text(tvp.quick, x - 3, 58, 50, R.f12, WHITE, short_name(*s).c_str(), LV_TEXT_ALIGN_CENTER, 224);
    if (s->id == tv.current) box(tvp.quick, x + 39, 9, 9, 9, WHITE, LV_OPA_COVER, 5);
    i++;
  }
}

inline std::string mmss(int s, bool neg = false) {
  char buf[16];
  if (s >= 3600) snprintf(buf, sizeof buf, "%s%d:%02d:%02d", neg ? "\xE2\x88\x92" : "", s / 3600, s / 60 % 60, s % 60);
  else snprintf(buf, sizeof buf, "%s%d:%02d", neg ? "\xE2\x88\x92" : "", s / 60, s % 60);
  return buf;
}

// Called every second and on every HA update.
inline void tick_tv(int64_t now_ms) {
  if (tvp.scrubbing) return;
  auto p = umote::progress(tv.duration, tv.position, tv.position_ms, now_ms, tv.playing);
  for (lv_obj_t *o : {tvp.scrub, tvp.pos, tvp.rem}) show(o, p.show && tv.seekable);
  show(tvp.back10, p.show && tv.seekable);
  show(tvp.fwd10, p.show && tv.seekable);
  if (p.show) {
    set_progress_bar(p.fraction);
    lv_label_set_text(tvp.pos, mmss(p.pos_s).c_str());
    lv_label_set_text(tvp.rem, mmss(p.remaining_s, true).c_str());
  }
  bool stale = umote::is_stale(tv.updated_ms, now_ms);
  lv_opa_t opa = stale ? LV_OPA_50 : LV_OPA_COVER;
  for (lv_obj_t *o : {tvp.np, tvp.noart}) lv_obj_set_style_opa(o, opa, 0);
  if (stale) {
    int ago = (int) ((now_ms - tv.updated_ms) / 1000);
    std::string s = "Last seen " + mmss(ago) + " ago";
    lv_label_set_text(tvp.sub, (" \xC2\xB7 " + s).c_str());
    lv_label_set_text(tvp.na_sub, s.c_str());
  }
}

inline void tint(lv_obj_t *page, uint32_t color) {
  lv_obj_set_style_bg_opa(page, LV_OPA_COVER, 0);
  lv_obj_set_style_bg_color(page, lv_color_hex(color), 0);
  lv_obj_set_style_bg_grad_color(page, lv_color_hex(BG), 0);
  lv_obj_set_style_bg_grad_dir(page, LV_GRAD_DIR_VER, 0);
  lv_obj_set_style_bg_main_stop(page, 0, 0);
  lv_obj_set_style_bg_grad_stop(page, 150, 0);
}

inline uint32_t darken(uint32_t c, int pct) {
  int r = (c >> 16 & 0xFF) * pct / 100, g = (c >> 8 & 0xFF) * pct / 100, b = (c & 0xFF) * pct / 100;
  return (uint32_t) (r << 16 | g << 8 | b);
}

inline void render_tv(int64_t now_ms) {
  auto view = umote::select_view(tv.tv_on, tv.cast_state.c_str(), !tv.title.empty(), tv.has_art,
                                 tv.activity.c_str());
  const Source *cur = find_source(tv.current);
  show(tvp.off, view == umote::TvView::OFF);
  show(tvp.np, view == umote::TvView::PLAYING_ART);
  show(tvp.noart, view != umote::TvView::OFF && view != umote::TvView::PLAYING_ART);
  tint(tvp.root, view == umote::TvView::OFF ? BG : darken(cur ? cur->color : GREY, 60));

  std::string app = umote::sanitize(tv.app_name, cur ? cur->name : "TV");
  std::string title = umote::sanitize(tv.title, app);
  if (view == umote::TvView::PLAYING_ART) {
    lv_label_set_text(tvp.title, title.c_str());
    lv_label_set_text(tvp.app, app.c_str());
    lv_obj_update_layout(tvp.app);
    int aw = lv_obj_get_width(tvp.app);
    lv_obj_set_x(tvp.sub, 14 + aw);
    lv_obj_set_width(tvp.sub, std::max(0, 212 - aw));
    lv_label_set_text(tvp.sub, tv.playing ? " \xC2\xB7 Playing" : " \xC2\xB7 Paused");
    set_icon(tvp.play_icon, tv.playing ? "pause" : "play", 22);
  } else if (view != umote::TvView::OFF) {
    lv_obj_clean(tvp.na_tile_holder);
    if (cur) source_tile(tvp.na_tile_holder, *cur, 0, 0, 68);
    bool media = view == umote::TvView::PLAYING_NOART;
    lv_label_set_text(tvp.na_name, media ? title.c_str() : cur ? cur->name.c_str() : "TV");
    std::string sub = cur && cur->kind == "input" ? "HDMI " + std::to_string(cur->port) + " \xC2\xB7 On"
                      : media                    ? app
                                                 : "On";
    lv_label_set_text(tvp.na_sub, sub.c_str());
  }
  render_quick();
  tick_tv(now_ms);
}

// ---- modal sheets ----------------------------------------------------------------------------------------
inline lv_obj_t *dim_layer(const std::string &id) {
  lv_obj_t *d = nm(box(lv_layer_top(), 0, 0, 240, 320, 0x000000, 140), id);
  lv_obj_add_flag(d, LV_OBJ_FLAG_CLICKABLE);   // swallow taps behind the sheet
  show(d, false);
  return d;
}

struct Sheets {
  lv_obj_t *src, *src_grid, *hdmi, *hdmi_title;
  int hdmi_port = 0;
  std::string hdmi_choice;
  std::vector<lv_obj_t *> hdmi_opts;
  lv_obj_t *hdmi_switch;
};
inline Sheets sh;

inline bool sheet_open() { return !lv_obj_has_flag(sh.src, LV_OBJ_FLAG_HIDDEN) || !lv_obj_has_flag(sh.hdmi, LV_OBJ_FLAG_HIDDEN); }

inline void close_sheets() {
  show(sh.src, false);
  show(sh.hdmi, false);
}

inline void open_new_hdmi(int port) {
  sh.hdmi_port = port;
  sh.hdmi_choice.clear();
  lv_label_set_text_fmt(sh.hdmi_title, "New on HDMI %d", port);
  for (auto *o : sh.hdmi_opts) lv_obj_set_style_bg_color(o, lv_color_hex(WHITE), 0), lv_obj_set_style_bg_opa(o, 31, 0);
  show(sh.src, false);
  show(sh.hdmi, true);
}

inline bool more_open = false;

inline void render_sources_sheet() {
  lv_obj_t *g = sh.src_grid;
  lv_obj_clean(g);
  int y = 0;
  auto cap = [&](const char *t) {
    text(g, 12, y, 0, R.f12s, WHITE, t, LV_TEXT_ALIGN_LEFT, 184);
    y += 20;
  };
  auto grid = [&](std::vector<const Source *> items) {
    int i = 0;
    for (auto *s : items) {
      int x = 11 + 58 * (i % 4), ty = y + 68 * (i / 4);
      lv_obj_t *t = nm(source_tile(g, *s, x, ty, 44), "src_" + s->id);
      std::string sid = s->id;
      int port = s->port;
      bool unnamed = s->unnamed();
      on_tap(t, [sid, port, unnamed] {
        if (unnamed) {
          open_new_hdmi(port);
          return;
        }
        close_sheets();
        if (hooks.launch) hooks.launch(sid);
      });
      text(g, x - 3, ty + 46, 50, R.f12, WHITE, short_name(*s).c_str(), LV_TEXT_ALIGN_CENTER, 224);
      if (unnamed) {
        lv_obj_t *chip = box(g, x + 3, ty - 7, 38, 16, YELLOW, LV_OPA_COVER, 7);
        lv_obj_center(text(chip, 0, 0, 0, R.f12s, 0x000000, "New"));
      }
      if (s->id == tv.current) box(g, x + 38, ty - 3, 9, 9, WHITE, LV_OPA_COVER, 5);
      i++;
    }
    y += 68 * ((i + 3) / 4) + 2;
  };
  std::vector<const Source *> inputs, apps, more;
  for (auto &s : tv.sources) {
    bool collapsed = std::find(tv.more.begin(), tv.more.end(), s.id) != tv.more.end();
    (s.kind == "app" ? (collapsed ? more : apps) : inputs).push_back(&s);
  }
  cap("Inputs");
  grid(inputs);
  cap("Apps");
  grid(apps);
  if (!more.empty()) {
    if (more_open) {
      cap("More apps");
      grid(more);
    } else {
      lv_obj_t *b = nm(text_button(g, 11, y, 218, 44, "More apps", WHITE, 26, 12, WHITE, [] {
                         more_open = true;
                         render_sources_sheet();
                       }), "row_more_apps");
      (void) b;
      y += 52;
    }
  }
  box(g, 0, y, 1, 8, WHITE, LV_OPA_TRANSP);   // bottom padding for scrolling
}

inline void open_sources() {
  more_open = false;
  render_sources_sheet();
  show(sh.src, true);
}

inline void build_sheets() {
  // Sources sheet
  sh.src = dim_layer("src_dim");
  lv_obj_t *s = nm(box(sh.src, 0, 26, 240, 294, SHEET, LV_OPA_COVER, 14), "src_sheet");
  lv_obj_add_flag(s, LV_OBJ_FLAG_CLICKABLE);
  box(s, 102, 6, 36, 5, WHITE, 77, 2);
  text(s, 14, 14, 0, R.f17b, WHITE, "Sources");
  nm(text_button(s, 172, 2, 60, 44, "Done", WHITE, LV_OPA_TRANSP, 12, LINK, [] { close_sheets(); }), "src_done");
  sh.src_grid = nm(box(s, 0, 52, 240, 242, WHITE, LV_OPA_TRANSP), "src_grid");
  lv_obj_add_flag(sh.src_grid, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_scroll_dir(sh.src_grid, LV_DIR_VER);
  lv_obj_set_scrollbar_mode(sh.src_grid, LV_SCROLLBAR_MODE_OFF);

  // New HDMI device dialog
  sh.hdmi = dim_layer("hdmi_dim");
  lv_obj_t *d = nm(box(sh.hdmi, 12, 40, 216, 248, CARD, LV_OPA_COVER, 14), "new_hdmi_dialog");
  lv_obj_add_flag(d, LV_OBJ_FLAG_CLICKABLE);
  sh.hdmi_title = text(d, 12, 12, 192, R.f17b, WHITE, "New on HDMI");
  lv_obj_t *body = text(d, 12, 38, 192, R.f13, WHITE, "It didn't say its name. What is it?", LV_TEXT_ALIGN_LEFT, 204);
  lv_label_set_long_mode(body, LV_LABEL_LONG_WRAP);
  lv_obj_set_height(body, LV_SIZE_CONTENT);
  struct Opt { const char *name; int x, y, w; };
  static const Opt opts[] = {{"Set-top box", 12, 78, 104}, {"Fire TV", 124, 78, 80}, {"PC", 12, 130, 64},
                             {"Other", 84, 130, 84}};
  for (auto &o : opts) {
    std::string name = o.name;
    lv_obj_t *b = nullptr;
    b = text_button(d, o.x, o.y, o.w, 44, o.name, WHITE, 31, 22, WHITE, [name] {
      sh.hdmi_choice = name;
      for (size_t i = 0; i < sh.hdmi_opts.size(); i++) {
        bool sel = opts[i].name == name;
        lv_obj_set_style_bg_color(sh.hdmi_opts[i], lv_color_hex(sel ? BLUE : WHITE), 0);
        lv_obj_set_style_bg_opa(sh.hdmi_opts[i], sel ? LV_OPA_COVER : 31, 0);
      }
    });
    nm(b, std::string("hdmi_opt_") + std::to_string(sh.hdmi_opts.size()));
    sh.hdmi_opts.push_back(b);
  }
  nm(text_button(d, 12, 192, 92, 44, "Later", WHITE, 26, 12, WHITE, [] { close_sheets(); }), "hdmi_later");
  sh.hdmi_switch = nm(text_button(d, 112, 192, 92, 44, "Switch", BLUE, LV_OPA_COVER, 12, WHITE, [] {
                        if (!sh.hdmi_choice.empty() && hooks.name_source)
                          hooks.name_source(sh.hdmi_port, sh.hdmi_choice, true);
                        else if (hooks.launch)
                          hooks.launch("hdmi" + std::to_string(sh.hdmi_port));
                        close_sheets();
                      }), "hdmi_switch");
}

// ---- pages -------------------------------------------------------------------------------------------------
struct Pages {
  lv_obj_t *view;
  lv_obj_t *page[4];
  int current = 0;
};
inline Pages pg;

inline void show_page(int i, bool anim = false) {
  pg.current = i;
  lv_tileview_set_tile_by_index(pg.view, i, 0, anim ? LV_ANIM_ON : LV_ANIM_OFF);
  if (hooks.page_shown) hooks.page_shown(i);
}

inline void build(lv_obj_t *view, std::array<lv_obj_t *, 4> pages) {
  pg.view = view;
  for (int i = 0; i < 4; i++) {
    pg.page[i] = pages[i];
    lv_obj_set_style_bg_color(pages[i], lv_color_hex(BG), 0);
    lv_obj_set_style_bg_opa(pages[i], LV_OPA_COVER, 0);
    lv_obj_remove_flag(pages[i], LV_OBJ_FLAG_SCROLLABLE);
  }
  lv_obj_add_event_cb(pg.view, [](lv_event_t *) {
    lv_obj_t *t = lv_tileview_get_tile_active(pg.view);
    for (int i = 0; i < 4; i++)
      if (pg.page[i] == t && pg.current != i) {
        pg.current = i;
        if (hooks.page_shown) hooks.page_shown(i);
      }
  }, LV_EVENT_VALUE_CHANGED, nullptr);
  build_tv(pg.page[0]);
  build_status();
  build_sheets();
  build_overlays();
}

}  // namespace ui
