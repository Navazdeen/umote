# umote Remote UI + Home Assistant Integration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the ESP32 remote into a context-aware, Apple-grade TV / soundbar / Living Room controller backed by a new `umote` Home Assistant integration.

**Architecture:** HA does the thinking. A custom integration (`/config/custom_components/umote`) discovers sources over HA's Android TV (ADB) integration, builds the Living Room tile list, shrinks artwork, and switches sources. It publishes JSON in entity attributes plus one image entity. The ESPHome firmware subscribes to those with the `homeassistant` platforms, renders four LVGL pages, and routes physical keys per page through a small pure-C++ logic header that is unit-tested on the host. Every UI page is also built in the desktop SDL simulator, dumped to JSON, and checked by an automated layout validator before it touches hardware.

**Tech Stack:** Python 3.13+ / Home Assistant 2026.10.3 custom integration (Pillow, `pytest-homeassistant-custom-component` matching HA 2026.10.3); ESPHome ≥ 2026.9.1 (HA build server runs 2026.9.1) with LVGL 9.5, `font: gfonts://Inter`, `image:` (SVG + PNG), `json`, `online_image`, `wake_on_lan`; C++17 host tests with g++; SDL2 simulator.

**Spec:** `docs/superpowers/specs/2026-10-30-remote-ui-ha-design.md` (read it first). Pixel reference: `docs/superpowers/specs/2026-10-30-remote-ui-assets/all-screens-v5.html`. Open it in a browser; it lists the coordinates of every element and validates itself.

## Global Constraints

- ESPHome configs must compile on **2026.9.1** (the HA build server) *and* 2026.10.x. No option newer than 2026.9.1.
- No PSRAM. **Free internal heap ≥ 40 KB** with WiFi up and the TV page showing artwork, logged at boot and on page change.
- Touch targets **≥ 44×44 px**; **≥ 8 px** between targets, with outer focus rings counted (stacked full-width list rows may touch); text **≥ 12 px**; nothing clipped or off-screen; **no emoji or Unicode glyphs as icons** (icons are SVG files → `image:`); no instruction text on screens.
- Fonts: Inter at exactly **12, 13, 14, 15, 17, 20 px**, `bpp: 4`. Built-in Montserrat is not used.
- Artwork: **212×76 baseline JPEG**. The remote decodes only JPEG (no WebP).
- The remote **never stores an HA token**. Artwork URLs carry HA's rotating access token from `entity_picture`.
- TV: `remote.navazdeen`, `media_player.navazdeen_2` (androidtv_remote), `media_player.navazdeen` (cast), `media_player.android_tv_192_168_31_100` (ADB). Wake-on-LAN MAC **<tv_mac>**. HDMI 1..4 passthrough ids `com.mediatek.tvinput/.hdmi.HDMIInputService/HW4..HW7`. Live TV package `com.mediatek.wwtv.tvcenter`.
- HA area: **`living_room`**.
- Inputs are switched by **HOME first, then** `media_player.play_media` (`media_content_type: url`, `content://android.media.tv/passthrough/<url-encoded id>`). Apps: `play_media` type `app` + package.
- IR is used **only for the soundbar** (Sony, remote RMT-AH103U → HT-CT80).
- Battery/sleep/no-board behaviour from the current `firmware/remote.yaml` stays as it is. Voice is **not** built (the VOICE key is reserved).
- `.secret`, `firmware/secrets.yaml`, `ha-backup/`, tokens: never committed, never uploaded.

## Review Focus

1. **TV in standby (ADB closed, entities unavailable).** The integration keeps the last sources and tiles, marks the TV off, and logs no error; the remote shows the TV-off view. Test: `test_coordinator_keeps_last_sources_when_adb_unavailable` (Task 6).
2. **HA or WiFi drops while a data page is open.** After 30 s the data dims with "Last seen"; nothing freezes; keys still work (IR immediately, HA keys show "No connection"). Test: `is_stale` cases (Task 7) plus the sim `stale` fixture (Task 10).
3. **Cast "playing" with duration 0 or missing position (live streams, Live TV).** Scrub strip and times are hidden; no divide-by-zero; play/pause stays. Test: `progress_for_live_stream_is_hidden` (Task 7).
4. **Artwork missing, broken, huge or not an image.** The integration returns no image (entity unavailable) instead of raising; the remote falls back to the no-artwork view. Test: `test_artwork_rejects_garbage` and `test_artwork_handles_portrait_and_tiny` (Task 4).
5. **Titles and names with characters the font lacks** (emoji in Cast titles, Hindi/Tamil titles, 60-char SSIDs). They render without boxes (unsupported code points dropped; empty result becomes the app name) and truncate with an ellipsis. Test: `sanitize_drops_unsupported_codepoints` (Task 7) and the sim `long_title` fixture (Task 10).

---

## File Structure

