#!/usr/bin/env python3
"""Build the Fn-unlock firmware from a dump of the stock Flow2 (PID 0x0027) firmware.

Usage: make_patch.py <full_dump.bin> <out_dir>

Writes:
  stock_code.bin      - the stock firmware code region (restore image)
  fn_unlocked.bin     - same image with the Fn-key write protection disabled
"""
import hashlib
import pathlib
import sys

# Stock dump of this keyboard (VID 0x388D / PID 0x0027), full 256 KiB read.
STOCK_DUMP_SHA256 = "16bb6cea92ddb09556dcdde131f0806f0b2de69bdc572ceb741f5bc3d632cf7d"

# Firmware code ends at 0xF220; round up to a 256-byte flash page.
CODE_LEN = 0xF300

# via_command_kb() at 0x080052BC drops VIA "set keycode" (0x05) writes when
# row == 5 && col == 0 (the Fn key). The row test is `cmp r2, #5` at 0x080052E6.
# Changing the immediate to 0xFF makes it unreachable (rows are 0-5), while the
# separate Bluetooth-key protection (layers 1/3, row 1, cols 1-4) stays intact.
PATCH_OFFSET = 0x52E6
OLD = bytes.fromhex("052a")  # cmp r2, #5
NEW = bytes.fromhex("ff2a")  # cmp r2, #0xff


def main() -> int:
    dump_path, out_dir = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    dump = dump_path.read_bytes()
    digest = hashlib.sha256(dump).hexdigest()
    if digest != STOCK_DUMP_SHA256:
        print(f"Dump hash {digest} does not match the known stock dump; refusing to patch.")
        return 1
    if any(dump[CODE_LEN:0x10000]):
        print("Unexpected data after the code region; refusing to patch.")
        return 1

    stock = dump[:CODE_LEN]
    if stock[PATCH_OFFSET:PATCH_OFFSET + 2] != OLD:
        print("Patch site does not contain the expected instruction; refusing to patch.")
        return 1
    patched = bytearray(stock)
    patched[PATCH_OFFSET:PATCH_OFFSET + 2] = NEW

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "stock_code.bin").write_bytes(stock)
    (out_dir / "fn_unlocked.bin").write_bytes(patched)
    diff = [i for i in range(CODE_LEN) if stock[i] != patched[i]]
    print(f"stock_code.bin   {hashlib.sha256(stock).hexdigest()}")
    print(f"fn_unlocked.bin  {hashlib.sha256(patched).hexdigest()}")
    print(f"Bytes changed: {len(diff)} at {[hex(0x08000000 + i) for i in diff]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
