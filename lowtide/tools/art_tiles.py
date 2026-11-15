"""Procedural 16x16 metatile painters + per-zone tilesets. Colour indices: 0 lightest .. 3 darkest."""
import random
from pix import Canvas, pal_bytes

def quad(c8):
    """tile an 8x8 pattern 2x2 -> 16x16"""
    c = Canvas(16, 16)
    for y in range(16):
        for x in range(16): c.p[y][x] = c8.p[y % 8][x % 8]
    return c
def spk(base, spots, seed, n):
    rs = random.Random(seed); c = Canvas(8, 8, base)
    for i in range(n): c.px(rs.randrange(8), rs.randrange(8), spots[i % len(spots)])
    return c
def floor(v, rs):
    """floor base colour is index 0 so props (bg idx 0) sit on it seamlessly"""
    if v == 'sand': return quad(spk(0, [1, 2, 1], 3, 5))
    if v == 'plain': return quad(Canvas(8, 8, 0))
    if v == 'dark': return quad(spk(0, [1, 2], 5, 4))
    if v == 'plank':
        c = Canvas(16, 16, 0)
        for y in (0, 8): c.rect(0, y + 7, 16, 1, 2); c.rect(0, y, 16, 1, 1)
        c.px(4, 3, 1); c.px(11, 11, 1)
        return c
    if v == 'stone':
        c = Canvas(8, 8, 0); c.rect(0, 0, 8, 1, 1); c.rect(0, 0, 1, 8, 1); c.px(3, 3, 1); c.px(5, 5, 2)
        return quad(c)
    if v == 'tile':
        c = Canvas(8, 8, 0); c.rect(0, 7, 8, 1, 1); c.rect(7, 0, 1, 8, 1); c.rect(1, 1, 2, 1, 1)
        return quad(c)
    if v == 'carpet':
        c = Canvas(8, 8, 1)
        for i in range(8): c.px(i, i, 0); c.px(7 - i, i, 0)
        return quad(c)
    if v == 'moss': return quad(spk(0, [1, 2, 1], 11, 7))
    return quad(Canvas(8, 8, 0))
