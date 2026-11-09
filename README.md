# Lofree Flow2 Fn unlock

A 1-byte patch to the Lofree Flow2 100 (OE926) firmware that lets VIA remap the Fn key, for example to swap Fn and Left Ctrl.

Target: **VID 0x388D / PID 0x0027** (the revision this was dumped from). The community 60-second backlight firmware is for PID 0x0003 and is a different build; don't mix them.

## What the stock firmware does

Lofree's `via_command_kb()` hook at `0x080052BC` intercepts VIA commands before QMK's handler. For "set keycode" (`0x05`) it answers as if the write succeeded, but drops it when:

- row 5, column 0: the Fn key, on any layer
- layer 1 or 3, row 1, columns 1–4: the Bluetooth/2.4G keys on the Fn layer

The patch changes `cmp r2, #5` at `0x080052E6` to `cmp r2, #0xFF`. Only the Fn-key branch becomes unreachable; the Bluetooth-key protection stays.

Nothing else in the firmware depends on which physical key sends `MO(1)`. One power-on check scans row 5 / column 0 together with Esc (holding both while plugging in enters a factory/test mode); it is unaffected.

See [docs/ANALYSIS.md](docs/ANALYSIS.md) for the disassembly.

## Files

| Path | What |
|---|---|
| `firmware/original/flow2_pid0027_full_256k.bin` | Full flash read from the keyboard (read twice, identical) |
| `firmware/patched/stock_code.bin` | Stock code region, the **restore image** |
| `firmware/patched/fn_unlocked.bin` | Patched image |
| `reference/` | Keymap backups taken over VIA before any changes |
| `tools/` | DFU entry, patch builder, flasher, disassembly helpers |

The firmware binaries are Lofree's code and are excluded from git (`.gitignore`). Keep them locally; don't publish them.

## Use

```bash
python3 -m venv .venv && .venv/bin/pip install capstone hidapi intelhex
brew install wb32-dfu-updater_cli
.venv/bin/python -I tools/make_patch.py firmware/original/flow2_pid0027_full_256k.bin firmware/patched
tools/flash.sh firmware/patched/fn_unlocked.bin
```

Connect by USB in wired mode and close VIA first. To undo:

```bash
tools/flash.sh firmware/patched/stock_code.bin
```

After flashing, set the far-left key to `Left Ctrl` and the second key to `MO(1)` in VIA.

## Status

Flashed 2026-11-08 on a PID 0x0027 board: write verified by readback, boots normally, keymap kept across the flash.
VIA now saves Left Ctrl on the far-left key (row 5, col 0) and `MO(1)` on the second key; before the patch the first write was silently dropped.

`tools/via.py` reads and writes single keys over raw HID (`get`, `set`, `dump`) without opening VIA.
