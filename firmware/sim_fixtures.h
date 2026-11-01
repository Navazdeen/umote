// Simulator only: canned Home Assistant data, picked with SIM_FIXTURE=<name>.
#pragma once

#include <cstdio>
#include <cstdlib>
#include <functional>
#include <string>
#include <vector>
#include "ui_lv.h"

inline const char *SIM_SOURCES = R"([
 {"id":"hdmi1","kind":"input","name":"PlayStation 5","port":1,"color":"#00439c","icon":"ps5"},
 {"id":"hdmi3","kind":"input","name":"HDMI 3","port":3,"color":"#3a3a3c","icon":"hdmi"},
 {"id":"tuner","kind":"tuner","name":"Live TV","port":null,"color":"#3a3a3c","icon":"tv"},
 {"id":"com.netflix.ninja","kind":"app","name":"Netflix","color":"#e50914","icon":"com.netflix.ninja"},
 {"id":"com.google.android.youtube.tv","kind":"app","name":"YouTube","color":"#ff0000","icon":"x"},
 {"id":"in.startv.hotstar","kind":"app","name":"Hotstar","color":"#16307a","icon":"x"},
 {"id":"com.amazon.amazonvideo.livingroom","kind":"app","name":"Prime Video","color":"#00a8e1","icon":"x"},
 {"id":"com.spotify.tv.android","kind":"app","name":"Spotify","color":"#3a3a3c","icon":"x"},
 {"id":"com.sonyliv","kind":"app","name":"Sony LIV","color":"#3a3a3c","icon":"x"},
 {"id":"com.graymatrix.did","kind":"app","name":"ZEE5","color":"#3a3a3c","icon":"x"},
 {"id":"org.videolan.vlc","kind":"app","name":"VLC","color":"#3a3a3c","icon":"x"},
 {"id":"nl.giejay.android.tv.immich","kind":"app","name":"Immich","color":"#3a3a3c","icon":"x"}])";

inline const char *SIM_TILES = R"([
 {"id":"a_fan","name":"TV fan","kind":"fan","icon":"fan","state":"on","label":"Speed 3","entities":["fan.tv_fan"],
  "options":{"led":"light.tv_fan_led","speed_count":6,"timer":"select.tv_fan_set_timer"}},
 {"id":"b_lights","name":"Cabinet lights","kind":"lights","icon":"bulb","state":"off","label":"Off","entities":["light.a","light.b"],"options":{}},
 {"id":"c_display","name":"Matrix clock","kind":"display","icon":"clock","state":"on","label":"On","entities":["switch.m"],"options":{}},
 {"id":"d_power","name":"Cabinet power","kind":"switches","icon":"plug","state":"off","label":"Off","entities":["switch.a"],"options":{}},
 {"id":"e_fan","name":"Fridge fan","kind":"fan","icon":"fan","state":"offline","label":"Offline","entities":["fan.fridge_fan"],"options":{}},
 {"id":"f_fan","name":"Clock fan","kind":"fan","icon":"fan","state":"offline","label":"Offline","entities":["fan.clock_fan"],"options":{}}])";

