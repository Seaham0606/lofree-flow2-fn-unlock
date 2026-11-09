#!/usr/bin/env bash
# Flash a firmware image to the Flow2 and verify it by reading it back.
# Usage: tools/flash.sh firmware/patched/fn_unlocked.bin   (or stock_code.bin to restore)
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="$1"
SIZE=$(stat -f%z "$IMAGE")
READBACK="$(mktemp -t flow2_readback).bin"

echo "Image: $IMAGE ($SIZE bytes)"
"$REPO/.venv/bin/python" -I "$REPO/tools/enter_dfu.py"
echo "Waiting for DFU device..."
wb32-dfu-updater_cli -w -l >/dev/null 2>&1 || true
sleep 2

wb32-dfu-updater_cli -s 0x08000000 -D "$IMAGE"
wb32-dfu-updater_cli -s 0x08000000 -Z "$SIZE" -U "$READBACK"

if cmp -s "$IMAGE" "$READBACK"; then
  echo "Verify OK: flash matches $IMAGE"
  wb32-dfu-updater_cli -R
else
  echo "VERIFY FAILED. Keyboard left in DFU mode; reflash firmware/patched/stock_code.bin."
  exit 1
fi