```
.gitignore                                     secrets, build dirs, backups
ha/custom_components/umote/                    HA integration (deployed to /config/custom_components/umote)
  manifest.json  const.py  __init__.py  config_flow.py  services.yaml  strings.json
  tvparse.py      pure: dumpsys / package-list text -> inputs, apps
  sources.py      pure: inputs+apps+names+usage -> ordered source list, quick row, collapsed
  artwork.py      pure: image bytes -> 212x76 baseline JPEG bytes | None
  home.py         pure: registry/state snapshots -> Living Room tiles
  coordinator.py  DataUpdateCoordinator: runs adb_command, keeps Store (names, usage)
  sensor.py       sensor.umote_sources, sensor.umote_home
  image.py        image.umote_artwork
ha/tests/                                      pytest (pure + pytest-homeassistant-custom-component)
  fixtures/{tv_input.txt,hdmi_control.txt,packages.txt}
  test_tvparse.py test_sources.py test_artwork.py test_home.py test_integration.py
ha/deploy.sh                                   copy integration to HA over the SSH add-on, restart core
tools/appicons.py  tools/test_appicons.py      launcher icons from the TV -> firmware/assets/apps/*.png
firmware/
  remote.yaml      (modify) HA bindings, router wiring, WoL, WiFi policy, heap log
  ui.yaml          (rewrite) four pages, sheets, dialogs
  sim.yaml         (modify) stub data from env, UI dump
  assets.yaml      fonts + icons + app icons
  assets/icons/*.svg  (split from the mockup sprite)   assets/apps/*.png
  logic.h          pure C++: view selection, key routing, progress, stale, sanitize, JSON decode
  test/test_logic.cpp
  tools/check_ui.py  tools/test_check_ui.py    layout validator over the sim dump
```

---

### Task 0: Repository hygiene

**Files:** Create `.gitignore`

- [ ] **Step 1:** `git init` in `/home/navazdeenshamsu/umote` (it is not a repo yet).
- [ ] **Step 2:** Write `.gitignore` with: `.secret`, `firmware/secrets.yaml`, `**/.esphome/`, `ha-backup/`, `.superpowers/`, `.playwright-mcp/`, `__pycache__/`, `.venv/`, `*.pyc`.
- [ ] **Step 3:** Verify: `git status --porcelain | grep -E '\.secret|secrets.yaml|ha-backup'` prints nothing.
- [ ] **Step 4:** Commit: `git add -A && git commit -m "chore: start repository"`.

---

### Task 1: TV output parsing (`tvparse.py`)

**Files:** Create `ha/custom_components/umote/tvparse.py`, `ha/tests/test_tvparse.py`, `ha/tests/fixtures/*.txt`

**Interfaces — Produces:**
```python
@dataclass(frozen=True)
class Input: port: int; passthrough_id: str; cec_name: str | None; connected: bool
@dataclass(frozen=True)
class App: package: str
def parse_inputs(tv_input: str, hdmi_control: str) -> list[Input]          # ports 1..4, sorted
def parse_current_input(hdmi_control: str) -> int | None                    # active CEC port or None
def parse_apps(packages: str, system: frozenset[str]) -> list[App]         # sorted by package
SYSTEM_PACKAGES: frozenset[str]  # in const.py
```

- [ ] **Step 1: Capture fixtures from the real TV** (TV on): `adb -s 192.168.31.100:5555 shell dumpsys tv_input > ha/tests/fixtures/tv_input.txt`, same for `dumpsys hdmi_control` → `hdmi_control.txt`, and `cmd package query-activities --brief -a android.intent.action.MAIN -c android.intent.category.LEANBACK_LAUNCHER` → `packages.txt` (adb is at `~/tools/platform-tools/adb`).
- [ ] **Step 2: Write failing tests**
```python
def test_parse_inputs_finds_ps5_on_hdmi1():
    ins = parse_inputs(fx("tv_input.txt"), fx("hdmi_control.txt"))
    assert [i.port for i in ins] == [1, 2, 3, 4]
    ps5 = ins[0]
    assert ps5.passthrough_id == "com.mediatek.tvinput/.hdmi.HDMIInputService/HW4"
    assert ps5.cec_name == "PlayStation 5"
    assert ins[1].cec_name is None

def test_parse_apps_drops_system_packages():
    pk = {a.package for a in parse_apps(fx("packages.txt"), SYSTEM_PACKAGES)}
    assert {"com.netflix.ninja", "in.startv.hotstar", "com.amazon.amazonvideo.livingroom"} <= pk
    assert not pk & {"com.android.vending", "com.gathin.tvhome", "com.haier.launcher.haiermatrix", "com.mediatek.wwtv.mediaplayer", "com.mediatek.wwtv.tvcenter"}

def test_parse_current_input_none_when_invalid():
    assert parse_current_input("mActiveSource: (invalid, invalid)") is None
    assert parse_current_input("mActiveSource: (0x04, 0x1000)\n ... display_name: PlayStation 5 power_status: 0 physical_address: 0x1000 port_id: 1") == 1

def test_parsers_tolerate_empty_output():
    assert parse_inputs("", "") == [] and parse_apps("", SYSTEM_PACKAGES) == []
```
- [ ] **Step 3:** Run `cd ha && pytest tests/test_tvparse.py -q`. Expected: FAIL (module missing).
- [ ] **Step 4:** Implement. Port ↔ id comes from `TvInputHardwareInfo {id=N, type=9, … hdmi_port=P, cable_connection_status=S}` lines paired with `…HDMIInputService/HW<N>`. `connected` = status 1. CEC names come from `CEC: … display_name: X … port_id: P` lines, excluding `port_id: -1` (the TV itself). `SYSTEM_PACKAGES` = the five packages in the test above plus `com.navazdeen.house`.
- [ ] **Step 5:** Run tests. Expected: PASS. Commit `feat(umote): parse TV inputs and apps`.

