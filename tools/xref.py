#!/usr/bin/env python3
"""Find bl/b.w/b calls to target addresses: xref.py <bin> <addr> [<addr>...]."""
import sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

BASE = 0x08000000
data = open(sys.argv[1], "rb").read()[:0x10000]
targets = {int(a, 16) for a in sys.argv[2:]}
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.skipdata = True
for ins in md.disasm(data, BASE):
    if ins.mnemonic in ("bl", "b.w", "b", "blx") and ins.op_str.startswith("#"):
        if int(ins.op_str[1:], 16) in targets:
            print(f"{ins.address:08x}: {ins.mnemonic} {ins.op_str}")
