#!/usr/bin/env python3
"""Header checks for the Game Boy / GBA ROMs: cartridge type, ROM/RAM size, checksums, logo."""
import sys
def gb(path):
    d = open(path, 'rb').read(); ok = True
    ct, rs, ramsz, cgb = d[0x147], d[0x148], d[0x149], d[0x143]
    names = {0x1A: 'MBC5+RAM', 0x1B: 'MBC5+RAM+BATTERY', 0x19: 'MBC5'}
    c = 0
    for i in range(0x134, 0x14D): c = (c - d[i] - 1) & 255
    hdr_ok = c == d[0x14D]
    logo_ok = d[0x104:0x108] == bytes([0xCE, 0xED, 0x66, 0x66])
    g = 0
    for i, b in enumerate(d):
        if i not in (0x14E, 0x14F): g = (g + b) & 0xFFFF
    glob_ok = g == (d[0x14E] << 8 | d[0x14F])
    print(f'{path}: type=0x{ct:02X} ({names.get(ct,"?")}) romcode={rs} ({32 << rs} KB, file {len(d)//1024} KB) ramcode={ramsz} cgbflag=0x{cgb:02X} title={d[0x134:0x144].rstrip(bytes(1))!r}')
    print(f'   header checksum {"OK" if hdr_ok else "BAD"}  logo {"OK" if logo_ok else "BAD"}  global checksum {"OK" if glob_ok else "BAD (not verified by hardware)"}  battery={ct==0x1B}  size match={len(d)==(32<<rs)*1024}')
    return hdr_ok and logo_ok and ct == 0x1B and len(d) == (32 << rs) * 1024
def gba(path):
    d = open(path, 'rb').read(); c = 0
    for i in range(0xA0, 0xBD): c -= d[i]
    chk = (c - 0x19) & 255
    ok = chk == d[0xBD] and d[0xB2] == 0x96 and d[4:8] == bytes([0x24, 0xFF, 0xAE, 0x51])
    has_sram = b'SRAM_V113' in d
    print(f'{path}: {len(d)} bytes title={d[0xA0:0xAC].rstrip(bytes(1))!r} code={d[0xAC:0xB0]!r} fixed=0x{d[0xB2]:02X} complement {"OK" if chk==d[0xBD] else "BAD"} logo {"OK" if d[4:8]==bytes([0x24,0xFF,0xAE,0x51]) else "BAD"} SRAM tag={has_sram}')
    return ok and has_sram
if __name__ == '__main__':
    r = True
    for p in sys.argv[1:]: r &= (gba(p) if p.endswith('.gba') else gb(p))
    sys.exit(0 if r else 1)