---

### Task 2: Source list (`sources.py`)

**Files:** Create `ha/custom_components/umote/sources.py`, `ha/tests/test_sources.py`

**Interfaces — Consumes:** `Input`, `App` (Task 1). **Produces:**
```python
def build_sources(inputs: list[Input], apps: list[App], names: dict[int, str],
                  usage: dict[str, tuple[int, float]], now: float, current: str | None) -> dict
# returns {"sources":[{id,kind,name,port,target,color,icon,uses}], "quick":[4 ids], "more":[ids], "current": id|None}
# id: "hdmi1".."hdmi4", "tuner", or the app package; kind: "input"|"tuner"|"app"
# target: passthrough url for inputs (url-encoded id), package for apps, "com.mediatek.wwtv.tvcenter" for tuner
def source_id_for_activity(activity: str | None, current_input: int | None) -> str | None
```

- [ ] **Step 1: Write failing tests**
```python
def test_disconnected_inputs_hidden_and_tuner_always_present()
def test_input_name_priority():                         # user name > CEC name ("PlayStation 5") > "HDMI <port>"
def test_apps_ordered_by_uses_then_name()
def test_apps_unused_30_days_go_to_more():             # last_used older than now-30*86400 -> in "more", not in "sources" order head
def test_quick_row_is_top4_and_always_contains_current():
    out = build_sources(..., current="in.startv.hotstar")
    assert len(out["quick"]) == 4 and "in.startv.hotstar" in out["quick"]
def test_passthrough_target_is_url_encoded():
    assert src["target"] == "content://android.media.tv/passthrough/com.mediatek.tvinput%2F.hdmi.HDMIInputService%2FHW4"
def test_source_id_for_activity():
    assert source_id_for_activity("com.mediatek.wwtv.tvcenter", 1) == "hdmi1"
    assert source_id_for_activity("com.mediatek.wwtv.tvcenter", None) == "tuner"
    assert source_id_for_activity("com.netflix.ninja", None) == "com.netflix.ninja"
    assert source_id_for_activity(None, None) is None
```
- [ ] **Step 2:** Run → FAIL. **Step 3:** Implement. Colors and icon keys come from a table in `const.py` (Netflix `#e50914`, Hotstar `#16307a`, Prime `#00a8e1`, YouTube `#ff0000`, PS5 `#00439c`, default `#3a3a3c`); the icon key is the app id or `ps5`/`hdmi`/`tv`. **Step 4:** PASS. **Step 5:** Commit `feat(umote): ordered source list`.

---

### Task 3: Living Room tiles (`home.py`)

**Files:** Create `ha/custom_components/umote/home.py`, `ha/tests/test_home.py`

**Interfaces — Produces:**
```python
def build_tiles(entities: list[dict], devices: dict[str, dict], states: dict[str, dict], area: str) -> list[dict]
# entities/devices = registry entries as dicts; states = {entity_id: {"state":..,"attributes":..}}
# tile: {"id": str, "name": str, "kind": "fan"|"lights"|"switches"|"display", "icon": "fan"|"bulb"|"plug"|"clock",
#        "state": "on"|"off"|"offline", "label": str, "entities": [entity_ids], "options": {...}}
```
Grouping rule (spec §4.1 Home): one **fan** tile per device that has a `fan.*` entity, with that device's `light.*` as `options.led` and `percentage_step` → `options.speed_count`. One **lights** tile and one **switches** tile per other device, grouping its `light.*` and `switch.*`. A device whose only control is a `switch.*` plus a `number.*` brightness becomes a **display** tile. Entities with `entity_category`, hidden or disabled are skipped. Order: on tiles first, then name.

- [ ] **Step 1: Write failing tests** using a fixture built from the real registry (fans: "TV Fan", "Fridge Fan", "clock fan"; tv_cabinet: 3 switches + 5 lights; Matrix Clock: switch + number).
```python
def test_tiles_for_living_room():
    names = [t["name"] for t in tiles]
    assert set(names) == {"TV Fan", "Fridge fan", "Clock fan", "Cabinet lights", "Cabinet power", "Matrix clock"}
def test_fan_label_shows_speed_when_on():          # percentage 50, step 16.67 -> "Speed 3"; off -> "Off"
def test_unavailable_is_offline_not_off()
def test_group_state_on_if_any_member_on():         # cabinet lights: 1 of 5 on -> state "on", label "1 on"
def test_other_areas_ignored()
```
- [ ] **Step 2–5:** FAIL → implement → PASS → commit `feat(umote): Living Room tiles`. Display names: the device's `name_by_user` or `name`, with the area prefix stripped and only the first letter capitalised ("Fridge fan"); group tiles are "<Device short name> lights" / "<…> power". `tv_cabinet` → "Cabinet".

---

### Task 4: Artwork shrink (`artwork.py`)

**Files:** Create `ha/custom_components/umote/artwork.py`, `ha/tests/test_artwork.py`

