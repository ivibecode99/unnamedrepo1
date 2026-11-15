"""Indexed-colour pixel canvas helpers. Colour indices 0..3 (0=transparent/lightest, 3=darkest)."""
import zlib, struct

class Canvas:
    def __init__(self, w, h, fill=0):
        self.w, self.h = w, h
        self.p = [[fill] * w for _ in range(h)]
    def copy(self):
        c = Canvas(self.w, self.h); c.p = [r[:] for r in self.p]; return c
    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h: self.p[y][x] = c
    def get(self, x, y):
        return self.p[y][x] if 0 <= x < self.w and 0 <= y < self.h else 0
    def rect(self, x, y, w, h, c):
        for j in range(h):
            for i in range(w): self.px(x + i, y + j, c)
    def frame(self, x, y, w, h, c):
        for i in range(w): self.px(x + i, y, c); self.px(x + i, y + h - 1, c)
        for j in range(h): self.px(x, y + j, c); self.px(x + w - 1, y + j, c)
    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0); sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1; e = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1: break
            e2 = 2 * e
            if e2 >= dy: e += dy; x0 += sx
            if e2 <= dx: e += dx; y0 += sy
    def ellipse(self, cx, cy, rx, ry, c, only=None):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                if ((x - cx) / (rx + .5)) ** 2 + ((y - cy) / (ry + .5)) ** 2 <= 1:
                    if only is None or self.get(x, y) == only: self.px(x, y, c)
    def outline(self, c=3, diag=False):
        """add outline colour around non-zero pixels (on zero pixels)"""
        out = self.copy()
        for y in range(-1, self.h + 1):
            for x in range(-1, self.w + 1):
                if self.get(x, y) == 0:
                    n = [(1, 0), (-1, 0), (0, 1), (0, -1)] + ([(1, 1), (1, -1), (-1, 1), (-1, -1)] if diag else [])
                    if any(self.get(x + a, y + b) not in (0,) for a, b in n): out.px(x, y, c)
        self.p = out.p
    def blit(self, o, x, y, flip=False, key=0):
        for j in range(o.h):
            for i in range(o.w):
                v = o.p[j][o.w - 1 - i] if flip else o.p[j][i]
                if v != key: self.px(x + i, y + j, v)
    def flipx(self):
        c = Canvas(self.w, self.h); c.p = [r[::-1] for r in self.p]; return c
    def shift(self, dx, dy):
        c = Canvas(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                c.px(x + dx, y + dy, self.p[y][x])
        return c
    def crop(self, x, y, w, h):
        c = Canvas(w, h)
        for j in range(h):
            for i in range(w): c.p[j][i] = self.get(x + i, y + j)
        return c
    def scale(self, k):
        c = Canvas(self.w * k, self.h * k)
        for y in range(c.h):
            for x in range(c.w): c.p[y][x] = self.p[y // k][x // k]
        return c
    def tile(self, tx, ty):
        """8x8 tile -> 16 bytes GB 2bpp planar"""
        out = bytearray()
        for r in range(8):
            lo = hi = 0
            for x in range(8):
                v = self.get(tx * 8 + x, ty * 8 + r) & 3
                lo |= (v & 1) << (7 - x); hi |= ((v >> 1) & 1) << (7 - x)
            out += bytes([lo, hi])
        return bytes(out)
    def tiles(self):
        """all tiles row-major"""
        assert self.w % 8 == 0 and self.h % 8 == 0, (self.w, self.h)
        b = bytearray()
        for ty in range(self.h // 8):
            for tx in range(self.w // 8): b += self.tile(tx, ty)
        return bytes(b)
    def tiles_col(self):
        b = bytearray()
        for tx in range(self.w // 8):
            for ty in range(self.h // 8): b += self.tile(tx, ty)
        return bytes(b)

def rgb555(r, g, b):
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)
def hexc(s):
    s = s.lstrip('#'); return rgb555(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
def pal_bytes(cols):
    return b''.join(struct.pack('<H', hexc(c) if isinstance(c, str) else c) for c in cols)
def c555_to_rgb(c):
    return ((c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31)

def save_png(path, rows_rgb):
    h = len(rows_rgb); w = len(rows_rgb[0])
    raw = b''.join(b'\x00' + bytes(v for px in r for v in px) for r in rows_rgb)
    def ch(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + ch(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)) + ch(b'IDAT', zlib.compress(raw, 9)) + ch(b'IEND', b''))

def canvas_png(path, cv, pal555, scale=1, bg=(0, 0, 0), transparent0=False):
    cols = [c555_to_rgb(c) for c in pal555]
    rows = []
    for y in range(cv.h):
        r = []
        for x in range(cv.w):
            v = cv.p[y][x]
            r.append(bg if (transparent0 and v == 0) else cols[v & 3])
        rows += [[px for px in r for _ in range(scale)]] * scale
    save_png(path, rows)
