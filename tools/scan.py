#!/usr/bin/env python3
"""Disassemble the Flow2 firmware (Thumb-2, base 0x08000000) and look for keymap-offset math."""
import sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

BASE = 0x08000000
data = open(sys.argv[1], "rb").read()[:0x10000]
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.skipdata = True
insns = list(md.disasm(data, BASE))
want = sys.argv[2:] or ["#0xd8", "#0x24", "#0x12"]
for i, ins in enumerate(insns):
    if ins.mnemonic in ("movs", "mov", "mov.w", "movw", "muls", "mul", "mla", "cmp", "cmp.w", "smlabb") and any(ins.op_str.endswith(w) for w in want):
        ctx = insns[max(0, i - 3): i + 6]
        if any(c.mnemonic.startswith(("mul", "mla", "smla")) for c in ctx):
            print("----")
            for c in ctx:
                print(f"{c.address:08x}: {c.mnemonic:8} {c.op_str}")