**Interfaces — Produces:** `def shrink(data: bytes) -> bytes | None` gives a 212×76 **baseline** (non-progressive) JPEG of at most 16 KB, or None.

- [ ] **Step 1: Write failing tests** (make inputs with Pillow in the test):
```python
def test_webp_1920x1080_becomes_212x76_baseline_jpeg():
    out = shrink(webp_bytes(1920, 1080)); im = Image.open(io.BytesIO(out))
    assert im.format == "JPEG" and im.size == (212, 76) and not im.info.get("progressive") and len(out) <= 16384
def test_artwork_handles_portrait_and_tiny():   # 300x900 and 40x20 -> still 212x76 (cover crop / upscale)
def test_artwork_rejects_garbage():
    assert shrink(b"not an image") is None and shrink(b"") is None
```
- [ ] **Step 2–5:** FAIL → implement (cover-crop to 212:76 centred, LANCZOS, quality from 85 down by 10 until ≤ 16 KB, `progressive=False`, catch `PIL.UnidentifiedImageError`/`OSError`) → PASS → commit `feat(umote): artwork shrink`.

---

### Task 5: App icons for the firmware (`tools/appicons.py`)

**Files:** Create `tools/appicons.py`, `tools/test_appicons.py`; output `firmware/assets/apps/<package>.png`

**Interfaces — Produces:**
```python
def compose_adaptive(background: Image.Image, foreground: Image.Image) -> Image.Image   # 108dp canvas, keep centre 72/108
def crop_opaque_square(img: Image.Image, alpha_threshold: int = 230) -> Image.Image
def finish(img: Image.Image, size: int = 44, radius: int = 12) -> Image.Image          # RGBA, rounded mask
def main(tv: str, packages: list[str], out_dir: Path) -> dict[str, str]                 # package -> "ok"|"missing: <reason>"
```
The icon is found from the APK's resource table (`androguard`'s `APK(...).get_app_icon(max_dpi=…)`), not by filename, so obfuscated apps (YouTube, Sony LIV) work. Adaptive XML icons resolve to their background and foreground layers.

- [ ] **Step 1: Failing tests** with synthetic images: adaptive composite keeps the centre (a 108×108 background with a red 72×72 centre and a blue margin → corners of the result are red); `crop_opaque_square` removes a 20 px transparent margin with a drop shadow (152×152 from 192×192, as seen on Prime); `finish` gives 44×44 RGBA with transparent corners.
- [ ] **Step 2–4:** FAIL → implement → PASS.
- [ ] **Step 5:** Run for real (TV on): `python tools/appicons.py --tv 192.168.31.100 --out firmware/assets/apps com.netflix.ninja in.startv.hotstar com.amazon.amazonvideo.livingroom com.google.android.youtube.tv com.spotify.tv.android com.sonyliv com.graymatrix.did com.suntv.sunnxt com.discoveryplus.tv.android com.jio.media.stb.ondemand com.google.android.youtube.tvmusic org.videolan.vlc nl.giejay.android.tv.immich`. Expected: every package `ok`. Open the PNGs and check that none shows a launcher bleed or a notification glyph (the Spotify trap from the mockups).
- [ ] **Step 6:** Commit `feat(tools): extract app icons from the TV`.

---

### Task 6: `umote` integration in HA (coordinator, entities, services, deploy)

**Files:** Create `manifest.json`, `const.py`, `__init__.py`, `config_flow.py`, `coordinator.py`, `sensor.py`, `image.py`, `services.yaml`, `strings.json`, `ha/tests/test_integration.py`, `ha/deploy.sh`

**Interfaces — Consumes:** Tasks 1–4. **Produces (the contract the firmware relies on):**
- `sensor.umote_sources`: state = number of sources; attributes `sources`, `quick`, `more`, `current`, `tv_on` (bool), `updated` (ISO). Attribute JSON must stay **≤ 3 KB** serialised; drop `more` details first if it would exceed that.
- `sensor.umote_home`: state = number of tiles; attribute `tiles`.
- `image.umote_artwork`: the current Cast artwork via `shrink()`; unavailable when there is none.
- Service `umote.launch` `{source_id: str}`. Unknown id → `ServiceValidationError`. Steps: if TV off → wait ≤ 15 s for `remote.navazdeen` on (the remote has already sent WoL); `remote.send_command HOME`; wait 1.5 s; then `play_media` url (inputs) or app (apps/tuner); count the use.
- Service `umote.name_source` `{port: int, name: str}`: stored in `Store("umote.names")`.
- manifest: `"domain": "umote"`, `"dependencies": ["androidtv", "media_player", "image"]`, `"requirements": ["Pillow"]` (HA ships it), `"iot_class": "local_polling"`, version `0.1.0`.

