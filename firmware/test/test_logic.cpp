// Host tests for logic.h: g++ -std=c++17 -Wall -Werror firmware/test/test_logic.cpp -o /tmp/tl && /tmp/tl
#include <cassert>
#include <cstdio>
#include <cmath>
#include <cstring>
#include "../logic.h"

using namespace umote;

static bool is(Action a, Target t, const char *code) { return a.target == t && std::strcmp(a.code, code) == 0; }

static void tv_volume_goes_to_soundbar_by_default() {
  assert(is(route(Page::TV, Key::VOL_UP, false, false), Target::SOUNDBAR_IR, "VOL_UP"));
  assert(is(route(Page::TV, Key::VOL_UP, true, false), Target::TV_KEY, "VOLUME_UP"));
  assert(is(route(Page::TV, Key::MUTE, true, false), Target::TV_KEY, "MUTE"));
}
static void tv_dpad_and_channels_go_to_tv() {
  assert(is(route(Page::TV, Key::UP, false, false), Target::TV_KEY, "DPAD_UP"));
  assert(is(route(Page::TV, Key::OK, false, false), Target::TV_KEY, "DPAD_CENTER"));
  assert(is(route(Page::TV, Key::BACK, false, false), Target::TV_KEY, "BACK"));
  assert(is(route(Page::TV, Key::CH_DOWN, false, false), Target::TV_KEY, "CHANNEL_DOWN"));
}
static void soundbar_page_is_all_ir() {
  assert(route(Page::SOUNDBAR, Key::UP, false, false).target == Target::SOUNDBAR_IR);
  assert(is(route(Page::SOUNDBAR, Key::OK, false, false), Target::SOUNDBAR_IR, "ENTER"));
  assert(is(route(Page::SOUNDBAR, Key::BACK, false, false), Target::SOUNDBAR_IR, "RETURN"));
  assert(route(Page::SOUNDBAR, Key::CH_UP, false, false).target == Target::NONE);
}
static void home_page_moves_focus() {
  assert(is(route(Page::HOME, Key::LEFT, false, false), Target::FOCUS_MOVE, "LEFT"));
  assert(route(Page::HOME, Key::OK, false, false).target == Target::FOCUS_TOGGLE);
  assert(route(Page::HOME, Key::OK_HOLD, false, false).target == Target::FOCUS_OPTIONS);
  assert(route(Page::HOME, Key::BACK, false, true).target == Target::CLOSE_SHEET);
  assert(is(route(Page::HOME, Key::CH_UP, false, false), Target::PAGE_SCROLL, "UP"));
  assert(route(Page::HOME, Key::VOL_DOWN, true, false).target == Target::SOUNDBAR_IR);
}
static void settings_and_global_keys() {
  assert(is(route(Page::SETTINGS, Key::DOWN, false, false), Target::LIST_MOVE, "DOWN"));
  assert(route(Page::SETTINGS, Key::OK, false, false).target == Target::LIST_SELECT);
  for (Page p : {Page::TV, Page::SOUNDBAR, Page::HOME, Page::SETTINGS}) {
    assert(route(p, Key::POWER, false, false).target == Target::POWER);
    assert(route(p, Key::VOICE, false, false).target == Target::NONE);
  }
}
static void views() {
  assert(select_view(false, "", false, false, "") == TvView::OFF);
  assert(select_view(true, "playing", true, true, "com.netflix.ninja") == TvView::PLAYING_ART);
  assert(select_view(true, "paused", true, false, "in.startv.hotstar") == TvView::PLAYING_NOART);
  assert(select_view(true, "idle", false, false, "com.mediatek.wwtv.tvcenter") == TvView::INPUT);
  assert(select_view(true, "off", false, false, "com.netflix.ninja") == TvView::APP);
  assert(select_view(true, "playing", false, true, "com.netflix.ninja") == TvView::APP);
}
static void progress_for_live_stream_is_hidden() {
  assert(!progress(0, 0, 0, 1000, true).show);
  assert(!progress(-1, 5, 0, 1000, true).show);
}
static void progress_extrapolates_while_playing() {
  Progress p = progress(4974.88f, 2112.477f, 0, 10000, true);
  assert(p.show && p.pos_s == 2122 && p.remaining_s == 2853);
  assert(p.fraction > 0.42f && p.fraction < 0.43f);
  Progress q = progress(4974.88f, 2112.477f, 0, 10000, false);
  assert(q.pos_s == 2112);
  Progress end = progress(100, 99, 0, 60000, true);
  assert(end.pos_s == 100 && end.remaining_s == 0 && end.fraction == 1.0f);
}
static void stale() {
  assert(is_stale(0, 30001) && !is_stale(0, 30000));
}
static void sanitize_drops_unsupported_codepoints() {
  assert(sanitize("Bigg Boss \xF0\x9F\x94\xA5", "Hotstar") == "Bigg Boss");
  assert(sanitize("\xE0\xAE\xA4\xE0\xAE\xAE", "Sun NXT") == "Sun NXT");
  assert(sanitize("Caf\xC3\xA9 \xE2\x80\xA6", "x") == "Caf\xC3\xA9 \xE2\x80\xA6");
  assert(sanitize("a\xF0\x9F\x94\xA5\xF0\x9F\x94\xA5" "b", "x") == "ab");
  assert(sanitize("bad \xFF\xFE bytes", "x") == "bad  bytes");
}
static void ellipsize_counts_characters() {
  assert(ellipsize("NavazAirFiber_EXT_5G_long", 12) == "NavazAirFib\xE2\x80\xA6");
  assert(ellipsize("short", 12) == "short");
  assert(ellipsize("\xC3\xA9\xC3\xA9\xC3\xA9", 2) == "\xC3\xA9\xE2\x80\xA6");
}

static void backlight_never_goes_dark() {
  assert(backlight_level(0.0f) == 0.3f && backlight_level(0.1f) == 0.3f && backlight_level(-1.0f) == 0.3f);
  assert(backlight_level(0.7f) == 0.7f && backlight_level(2.0f) == 1.0f);
  assert(backlight_level(std::nanf("")) == 0.6f);           // a corrupt saved value falls back to the default
  assert(slider_to_backlight(0.0f) == 0.3f && slider_to_backlight(1.0f) == 1.0f);
  assert(slider_to_backlight(0.5f) > 0.64f && slider_to_backlight(0.5f) < 0.66f);
  assert(backlight_to_slider(0.3f) == 0.0f && backlight_to_slider(1.0f) == 1.0f);
}

static void scan_text_is_parsed() {
  auto r = parse_scan_text("NavazAirFiber_EXT: -33dB\nCafe: Guest: -79dB\nJio-5G: -74dB\n");
  assert(r.size() == 3);
  assert(r[0].first == "NavazAirFiber_EXT" && r[0].second == -33);
  assert(r[1].first == "Cafe: Guest" && r[1].second == -79);    // SSIDs may contain ": "
  assert(parse_scan_text("").empty() && parse_scan_text("garbage\n").empty());
}

int main() {
  tv_volume_goes_to_soundbar_by_default();
  tv_dpad_and_channels_go_to_tv();
  soundbar_page_is_all_ir();
  home_page_moves_focus();
  settings_and_global_keys();
  views();
  progress_for_live_stream_is_hidden();
  progress_extrapolates_while_playing();
  stale();
  sanitize_drops_unsupported_codepoints();
  ellipsize_counts_characters();
  backlight_never_goes_dark();
  scan_text_is_parsed();
  std::puts("all logic tests passed");
  return 0;
}
