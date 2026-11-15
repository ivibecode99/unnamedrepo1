#!/usr/bin/env python3
"""Pack blob chunks into 16KB ROM banks and emit GBDK C sources + chunk directory."""
import sys, os, struct
def pack(blob_path, outdir, first_bank=16):
    blob = open(blob_path, 'rb').read()
    n = struct.unpack('<H', blob[:2])[0]
    ents = []
    for i in range(n):
        off, sz = struct.unpack('<IH', blob[2 + i * 6: 8 + i * 6]); ents.append((off, sz))
    banks = [bytearray()]
    dirrows = []
    for i, (off, sz) in enumerate(ents):
        data = blob[off: off + sz]
        assert sz <= 16384
        if len(banks[-1]) + sz > 16384: banks.append(bytearray())
        dirrows.append((len(banks) - 1 + first_bank, len(banks[-1]), sz))
        banks[-1] += data
    os.makedirs(outdir, exist_ok=True)
    for bi, b in enumerate(banks):
        bn = first_bank + bi
        with open(os.path.join(outdir, f'bank_{bn}.c'), 'w') as f:
            f.write(f'#pragma bank {bn}\nconst unsigned char bank_data_{bn}[] = {{\n')
            for i in range(0, len(b), 32): f.write(','.join(str(x) for x in b[i:i+32]) + ',\n')
            if not b: f.write('0\n')
            f.write('};\n')
    with open(os.path.join(outdir, 'chunkdir.c'), 'w') as f:
        f.write(f'const unsigned int lt_nchunks = {n};\nconst unsigned char lt_dir[] = {{\n')
        for bank, addr, sz in dirrows: f.write(f'{bank},{addr & 255},{addr >> 8},{sz & 255},{sz >> 8},\n')
        f.write('};\n')
    return first_bank + len(banks)
if __name__ == '__main__':
    last = pack(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 16)
    print('data banks', sys.argv[3] if len(sys.argv) > 3 else 16, 'to', last - 1)