- [ ] **Step 1: Failing tests** (pytest-homeassistant-custom-component pinned to the release whose HA is 2026.10.3):
```python
async def test_sources_sensor_publishes_json(hass, mock_adb):          # mock_adb returns the Task 1 fixtures
    st = hass.states.get("sensor.umote_sources"); assert st.attributes["sources"][0]["id"] == "hdmi1"
async def test_coordinator_keeps_last_sources_when_adb_unavailable(hass, mock_adb):
    mock_adb.go_unavailable(); await refresh(); st = hass.states.get("sensor.umote_sources")
    assert st.attributes["sources"] and st.attributes["tv_on"] is False
async def test_launch_input_sends_home_then_passthrough(hass, calls)  # order: remote.send_command HOME, then play_media url
async def test_launch_unknown_source_raises(hass)
async def test_usage_counted_and_persisted(hass, hass_storage)
async def test_home_sensor_lists_living_room_tiles(hass, registry_fixture)
async def test_artwork_entity_unavailable_without_art(hass)
```
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement. ADB reads go through `androidtv.adb_command` on `media_player.android_tv_192_168_31_100`, then the `adb_response` attribute is read. The coordinator refreshes every 120 s while the TV is on and immediately when `remote.navazdeen` changes state or `current_activity`; it skips refreshes while the TV is off. Usage comes from `current_activity` changes (count +1 when an app stays in front ≥ 10 s). Config flow: a single step with no fields (one instance).
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5: Deploy and check live.** `ha/deploy.sh` copies the folder over the SSH add-on (`ssh -p 2222 -i ~/.ssh/home3d_ha_ed25519 root@192.168.31.91`) to `/config/custom_components/umote`, then runs `ha core restart`. Add the integration through the config flow (REST `POST /api/config/config_entries/flow {"handler":"umote"}`). Check: `sensor.umote_sources` lists PS5 on hdmi1, `sensor.umote_home` has the 6 tiles, and `umote.launch {source_id: hdmi1}` lands on HDMI 1 (CEC active source 0x1000), then `umote.launch {source_id: "com.gathin.tvhome"}` is refused (system package).
- [ ] **Step 6:** Commit `feat(umote): integration entities and services`.

---

### Task 7: Firmware logic (`logic.h`) with host tests

**Files:** Create `firmware/logic.h`, `firmware/test/test_logic.cpp`

**Interfaces — Produces** (namespace `umote`, header-only, no ESPHome includes):
```cpp
enum class Page { TV, SOUNDBAR, HOME, SETTINGS };
enum class Key { UP, DOWN, LEFT, RIGHT, OK, BACK, HOME, POWER, VOL_UP, VOL_DOWN, MUTE, CH_UP, CH_DOWN, VOICE, OK_HOLD };
enum class Target { TV_KEY, SOUNDBAR_IR, FOCUS_MOVE, FOCUS_TOGGLE, FOCUS_OPTIONS, CLOSE_SHEET, LIST_MOVE, LIST_SELECT, PAGE_SCROLL, POWER, NONE };
struct Action { Target target; const char *code; };   // code: "DPAD_UP", "VOL_UP", "UP", ... per table below
Action route(Page page, Key key, bool volume_to_tv, bool sheet_open);
enum class TvView { OFF, PLAYING_ART, PLAYING_NOART, INPUT, APP };
TvView select_view(bool tv_on, const char *cast_state, bool has_title, bool has_art, const char *activity);
struct Progress { bool show; float fraction; int pos_s; int remaining_s; };
Progress progress(float duration, float position, int64_t position_updated_ms, int64_t now_ms, bool playing);
// show=false when duration <= 0; position extrapolated only while playing, clamped to [0,duration]; pos_s = floor, remaining_s = ceil
bool is_stale(int64_t last_update_ms, int64_t now_ms);            // > 30000 ms
std::string sanitize(const std::string &utf8, const std::string &fallback);  // keep U+0020..U+024F; trim; empty -> fallback
std::string ellipsize(const std::string &s, size_t max_chars);
```
The routing table is spec §4.4: TV page D-pad/OK/Back/Home → `TV_KEY` ("DPAD_UP"…"DPAD_CENTER","BACK","HOME"), Vol/Mute → `SOUNDBAR_IR` unless `volume_to_tv`, CH → `TV_KEY` ("CHANNEL_UP"/"CHANNEL_DOWN"); Soundbar page → all `SOUNDBAR_IR` (D-pad codes "UP","DOWN","LEFT","RIGHT","ENTER","RETURN"), CH → `NONE`; Home page D-pad → `FOCUS_MOVE`, OK → `FOCUS_TOGGLE`, OK_HOLD → `FOCUS_OPTIONS`, Back with `sheet_open` → `CLOSE_SHEET`, CH → `PAGE_SCROLL`, Vol/Mute → `SOUNDBAR_IR`; Settings D-pad → `LIST_MOVE`, OK → `LIST_SELECT`; POWER anywhere → `POWER`; VOICE → `NONE` (reserved).