def wall(v, rs):
    c = Canvas(16, 16, 2)
    if v == 'brick':
        for y in (0, 8): c.rect(0, y + 7, 16, 1, 3)
        c.rect(7, 0, 1, 8, 3); c.rect(3, 8, 1, 8, 3); c.rect(11, 8, 1, 8, 3)
        c.rect(0, 0, 16, 1, 1); c.rect(0, 8, 16, 1, 1)
    elif v == 'hull':
        for x in (0, 5, 10): c.rect(x + 4, 0, 1, 16, 3); c.rect(x, 0, 1, 16, 1)
        for y in (3, 12): c.px(2, y, 0); c.px(8, y, 0); c.px(13, y, 0)
    elif v == 'coral':
        c = Canvas(16, 16, 2)
        for cx, cy, r in ((4, 4, 4), (11, 5, 4), (7, 11, 5), (13, 12, 3)): c.ellipse(cx, cy, r, r, 1)
        for cx, cy in ((4, 3), (11, 4), (6, 10)): c.px(cx, cy, 0); c.px(cx + 1, cy, 0)
        c.outline(3) if False else None
        for y in range(16):
            for x in range(16):
                if c.p[y][x] == 2 and (x + y) % 5 == 0: c.p[y][x] = 3
    elif v == 'salt':
        c = Canvas(16, 16, 1)
        for x, y in ((0, 0), (8, 0), (0, 8), (8, 8)): c.rect(x, y, 8, 8, 0); c.frame(x, y, 8, 8, 2); c.px(x + 2, y + 2, 1); c.px(x + 3, y + 2, 1)
    elif v == 'cave':
        c = Canvas(16, 16, 3)
        for x, y, w, h in ((1, 1, 6, 5), (8, 2, 7, 6), (2, 8, 8, 7), (11, 9, 4, 6)): c.rect(x, y, w, h, 2); c.rect(x, y, w, 1, 1)
    elif v == 'book':
        c = Canvas(16, 16, 3)
        for i in range(6):
            col = (0, 1, 2)[i % 3]; c.rect(1 + i * 2 + (i // 3), 2, 2, 12, col)
        c.rect(0, 1, 16, 1, 1); c.rect(0, 14, 16, 2, 1)
    elif v == 'night':
        c = Canvas(16, 16, 3)
        for i in range(10): c.px(rs.randrange(16), rs.randrange(16), 2)
    return c
def water(v, rs):
    c = Canvas(16, 16, 1)
    for y, x0 in ((3, 1), (8, 7), (13, 3)):
        for i in range(6): c.px(x0 + i, y + (1 if i % 4 in (1, 2) else 0), 0)
    for y, x0 in ((6, 9), (11, 1)):
        for i in range(4): c.px(x0 + i, y + (i % 2), 2)
    return c
def prop(v, rs):
    c = Canvas(16, 16, 0)       # background 0 shows ground colour only if palette matches; props use own palette
    if v == 'pillar':
        c.rect(4, 0, 8, 16, 1); c.rect(4, 0, 2, 16, 0); c.rect(10, 0, 2, 16, 2); c.rect(3, 0, 10, 2, 0); c.rect(3, 14, 10, 2, 2); c.frame(3, 0, 10, 16, 3)
    elif v == 'barrel':
        c.ellipse(8, 8, 6, 7, 1); c.rect(2, 4, 12, 1, 2); c.rect(2, 11, 12, 1, 2); c.rect(5, 2, 2, 11, 0); c.outline(3)
        c.rect(0, 0, 16, 16, 0) if False else None
    elif v == 'crate':
        c.rect(1, 1, 14, 14, 1); c.frame(1, 1, 14, 14, 3); c.line(1, 1, 14, 14, 2); c.line(14, 1, 1, 14, 2); c.rect(2, 2, 12, 1, 0)
    elif v == 'lamp':
        c.rect(7, 6, 2, 10, 3); c.ellipse(8, 4, 3, 3, 0); c.px(8, 4, 1); c.frame(5, 1, 6, 6, 3) if False else None; c.outline(3)
        c.rect(5, 14, 6, 2, 3)
    elif v == 'kelp':
        for x0 in (4, 8, 12):
            for y in range(16): c.px(x0 + (1 if (y // 3) % 2 else 0), y, 1 if x0 != 8 else 0)
        for y in range(0, 16, 5): c.px(5, y, 3); c.px(9, y + 1, 3)
    elif v == 'coralc':
        c.rect(7, 6, 2, 10, 2); c.rect(3, 4, 2, 6, 2); c.rect(11, 3, 2, 7, 2); c.rect(3, 9, 6, 2, 2); c.rect(8, 9, 5, 2, 2)
        for x, y in ((7, 5), (3, 3), (11, 2)): c.rect(x, y, 2, 2, 0)
    elif v == 'rock':
        c.ellipse(8, 10, 7, 5, 2); c.ellipse(6, 8, 4, 3, 1); c.px(5, 7, 0); c.outline(3)
    elif v == 'door':
        c.rect(2, 1, 12, 15, 2); c.rect(4, 3, 8, 13, 3); c.frame(2, 1, 12, 15, 1); c.px(10, 10, 0)
    elif v == 'window':
        c.rect(2, 3, 12, 10, 3); c.rect(3, 4, 10, 8, 0); c.rect(7, 4, 2, 8, 3); c.rect(3, 7, 10, 2, 3); c.frame(2, 3, 12, 10, 2)
    elif v == 'sign':
        c.rect(7, 8, 2, 8, 3); c.rect(2, 2, 12, 8, 1); c.frame(2, 2, 12, 8, 3); c.rect(4, 4, 8, 1, 3); c.rect(4, 6, 6, 1, 3)
    elif v == 'rug':
        c.rect(0, 0, 16, 16, 2); c.frame(1, 1, 14, 14, 0); c.rect(4, 4, 8, 8, 1); c.rect(6, 6, 4, 4, 0)
    elif v == 'shelf':
        c.rect(1, 1, 14, 15, 3); c.rect(1, 6, 14, 1, 1); c.rect(1, 11, 14, 1, 1)
        for i in range(5): c.rect(2 + i * 3, 2, 2, 4, (0, 1, 2)[i % 3]); c.rect(2 + i * 3, 7, 2, 4, (1, 0, 2)[i % 3])
        c.rect(3, 12, 4, 3, 0); c.rect(9, 12, 4, 3, 1)
    elif v == 'bed':
        c.rect(1, 3, 14, 12, 2); c.rect(1, 3, 14, 5, 0); c.rect(2, 4, 5, 3, 1); c.frame(1, 3, 14, 12, 3)
    elif v == 'table':
        c.rect(1, 3, 14, 8, 1); c.frame(1, 3, 14, 8, 3); c.rect(2, 11, 2, 5, 3); c.rect(12, 11, 2, 5, 3); c.rect(2, 4, 12, 1, 0)
    elif v == 'stairs':
        for i in range(4): c.rect(0, i * 4, 16, 4, (0, 1, 1, 2)[i]); c.rect(0, i * 4 + 3, 16, 1, 3)
    elif v == 'crystal':
        c.line(8, 0, 4, 12, 0); c.line(8, 0, 12, 12, 0); c.rect(4, 12, 9, 2, 2)
        for y in range(1, 12): 
            for x in range(16):
                if c.p[y][x] == 0 and abs(x - 8) < y // 2: c.p[y][x] = 1
        c.rect(7, 4, 2, 6, 0)
        c.outline(3)
    elif v == 'statue':
        c.rect(4, 10, 8, 6, 2); c.rect(6, 2, 4, 9, 1); c.ellipse(8, 3, 3, 3, 0); c.rect(3, 6, 10, 2, 1); c.frame(4, 10, 8, 6, 3)
    elif v == 'mast':
        c.rect(7, 0, 2, 16, 3); c.rect(2, 2, 12, 2, 2); c.rect(4, 8, 8, 2, 2); c.line(8, 0, 2, 7, 1) if False else None
    elif v == 'chain':
        for y in range(0, 16, 4): c.ellipse(8, y + 2, 2, 2, 1); c.px(8, y + 2, 0)
    elif v == 'tank':
        c.rect(2, 2, 12, 13, 1); c.rect(3, 3, 10, 11, 0); c.frame(2, 2, 12, 13, 3); c.ellipse(8, 9, 2, 2, 2)
    elif v == 'glow':
        c.ellipse(8, 8, 5, 5, 2); c.ellipse(8, 8, 3, 3, 1); c.ellipse(8, 8, 1, 1, 0)
    elif v == 'desk':
        c.rect(0, 4, 16, 9, 1); c.rect(0, 4, 16, 2, 0); c.frame(0, 4, 16, 9, 3); c.rect(3, 6, 4, 4, 2); c.rect(9, 6, 5, 1, 3)
    elif v == 'gate':
        c.rect(0, 0, 16, 16, 3)
        for x in range(1, 16, 3): c.rect(x, 0, 1, 16, 1)
        c.rect(0, 6, 16, 1, 1)
    elif v == 'seat':
        c.rect(2, 6, 12, 8, 2); c.rect(2, 3, 12, 4, 1); c.frame(2, 3, 12, 11, 3)
    elif v == 'save':
        c.ellipse(8, 8, 6, 6, 1); c.ellipse(8, 8, 3, 3, 0)
    return c

PAINT = {'floor': floor, 'wall': wall, 'water': water, 'prop': prop}

class Tileset:
    def __init__(self, name, pals, defs, dmg_bgp=0xE4, dmg_obp=0xE4, flags=0):
        self.name, self.pals, self.defs, self.dmg_bgp, self.dmg_obp, self.flags = name, pals, defs, dmg_bgp, dmg_obp, flags
        self.legend = {}; self.metas = []; self.uniq = []; self.ids = {}
        rs = random.Random(hash(name) & 0xffff)
        for i, (ch, (kind, var, pal, fl)) in enumerate(defs.items()):
            cv = PAINT[kind](var, rs)
            quads = []
            for ty in range(2):
                for tx in range(2):
                    b = cv.tile(tx, ty)
                    if b not in self.ids: self.ids[b] = len(self.uniq); self.uniq.append(b)
                    quads.append(self.ids[b])
            self.metas.append(quads + [pal, fl]); self.legend[ch] = i
            if kind == 'prop' and False: pass
        assert len(self.uniq) <= 64, (name, len(self.uniq))
        assert len(self.metas) <= 48
    def tiles_bytes(self): return b''.join(self.uniq)
    def meta_bytes(self): return bytes([len(self.metas)]) + b''.join(bytes(m) for m in self.metas)
    def pal_bytes(self): return b''.join(pal_bytes(p) for p in self.pals)
    def preview(self, path, scale=3):
        from pix import canvas_png
        n = len(self.defs); cv = Canvas(16 * 8, 16 * ((n + 7) // 8))
        for i, (ch, (kind, var, pal, fl)) in enumerate(self.defs.items()):
            t = PAINT[kind](var, random.Random(1)); cv.blit(t, (i % 8) * 16, (i // 8) * 16, key=-1)
        # colour each by palette: render manually
        from pix import c555_to_rgb, save_png, hexc
        rows = []
        for y in range(cv.h):
            r = []
            for x in range(cv.w):
                i = (y // 16) * 8 + x // 16
                key = list(self.defs.values())[i][2] if i < n else 0
                col = self.pals[key][cv.p[y][x]]; col = hexc(col) if isinstance(col, str) else col
                r += [c555_to_rgb(col)] * scale
            rows += [r] * scale
        save_png(path, rows)
