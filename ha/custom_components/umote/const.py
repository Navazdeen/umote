"""Constants for the umote integration."""

DOMAIN = "umote"

TV_REMOTE = "remote.navazdeen"
TV_CAST = "media_player.navazdeen"
TV_ADB = "media_player.android_tv_192_168_31_100"
AREA = "living_room"

TUNER_PACKAGE = "com.mediatek.wwtv.tvcenter"
PASSTHROUGH_PREFIX = "content://android.media.tv/passthrough/"

SYSTEM_PACKAGES = frozenset({
    "com.android.vending",
    "com.gathin.tvhome",
    "com.haier.launcher.haiermatrix",
    "com.mediatek.wwtv.mediaplayer",
    "com.mediatek.wwtv.tvcenter",
    "com.navazdeen.house",
})

# source id -> (color, icon key)
STYLE = {
    "com.netflix.ninja": "#e50914",
    "in.startv.hotstar": "#16307a",
    "com.amazon.amazonvideo.livingroom": "#00a8e1",
    "com.google.android.youtube.tv": "#ff0000",
    "ps5": "#00439c",
}
DEFAULT_COLOR = "#3a3a3c"

APP_NAMES = {
    "com.netflix.ninja": "Netflix",
    "in.startv.hotstar": "Hotstar",
    "com.amazon.amazonvideo.livingroom": "Prime Video",
    "com.google.android.youtube.tv": "YouTube",
    "com.google.android.youtube.tvmusic": "YouTube Music",
    "com.spotify.tv.android": "Spotify",
    "com.sonyliv": "Sony LIV",
    "com.graymatrix.did": "ZEE5",
    "com.suntv.sunnxt": "Sun NXT",
    "com.discoveryplus.tv.android": "discovery+",
    "com.jio.media.stb.ondemand": "JioHotstar",
    "org.videolan.vlc": "VLC",
    "nl.giejay.android.tv.immich": "Immich",
}
UNUSED_AFTER_S = 30 * 86400

# device name -> short display name, where the rule (strip area, sentence case) is not enough
SHORT_NAMES = {"tv_cabinet": "Cabinet"}
AREA_PREFIXES = ("living room ", "living_room_")
