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
  } else {
    return false;
  }
  ui::render_tv(now_ms);
  if (f == "sheet") ui::open_sources();
  if (f == "new_hdmi") ui::open_new_hdmi(3);
  return true;
}
