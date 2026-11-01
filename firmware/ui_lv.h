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
#include "esphome/core/log.h"
#include "logic.h"

#ifdef USE_ESP32
#include <esp_heap_caps.h>
#else
#include <malloc.h>
#endif

namespace ui {

// Free heap (device) or a stand-in that falls as memory is used (host), for build-time logging.
inline size_t heap_free() {
#ifdef USE_ESP32
  return heap_caps_get_free_size(MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);
#else
  return ((size_t) 1 << 30) - mallinfo2().uordblks;
#endif
}

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

// "Large" text size: every font one step up (applied before build, so it needs a restart).
inline void enlarge_fonts() {
  R = Res{R.f13, R.f14, R.f15, R.f17, R.f20, R.f20, R.f15b, R.f17b, R.f20b, R.f20b, R.f13b, R.f15b, R.img};
}
inline bool large_text = false;

// Widget names, used by the simulator's layout dump (tools/check_ui.py rules key off them).
inline std::map<const lv_obj_t *, std::string> &names() {
  static std::map<const lv_obj_t *, std::string> m;
  return m;
}
inline lv_obj_t *nm(lv_obj_t *o, const std::string &n) {
#ifdef USE_HOST
  if (!names().count(o))
    lv_obj_add_event_cb(o, [](lv_event_t *e) { names().erase((lv_obj_t *) lv_event_get_target(e)); },
                        LV_EVENT_DELETE, nullptr);
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
  std::function<void(const std::string &)> sb_ir;               // soundbar IR code name
  // Home Assistant call: kind = "toggle" | "on" | "off" | "fan_pct" | "timer"; entities comma-separated.
  std::function<void(const std::string &, const std::string &, const std::string &)> ha;
  std::function<void()> wifi_scan;
  std::function<void(const std::string &, const std::string &)> wifi_join;   // ssid, password
  std::function<void()> settings_changed;                                    // ui::cfg was edited
  std::function<void()> keep_awake;   // toggle: WiFi on, no sleep for 10 min (for wireless updates)
  std::function<void(const std::string &)> log;
};
inline Hooks hooks;

// False until build() has run. The device calls into the UI before LVGL exists (on_boot at
// priority 800, the battery sensor, toasts from start_session), so every entry point checks it.
inline bool ready = false;

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
  lv_obj_set_style_bg_opa(b, opa > LV_OPA_50 ? (lv_opa_t) LV_OPA_70 : (lv_opa_t) (opa + 30), LV_STATE_PRESSED);
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
  if (!ready) return;
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
  if (!ready) return;
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
  if (large_text) lv_obj_add_flag(tvp.art, LV_OBJ_FLAG_HIDDEN);   // room for bigger text
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
  char buf[32];
  if (s >= 3600) snprintf(buf, sizeof buf, "%s%d:%02d:%02d", neg ? "\xE2\x88\x92" : "", s / 3600, s / 60 % 60, s % 60);
  else snprintf(buf, sizeof buf, "%s%d:%02d", neg ? "\xE2\x88\x92" : "", s / 60, s % 60);
  return buf;
}