// Returns false for an unknown fixture name.
inline bool sim_load_fixture(const std::string &f, int64_t now_ms) {
  ui::parse_sources(SIM_SOURCES);
  ui::tv.quick = {"hdmi1", "com.netflix.ninja", "com.google.android.youtube.tv", "in.startv.hotstar"};
  ui::tv.more = {"org.videolan.vlc", "nl.giejay.android.tv.immich"};
  ui::tv.tv_on = true;
  ui::tv.updated_ms = now_ms;
  ui::tv.position_ms = now_ms;
  auto playing = [&](const char *title, const char *app, const char *cur, float dur, float pos) {
    ui::tv.cast_state = "playing";
    ui::tv.playing = true;
    ui::tv.title = title;
    ui::tv.app_name = app;
    ui::tv.current = cur;
    ui::tv.activity = cur;
    ui::tv.duration = dur;
    ui::tv.position = pos;
    ui::tv.has_art = true;
  };
  if (f == "art" || f == "sheet" || f == "new_hdmi") {
    playing("The Long Road", "Hotstar", "in.startv.hotstar", 4395, 1930);
  } else if (f == "noart_ps5") {
    ui::tv.current = "hdmi1";
    ui::tv.activity = "com.mediatek.wwtv.tvcenter";
  } else if (f == "off") {
    ui::tv.tv_on = false;
  } else if (f == "live") {
    playing("Sun News Live", "Sun NXT", "com.suntv.sunnxt", 0, 0);
  } else if (f == "long_title") {
    playing("Sa Re Ga Ma Pa 2026 Grand Finale Part 2 \xF0\x9F\x94\xA5 Special", "ZEE5", "com.graymatrix.did", 5400, 600);
  } else if (f == "stale") {
    playing("The Long Road", "Hotstar", "in.startv.hotstar", 4395, 1930);
    ui::tv.updated_ms = now_ms - 95000;
  } else if (f == "soundbar") {
    ui::show_page(1);
  } else if (f == "home" || f == "home_focus_each" || f == "options_fan" || f == "picker") {
    ui::parse_tiles(SIM_TILES);
    ui::render_home();
    ui::show_page(2);
    if (f == "options_fan") ui::open_options(0);
    if (f == "picker") ui::open_page_picker(2);
  } else if (f == "settings" || f == "wifi_scan" || f == "keypad" || f == "keypad_pick" || f == "about") {
    ui::show_page(3);
    if (f == "wifi_scan") {
      ui::open_wifi();
    } else if (f == "about") {
      ui::open_about();
    } else if (f != "settings") {
      ui::open_keypad("NavazAirFiber");
      ui::kb.pw = "navazde";
      ui::kb_paint();
      if (f == "keypad_pick") ui::kb_open_pick(4);
    }
  } else if (f == "cycle") {
    // Open and close every lazily built sheet/view many times: no crash, no heap growth.
    ui::parse_tiles(SIM_TILES);
    ui::render_home();
    auto settle = [] { for (int k = 0; k < 3; k++) lv_timer_handler(); };
    struct Part { const char *name; std::function<void()> fn; };
    std::vector<Part> parts = {
      {"sources", [] { ui::open_sources(); ui::close_sheets(); }},
      {"new_hdmi", [] { ui::open_new_hdmi(3); ui::close_sheets(); }},
      {"options", [] { ui::open_options(0); ui::close_sheets(); }},
      {"picker", [] { ui::open_page_picker(0); ui::close_sheets(); }},
      {"wifi", [] { ui::open_wifi(); ui::settings_key("BACK"); }},
      {"keypad", [] { ui::open_keypad("X"); ui::kb_open_pick(2); ui::settings_key("BACK"); ui::settings_key("BACK"); ui::settings_key("BACK"); }},
      {"about", [] { ui::open_about(); ui::settings_key("BACK"); }},
    };
    ui::show_page(3);
    bool ok = !ui::sheet_open();
    for (auto &p : parts) {
      p.fn(); settle();
      size_t base = ui::heap_free();
      int n = getenv("SIM_ROUNDS") ? atoi(getenv("SIM_ROUNDS")) : 20; for (int i = 0; i < n; i++) { p.fn(); settle(); }
      long grew = (long) base - (long) ui::heap_free();
      printf("cycle %-9s grew %7ld B over 20  top=%u page3=%u\n", p.name, grew,
             (unsigned) lv_obj_get_child_count(lv_layer_top()), (unsigned) lv_obj_get_child_count(ui::pg.page[3]));
      if (grew > 3 * 1024 * n) ok = false;   // sessions end in deep sleep; only per-session peak matters
    }
    printf("cycle: %s\n", ok ? "PASS" : "FAIL");
    exit(ok ? 0 : 3);
  } else if (f == "outside_tap") {
    // A tap on the dimmed area around any sheet closes it (touch-only remotes have no Back key).
    ui::parse_tiles(SIM_TILES);
    ui::render_home();
    auto tap_dim = [] {
      for (auto *m : ui::modals())
        if (!lv_obj_has_flag(m, LV_OBJ_FLAG_HIDDEN)) lv_obj_send_event(m, LV_EVENT_CLICKED, nullptr);
      for (int k = 0; k < 3; k++) lv_timer_handler();
    };
    bool ok = true;
    ui::open_options(0); tap_dim(); ok &= !ui::sheet_open();
    ui::open_page_picker(2); tap_dim(); ok &= !ui::sheet_open();
    ui::open_sources(); tap_dim(); ok &= !ui::sheet_open();
    ui::open_new_hdmi(3); tap_dim(); ok &= !ui::sheet_open();
    ui::show_page(3); ui::open_keypad("X"); ui::kb_open_pick(4); tap_dim();
    ok &= !ui::sheet_open() && ui::kb.pick_group == -1 && ui::keypad_open();
    printf("outside_tap: %s\n", ok ? "PASS" : "FAIL");
    exit(ok ? 0 : 3);
  } else if (f == "fan_reorder") {
    // The options sheet must keep acting on its fan when HA re-sorts the tiles under it.
    static std::vector<std::string> calls;
    ui::hooks.ha = [](const std::string &k, const std::string &e, const std::string &v) { calls.push_back(k + " " + e + " " + v); };
    std::string tiles = SIM_TILES;
    ui::parse_tiles(tiles);
    ui::render_home();
    ui::open_options(0);                        // TV fan, Speed 3 of 6
    ui::set_speed(1);                           // -> 4
    // HA reports the change and moves another tile to the front
    std::string moved = tiles;
    size_t a = moved.find("{\"id\":\"c_display\"");
    std::string disp = moved.substr(a, moved.find("},", a) + 2 - a);
    moved.erase(a, disp.size());
    moved.insert(2, disp);
    ui::parse_tiles(moved);
    ui::render_home();
    ui::set_speed(1);                           // -> 5, still the TV fan
    bool ok = calls.size() == 2 && calls[0] == "fan_pct fan.tv_fan 66" && calls[1] == "fan_pct fan.tv_fan 83";
    for (auto &c : calls) printf("  %s\n", c.c_str());
    printf("fan_reorder: %s\n", ok ? "PASS" : "FAIL");
    exit(ok ? 0 : 3);
  } else if (f == "keypad_type") {
    // Type "abc1" with D-pad events only, then check the field.
    ui::show_page(3);
    ui::open_keypad("NavazAirFiber");
    const char *seq[] = {"UP", "LEFT", "OK", "OK",                 // focus abc, open picker, a
                         "OK", "RIGHT", "OK",                       // b
                         "OK", "RIGHT", "RIGHT", "OK",              // c
                         "DOWN", "DOWN", "DOWN", "OK", "OK",        // shift x2 -> 123
                         "UP", "UP", "UP", "OK", "OK"};             // group "12", pick 1
    for (const char *k : seq) ui::settings_key(k);
    bool ok = ui::kb.pw == "abc1" && lv_obj_get_child_count(ui::kb.dots) == 3 &&
              std::string(lv_label_get_text(ui::kb.last)) == "1";
    printf("keypad_type: pw=%s dots=%u %s\n", ui::kb.pw.c_str(), (unsigned) lv_obj_get_child_count(ui::kb.dots),
           ok ? "PASS" : "FAIL");
    exit(ok ? 0 : 3);
  } else {
    return false;
  }
  ui::render_tv(now_ms);
  if (f == "sheet") ui::open_sources();
  if (f == "new_hdmi") ui::open_new_hdmi(3);
  return true;
}
