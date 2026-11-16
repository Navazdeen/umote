// Pure logic for the umote remote: key routing, TV view choice, progress, staleness, text clean-up.
// Header-only and free of ESPHome includes so it is unit-tested on the host (firmware/test/test_logic.cpp).
#pragma once

#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <string>
#include <utility>
#include <vector>

namespace umote {

enum class Page { TV, SOUNDBAR, HOME, SETTINGS };
enum class Key { UP, DOWN, LEFT, RIGHT, OK, BACK, HOME, POWER, VOL_UP, VOL_DOWN, MUTE, CH_UP, CH_DOWN, VOICE, OK_HOLD, ROLL_UP, ROLL_DOWN };
enum class Target {
  TV_KEY, SOUNDBAR_IR, FOCUS_MOVE, FOCUS_TOGGLE, FOCUS_OPTIONS, CLOSE_SHEET, LIST_MOVE, LIST_SELECT, PAGE_SCROLL,
  POWER, NONE
};
struct Action {
  Target target;
  const char *code;
};

inline const char *dir_name(Key k) {
  switch (k) {
    case Key::UP: return "UP";
    case Key::DOWN: return "DOWN";
    case Key::LEFT: return "LEFT";
    default: return "RIGHT";
  }
}

inline bool is_dpad(Key k) { return k == Key::UP || k == Key::DOWN || k == Key::LEFT || k == Key::RIGHT; }

inline Action soundbar_volume(Key key) {
  switch (key) {
    case Key::VOL_UP: return {Target::SOUNDBAR_IR, "VOL_UP"};
    case Key::VOL_DOWN: return {Target::SOUNDBAR_IR, "VOL_DOWN"};
    default: return {Target::SOUNDBAR_IR, "MUTE"};
  }
}

// Volume follows Settings > Buttons on every page, for the keys and the on-screen buttons alike.
inline Action volume_action(Key key, bool to_tv) {
  if (!to_tv) return soundbar_volume(key);
  return {Target::TV_KEY, key == Key::VOL_UP ? "VOLUME_UP" : key == Key::VOL_DOWN ? "VOLUME_DOWN" : "VOLUME_MUTE"};
}

// Crease roller (case v5): an EC11 on MCP23017 GPB1/GPB5. feed() takes the new A/B state (A = bit 1)
// and returns +1 / -1 when a detent completes, 0 otherwise. A detent completes on arrival at the rest
// state (A = B = 1 with the pull-ups) after at least half a detent of travel, so a half-click brush,
// a missed edge or the boot order (A published before B) can't put it out of phase. A transition
// that skips a state is ignored. The first reading only seeds it.
struct RollDecoder {
  int8_t acc = 0;
  uint8_t last = 0;
  bool seeded = false;
  uint8_t rest = 3;
  int feed(uint8_t ab) {
    static const int8_t STEP[16] = {0, 1, -1, 0, -1, 0, 0, 1, 1, 0, 0, -1, 0, -1, 1, 0};
    ab &= 3;
    if (!seeded) { seeded = true; last = ab; return 0; }
    acc += STEP[(last << 2) | ab];
    last = ab;
    if (ab != rest) return 0;
    int out = acc >= 2 ? 1 : acc <= -2 ? -1 : 0;
    acc = 0;
    return out;
  }
};

// Routing table from spec §4.4. The roller is volume on the TV and soundbar pages, scroll elsewhere.
inline Action route(Page page, Key key, bool volume_to_tv, bool sheet_open) {
  if (key == Key::ROLL_UP || key == Key::ROLL_DOWN) {
    bool up = key == Key::ROLL_UP;
    if (page == Page::HOME) return {Target::PAGE_SCROLL, up ? "UP" : "DOWN"};
    if (page == Page::SETTINGS) return {Target::LIST_MOVE, up ? "UP" : "DOWN"};
    key = up ? Key::VOL_UP : Key::VOL_DOWN;
  }
  if (key == Key::POWER) return {Target::POWER, "POWER"};
  if (key == Key::VOICE) return {Target::NONE, ""};
  if (key == Key::BACK && sheet_open) return {Target::CLOSE_SHEET, "BACK"};
  bool vol = key == Key::VOL_UP || key == Key::VOL_DOWN || key == Key::MUTE;
  bool ch = key == Key::CH_UP || key == Key::CH_DOWN;
  if (vol) return volume_action(key, volume_to_tv);
  switch (page) {
    case Page::TV:
      if (ch) return {Target::TV_KEY, key == Key::CH_UP ? "CHANNEL_UP" : "CHANNEL_DOWN"};
      switch (key) {
        case Key::UP: return {Target::TV_KEY, "DPAD_UP"};
        case Key::DOWN: return {Target::TV_KEY, "DPAD_DOWN"};
        case Key::LEFT: return {Target::TV_KEY, "DPAD_LEFT"};
        case Key::RIGHT: return {Target::TV_KEY, "DPAD_RIGHT"};
        case Key::OK: return {Target::TV_KEY, "DPAD_CENTER"};
        case Key::BACK: return {Target::TV_KEY, "BACK"};
        case Key::HOME: return {Target::TV_KEY, "HOME"};
        default: return {Target::NONE, ""};
      }
    case Page::SOUNDBAR:
      if (is_dpad(key)) return {Target::SOUNDBAR_IR, dir_name(key)};
      if (key == Key::OK) return {Target::SOUNDBAR_IR, "ENTER"};
      if (key == Key::BACK) return {Target::SOUNDBAR_IR, "RETURN"};
      if (key == Key::HOME) return {Target::SOUNDBAR_IR, "HOME"};
      return {Target::NONE, ""};
    case Page::HOME:
      if (ch) return {Target::PAGE_SCROLL, key == Key::CH_UP ? "UP" : "DOWN"};
      if (is_dpad(key)) return {Target::FOCUS_MOVE, dir_name(key)};
      if (key == Key::OK) return {Target::FOCUS_TOGGLE, "OK"};
      if (key == Key::OK_HOLD) return {Target::FOCUS_OPTIONS, "OK"};
      if (key == Key::HOME) return {Target::TV_KEY, "HOME"};
      return {Target::NONE, ""};
    case Page::SETTINGS:
      if (is_dpad(key)) return {Target::LIST_MOVE, dir_name(key)};
      if (key == Key::OK) return {Target::LIST_SELECT, "OK"};
      if (key == Key::HOME) return {Target::TV_KEY, "HOME"};
      return {Target::NONE, ""};
  }
  return {Target::NONE, ""};
}

enum class TvView { OFF, PLAYING_ART, PLAYING_NOART, INPUT, APP };

inline TvView select_view(bool tv_on, const char *cast_state, bool has_title, bool has_art, const char *activity) {
  if (!tv_on) return TvView::OFF;
  bool active = cast_state && (std::strcmp(cast_state, "playing") == 0 || std::strcmp(cast_state, "paused") == 0 ||
                               std::strcmp(cast_state, "buffering") == 0);
  if (active && has_title) return has_art ? TvView::PLAYING_ART : TvView::PLAYING_NOART;
  if (activity && std::strcmp(activity, "com.mediatek.wwtv.tvcenter") == 0) return TvView::INPUT;
  return TvView::APP;
}

struct Progress {
  bool show;
  float fraction;
  int pos_s;
  int remaining_s;
};

// show=false when duration <= 0 (live streams); position extrapolated only while playing, clamped to [0, duration].
inline Progress progress(float duration, float position, int64_t position_updated_ms, int64_t now_ms, bool playing) {
  if (!(duration > 0)) return {false, 0, 0, 0};
  double pos = position;
  if (playing && now_ms > position_updated_ms) pos += (now_ms - position_updated_ms) / 1000.0;
  if (pos < 0) pos = 0;
  if (pos > duration) pos = duration;
  return {true, (float) (pos / duration), (int) std::floor(pos), (int) std::ceil(duration - pos)};
}

inline bool is_stale(int64_t last_update_ms, int64_t now_ms) { return now_ms - last_update_ms > 30000; }

// Wi-Fi scan as published by ESPHome's wifi_info scan_results sensor: "SSID: -60dB" per line.
inline std::vector<std::pair<std::string, int>> parse_scan_text(const std::string &text) {
  std::vector<std::pair<std::string, int>> out;
  size_t start = 0;
  while (start < text.size()) {
    size_t end = text.find('\n', start);
    if (end == std::string::npos) end = text.size();
    std::string line = text.substr(start, end - start);
    start = end + 1;
    size_t sep = line.rfind(": ");
    if (sep == std::string::npos || line.size() < sep + 4 || line.compare(line.size() - 2, 2, "dB") != 0) continue;
    std::string num = line.substr(sep + 2, line.size() - sep - 4);
    char *rest = nullptr;
    long rssi = strtol(num.c_str(), &rest, 10);
    if (rest == num.c_str() || *rest) continue;
    out.emplace_back(line.substr(0, sep), (int) rssi);
  }
  return out;
}

// ---- charging, guessed from the battery voltage -------------------------------------------------------
// No pin says "charging" on this board, so it is inferred. The TP4054 pushes about 300 mA into the
// cell: the voltage steps up when the charger goes on, climbs, then sits near 4.2 V; it steps down
// when the charger comes off. "Full on the charger" and "full, just unplugged" look the same, so
// FULL is shown for a limited time only. Thresholds are estimates [CHECK on the device].
enum class Charge : uint8_t { NONE, CHARGING, FULL };
constexpr int CHG_RISE_MV = 35;         // rise over the last resting reading that means "charger on"
constexpr int CHG_DROP_MV = 35;         // fall below the peak, at rest, that means "charger off"
constexpr int CHG_DROP_LOADED_MV = 60;  // the same while awake (screen and WiFi pull the reading down)
constexpr int CHG_FULL_MV = 4100;       // at or above this the cell is in the constant-voltage phase
constexpr int CHG_FLAT_MV = 8;          // "not rising any more" between two resting readings
constexpr int CHG_FLAT_POLLS = 3;       // that many flat readings in a row = full
constexpr int CHG_FULL_POLLS = 12;      // resting readings FULL is shown for (1 h at one per 5 min)
constexpr int CHG_MAX_POLLS = 144;      // give up on CHARGING after this many (12 h)

// Plain data: kept in RTC memory across deep sleep (all zero = fresh). feed() takes every battery
// reading; `rested` is true for one taken with the screen and WiFi off (at wake).
struct ChargeTracker {
  uint8_t state, flat;
  uint16_t ref_mv, peak_mv, last_mv, polls;
  Charge get() const { return (Charge) state; }
  void set(Charge c, int ref) {
    state = (uint8_t) c;
    flat = 0;
    polls = 0;
    ref_mv = (uint16_t) ref;
  }
  Charge feed(int mv, bool rested) {
    switch (get()) {
      case Charge::NONE:
        if (ref_mv && mv >= ref_mv + CHG_RISE_MV) {
          set(Charge::CHARGING, ref_mv);
          peak_mv = last_mv = (uint16_t) mv;
        } else if (rested) {
          ref_mv = (uint16_t) mv;
        }
        break;
      case Charge::CHARGING:
        if (mv > peak_mv) peak_mv = (uint16_t) mv;
        if (!rested) {
          if (mv + CHG_DROP_LOADED_MV <= peak_mv) set(Charge::NONE, 0);   // 0: the next resting reading seeds it
          break;
        }
        polls++;
        if (mv + CHG_DROP_MV <= peak_mv) {
          // the charger chip switching off at the end of a charge looks like an unplug
          if (peak_mv >= CHG_FULL_MV) set(Charge::FULL, mv);
          else set(Charge::NONE, mv);
        } else if (polls > CHG_MAX_POLLS) {
          set(Charge::NONE, mv);
        } else if (mv >= CHG_FULL_MV) {
          flat = mv - last_mv <= CHG_FLAT_MV ? flat + 1 : 0;
          if (flat >= CHG_FLAT_POLLS) set(Charge::FULL, mv);
        }
        last_mv = (uint16_t) mv;
        break;
      case Charge::FULL:
        if (!rested) {
          if (mv + 2 * CHG_DROP_LOADED_MV < CHG_FULL_MV) set(Charge::NONE, 0);
        } else if (++polls >= CHG_FULL_POLLS || mv + CHG_DROP_LOADED_MV < CHG_FULL_MV) {
          set(Charge::NONE, mv);
        }
        break;
    }
    return get();
  }
};

// Backlight: never below 30 % (lower is unreadable on this panel and can't be undone by touch).
constexpr float BACKLIGHT_MIN = 0.3f, BACKLIGHT_DEFAULT = 0.6f;
inline float backlight_level(float setting) {
  if (std::isnan(setting)) return BACKLIGHT_DEFAULT;
  return setting < BACKLIGHT_MIN ? BACKLIGHT_MIN : setting > 1.0f ? 1.0f : setting;
}
// The Settings slider spans the usable range: 0 -> 30 %, 1 -> 100 %.
inline float slider_to_backlight(float f) {
  f = f < 0 ? 0 : f > 1 ? 1 : f;
  return BACKLIGHT_MIN + f * (1.0f - BACKLIGHT_MIN);
}
inline float backlight_to_slider(float level) {
  return (backlight_level(level) - BACKLIGHT_MIN) / (1.0f - BACKLIGHT_MIN);
}

// Decode one UTF-8 code point at s[i]; returns its length (0 for an invalid byte).
inline size_t utf8_next(const std::string &s, size_t i, uint32_t &cp) {
  unsigned char c = s[i];
  size_t n = c < 0x80 ? 1 : (c >> 5) == 0x6 ? 2 : (c >> 4) == 0xE ? 3 : (c >> 3) == 0x1E ? 4 : 0;
  if (n == 0 || i + n > s.size()) return 0;
  cp = n == 1 ? c : c & (0xFF >> (n + 1));
  for (size_t k = 1; k < n; k++) {
    unsigned char cc = s[i + k];
    if ((cc >> 6) != 0x2) return 0;
    cp = (cp << 6) | (cc & 0x3F);
  }
  return n;
}

// Code points the Inter fonts carry: Latin up to Latin Extended-B, plus … · −.
inline bool in_font(uint32_t cp) {
  return (cp >= 0x20 && cp <= 0x24F) || cp == 0x2026 || cp == 0x00B7 || cp == 0x2212;
}

// Keep code points the font has, drop the rest, trim; empty -> fallback.
inline std::string sanitize(const std::string &utf8, const std::string &fallback) {
  std::string out;
  for (size_t i = 0; i < utf8.size();) {
    uint32_t cp = 0;
    size_t n = utf8_next(utf8, i, cp);
    if (n == 0) {
      i++;
      continue;
    }
    if (in_font(cp)) out.append(utf8, i, n);
    i += n;
  }
  size_t a = out.find_first_not_of(' '), b = out.find_last_not_of(' ');
  return a == std::string::npos ? fallback : out.substr(a, b - a + 1);
}

// At most max_chars code points; the last one becomes "…" when cut.
inline std::string ellipsize(const std::string &s, size_t max_chars) {
  size_t i = 0, count = 0, cut = 0;
  while (i < s.size()) {
    uint32_t cp;
    size_t n = utf8_next(s, i, cp);
    if (n == 0) n = 1;
    if (count == max_chars - 1) cut = i;
    i += n;
    if (++count > max_chars) return s.substr(0, cut) + "\xE2\x80\xA6";
  }
  return s;
}

}  // namespace umote
