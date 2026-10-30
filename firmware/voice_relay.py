#!/usr/bin/env python3
"""Voice relay: remote's mic (UDP) -> Android TV voice search.

The remote streams raw I2S samples (32-bit, 16 kHz, mono) over UDP while the
voice button is held. This converts them to 16-bit / 8 kHz and feeds a voice
session on the TV through the Android TV Remote protocol v2 (the same one the
Google TV phone app uses), via the androidtvremote2 library.

Setup (run on the Rock 5C or the Zero 3W):
    pip install androidtvremote2
    python3 voice_relay.py --tv 192.168.31.50 --pair      # once: enter the code shown on the TV
    python3 voice_relay.py --tv 192.168.31.50             # then run it as a service

Test the TV first: if `--pair` works but voice never starts, your TV doesn't
accept third-party voice sessions and this path won't work on it.
"""
import argparse, array, asyncio, logging, os, time

from androidtvremote2 import AndroidTVRemote

LOG = logging.getLogger("voice_relay")
GAP_END = 0.6          # seconds of no packets = button released
CHUNK = 8192           # bytes per voice chunk (library minimum; smaller is zero-padded)


def convert(raw: bytes) -> bytes:
    """32-bit 16 kHz mono -> 16-bit 8 kHz mono (pairwise average as a simple low-pass)."""
    s32 = array.array("i"); s32.frombytes(raw[: len(raw) // 4 * 4])
    s16 = [v >> 16 for v in s32]                 # INMP441 data is left-justified 24-bit
    out = array.array("h", ((s16[i] + s16[i + 1]) // 2 for i in range(0, len(s16) - 1, 2)))
    return out.tobytes()


class Relay(asyncio.DatagramProtocol):
    def __init__(self, tv: AndroidTVRemote):
        self.tv, self.stream, self.buf, self.last = tv, None, bytearray(), 0.0
        self.starting = False

    def datagram_received(self, data, addr):
        self.last = time.monotonic()
        self.buf += convert(data)
        if self.stream is None and not self.starting:
            self.starting = True
            asyncio.ensure_future(self.begin())
        self.flush(False)

    async def begin(self):
        try:
            self.stream = await self.tv.start_voice()
            LOG.info("voice session started")
        except Exception as e:                  # TV refused or timed out
            LOG.warning("could not start voice: %s", e)
            self.buf.clear()
        finally:
            self.starting = False

    def flush(self, final):
        if self.stream is None:
            return
        while len(self.buf) >= CHUNK or (final and self.buf):
            chunk, self.buf = bytes(self.buf[:CHUNK]), self.buf[CHUNK:]
            self.stream.send_chunk(chunk)

    async def watchdog(self):
        while True:
            await asyncio.sleep(0.1)
            if self.stream and time.monotonic() - self.last > GAP_END:
                self.flush(True)
                self.stream.end()
                self.stream = None
                LOG.info("voice session ended")


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tv", required=True, help="TV IP address")
    ap.add_argument("--port", type=int, default=7777, help="UDP port the remote sends to")
    ap.add_argument("--dir", default=os.path.expanduser("~/.voice_relay"))
    ap.add_argument("--pair", action="store_true")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    os.makedirs(a.dir, exist_ok=True)
    tv = AndroidTVRemote("ESP32 remote", os.path.join(a.dir, "cert.pem"), os.path.join(a.dir, "key.pem"),
                         a.tv, enable_voice=True)
    if await tv.async_generate_cert_if_missing() or a.pair:
        await tv.async_start_pairing()
        await tv.async_finish_pairing(input("Code shown on the TV: ").strip())
        print("Paired.")
        if a.pair:
            return
    await tv.async_connect()
    tv.keep_reconnecting()
    LOG.info("connected to %s, voice supported: %s", a.tv, tv.is_voice_enabled)
    loop = asyncio.get_running_loop()
    relay = Relay(tv)
    await loop.create_datagram_endpoint(lambda: relay, local_addr=("0.0.0.0", a.port))
    LOG.info("listening on UDP %d", a.port)
    await relay.watchdog()


if __name__ == "__main__":
    asyncio.run(main())