- [ ] **Step 1: Failing tests** in `test_logic.cpp` (plain `assert`, one function per case, `main` runs all):
```cpp
route(Page::TV, Key::VOL_UP, false, false) == {SOUNDBAR_IR, "VOL_UP"}; route(Page::TV, Key::VOL_UP, true, false) == {TV_KEY, "VOLUME_UP"}
route(Page::SOUNDBAR, Key::UP, false, false).target == SOUNDBAR_IR
route(Page::HOME, Key::BACK, false, true).target == CLOSE_SHEET
select_view(false, "", false, false, "") == TvView::OFF
select_view(true, "playing", true, true, "com.netflix.ninja") == TvView::PLAYING_ART
select_view(true, "idle", false, false, "com.mediatek.wwtv.tvcenter") == TvView::INPUT
progress_for_live_stream_is_hidden: progress(0, 0, 0, 1000, true).show == false
progress(4974.88, 2112.477, 0, 10000, true).pos_s == 2122 && .remaining_s == 2853   // extrapolated 10 s
progress(...paused...) does not extrapolate
is_stale(0, 30001) && !is_stale(0, 30000)
sanitize_drops_unsupported_codepoints: sanitize("Bigg Boss \xF0\x9F\x94\xA5", "Hotstar") == "Bigg Boss"; sanitize("\xE0\xAE\xA4\xE0\xAE\xAE", "Sun NXT") == "Sun NXT"
ellipsize("NavazAirFiber_EXT_5G_long", 12) == "NavazAirFib…"
```
- [ ] **Step 2:** `g++ -std=c++17 -Wall -Werror firmware/test/test_logic.cpp -o /tmp/tl && /tmp/tl` → fails to compile (header missing).
- [ ] **Step 3:** Implement `logic.h`.
- [ ] **Step 4:** Same command → prints `all logic tests passed`.
- [ ] **Step 5:** Commit `feat(firmware): pure logic for routing, views, progress`.

---

### Task 8: Assets: fonts, icons, app icons

**Files:** Create `firmware/assets.yaml`, `firmware/assets/icons/*.svg`; modify `firmware/sim.yaml` and `firmware/remote.yaml` to `!include` it via `packages`

**Interfaces — Produces:** font ids `f12, f13, f14, f15, f17, f20` (regular), `f13b, f15b, f17b, f20b` (bold 700), `f12s, f14s` (semibold 600). Image ids `ic_<name>_<px>` (alpha-only, tinted at runtime) for the names in the mockup sprite (`chev_down, chev_right, chev_left, check, pause, play, back10, fwd10, fan, bulb, clock, power, plug, tv, soundbar, home, sliders, vol_down, vol_up, mute, minus, plus, lock, wifi, mic, del, eye, shift, more`) at the sizes the mockup uses (14, 16, 20, 22, 24, 34). App icons `app_<package with dots as underscores>` (RGB565 + alpha, 44×44).

- [ ] **Step 1:** Split the `<symbol>`s in `all-screens-v5.html` into standalone `assets/icons/<name>.svg` (viewBox 0 0 24 24, stroke `#fff`, stroke-width 2, round caps/joins; filled parts `fill="#fff"`). A tiny script is fine; commit the SVGs, not the script.
- [ ] **Step 2:** `assets.yaml`: `font:` entries `gfonts://Inter` with weight and size per id, `bpp: 4`, glyphs = printable Latin-1 + Latin Extended-A + `…`, `·`, `−` (U+2212). `image:` entries per icon size (`type: GRAYSCALE`, `transparency: alpha_channel`, `resize: NxN`) and per app PNG (`type: RGB565`, `transparency: alpha_channel`).
- [ ] **Step 3:** Verify: `esphome compile sim.yaml` succeeds, and on the device side `esphome compile remote.yaml` (placeholder secrets) succeeds with flash ≤ 85 % and static RAM ≤ 60 KB (from the size report). If flash exceeds that, drop icon sizes that no page uses (grep `ui.yaml`).
- [ ] **Step 4:** Commit `feat(firmware): Inter fonts, SVG icons, app icons`.

---

### Task 9: UI dump and layout validator

**Files:** Create `firmware/tools/check_ui.py`, `firmware/tools/test_check_ui.py`; modify `firmware/sim.yaml`

