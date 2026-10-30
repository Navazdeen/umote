// Simulator only: canned Home Assistant data, picked with SIM_FIXTURE=<name>.
#pragma once

#include <string>
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
  } else {
    return false;
  }
  ui::render_tv(now_ms);
  if (f == "sheet") ui::open_sources();
  if (f == "new_hdmi") ui::open_new_hdmi(3);
  return true;
}
