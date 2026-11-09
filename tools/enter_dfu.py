#!/usr/bin/env python3
"""Put a Lofree Flow2 into WB32 DFU mode via the VIA raw HID "bootloader jump" command.

After this the keyboard re-enumerates as VID 0x342D / PID 0xDFA0 (WB Device in DFU Mode)
and stops typing until it is reset (wb32-dfu-updater_cli -R) or replugged.
"""
import sys
import time

import hid

VID = 0x388D
PIDS = (0x0027, 0x0003)
RAW_USAGE_PAGE = 0xFF60
RAW_USAGE = 0x61
CMD_BOOTLOADER_JUMP = 0x0B


def main() -> int:
    matches = [
        d
        for pid in PIDS
        for d in hid.enumerate(VID, pid)
        if d.get("usage_page") == RAW_USAGE_PAGE and d.get("usage") == RAW_USAGE
    ]
    if not matches:
        print("Flow2 raw HID interface not found. Connect it by USB in wired mode and close VIA.")
        return 2

    info = matches[0]
    print(f"Found {info.get('product_string')} PID=0x{info['product_id']:04X}")
    dev = hid.device()
    dev.open_path(info["path"])
    dev.set_nonblocking(True)
    # Drain any stale reports so they can't be mistaken for a reply.
    deadline = time.time() + 0.2
    while time.time() < deadline:
        dev.read(32, 20)
    written = dev.write([0x00, CMD_BOOTLOADER_JUMP] + [0x00] * 31)
    print(f"Bootloader jump sent ({written} bytes)")
    try:
        dev.close()
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
