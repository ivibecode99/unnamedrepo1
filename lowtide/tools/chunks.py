"""Chunk registry + blob emitters. Chunk ids < CH_CONTENT are fixed (see core/layout.h)."""
import struct, re, os
LAYOUT = {}
for line in open(os.path.join(os.path.dirname(__file__), '..', 'core', 'layout.h')):
    m = re.match(r'#define\s+(\w+)\s+(\d+)', line)
    if m: LAYOUT[m.group(1)] = int(m.group(2))
class Chunks:
    def __init__(self):
        self.d = {}; self.names = {}; self.next = LAYOUT['CH_CONTENT']
    def fixed(self, cid, data, name=None):
        assert cid not in self.d, cid; self.d[cid] = bytes(data); self.names[cid] = name or str(cid); return cid
    def add(self, data, name=None):
        cid = self.next; self.next += 1; self.d[cid] = bytes(data); self.names[cid] = name or f'c{cid}'; return cid
    def reserve(self, name=None):
        cid = self.next; self.next += 1; self.d[cid] = b''; self.names[cid] = name or f'c{cid}'; return cid
    def set(self, cid, data): self.d[cid] = bytes(data)
    def maxid(self): return max(self.d) + 1
    def blob(self):
        n = self.maxid(); dirsz = 2 + n * 6
        out = bytearray(); offs = []
        pos = dirsz
        for i in range(n):
            data = self.d.get(i, b''); offs.append((pos, len(data))); pos += len(data)
            assert len(data) < 65536
        out += struct.pack('<H', n)
        for o, l in offs: out += struct.pack('<IH', o, l)
        for i in range(n): out += self.d.get(i, b'')
        return bytes(out)
    def emit_c(self, path, blob):
        with open(path, 'w') as f:
            f.write('const unsigned int lt_blob_len = %d;\nconst unsigned char lt_blob[] = {\n' % len(blob))
            for i in range(0, len(blob), 24): f.write(','.join(str(b) for b in blob[i:i+24]) + ',\n')
            f.write('};\n')