**Interfaces — Produces:**
- In the sim: when env `SIM_DUMP=<path>` is set, 1.5 s after boot a lambda walks the LVGL tree of the active screen plus `lv_layer_top()` and writes JSON lines `{"screen": str, "obj": str, "x":…, "y":…, "w":…, "h":…, "clickable": bool, "hidden": bool, "text": str|null, "font_px": int|null, "text_w": int|null, "outline": int, "layer": "base"|"modal"}`. `text_w` comes from `lv_text_get_size` with the label's font; `outline` is outline width + pad. Objects inside a widget flagged with user data `"modal"` get `layer: modal`. Then it exits.
- `check_ui.py dump.jsonl` exits 0 or prints one line per failure and exits 1. Rules: exactly spec §4.3 / Global Constraints (target ≥ 44, gap ≥ 8 with outline counted, list-row exception for full-width stacked rows whose `obj` name starts `row_`, text ≥ 12, `text_w ≤ w` unless the name ends `_trunc`, inside 240×320, glyph regex identical to the mockup validator's).

- [ ] **Step 1: Failing tests** on hand-written dump fixtures: a 40×44 button fails "target"; two buttons 6 px apart fail "gap"; a 12 px label inside a 30 px-wide box with `text_w` 50 fails "clipped"; a label with "✓" fails "glyph"; two stacked `row_` objects 0 px apart pass; a correct fixture passes.
- [ ] **Step 2–4:** FAIL → implement both sides → PASS. Prove it end to end once: `SIM_DUMP=/tmp/d.jsonl SIM_STATE=normal SIM_TAB=0 <sim binary> && python firmware/tools/check_ui.py /tmp/d.jsonl`. It **must report failures on the current mock UI** (e.g. the 34 px-tall buttons), which shows the harness works.
- [ ] **Step 5:** Commit `test(firmware): LVGL dump and layout validator`.

---

### Task 10: TV page, Sources sheet, New-HDMI dialog

**Files:** Rewrite `firmware/ui.yaml` (TV page part); modify `firmware/sim.yaml` stub data

**Interfaces — Consumes:** fonts/images (Task 8), `umote::select_view/progress/sanitize/ellipsize` (Task 7). **Produces:** LVGL ids used by Task 13: `tv_root`, `np_art` (image), `np_title`, `np_sub`, `np_scrub` (slider), `np_pos`, `np_rem`, `np_play`, `np_back10`, `np_fwd10`, `quick_0..3` (+ `quick_peek`), `tv_off_power`, `src_sheet` (modal), `src_grid`, `new_hdmi_dialog` (modal), and the script `ui_render_tv(json sources, cast fields)`.

- [ ] **Step 1:** Add sim fixtures (env `SIM_FIXTURE=`): `art`, `noart_ps5`, `off`, `live` (duration 0), `long_title` ("Sa Re Ga Ma Pa 2026 Grand Finale Part 2 🔥 Special"), `stale`, `sheet`, `new_hdmi`. Each loads a JSON string identical in shape to `sensor.umote_sources` plus Cast fields.
- [ ] **Step 2:** Run the validator across all eight fixtures. Expected: FAIL (pages not built yet).
- [ ] **Step 3:** Build the widgets at the mockup coordinates (spec §4.1, `all-screens-v5.html` screens 1–4). The scrub strip uses `lv_slider` with an 8 px drag threshold before it emits a seek; the play/pause, ±10 and source tiles act on release; the TV-off view uses `tv_off_power` (centered, 120×56) above the quick row; the stale fixture dims data labels to 50 % and replaces `np_sub` with "Last seen m:ss ago".
- [ ] **Step 4:** Validator → PASS on all eight. Take sim screenshots (`screens/tv_*.png`) and compare against the mockup by eye; positions within ±2 px.
- [ ] **Step 5:** Commit `feat(ui): TV page, sources sheet, new-HDMI dialog`.

---

### Task 11: Soundbar, Home (+options sheet), page picker and swipe

**Files:** `firmware/ui.yaml` (other pages), `firmware/sim.yaml`

**Interfaces — Produces:** `sb_*` buttons (`sb_in_0..2`, `sb_mode_0..2`, `sb_vol_down`, `sb_mute`, `sb_vol_up`), `home_tile_0..N` with focus index global `g_focus`, `opt_sheet` (modal) with `opt_power`, `opt_speed_minus/plus`, `opt_timer_0..3`, `opt_led`, `page_picker` (modal) rows `pp_tv/sb/home/settings`, script `ui_render_home(json tiles)`, script `ui_show_page(int)`.

- [ ] **Step 1:** Sim fixtures `soundbar`, `home` (the 6 real tiles from Task 3 output), `home_focus_each` (moves the focus ring through every tile and dumps each state), `options_fan`, `picker`.
- [ ] **Step 2:** Validator → FAIL.
- [ ] **Step 3:** Build at mockup coordinates. The focus ring is an outline (3 px + 2 px offset) on tiles; tiles are 100×64, 16 px apart sideways and 13 px down. Soundbar button labels are placeholders `TV/Bluetooth/Music` and `Cinema/Voice/Night`, set from a substitution list so Task 14 can rename them. The page swipe is an `lv_tileview` with 4 tiles; drags that start on `np_scrub` must not change page (set `LV_OBJ_FLAG_SCROLL_CHAIN` off on the slider).
- [ ] **Step 4:** Validator → PASS on every fixture, including every focus position. Commit `feat(ui): soundbar, home, page picker`.

---

### Task 12: Settings, Wi-Fi join and keypad

**Files:** `firmware/ui.yaml` (settings part), `firmware/remote.yaml` (Wi-Fi scan/join), `firmware/sim.yaml`

**Interfaces — Produces:** `set_row_wifi/brightness/buttons/sleep/textsize/about`, `wifi_list` rows `wifi_row_N_trunc`, `kb_field`, `kb_key_<group>`, `kb_pick` (modal) keys `kb_pick_0..3`, script `ui_render_wifi(scan results)`, settings globals `g_vol_to_tv` (bool, restored), `g_text_large` (bool, restored), `g_brightness` (float, restored), `g_sleep_s` (int, restored).

- [ ] **Step 1:** Sim fixtures `settings`, `wifi_scan` (6 networks incl. a 32-char SSID), `keypad`, `keypad_pick`, `text_large` (whole UI one size up, artwork hidden: every page must still pass).
- [ ] **Step 2:** Validator → FAIL.
- [ ] **Step 3:** Build. Keypad logic: tap or OK on a group opens `kb_pick`; left/right moves the inset focus; OK appends; Back cancels; shift cycles `abc → ABC → 123 → #+=`, where the 123 and #+= layouts reuse the same 8 groups (digits, then symbols `!@#$%&*?` in pairs). Scan: `wifi::global_wifi_component->start_scanning()`, then read `get_scan_result()` (both exist in 2026.9.1 and 2026.10), dedupe by SSID keeping the strongest, sort by RSSI; signal words: ≥ −60 dBm Strong, ≥ −70 Good, ≥ −80 Fair, else Weak. Join: `save_wifi_sta(ssid, pass)`; if not connected within 20 s, show "Couldn't join" and `save_wifi_sta` the previous credentials back. **About** view (from `set_row_about`): rows Battery (`82%, 3.99 V`), Wi-Fi (`Strong, −33 dBm`), IP, Firmware (`ESPHOME_VERSION` + build date), Button board (`Found`/`Not found`), Free memory (KB); all read-only `row_` rows. Brightness slider writes `g_brightness` and applies to the backlight light immediately; Sleep after offers 10/20/30/60 s and feeds the existing idle timer (saver-mode 8 s still wins).
- [ ] **Step 4:** Validator → PASS. Sim: type "abc1" by key events and assert `kb_field` holds 4 dots plus "1".
- [ ] **Step 5:** Commit `feat(ui): settings, Wi-Fi join, keypad`.

---

### Task 13: Wire the device to HA (bindings, routing, WoL, WiFi policy)

**Files:** Modify `firmware/remote.yaml`

**Interfaces — Consumes:** everything above; entity contract from Task 6.

- [ ] **Step 1:** HA bindings: `text_sensor: platform: homeassistant` for `sensor.umote_sources` attribute `sources` / `quick` / `current` / `tv_on`, `sensor.umote_home` attribute `tiles`, `image.umote_artwork` attribute `entity_picture`, `media_player.navazdeen` state + `media_title`, `app_name`, `media_duration`, `media_position`, `media_position_updated_at`, `supported_features`, and `remote.navazdeen` state + `current_activity`. `online_image` loads `http://192.168.31.91:8123` + entity_picture (JPEG, 212×76, RGB565), only while `np_art` is visible, and is released otherwise.
- [ ] **Step 2:** Replace the old `press` / `tv_key` scripts with one `route_key(page, key)` calling `umote::route` and executing the action: TV_KEY → `homeassistant.action remote.send_command {entity_id: remote.navazdeen, command: code}`; SOUNDBAR_IR → `soundbar_ir(code)` (Task 14 fills codes; unknown codes show "Code not captured"); POWER → if `tv_on` false: `wake_on_lan` button press, then `homeassistant.action umote.launch` only if a source was tapped, else `remote.turn_off`. Source tiles → WoL if off, then `umote.launch {source_id}`. New-HDMI dialog → `umote.name_source {port, name}` (Later just closes; Switch also launches). Home tiles → the entity's toggle service; options sheet → `fan.set_percentage`, `light.toggle`, Atomberg timer per Task 3 `options`.
- [ ] **Step 3:** WiFi policy: showing TV, Home or Settings calls `net_up`; the Soundbar page and IR-only keys don't. Stale data dims after 30 s (`umote::is_stale`). Log `heap_caps_get_free_size(MALLOC_CAP_INTERNAL)` at boot and on every page change; warn under 40 KB.
- [ ] **Step 4:** Compile locally (placeholder secrets) on 2026.10.x, then push with `firmware/deploy_to_ha.sh` and compile on the HA build server (2026.9.1). Both succeed.
- [ ] **Step 5: Hardware acceptance** (spec §10; the user flashes via the build server, wirelessly):
  1. TV in standby → POWER → screen on ≤ 10 s; tap PS5 from the TV-off view → HDMI 1 (CEC active source 0x1000).
  2. Play something in Hotstar/ZEE5 → title, app and artwork within 3 s; progress within ±2 s of the TV; scrub seeks when SEEK is advertised.
  3. Home shows exactly the 6 Living Room tiles; toggling the TV Fan changes it in HA; adding a test switch to the Living Room area makes it appear after the next refresh with no reflash.
  4. Volume keys go to the soundbar by default and to the TV after changing the setting.
  5. Logged free heap ≥ 40 KB on the TV page with artwork; deep sleep and battery modes unchanged (sleep current as before).
- [ ] **Step 6:** Commit `feat(firmware): HA-driven pages, routing, WoL`.

---

### Task 14: Soundbar IR codes (depends on the user and the "Ir Sensor" ESPHome device)

**Files:** Modify `firmware/remote.yaml` (`soundbar_ir` table), `firmware/ui.yaml` substitutions (button names)

- [ ] **Step 1:** With the user pressing each RMT-AH103U button at the "Ir Sensor" device (`remote_receiver: dump: sony`), record power, vol±, mute, every input button, every sound-mode button, Night, and the menu/arrow/enter/return keys (if the remote has them) as Sony SIRC data + bit count.
- [ ] **Step 2:** Fill the `soundbar_ir` table. Rename the Soundbar page buttons to the remote's labels (3 inputs + 3 modes; extras go in a scrolling row). Re-run the Soundbar sim fixture through the validator → PASS.
- [ ] **Step 3:** On hardware: each Soundbar button changes the bar. Commit `feat(firmware): real HT-CT80 IR codes`.
