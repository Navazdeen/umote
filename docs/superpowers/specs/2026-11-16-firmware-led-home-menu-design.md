# Firmware fixes: status LED, hold menus, launch path (2026-11-16)

Short design for the batch of fixes the user asked for on 2026-11-16. Branch `firmware-led-home-menu`.

## What was wrong, and the fix

| Reported | Cause | Fix |
|---|---|---|
| "Battery critical" runs out of its pill | Pill fixed at 100 px | Pill takes the width of its text (`ui::set_status`); Large text says "Low battery" so it clears the page title |
| Home tiles reorder when tapped | HA sorted tiles "on" first | Fixed order by name (`home.py`) |
| Hold should open a device menu | Only fans had one; and LVGL sends CLICKED after a long press, so a hold also toggled the tile | Tiles toggle on SHORT_CLICKED. New group sheet (`open_group`): one row per light or relay with a switch, a brightness slider where the light dims, an "All" row; Matrix clock gets Power and Brightness. Rows come from a new `members` attribute on `sensor.umote_home` (not kept in the RTC cache) |
| Hold animation | None | While held, the tile sinks 3 px and a fill sweeps across it (90 ms delay, 300 ms), then the sheet slides up |
| TV apps don't open | `media_player.play_media` type `app` (a `market://` link) reports success on this TV and does nothing. Measured: the same was true for Live TV | `umote.launch` starts everything over ADB (`monkey -p <package>` for apps and Live TV, `am start -a VIEW -d <passthrough>` for inputs). Old path is the fallback when ADB is down |
| Source switch is slow, first tap lost | Old path: HOME, 1.5 s, play_media, about 10 s measured. The remote waited 6 s for HA after a wake, then sent into a link that takes about 10 s to come up | ADB path measured at 1 to 3 s. The remote waits 15 s, says "Opening …" at once and "No link to Home Assistant" if it gives up, and starts WiFi on a touch wake instead of at the first tap |
| On-screen volume ignores "Volume: TV" | Soundbar page buttons always sent IR | `umote::volume_action`: the setting applies to the keys and the on-screen buttons on every page. TV mute is `VOLUME_MUTE` (was `MUTE`, the microphone key) |
| Running app should lead the TV list | Quick row was the 4 most used, current swapped into the last slot | Quick row: what is running, then most recently used. Apps in the sheet are ordered the same way |

## Status LED and charging

The on-board RGB LED (IO22/16/17) already flashed for IR and WiFi. It now has a base colour it returns to (`led_base` in `remote.yaml`): amber = charging, green = full, red blink = battery ≤ 20 %, red = ≤ 5 % (the red ones only while awake).

No pin reports charging on the E32R24P, so it is inferred from the battery voltage (`umote::ChargeTracker`, `logic.h`, host-tested):

- a rise of 35 mV over the last resting reading means the charger went on;
- a fall of 35 mV below the peak (60 mV while awake) means it came off;
- at 4.10 V or more, three flat resting readings, or the fall when the charger chip ends the charge, mean full;
- full is shown for 12 resting readings (about an hour): "full on the charger" and "full, just unplugged" look the same;
- the state lives in RTC memory.

Asleep, the LED pins are held: red + green full on for charging (no PWM in deep sleep, so it is yellower than the awake amber), green for full. The remote wakes dark for about a second every 15 min to look for a charger and every 5 min while charging (`poll_idle_min`, `poll_charge_min`).

## Approaches considered

- Charging: voltage inference (chosen by the user), a sense wire from the TP4054 CHRG pin (exact, needs soldering), or no charging status.
- LED asleep: steady light with timer wakes (chosen), or LED only while awake.
- Menu data: inside the tile JSON (would pass the 2 KB RTC cache slot) or a separate `members` attribute (chosen).

## To check on the device

1. Charge thresholds against a real charge: watch `sensor.tv_remote_charging` and the battery voltage in HA.
2. Sleep current with the 15 min dark wake (estimate: 2 to 3 mAh a day).
3. LED colours through the back plate; amber asleep vs awake.
4. Flash is at 93.3 % of the OTA slot.

## Not built

D-pad navigation inside the new sheet; a charging mark on the screen.
