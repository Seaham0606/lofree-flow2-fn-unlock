#!/usr/bin/env python3
"""Minimal VIA raw HID client for the Flow2.

  via.py get <layer> <row> <col>
  via.py set <layer> <row> <col> <keycode-hex>
  via.py dump <layer>
"""
import sys
import time

import hid

VID = 0x388D
PIDS = (0x0027, 0x0003)


class Via:
    def __init__(self):
        info = next(
            d for pid in PIDS for d in hid.enumerate(VID, pid)
            if d["usage_page"] == 0xFF60 and d["usage"] == 0x61
        )
        self.dev = hid.device()
        self.dev.open_path(info["path"])
        self.dev.set_nonblocking(True)
        while self.dev.read(32):
            pass

    def cmd(self, payload):
        # Replies echo the request header; match on it so a stale report can't be mistaken for ours.
        self.dev.write([0x00] + payload + [0x00] * (32 - len(payload)))
        deadline = time.time() + 1.0
        while time.time() < deadline:
            r = self.dev.read(32)
            if r and r[:len(payload[:4])] == payload[:4]:
                return r
            time.sleep(0.005)
        raise TimeoutError(f"no reply to {payload}")

    def get(self, layer, row, col):
        r = self.cmd([0x04, layer, row, col])
        return (r[4] << 8) | r[5]

    def set(self, layer, row, col, keycode):
        self.cmd([0x05, layer, row, col, keycode >> 8, keycode & 0xFF])


def main() -> int:
    via = Via()
    op, args = sys.argv[1], [int(a, 0) for a in sys.argv[2:5]]
    if op == "get":
        print(hex(via.get(*args)))
    elif op == "set":
        via.set(*args, int(sys.argv[5], 16))
        print(hex(via.get(*args)))
    elif op == "dump":
        for row in range(6):
            print(" ".join(f"{via.get(args[0], row, c):04x}" for c in range(18)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
