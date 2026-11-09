# Analysis notes

Firmware: dumped 2026-11-08 from a Flow2 100 reporting VID 0x388D / PID 0x0027, VIA protocol 0x000C.
MCU: Westberry WB32 (DFU VID 0x342D / PID 0xDFA0), Thumb-2, flash at 0x08000000. Code ends at 0xF220.

## Dynamic keymap (stock QMK)

```
08007dbe  dynamic_keymap_key_to_eeprom_address  (layer*0xD8 + row*0x24 + col*2 + 0x28)
08007dd0  dynamic_keymap_get_keycode            (layer<=5, row<=5, col<=0x11)
08007dfc  dynamic_keymap_set_keycode            no extra checks
08008be2  via_command_handler                   calls via_command_kb first
08008cc6    case 0x05 -> bl dynamic_keymap_set_keycode
```

## Lofree hook: via_command_kb @ 0x080052BC

```
080052be  ldrb r3, [r0]          ; command id
080052c2  cmp  r3, #5            ; id_dynamic_keymap_set_keycode
080052c6  beq  0x80052e4
...
080052e4  ldrb r2, [r0, #2]      ; row
080052e6  cmp  r2, #5            ; <-- patched to #0xff
080052e8  bne  0x80052f8
080052ea  ldrb r3, [r0, #3]      ; col
080052ec  cbnz r3, 0x80052f8
080052ee  data[4..5] = 0x0002    ; fake the reply
080052f6  b    0x80052d8         ; raw_hid_send(reply); return true (write dropped)
080052f8  if ((layer & 0xFD) == 1 && row == 1 && col-1 <= 3) -> same drop   ; BT keys on Fn layer
0800530e  return false           ; let QMK handle it
```

## Other Fn-position references

`0x08005154` scans the matrix at boot/wake and sets two flags: row 5 / col 0 → `0x2000243A`, row 0 / col 0 (Esc) → `0x20002439`.
They gate a power-on Fn+Esc factory/test mode (`0x08003F66`, `0x08004406`, `0x08004A54…`). This doesn't affect runtime keymaps.

No code compares against the keycode `MO(1)` (0x5221); Fn-layer functions are custom keycodes (0x7Exx) on layer 1 and work from any key that activates it.
