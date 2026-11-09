#!/usr/bin/env python3
"""Disassemble a flash address range of the Flow2 firmware: dis.py <bin> <start> <end>."""
import sys
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

BASE = 0x08000000
data = open(sys.argv[1], "rb").read()
start, end = int(sys.argv[2], 16), int(sys.argv[3], 16)
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.skipdata = True
for ins in md.disasm(data[start - BASE:end - BASE], start):
    print(f"{ins.address:08x}: {ins.bytes.hex():10} {ins.mnemonic:8} {ins.op_str}")
