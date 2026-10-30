# umote: Apple-grade UI and real Home Assistant integration

Date: 2026-10-30. Status: design, approved in conversation and pending review of this document.
Mockups: `2026-10-30-remote-ui-assets/all-screens-v5.html` (open in a browser; its live validator must say "All screens pass").

## 1. Intent

The remote (LCDwiki E32R24P: ESP32-WROOM-32E with no PSRAM, 2.4" 240×320 ST7789, XPT2046 resistive touch) works today as a bring-up build. It has touch, board detection, deep sleep and battery modes, but its UI is a mock and its Home Assistant (HA) calls point at an entity that doesn't exist. This project turns it into the living room's main remote:

- It should look and behave like Apple made it: calm, legible, no clutter, nothing cut off, no emoji or text-glyph icons.
- The screen shows what the TV is doing (app, title, artwork, live progress) and switches sources (PS5, apps) in one tap.
- The same physical keys do the right thing for whatever you're looking at: the TV, the soundbar or the Living Room devices.
- It is controlled through HA, which already knows the TV, the fans and the lights.

## 2. Goals, non-goals, anti-goals

**Goals**
1. A context-aware **TV page**: Now Playing with artwork, title, scrubbable progress and transport controls, plus a quick row of sources, plus a Sources sheet with inputs and apps.
2. A **Soundbar page** (IR only), a **Home page** (Living Room devices from HA) and a **Settings page** (Wi-Fi join, brightness, volume target, sleep, text size, About).
3. Physical keys routed **per page** with smart defaults. The only key setting is where Volume/Mute goes on the TV page.
4. **TV over WiFi only**: Wake-on-LAN to power on; HA Android TV Remote for keys, power off and app launch; HDMI passthrough links for inputs.
5. **Dynamic sources**: a newly plugged HDMI device appears by itself. CEC devices name themselves; others ask once.
6. The existing power and robustness work keeps working: no-board mode, deep sleep, ultra saver at 20 % or less, critical at 5 % or less.

**Non-goals (this round)**
- **Voice.** The VOICE key and the two voice screens are reserved and designed, but not built. It waits for the user to repair the Wyoming STT server, since the "Coder" agent (Qwen 3.1 VL) has no speech input today.
- Set-top-box IR. The STB isn't connected; if it returns it comes in as an HDMI source.
- Rooms other than the Living Room.
- Per-key remapping (rejected in favour of smart defaults).

**Anti-goals: these count as failure even if everything technically works**
- Any emoji or Unicode glyph used as an icon (see `~/.claude/CLAUDE.md`).
- Any touch target under 44 px, text under 12 px, or clipped or overlapping element on any screen.
- Instruction text on screens ("tap here to…"). Labels name things; they don't explain.
- A UI that freezes or shows stale data as if it were live. Stale data must look stale (dimmed, "Last seen").
- Losing the months-long battery life, for example by keeping WiFi up for UI updates while the screen is off.

## 3. Hard constraints (measured, not assumed)

| Area | Fact | Source |
|---|---|---|
| Display | 240×320, lit area 36.2 × 49 mm, so **167 ppi (6.6 px/mm)** | user's calipers |
| Touch | Resistive, single touch; after calibration taps land within **about 6 px (1 mm)**; X axis mirrored (fixed: `transform: mirror_x`, calibration 280–3720 / 300–3850) | tap test 2026-10-30 |
| Memory | No PSRAM; about 180 KB DRAM, of which 54 KB is static today; LVGL draw buffer 25 % (38 KB) | build output |
| Images | `online_image` decodes **JPEG, PNG, BMP, QOI, not WebP** | ESPHome 2026.10 source |
| TV | Haier haierATV, Android TV 11, 192.168.31.100, wired MAC `<tv_mac>`. HA `turn_on` can't wake it. **Wake-on-LAN wakes it fully** (screen on within about 3–8 s, last app resumes) | WoL test 2026-10-30 |
| TV inputs | HDMI 1 to 4 = `com.mediatek.tvinput/.hdmi.HDMIInputService/HW4..HW7`. **PS5 on HDMI 1** (CEC name "PlayStation 5"). Switching = HOME, then `play_media` url `content://android.media.tv/passthrough/<id>`. It works and wakes the PS5 over CEC, but **not from the screensaver** (HOME first) | live test |
| TV apps | `play_media` type `app` + package launches apps. Leaving HDMI needs HOME | live test, cleanyourtv notes |
| Now Playing | Google Cast `media_player.navazdeen` gives `app_name`, `media_title`, `media_duration`, `media_position(_updated_at)`, `entity_picture`, and SEEK when the app supports it. Artwork is **1920×1080 WebP, about 205 KB** from the app's CDN | live read (ZEE5) |
| HA entities | `remote.navazdeen` and `media_player.navazdeen_2` (androidtv_remote), `media_player.navazdeen` (cast) | registry |
| Living Room (HA area `living_room`) | TV Fan, Fridge Fan, Clock Fan (Atomberg: fan + LED light + timer); TV cabinet (3 relays, 5 lights); Matrix clock (display power, brightness); weather | registry |

## 4. The UI (decided)

The pixel-level reference is the mockup file. Every screen there passes the validator (§4.3). The firmware must reproduce those layouts at the same pixel positions.

### 4.1 Pages and navigation
- Four pages: **TV, Soundbar, Home, Settings**. Move between them by a slow side-swipe, or by tapping the **title** at top left ("TV" with a chevron icon), which opens a 4-row page picker. The picker is also usable with the D-pad.
- Status bar on every page: page title on the left (a 44 px-tall touch target), then the WiFi icon, battery % and battery outline on the right.
- **TV page, playing with artwork**: artwork 212×76 at y 36; title 20 px; "App · S1 E3 · Episode" 13 px; scrub strip 224×44 at y 148 (moves only after an 8 px drag); back-10 / play-pause / forward-10 at y 200 (56/64/56 × 44); a divider at y 250; four 50 px source tiles from y 256 with a fifth peeking.
- **TV page, no artwork** (PS5, Live TV, apps that report nothing): large source tile, name, "HDMI 1 · On", **Back to TV** and **Sources** buttons. The background takes the source's colour.
- **TV page, TV off** (my call): a large Power button with the source row below. Tapping a source powers on and then switches.
- **Which TV view shows** (builder-check call): TV off if `remote.navazdeen` is off or unavailable. Otherwise, "playing" if Cast is playing, paused or buffering and has a title (artwork view when `image.umote_artwork` is available). Otherwise, if `current_activity` is `com.mediatek.wwtv.tvcenter`, the current input from `sensor.umote_sources` (no-artwork view). Otherwise, the foreground app's tile (no-artwork view, app colour).
- **Quick row** (call): the four most-used sources overall (inputs and apps), always including the active one; a fifth peeks to show the row scrolls.
- **Swipe vs scrub** (call): a drag that starts on the scrub strip scrubs; a drag anywhere else changes page.
- **Sources sheet**: Inputs (only connected ones, plus Live TV), then Apps ordered by use. Apps unused for 30 days collapse into "More apps". Done or Back closes it. The active source shows an outline **and** a dot.
- **New HDMI device without CEC**: a one-time dialog asking what it is (Set-top box, Fire TV, PC, Other), with Later and Switch.
- **Soundbar page**: Input (TV, Bluetooth, Music), Sound (Cinema, Voice, Night), and Volume Down, Mute, Up as large buttons with icon and word. It shows the last *sent* state, because IR is one-way.
- **Home page**: two-column tiles, 100×64, 16 px apart sideways and 13 px apart down, so the D-pad's yellow focus ring always stays clear. Tiles show icon, state ("Speed 3", "Off", "Offline") and name (up to 2 lines). Offline devices are dimmed. Tap or OK toggles; hold opens the device's options sheet (e.g. Atomberg fan: on/off, speed −/+ of 6, timer Off/1/2/4 h, LED light).
- **Settings**: Wi-Fi, Brightness (slider row), Buttons ("Volume: Soundbar"), Sleep after, Text size, About (battery, signal in words and dBm, IP, firmware, button board).
- **Wi-Fi**: current network with a check icon and "Strong"; other networks with lock icon and Good/Fair/Weak; Scan again.
- **Keyboard** (Wi-Fi password): phone-style 3×4 keypad (abc to wxyz, delete, shift/123, space, Join). Tapping a group, or OK on it, opens a 4-key picker. Show/hide password. D-pad focus here is drawn *inside* the key.
- **Voice** (reserved, not built): Listening (mic, level bars, live transcript); result ("Opening Hotstar", Cancel).

### 4.2 Visual system
- Dark theme. Backgrounds tint toward the active app's colour.
- Font: an Inter-based family converted for LVGL at exactly **12, 13, 14, 15, 17, 20 px**, regular/semibold/bold as used, 4-bit anti-aliasing. Built-in Montserrat is not used.
- Icons: one SVG set (the sprite in the mockup file, 24-unit grid, 2 px stroke), rasterised at build time to A8 alpha masks at 14, 16, 20, 22, 24, 34 px and tinted at runtime. No font glyphs.
- App icons: the real launcher icons from the TV's APKs, composed like the launcher does (adaptive icons: background plus foreground, cropped to the centre 72/108; legacy icons: cropped to the opaque square), 44×44 RGB565 with alpha, stored in flash (about 4 KB each). YouTube, Spotify and Sony LIV need the APK resource table read to find their icon (obfuscated names).
- Secondary text at least 78 % white. Contrast at least 4.5:1 everywhere.

### 4.3 Accessibility rules (enforced by the validator)
Targets ≥ 44×44 px; ≥ 8 px between targets, with outer focus rings counted (stacked full-width list rows may touch, like iOS lists); text ≥ 12 px; nothing clipped, overflowing or off-screen; no emoji or glyph characters; state never shown by colour alone; actions fire on release; no fast or two-finger gestures. A **Text size** setting moves every size up one step and hides the artwork.

### 4.4 Keys per page

| Page | D-pad / OK / Back / Home | Vol± / Mute | CH± |
|---|---|---|---|
| TV | to the TV via HA (`remote.send_command`) | **setting**: Soundbar (IR, default) or TV (HA) | to the TV via HA (CH keys) |
| Soundbar | soundbar menu IR codes | soundbar IR | unused |
| Home | move focus ring / toggle / hold for options / Back closes the sheet | soundbar IR | page up/down |
| Settings | move through the list / select / back | soundbar IR | unused |
| any | POWER: TV on (WoL) or off (HA), plus soundbar power IR | | |

Without the button board, everything is reachable by touch (existing behaviour).

## 5. Integration architecture

### 5.1 Remote → HA (actions)
- ESPHome API `homeassistant.action` for `remote.send_command`, `remote.turn_off`, `media_player.play_media` (app, url), `media_player.media_play_pause` / `media_seek`, and device services (fan, light, switch, number).
- **The ESPHome device must be added to HA with "Allow the device to perform Home Assistant actions" on.** Without it every action is refused.
- **Wake-on-LAN is sent by the remote itself** (ESPHome `wake_on_lan`, MAC above) once its WiFi is up.
- The firmware's old `remote.android_tv` target is replaced by `remote.navazdeen`.

### 5.2 HA → remote (state)
- Scalars come from the ESPHome `homeassistant` sensor/text_sensor platforms (Cast attributes, `remote.navazdeen` `current_activity`, Living Room device states). Progress is extrapolated on the remote from `media_position` + `media_position_updated_at` while playing, so no per-second traffic is needed.
- Lists come in as JSON in an entity **attribute** (sources, Home tiles), read with a `homeassistant` text_sensor `attribute:` and parsed with `json` on the remote. No HTTP auth, no token on the remote.
- Artwork: the remote reads `image.umote_artwork`'s `entity_picture` (HA adds a rotating access token to it) and loads that URL with `online_image` (JPEG). The remote stores no long-lived token.

### 5.3 `umote` custom integration (new; runs inside HA, user's decision 2026-10-30)
All HA-side helpers live in HA itself (`/config/custom_components/umote`), keeping the isolation the user wants: HA runs HA services, the Rock 5C runs only LLMs. Running in HA's process means it needs no token. It reaches the TV through HA's **Android TV (ADB) integration** (`media_player.android_tv_192_168_31_100`, added 2026-10-30): `androidtv.adb_command` plus the `adb_response` attribute, verified working. It resizes with Pillow, which HA already ships.

| It provides | Contents |
|---|---|
| `sensor.umote_sources` (attribute `sources`, `current`) | Connected HDMI inputs from `dumpsys tv_input` / `hdmi_control` (CEC names, port, passthrough id), user-given names, Live TV, launchable apps minus system packages, usage counts and order, and which source is active. Refreshed on TV state changes and every few minutes while the TV is on; the last list is kept while the TV sleeps (standby closes ADB). |
| `sensor.umote_home` (attribute `tiles`) | Living Room entities from the area registry: id, name, kind, state, and the options the hold sheet offers (fan speed range, timer, LED). |
| `image.umote_artwork` | The current Cast `entity_picture`, downloaded, cropped and resized to **212×76 baseline JPEG** (about 8 KB), cached per URL; unavailable when there's no art. |
| service `umote.name_source` | Stores the name picked in the "New on HDMI" dialog. |
| service `umote.launch` | Source switching done in one place: TV off → wake (the remote has already sent WoL; this waits for the TV), HOME, then the input's passthrough url or `play_media` app. Also counts usage. |

Build-time (not part of the integration): an icon extractor script pulls launcher icons over ADB (§4.2) into the firmware tree.

### 5.4 HA changes already made (2026-10-30)
- Added HA's **Android TV (ADB)** integration for 192.168.31.100: `media_player.android_tv_192_168_31_100`, `remote.android_tv_192_168_31_100`. ADB commands through HA verified (CEC list read).
- Firemote card (Overview): `entity` changed to the ADB media player (its app buttons use `androidtv.adb_command`) and `android_tv_remote_entity: remote.navazdeen` added (its keys use Android TV Remote). Backups: `umote/ha-backup/lovelace-default-20261030-104719.json`, `…-110452.json`.

## 6. Firmware architecture (ESPHome 2026.9+, LVGL 9.5)
- Keep `remote.yaml` power, sleep, board-detection and battery logic. Replace `ui.yaml` with the new pages. Keep `sim.yaml` working, with stubbed data, so every page can be screenshotted on the desktop and checked by a port of the mockup validator before flashing.
- An input router (one script) maps (page, key) to an action per §4.4.
- WiFi policy: the TV, Home and Settings pages bring WiFi up when shown (data needs it). The Soundbar page and IR-only key presses do not. A screen showing data from more than 30 s ago dims it and says "Last seen". Sleep timers are unchanged.
- Memory: the artwork buffer (212×76 RGB565, about 32 KB) is allocated only while the TV page shows artwork. App icons and icon masks live in flash. Target: ≥ 40 KB free heap with WiFi up and the TV page shown, logged on every boot.

## 7. Dependencies outside this project
- **Soundbar IR codes**: capture the Sony bar's real codes (power, volume ±, mute, inputs, sound modes, menu/D-pad) with the existing "Ir Sensor" ESPHome device. Until then those buttons show "Code not captured".
- **CH340C sleep current**: measure; lift its VCC pin if it's over about 1 mA (hardware, from earlier sessions).
- **Voice**: Wyoming STT repair (user).

## 8. Decisions from the builder check (2026-10-30)
- Companion host: **inside HA** as the `umote` custom integration (user). Not the Rock 5C, which is LLM-only.
- HA Android TV (ADB) integration: **added** (user said yes).
- Soundbar: the user's remote is a Sony **RMT-AH103U**, the remote for the **HT-CT80** (also seen with the HT-CT780). The Soundbar page's input and sound-mode buttons take their names and codes from that remote's buttons when its IR codes are captured. The 3+3 layout holds up to 3 inputs and 3 modes; more goes in a scrolling row.
- Firemote "buttons do nothing" (2026-10-30): the card now sends the correct `remote.send_command` calls (recorded in a test browser), and the same call changed the TV volume 0.23 → 0.24 → 0.23 through HA. The open browser was most likely still on the old dashboard config; reloading fixes it. (Separately, HA's own media-control card throws `Cannot read properties of undefined (reading 'entity')` in `_computeProgress`; that's harmless and not ours.)

## 9. Left to the builder
- Exact LVGL widget structure, styles and animation curves (Apple-like: 200–250 ms ease-out; respect Reduce motion).
- `umote` integration internals: refresh cadence, caching, parsing of dumpsys output.
- How usage counts are gathered (TV foreground history via HA `current_activity` changes is acceptable).
- Icon rasterisation tooling (e.g. cairosvg plus a script into LVGL C arrays).

## 10. Acceptance
1. The firmware's screens, rendered in `sim.yaml` with stub data, pass the validator rules in §4.3 and match the mockup positions to within ±2 px.
2. From standby, pressing POWER (or tapping PS5) wakes the TV within 10 s, and PS5 lands on HDMI 1.
3. On the TV page during playback: correct title, app, artwork within 3 s of a title change, progress within ±2 s, and scrub/seek works when Cast reports SEEK.
4. Home page shows exactly the Living Room devices. A new device added to the area in HA appears after a refresh, without reflashing.
5. Volume keys follow the setting. On the Soundbar page every key sends IR.
6. Battery behaviour unchanged: sleep current, ultra-saver and critical modes as before. Free heap ≥ 40 KB as above.