// Called every second and on every HA update.
inline void tick_tv(int64_t now_ms) {
  if (!ready) return;
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
  if (!ready) return;
  auto view = umote::select_view(tv.tv_on, tv.cast_state.c_str(), !tv.title.empty(), tv.has_art,
                                 tv.activity.c_str());
  const Source *cur = find_source(tv.current);
  show(tvp.off, view == umote::TvView::OFF);
  show(tvp.np, view == umote::TvView::PLAYING_ART);
  if (large_text) show(tvp.art, false);
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
inline std::vector<lv_obj_t *> &modals() {
  static std::vector<lv_obj_t *> m;
  return m;
}
inline lv_obj_t *dim_layer(const std::string &id) {
  lv_obj_t *d = nm(box(lv_layer_top(), 0, 0, 240, 320, 0x000000, 140), id);
  lv_obj_add_flag(d, LV_OBJ_FLAG_CLICKABLE);   // swallow taps behind the sheet
  show(d, false);
  modals().push_back(d);
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

inline bool sheet_open() {
  for (auto *m : modals())
    if (!lv_obj_has_flag(m, LV_OBJ_FLAG_HIDDEN)) return true;
  return false;
}
// Sheets and dialogs are built when they open and freed when they close: with no PSRAM the
// hidden copies would cost ~40 KB of heap. Deletion is async because the tap that closes a
// sheet usually comes from a button inside it.
inline void drop_modal(lv_obj_t *&m) {
  if (!m) return;
  auto &v = modals();
  v.erase(std::remove(v.begin(), v.end(), m), v.end());
  lv_obj_delete_async(m);
  m = nullptr;
}
inline void destroy_sheets();
inline void destroy_options();
inline void destroy_picker();
inline void close_sheets() {
  for (auto *m : modals()) show(m, false);
  destroy_sheets();
  destroy_options();
  destroy_picker();
}
inline void build_sheets();
inline void ensure_sheets() {
  if (!sh.src) build_sheets();
}

inline void open_new_hdmi(int port) {
  ensure_sheets();
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
  if (!g) return;   // only while the sheet exists
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
  if (!ready) return;
  ensure_sheets();
  more_open = false;
  render_sources_sheet();
  show(sh.src, true);
}

inline void destroy_sheets() {
  if (!sh.src) return;
  drop_modal(sh.src);
  drop_modal(sh.hdmi);
  sh = Sheets{};
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

// ---- Soundbar page --------------------------------------------------------------------------------------
// Button names come from the soundbar remote (substitutions in ui.yaml); codes are the upper-case names.
inline std::vector<std::string> sb_inputs = {"TV", "Bluetooth", "Music"}, sb_modes = {"Cinema", "Voice", "Night"};
struct SbPage {
  std::vector<lv_obj_t *> in, mode;
  int in_sel = 0, mode_sel = -1;
};
inline SbPage sbp;

inline std::string ir_code(std::string n) {
  for (auto &c : n) c = c == ' ' ? '_' : (char) toupper(c);
  return n;
}

inline void sb_select(std::vector<lv_obj_t *> &row, int sel) {
  for (size_t i = 0; i < row.size(); i++)
    lv_obj_set_style_bg_color(row[i], lv_color_hex((int) i == sel ? BLUE : CARD), 0);
}

inline void build_soundbar(lv_obj_t *page) {
  page_title(page, "Soundbar", "sb_title");
  auto row = [&](const char *cap, int y, std::vector<std::string> &names, std::vector<lv_obj_t *> &out,
                 const char *id, int *sel) {
    text(page, 12, y - 18, 0, R.f12s, WHITE, cap, LV_TEXT_ALIGN_LEFT, 184);
    for (int i = 0; i < 3 && i < (int) names.size(); i++) {
      std::string code = ir_code(names[i]);
      auto *row_ref = &out;
      lv_obj_t *b = text_button(page, 12 + 75 * i, y, 66, 44, "", CARD, LV_OPA_COVER, 12, WHITE, [code, i, row_ref, sel] {
        *sel = i;
        sb_select(*row_ref, i);
        if (hooks.sb_ir) hooks.sb_ir(code);
      });
      lv_obj_t *l = lv_obj_get_child(b, 0);
      lv_label_set_text(l, names[i].c_str());
      lv_obj_update_layout(l);
      if (lv_obj_get_width(l) > 60) lv_obj_set_style_text_font(l, R.f12s, 0);
      lv_obj_center(l);
      out.push_back(nm(b, std::string(id) + std::to_string(i)));
    }
  };
  row("Input", 54, sb_inputs, sbp.in, "sb_in_", &sbp.in_sel);
  row("Sound", 124, sb_modes, sbp.mode, "sb_mode_", &sbp.mode_sel);
  sb_select(sbp.in, sbp.in_sel);
  struct Vol { const char *icon, *label, *code, *id; };
  static const Vol vols[] = {{"vol_down", "Down", "VOL_DOWN", "sb_vol_down"}, {"mute", "Mute", "MUTE", "sb_mute"},
                             {"vol_up", "Up", "VOL_UP", "sb_vol_up"}};
  for (int i = 0; i < 3; i++) {
    std::string code = vols[i].code;
    lv_obj_t *b = nm(button(page, 12 + 75 * i, 178, 66, 64, CARD, LV_OPA_COVER, 12, [code] {
                       if (hooks.sb_ir) hooks.sb_ir(code);
                     }), vols[i].id);
    icon(b, vols[i].icon, 24, 21, 12, WHITE);
    text(b, 0, 38, 66, R.f12, WHITE, vols[i].label, LV_TEXT_ALIGN_CENTER, 204);
  }
}

// ---- Home page ------------------------------------------------------------------------------------------
struct Tile {
  std::string id, name, kind, icon, state, label, entities, led, timer;
  int speed_count = 0;
};
struct HomePage {
  lv_obj_t *page, *grid;
  std::vector<Tile> tiles;
  std::vector<lv_obj_t *> objs;
  int focus = 0;
  int64_t updated_ms = 0;
};
inline HomePage hp;

inline void parse_tiles(const std::string &json) {
  JsonDocument doc;
  if (deserializeJson(doc, json)) return;
  hp.tiles.clear();
  for (JsonObject t : doc.as<JsonArray>()) {
    Tile tile;
    tile.id = t["id"] | "";
    tile.name = umote::sanitize(t["name"] | "", "Device");
    tile.kind = t["kind"] | "";
    tile.icon = t["icon"] | "plug";
    tile.state = t["state"] | "off";
    tile.label = t["label"] | "";
    JsonArray entities = t["entities"];
    for (JsonVariant e : entities) {
      if (!tile.entities.empty()) tile.entities += ",";
      tile.entities += e.as<std::string>();
    }
    tile.led = t["options"]["led"] | "";
    tile.timer = t["options"]["timer"] | "";
    tile.speed_count = t["options"]["speed_count"] | 0;
    hp.tiles.push_back(tile);
  }
  if (hp.focus >= (int) hp.tiles.size()) hp.focus = 0;
}

inline void open_options(int i);
inline void render_home();

inline void paint_focus() {
  for (size_t i = 0; i < hp.objs.size(); i++) {
    bool f = (int) i == hp.focus;
    lv_obj_set_style_outline_width(hp.objs[i], f ? 3 : 0, 0);
    lv_obj_set_style_outline_pad(hp.objs[i], f ? 2 : 0, 0);
  }
  if (hp.focus < (int) hp.objs.size()) lv_obj_scroll_to_view(hp.objs[hp.focus], LV_ANIM_ON);
}

inline void toggle_tile(int i) {
  if (i >= (int) hp.tiles.size()) return;
  Tile &t = hp.tiles[i];
  if (t.state == "offline") return;
  bool on = t.state == "on";
  if (hooks.ha) hooks.ha(on ? "off" : "on", t.entities, "");
  t.state = on ? "off" : "on";   // optimistic until HA reports back
  t.label = on ? "Off" : "On";
  render_home();
}

inline void render_home() {
  if (!ready) return;
  lv_obj_clean(hp.grid);
  hp.objs.clear();
  for (size_t i = 0; i < hp.tiles.size(); i++) {
    const Tile &t = hp.tiles[i];
    bool on = t.state == "on", off_line = t.state == "offline";
    int x = 12 + 116 * (i % 2), y = 5 + 77 * (i / 2);
    lv_obj_t *o = nm(button(hp.grid, x, y, 100, 64, on ? 0xF2F2F7 : 0x1F1F22, LV_OPA_COVER, 14, [i] {
                       hp.focus = (int) i;
                       toggle_tile((int) i);
                     }), "home_tile_" + std::to_string(i));
    lv_obj_set_style_outline_color(o, lv_color_hex(YELLOW), 0);
    lv_obj_add_event_cb(o, [](lv_event_t *e) { open_options((int) (intptr_t) lv_event_get_user_data(e)); },
                        LV_EVENT_LONG_PRESSED, (void *) (intptr_t) i);
    if (off_line) lv_obj_set_style_opa(o, 153, 0);
    lv_obj_t *ib = box(o, 9, 6, 22, 22, on ? 0xFFCC00 : GREY, LV_OPA_COVER, 8);
    icon(ib, t.icon, 14, 4, 4, on ? 0x000000 : WHITE);
    uint32_t fg = on ? 0x000000 : WHITE;
    text(o, 37, 9, 58, R.f12, fg, t.label.c_str(), LV_TEXT_ALIGN_LEFT, on ? 178 : 199);
    lv_obj_t *n = text(o, 9, 28, 86, R.f13b, fg, t.name.c_str());
    if (!large_text) {   // two lines fit at the default size; Large keeps one line with an ellipsis
      lv_label_set_long_mode(n, LV_LABEL_LONG_WRAP);
      lv_obj_set_height(n, 36);
    }
    hp.objs.push_back(o);
  }
  box(hp.grid, 0, 5 + 77 * ((hp.tiles.size() + 1) / 2), 1, 4, WHITE, LV_OPA_TRANSP);
  paint_focus();
}

inline void build_home(lv_obj_t *page) {
  hp.page = page;
  page_title(page, "Home", "home_title");
  text(page, 12, large_text ? 34 : 38, 0, R.f12s, WHITE, "Living room", LV_TEXT_ALIGN_LEFT, 184);
  hp.grid = nm(box(page, 0, 52, 240, 268, WHITE, LV_OPA_TRANSP), "home_grid");
  lv_obj_add_flag(hp.grid, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_scroll_dir(hp.grid, LV_DIR_VER);
  lv_obj_set_scrollbar_mode(hp.grid, LV_SCROLLBAR_MODE_OFF);
}

// D-pad on the Home page: left/right by one, up/down by a row.
inline void home_move(const char *dir) {
  if (!ready) return;
  int n = (int) hp.tiles.size();
  if (!n) return;
  int d = !strcmp(dir, "LEFT") ? -1 : !strcmp(dir, "RIGHT") ? 1 : !strcmp(dir, "UP") ? -2 : 2;
  int f = hp.focus + d;
  if (f >= 0 && f < n) hp.focus = f;
  paint_focus();
}
inline void home_scroll(bool up) { lv_obj_scroll_by(hp.grid, 0, up ? 154 : -154, LV_ANIM_ON); }
inline void home_toggle_focus() {
  if (!ready) return;
  toggle_tile(hp.focus); }

// ---- device options sheet (fans) -------------------------------------------------------------------------
struct OptSheet {
  lv_obj_t *root, *title, *power_tog, *speed, *of, *led_tog, *led_row;
  std::vector<lv_obj_t *> timers;
  int tile = -1, speed_val = 0;
};
inline OptSheet op;

inline void paint_toggle(lv_obj_t *tog, bool on) {
  lv_obj_set_style_bg_color(tog, lv_color_hex(on ? 0x34C759 : GREY), 0);
  lv_obj_set_x(lv_obj_get_child(tog, 0), on ? 20 : 2);
}

inline lv_obj_t *toggle(lv_obj_t *row) {
  lv_obj_t *t = box(row, 184, 9, 44, 26, GREY, LV_OPA_COVER, 13);
  box(t, 2, 2, 22, 22, WHITE, LV_OPA_COVER, 11);
  return t;
}

inline void build_options();
inline void destroy_options() {
  if (!op.root) return;
  drop_modal(op.root);
  op = OptSheet{};
}
inline void open_options(int i) {
  if (!ready) return;
  if (i < 0 || i >= (int) hp.tiles.size() || hp.tiles[i].kind != "fan") return;
  if (!op.root) build_options();
  op.tile = i;
  const Tile &t = hp.tiles[i];
  lv_label_set_text(op.title, t.name.c_str());
  paint_toggle(op.power_tog, t.state == "on");
  int step = 0;
  sscanf(t.label.c_str(), "Speed %d", &step);
  op.speed_val = t.state == "on" ? step : 0;
  lv_label_set_text_fmt(op.speed, "%d", op.speed_val);
  lv_label_set_text_fmt(op.of, "of %d", t.speed_count);
  show(op.led_row, !t.led.empty());
  show(op.root, true);
}

inline void set_speed(int d) {
  if (op.tile < 0) return;
  Tile &t = hp.tiles[op.tile];
  int n = std::max(1, t.speed_count);
  op.speed_val = std::max(0, std::min(n, op.speed_val + d));
  lv_label_set_text_fmt(op.speed, "%d", op.speed_val);
  if (hooks.ha) hooks.ha("fan_pct", t.entities, std::to_string(op.speed_val * 100 / n));
  paint_toggle(op.power_tog, op.speed_val > 0);
}

inline void build_options() {
  op.root = dim_layer("opt_dim");
  lv_obj_t *s = nm(box(op.root, 0, 46, 240, 274, SHEET, LV_OPA_COVER, 14), "opt_sheet");
  lv_obj_add_flag(s, LV_OBJ_FLAG_CLICKABLE);
  box(s, 102, 6, 36, 5, WHITE, 77, 2);
  lv_obj_t *pw = nm(button(s, 0, 14, 240, 44, WHITE, LV_OPA_TRANSP, 0, [] {
                      if (op.tile < 0) return;
                      Tile &t = hp.tiles[op.tile];
                      bool on = t.state != "on";
                      if (hooks.ha) hooks.ha(on ? "on" : "off", t.entities, "");
                      t.state = on ? "on" : "off";
                      paint_toggle(op.power_tog, on);
                    }), "row_opt_power");
  op.title = text(pw, 14, 12, 160, R.f17b, WHITE, "");
  op.power_tog = toggle(pw);
  text(s, 12, 66, 0, R.f12s, WHITE, "Speed", LV_TEXT_ALIGN_LEFT, 184);
  lv_obj_t *minus = nm(button(s, 12, 84, 56, 44, CARD, LV_OPA_COVER, 12, [] { set_speed(-1); }), "opt_speed_minus");
  icon(minus, "minus", 20, 18, 12, WHITE);
  op.speed = text(s, 76, 92, 40, R.f20b, WHITE, "0", LV_TEXT_ALIGN_RIGHT);
  op.of = text(s, 120, 97, 48, R.f13, WHITE, "of 6", LV_TEXT_ALIGN_LEFT, 191);
  lv_obj_t *plus = nm(button(s, 172, 84, 56, 44, CARD, LV_OPA_COVER, 12, [] { set_speed(1); }), "opt_speed_plus");
  icon(plus, "plus", 20, 18, 12, WHITE);
  text(s, 12, 138, 0, R.f12s, WHITE, "Timer", LV_TEXT_ALIGN_LEFT, 184);
  // Atomberg timer options: Off, 1, 2, 3, 6 hours
  static const char *const T[] = {"Off", "1 h", "3 h", "6 h"};
  static const int H[] = {0, 1, 3, 6};
  for (int i = 0; i < 4; i++) {
    int hours = H[i];
    lv_obj_t *b = nm(text_button(s, 12 + 56 * i, 156, 48, 44, T[i], CARD, LV_OPA_COVER, 12, WHITE, [i, hours] {
                       for (int k = 0; k < 4; k++)
                         lv_obj_set_style_bg_color(op.timers[k], lv_color_hex(k == i ? BLUE : CARD), 0);
                       if (op.tile >= 0 && hooks.ha) hooks.ha("timer", hp.tiles[op.tile].timer, std::to_string(hours));
                     }), "opt_timer_" + std::to_string(i));
    op.timers.push_back(b);
  }
  lv_obj_set_style_bg_color(op.timers[0], lv_color_hex(BLUE), 0);
  op.led_row = nm(button(s, 0, 210, 240, 44, WHITE, LV_OPA_TRANSP, 0, [] {
                    if (op.tile < 0) return;
                    if (hooks.ha) hooks.ha("toggle", hp.tiles[op.tile].led, "");
                    lv_obj_t *t = op.led_tog;
                    paint_toggle(t, lv_obj_get_x(lv_obj_get_child(t, 0)) == 2);
                  }), "row_opt_led");
  text(op.led_row, 14, 13, 160, R.f15, WHITE, "LED light");
  op.led_tog = toggle(op.led_row);
}

// ---- page picker ----------------------------------------------------------------------------------------
struct Picker {
  lv_obj_t *root;
  std::vector<lv_obj_t *> rows, checks;
};
inline Picker pk;
inline void show_page(int i, bool anim = false);

inline void build_picker() {
  pk.root = dim_layer("picker_dim");
  lv_obj_t *card = nm(box(pk.root, 8, 36, 164, 176, CARD, LV_OPA_COVER, 12), "page_picker");
  lv_obj_set_style_clip_corner(card, true, 0);
  lv_obj_add_flag(card, LV_OBJ_FLAG_CLICKABLE);
  static const char *const N[] = {"TV", "Soundbar", "Home", "Settings"};
  static const char *const I[] = {"tv", "soundbar", "home", "sliders"};
  static const char *const ID[] = {"row_pp_tv", "row_pp_sb", "row_pp_home", "row_pp_settings"};
  for (int i = 0; i < 4; i++) {
    lv_obj_t *r = nm(button(card, 0, 44 * i, 164, 44, 0x3A3A3C, LV_OPA_TRANSP, 0, [i] {
                       close_sheets();
                       show_page(i, true);
                     }), ID[i]);
    icon(r, I[i], 20, 12, 12, WHITE);
    text(r, 42, 13, 90, R.f15b, WHITE, N[i]);
    pk.checks.push_back(icon(r, "check", 16, 136, 14, WHITE));
    pk.rows.push_back(r);
  }
}

inline void destroy_picker() {
  if (!pk.root) return;
  drop_modal(pk.root);
  pk = Picker{};
}
inline void open_page_picker(int current) {
  if (!pk.root) build_picker();
  for (int i = 0; i < 4; i++) {
    lv_obj_set_style_bg_opa(pk.rows[i], i == current ? LV_OPA_COVER : LV_OPA_TRANSP, 0);
    show(pk.checks[i], i == current);
  }
  show(pk.root, true);
}

// ---- Settings page --------------------------------------------------------------------------------------
struct Config {
  bool vol_to_tv = false, text_large = false;
  float brightness = 0.6f;
  int sleep_s = 20;
};
inline Config cfg;

struct Net {
  std::string ssid;
  int rssi = 0;
  bool secure = true;
};
struct About {
  int batt_pct = 0, batt_mv = 0, rssi = 0, free_kb = 0;
  bool board = false, awake = false;
  std::string ssid, ip, firmware;
};
inline About about;

inline const char *signal_word(int rssi) {
  return rssi >= -60 ? "Strong" : rssi >= -70 ? "Good" : rssi >= -80 ? "Fair" : "Weak";
}

// Horizontal slider drawn inside a 44 px tall hit area; on_change gets 0..1 when released.
struct HSlider {
  lv_obj_t *hit, *fill, *knob;
  int w;
  std::function<void(float)> on_change;
};
inline void hslider_set(HSlider *h, float f) {
  int x = (int) (h->w * f);
  lv_obj_set_width(h->fill, std::max(1, x));
  lv_obj_set_x(h->knob, std::max(0, std::min(h->w - 18, x - 9)));
}
// Touches go to `parent` (a full-width row), so the row is the single touch target.
inline HSlider *hslider(lv_obj_t *parent, int x, int y, int w, std::function<void(float)> fn) {
  auto *h = new HSlider{nullptr, nullptr, nullptr, w, std::move(fn)};
  h->hit = box(parent, x, y, w, 44, WHITE, LV_OPA_TRANSP);
  lv_obj_add_flag(parent, LV_OBJ_FLAG_CLICKABLE);
  lv_obj_remove_flag(parent, LV_OBJ_FLAG_SCROLL_CHAIN);
  lv_obj_remove_flag(parent, LV_OBJ_FLAG_GESTURE_BUBBLE);
  lv_obj_t *track = box(h->hit, 0, 20, w, 5, GREY, LV_OPA_COVER, 2);
  h->fill = box(track, 0, 0, 1, 5, WHITE, LV_OPA_COVER, 2);
  h->knob = box(h->hit, 0, 13, 18, 18, WHITE, LV_OPA_COVER, 9);
  auto cb = [](lv_event_t *e) {
    auto *h = static_cast<HSlider *>(lv_event_get_user_data(e));
    lv_point_t p;
    lv_indev_get_point(lv_indev_active(), &p);
    lv_area_t a;
    lv_obj_get_coords(h->hit, &a);
    if (p.x < a.x1 - 12) return;   // the row's label side does nothing
    float f = std::max(0.0f, std::min(1.0f, (p.x - a.x1) / (float) h->w));
    hslider_set(h, f);
    if (lv_event_get_code(e) == LV_EVENT_RELEASED && h->on_change) h->on_change(f);
  };
  lv_obj_add_event_cb(parent, cb, LV_EVENT_PRESSING, h);
  lv_obj_add_event_cb(parent, cb, LV_EVENT_RELEASED, h);
  return h;
}

struct SetPage {
  lv_obj_t *page, *list, *wifi, *wifi_list, *about_view, *kb;
  lv_obj_t *v_wifi, *v_buttons, *v_sleep, *v_text, *v_about, *v_awake;
  HSlider *bright;
  std::vector<lv_obj_t *> rows;   // focusable rows of the visible list
  int focus = -1;
  std::vector<Net> nets;
  std::vector<lv_obj_t *> about_vals;
};
inline SetPage sp;

inline lv_obj_t *list_row(lv_obj_t *parent, int y, const std::string &id, const char *label, Tap fn) {
  lv_obj_t *r = nm(button(parent, 0, y, 240, 44, CARD, LV_OPA_TRANSP, 0, std::move(fn)), id);
  text(r, 14, 12, 0, R.f15, WHITE, label);
  return r;
}
inline lv_obj_t *row_value(lv_obj_t *row, const char *v, bool chevron = true) {
  lv_obj_t *l = text(row, 70, 13, chevron ? 140 : 156, R.f13, WHITE, v, LV_TEXT_ALIGN_RIGHT, 191);
  if (chevron) icon(row, "chev_right", 16, 212, 14, WHITE, 191);
  return l;
}

inline void set_focus_rows(std::vector<lv_obj_t *> rows) {
  sp.rows = std::move(rows);
  sp.focus = -1;
}
inline void paint_set_focus() {
  for (size_t i = 0; i < sp.rows.size(); i++)
    lv_obj_set_style_bg_opa(sp.rows[i], (int) i == sp.focus ? LV_OPA_COVER : LV_OPA_TRANSP, 0);
  if (sp.focus >= 0 && sp.focus < (int) sp.rows.size()) lv_obj_scroll_to_view(sp.rows[sp.focus], LV_ANIM_ON);
}

inline void refresh_settings() {
  if (!ready) return;
  lv_label_set_text(sp.v_wifi, about.ssid.empty() ? "Not connected" : about.ssid.c_str());
  lv_label_set_text(sp.v_buttons, cfg.vol_to_tv ? "Volume: TV" : "Volume: Soundbar");
  lv_label_set_text_fmt(sp.v_sleep, "%d s", cfg.sleep_s);
  lv_label_set_text(sp.v_text, cfg.text_large ? "Large" : "Default");
  lv_label_set_text_fmt(sp.v_about, "%d%%, %s", about.batt_pct, about.firmware.c_str());
  lv_label_set_text(sp.v_awake, about.awake ? "10 min" : "Off");
  hslider_set(sp.bright, cfg.brightness);
}

inline void show_settings_view(lv_obj_t *v);
inline void open_wifi();
inline void open_about();
inline void open_keypad(const std::string &ssid);

inline void build_settings(lv_obj_t *page) {
  sp.page = page;
  page_title(page, "Settings", "set_title");
  sp.list = box(page, 0, 52, 240, 268, WHITE, LV_OPA_TRANSP);
  lv_obj_add_flag(sp.list, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_scrollbar_mode(sp.list, LV_SCROLLBAR_MODE_OFF);
  auto changed = [] {
    refresh_settings();
    if (hooks.settings_changed) hooks.settings_changed();
  };
  lv_obj_t *wifi = list_row(sp.list, 0, "row_set_wifi", "Wi-Fi", [] { open_wifi(); });
  sp.v_wifi = row_value(wifi, "");
  lv_obj_t *br = nm(box(sp.list, 0, 44, 240, 44, CARD, LV_OPA_TRANSP), "row_set_brightness");
  text(br, 14, 12, 0, R.f15, WHITE, "Brightness");
  sp.bright = hslider(br, 118, 0, 110, [changed](float f) {
    cfg.brightness = std::max(0.1f, f);
    changed();
  });
  lv_obj_t *bt = list_row(sp.list, 88, "row_set_buttons", "Buttons", [changed] {
    cfg.vol_to_tv = !cfg.vol_to_tv;
    changed();
  });
  sp.v_buttons = row_value(bt, "");
  lv_obj_t *sl = list_row(sp.list, 132, "row_set_sleep", "Sleep after", [changed] {
    static const int S[] = {10, 20, 30, 60};
    int i = 0;
    while (i < 4 && S[i] != cfg.sleep_s) i++;
    cfg.sleep_s = S[(i + 1) % 4];
    changed();
  });
  sp.v_sleep = row_value(sl, "");
  lv_obj_t *ts = list_row(sp.list, 176, "row_set_textsize", "Text size", [changed] {
    cfg.text_large = !cfg.text_large;
    changed();   // takes effect after a restart (the YAML side reboots)
  });
  sp.v_text = row_value(ts, "");
  lv_obj_t *ab = list_row(sp.list, 220, "row_set_about", "About", [] { open_about(); });
  sp.v_about = row_value(ab, "");
  lv_obj_t *aw = list_row(sp.list, 264, "row_set_awake", "Keep awake", [] {
    if (hooks.keep_awake) hooks.keep_awake();
  });
  sp.v_awake = row_value(aw, "", false);
  box(sp.list, 0, 308, 1, 4, WHITE, LV_OPA_TRANSP);   // bottom padding for scrolling

}

struct Keypad {
  lv_obj_t *title, *field, *dots, *last, *caret, *full, *eye_icon;
  lv_obj_t *pick_root, *pick_cap;
  std::vector<lv_obj_t *> keys, key_main, key_sub, picks;
  int layout = 0;          // 0 abc, 1 ABC, 2 123, 3 #+=
  int key_focus = 4, pick_focus = 0, pick_group = -1;
  bool show_pw = false;
  std::string ssid, pw;
};
inline Keypad kb;

inline void build_wifi_view() {
  lv_obj_t *page = sp.page;
  sp.wifi = box(page, 0, 0, 240, 320, BG, LV_OPA_COVER);
  lv_obj_t *back = nm(button(sp.wifi, 4, 0, 130, 44, WHITE, LV_OPA_TRANSP, 9, [] { show_settings_view(sp.list); }),
                      "wifi_back");
  icon(back, "chev_left", 20, 2, 7, WHITE);
  text(back, 26, 10, 0, R.f17b, WHITE, "Wi-Fi");
  sp.wifi_list = box(sp.wifi, 0, 52, 240, 268, WHITE, LV_OPA_TRANSP);
  lv_obj_add_flag(sp.wifi_list, LV_OBJ_FLAG_SCROLLABLE);
  lv_obj_set_scrollbar_mode(sp.wifi_list, LV_SCROLLBAR_MODE_OFF);
}

inline void build_about_view() {
  lv_obj_t *page = sp.page;
  sp.about_view = box(page, 0, 0, 240, 320, BG, LV_OPA_COVER);
  lv_obj_t *ab_back = nm(button(sp.about_view, 4, 0, 130, 44, WHITE, LV_OPA_TRANSP, 9,
                                [] { show_settings_view(sp.list); }), "about_back");
  icon(ab_back, "chev_left", 20, 2, 7, WHITE);
  text(ab_back, 26, 10, 0, R.f17b, WHITE, "About");
  static const char *const A[] = {"Battery", "Wi-Fi", "IP", "Firmware", "Button board", "Free memory"};
  for (int i = 0; i < 6; i++) {
    lv_obj_t *r = nm(box(sp.about_view, 0, 52 + 44 * i, 240, 44, WHITE, LV_OPA_TRANSP), "row_about_" + std::to_string(i));
    text(r, 14, 12, 0, R.f15, WHITE, A[i]);
    sp.about_vals.push_back(row_value(r, "", false));
  }
}

inline void show_settings_view(lv_obj_t *v) {
  // Only the shown view exists; the others are freed (async: the tap may come from inside them).
  auto drop = [v](lv_obj_t *&o) {
    if (o && o != v) {
      lv_obj_delete_async(o);
      o = nullptr;
    }
  };
  if (sp.wifi != v) sp.wifi_list = nullptr;
  if (sp.about_view != v) sp.about_vals.clear();
  drop(sp.wifi);
  drop(sp.about_view);
  if (sp.kb && sp.kb != v) {
    drop_modal(kb.pick_root);
    drop(sp.kb);
    kb = Keypad{};
  }
  show(sp.list, v == sp.list);
  if (v) show(v, true);
  if (v == sp.list) {
    std::vector<lv_obj_t *> rows;
    for (uint32_t i = 0; i < lv_obj_get_child_count(sp.list); i++) rows.push_back(lv_obj_get_child(sp.list, i));
    set_focus_rows(rows);
    refresh_settings();
  }
}

inline void render_wifi() {
  lv_obj_t *l = sp.wifi_list;
  if (!l) return;   // scan results can land after the view closed
  lv_obj_clean(l);
  std::vector<lv_obj_t *> rows;
  int y = 0;
  if (!about.ssid.empty()) {
    lv_obj_t *cur = nm(box(l, 0, 0, 240, 44, WHITE, LV_OPA_TRANSP), "row_wifi_current");
    icon(cur, "check", 16, 12, 14, 0x30D158);
    text(cur, 34, 12, 140, R.f15, WHITE, umote::sanitize(about.ssid, "Wi-Fi").c_str());
    text(cur, 176, 13, 52, R.f13, WHITE, signal_word(about.rssi), LV_TEXT_ALIGN_RIGHT, 191);
    y = 52;
  }
  text(l, 12, y, 0, R.f12s, WHITE, "Other networks", LV_TEXT_ALIGN_LEFT, 184);
  y += 18;
  int n = 0;
  for (auto &net : sp.nets) {
    if (net.ssid == about.ssid) continue;
    std::string ssid = net.ssid;
    bool secure = net.secure;
    lv_obj_t *r = nm(button(l, 0, y, 240, 44, CARD, LV_OPA_TRANSP, 0, [ssid, secure] {
                       if (secure) open_keypad(ssid);
                       else if (hooks.wifi_join) hooks.wifi_join(ssid, "");
                     }), "row_wifi_" + std::to_string(n) + "_trunc");
    text(r, 14, 12, 140, R.f15, WHITE, umote::sanitize(net.ssid, "Hidden network").c_str());
    if (net.secure) icon(r, "lock", 16, 162, 14, WHITE, 191);
    text(r, 180, 13, 48, R.f13, WHITE, signal_word(net.rssi), LV_TEXT_ALIGN_RIGHT, 191);
    rows.push_back(r);
    y += 44;
    n++;
  }
  lv_obj_t *again = nm(button(l, 0, y, 240, 44, CARD, LV_OPA_TRANSP, 0, [] {
                         if (hooks.wifi_scan) hooks.wifi_scan();
                       }), "row_wifi_scan");
  text(again, 14, 12, 0, R.f15, LINK, "Scan again");
  rows.push_back(again);
  set_focus_rows(rows);
}

// Scan results from the device: dedupe by SSID keeping the strongest, strongest first.
inline void set_wifi_scan(std::vector<Net> nets) {
  std::vector<Net> out;
  for (auto &n : nets) {
    if (n.ssid.empty()) continue;
    auto it = std::find_if(out.begin(), out.end(), [&](const Net &o) { return o.ssid == n.ssid; });
    if (it == out.end()) out.push_back(n);
    else if (n.rssi > it->rssi) *it = n;
  }
  std::sort(out.begin(), out.end(), [](const Net &a, const Net &b) { return a.rssi > b.rssi; });
  sp.nets = out;
  render_wifi();
}

inline void open_wifi() {
  if (!sp.wifi) build_wifi_view();
  render_wifi();
  show_settings_view(sp.wifi);
  if (hooks.wifi_scan) hooks.wifi_scan();
}

inline void open_about() {
  if (!sp.about_view) build_about_view();
  char buf[48];
  snprintf(buf, sizeof buf, "%d%%, %d.%02d V", about.batt_pct, about.batt_mv / 1000, about.batt_mv % 1000 / 10);
  lv_label_set_text(sp.about_vals[0], buf);
  snprintf(buf, sizeof buf, "%s, \xE2\x88\x92%d dBm", signal_word(about.rssi), std::abs(about.rssi));
  lv_label_set_text(sp.about_vals[1], about.ssid.empty() ? "Off" : buf);
  lv_label_set_text(sp.about_vals[2], about.ip.empty() ? "None" : about.ip.c_str());
  lv_label_set_text(sp.about_vals[3], about.firmware.c_str());
  lv_label_set_text(sp.about_vals[4], about.board ? "Found" : "Not found");
  lv_label_set_text_fmt(sp.about_vals[5], "%d KB", about.free_kb);
  show_settings_view(sp.about_view);
  set_focus_rows({});
}

// ---- keypad (Wi-Fi password) ---------------------------------------------------------------------------

inline const std::vector<std::string> &kb_groups(int layout) {
  static const std::vector<std::string> L[4] = {
      {"abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"},
      {"ABC", "DEF", "GHI", "JKL", "MNO", "PQRS", "TUV", "WXYZ"},
      {"12", "34", "56", "78", "90", ".-", "_@", "/:"},
      {"!@", "#$", "%&", "*?", "()", "+=", ",;", "'\""}};
  return L[layout];
}
// Picks for a group: its characters, plus the digit when there is room (at most 4 keys).
inline std::string kb_picks(int g) {
  std::string p = kb_groups(kb.layout)[g];
  if (kb.layout < 2 && p.size() < 4) p += (char) ('2' + g);
  return p;
}

inline void kb_paint() {
  static const char *const SHIFT[] = {"aA 1#", "ABC", "123", "#+="};
  for (int i = 0; i < 8; i++) {
    lv_label_set_text(kb.key_main[i], kb_groups(kb.layout)[i].c_str());
    char d[2] = {(char) ('2' + i), 0};
    lv_label_set_text(kb.key_sub[i], kb.layout < 2 ? d : "");
  }
  lv_label_set_text(kb.key_sub[8], SHIFT[kb.layout]);
  for (size_t i = 0; i < kb.keys.size(); i++)
    lv_obj_set_style_bg_color(kb.keys[i], lv_color_hex((int) i == kb.key_focus ? 0x4A4A4C : i >= 8 && i != 11 ? GREY : CARD), 0);
  // field: dots for all but the last character, which shows briefly; or everything with the eye on
  lv_obj_clean(kb.dots);
  size_t n = kb.pw.size();
  bool plain = kb.show_pw;
  show(kb.full, plain);
  show(kb.dots, !plain);
  show(kb.last, !plain && n > 0);
  lv_label_set_text(kb.full, kb.pw.c_str());
  int x = 0;
  for (size_t i = 0; !plain && i + 1 < n && x < 120; i++, x += 11) box(kb.dots, x, 0, 8, 8, WHITE, LV_OPA_COVER, 4);
  if (n) lv_label_set_text(kb.last, kb.pw.substr(n - 1).c_str());
  lv_obj_set_x(kb.last, 11 + x);
  lv_obj_update_layout(plain ? kb.full : kb.last);
  int cx = plain ? 11 + std::min((int) lv_obj_get_width(kb.full), 136) : 11 + x + (n ? lv_obj_get_width(kb.last) + 2 : 0);
  lv_obj_set_x(kb.caret, cx);
  set_icon(kb.eye_icon, "eye", 20);
  lv_obj_set_style_image_recolor(kb.eye_icon, lv_color_hex(kb.show_pw ? LINK : WHITE), 0);
}

inline void kb_open_pick(int g) {
  kb.pick_group = g;
  kb.pick_focus = 0;
  std::string p = kb_picks(g);
  std::string cap = kb_groups(kb.layout)[g];
  for (auto &c : cap) c = (char) toupper(c);
  lv_label_set_text(kb.pick_cap, cap.c_str());
  for (int i = 0; i < 4; i++) {
    show(kb.picks[i], i < (int) p.size());
    if (i < (int) p.size()) {
      char t[2] = {p[i], 0};
      lv_label_set_text(lv_obj_get_child(kb.picks[i], 0), t);
    }
    lv_obj_set_style_bg_color(kb.picks[i], lv_color_hex(i == 0 ? 0x4A4A4C : GREY), 0);
  }
  show(kb.pick_root, true);
}

inline void kb_append(char c) {
  if (kb.pw.size() < 63) kb.pw += c;
  show(kb.pick_root, false);
  kb.pick_group = -1;
  if (kb.layout == 1) kb.layout = 0;   // one capital, like a phone
  kb_paint();
}

// Keys: 0..7 groups, 8 shift, 9 space, 10 delete (drawn at slot 8 of the grid), 11 join.
inline void kb_press(int k) {
  if (k < 8) kb_open_pick(k);
  else if (k == 8) kb.layout = (kb.layout + 1) % 4;
  else if (k == 9) kb_append(' ');
  else if (k == 10 && !kb.pw.empty()) kb.pw.pop_back();
  else if (k == 11 && hooks.wifi_join) hooks.wifi_join(kb.ssid, kb.pw);
  kb_paint();
}

inline void build_keypad(lv_obj_t *page) {
  sp.kb = box(page, 0, 0, 240, 320, BG, LV_OPA_COVER);
  lv_obj_t *back = nm(button(sp.kb, 4, 0, 146, 44, WHITE, LV_OPA_TRANSP, 9, [] { open_wifi(); }), "kb_back");
  icon(back, "chev_left", 20, 2, 7, WHITE);
  kb.title = text(back, 25, 10, 118, R.f17b, WHITE, "");
  kb.field = nm(box(sp.kb, 12, 52, 160, 44, SHEET, LV_OPA_COVER, 10), "kb_field");
  lv_obj_set_style_border_color(kb.field, lv_color_hex(BLUE), 0);
  lv_obj_set_style_border_width(kb.field, 2, 0);
  kb.dots = box(kb.field, 11, 16, 128, 8, WHITE, LV_OPA_TRANSP);
  kb.last = text(kb.field, 11, 11, 0, R.f15b, WHITE, "");
  kb.full = text(kb.field, 11, 12, 136, R.f15, WHITE, "");
  kb.caret = box(kb.field, 11, 10, 2, 20, BLUE, LV_OPA_COVER);
  lv_obj_t *eye = nm(button(sp.kb, 180, 52, 48, 44, CARD, LV_OPA_COVER, 12, [] {
                       kb.show_pw = !kb.show_pw;
                       kb_paint();
                     }), "kb_eye");
  kb.eye_icon = icon(eye, "eye", 20, 14, 12, WHITE);
  // grid slots: 3 columns x 4 rows; slot -> key id
  static const int SLOT_KEY[12] = {0, 1, 2, 3, 4, 5, 6, 7, 10, 8, 9, 11};
  kb.keys.assign(12, nullptr);
  kb.key_main.assign(8, nullptr);
  kb.key_sub.assign(9, nullptr);
  for (int slot = 0; slot < 12; slot++) {
    int k = SLOT_KEY[slot];
    int x = 12 + 75 * (slot % 3), y = 104 + 52 * (slot / 3);
    lv_obj_t *b = nm(button(sp.kb, x, y, 66, 44, CARD, LV_OPA_COVER, 10, [k] { kb_press(k); }),
                     "kb_key_" + std::to_string(k));
    kb.keys[k] = b;
    if (k < 8) {
      kb.key_main[k] = text(b, 0, 6, 66, R.f15b, WHITE, "", LV_TEXT_ALIGN_CENTER);
      kb.key_sub[k] = text(b, 0, 23, 66, R.f12, WHITE, "", LV_TEXT_ALIGN_CENTER, 178);
    } else if (k == 8) {
      icon(b, "shift", 20, 23, 3, WHITE);
      kb.key_sub[8] = text(b, 0, 25, 66, R.f12, WHITE, "", LV_TEXT_ALIGN_CENTER, 178);
    } else if (k == 9) {
      lv_obj_center(text(b, 0, 0, 0, R.f13, WHITE, "space"));
    } else if (k == 10) {
      icon(b, "del", 20, 23, 12, WHITE);
    } else {
      lv_obj_center(text(b, 0, 0, 0, R.f14s, WHITE, "Join"));
    }
  }
  // letter picker
  kb.pick_root = dim_layer("kb_pick_dim");
  lv_obj_t *card = nm(box(kb.pick_root, 4, 136, 232, 92, SHEET, LV_OPA_COVER, 14), "kb_pick");
  lv_obj_add_flag(card, LV_OBJ_FLAG_CLICKABLE);
  kb.pick_cap = text(card, 12, 8, 0, R.f12s, WHITE, "", LV_TEXT_ALIGN_LEFT, 184);
  for (int i = 0; i < 4; i++) {
    lv_obj_t *b = nm(button(card, 8 + 58 * i, 30, 48, 52, GREY, LV_OPA_COVER, 10, [i] {
                       std::string p = kb_picks(kb.pick_group);
                       if (i < (int) p.size()) kb_append(p[i]);
                     }), "kb_pick_" + std::to_string(i));
    lv_obj_center(text(b, 0, 0, 0, R.f20b, WHITE, ""));
    kb.picks.push_back(b);
  }
  show(sp.kb, false);
}

inline void open_keypad(const std::string &ssid) {
  if (!sp.kb) build_keypad(sp.page);
  kb.ssid = ssid;
  kb.pw.clear();
  kb.layout = 0;
  kb.key_focus = 4;
  kb.show_pw = false;
  lv_label_set_text(kb.title, umote::sanitize(ssid, "Wi-Fi").c_str());
  kb_paint();
  show_settings_view(sp.kb);
  set_focus_rows({});
}

inline bool keypad_open() { return sp.kb && !lv_obj_has_flag(sp.kb, LV_OBJ_FLAG_HIDDEN); }

// D-pad, OK and Back on the Settings page (lists, keypad and its picker).
inline void settings_key(const char *what) {
  if (!ready) return;
  bool ok = !strcmp(what, "OK"), back = !strcmp(what, "BACK");
  if (keypad_open()) {
    if (kb.pick_group >= 0) {
      int n = (int) kb_picks(kb.pick_group).size();
      if (back) { show(kb.pick_root, false); kb.pick_group = -1; return; }
      if (ok) { kb_append(kb_picks(kb.pick_group)[kb.pick_focus]); return; }
      if (!strcmp(what, "LEFT") && kb.pick_focus > 0) kb.pick_focus--;
      if (!strcmp(what, "RIGHT") && kb.pick_focus < n - 1) kb.pick_focus++;
      for (int i = 0; i < 4; i++)
        lv_obj_set_style_bg_color(kb.picks[i], lv_color_hex(i == kb.pick_focus ? 0x4A4A4C : GREY), 0);
      return;
    }
    if (back) { open_wifi(); return; }
    static const int SLOT_KEY[12] = {0, 1, 2, 3, 4, 5, 6, 7, 10, 8, 9, 11};
    int slot = 0;
    while (SLOT_KEY[slot] != kb.key_focus) slot++;
    if (ok) { kb_press(kb.key_focus); return; }
    int d = !strcmp(what, "LEFT") ? -1 : !strcmp(what, "RIGHT") ? 1 : !strcmp(what, "UP") ? -3 : 3;
    if (slot + d >= 0 && slot + d < 12) kb.key_focus = SLOT_KEY[slot + d];
    kb_paint();
    return;
  }
  if (back) {
    show_settings_view(sp.list);
    return;
  }
  if (ok) {
    if (sp.focus >= 0 && sp.focus < (int) sp.rows.size()) lv_obj_send_event(sp.rows[sp.focus], LV_EVENT_CLICKED, nullptr);
    return;
  }
  int n = (int) sp.rows.size();
  if (!n) return;
  if (!strcmp(what, "UP")) sp.focus = std::max(0, sp.focus - 1);
  else if (!strcmp(what, "DOWN")) sp.focus = std::min(n - 1, sp.focus + 1);
  else if (sp.focus >= 0 && sp.rows[sp.focus] == lv_obj_get_parent(sp.bright->hit)) {   // brightness row
    cfg.brightness = std::max(0.1f, std::min(1.0f, cfg.brightness + (!strcmp(what, "LEFT") ? -0.1f : 0.1f)));
    refresh_settings();
    if (hooks.settings_changed) hooks.settings_changed();
  }
  paint_set_focus();
}

// ---- pages -------------------------------------------------------------------------------------------------
struct Pages {
  lv_obj_t *view;
  lv_obj_t *page[4];
  int current = 0;
};
inline Pages pg;

inline void show_page(int i, bool anim) {
  pg.current = i;
  lv_obj_update_layout(pg.view);   // tiles need their size before scrolling to one
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
  open_picker = [] { open_page_picker(pg.current); };
  size_t h = heap_free();
  auto step = [&h](const char *what) {   // heap per part, so memory growth is visible in the log
    size_t now = heap_free();
    ESP_LOGD("ui", "%-10s %6u B", what, (unsigned) (h - now));
    h = now;
  };
  build_tv(pg.page[0]);
  step("tv");
  build_soundbar(pg.page[1]);
  step("soundbar");
  build_home(pg.page[2]);
  step("home");
  build_settings(pg.page[3]);
  step("settings");
  build_status();
  show_settings_view(sp.list);
  build_overlays();
  step("overlays");
  ready = true;
}

}  // namespace ui
