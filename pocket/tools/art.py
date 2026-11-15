#!/usr/bin/env python3
"""Procedural pixel art for Capt & Co. Pocket Edition. Every tile/sprite is drawn in code (original art).
Pixels are 2-bit indices 0..3 (0 = lightest / transparent for sprites). Palettes are applied per platform."""
import math

class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.p = [[0] * w for _ in range(h)]
    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = c
    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)
    def ellipse(self, cx, cy, rx, ry, c, outline=None):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                v = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2
                if v <= 1.0:
                    self.set(x, y, c)
        if outline is not None:
            for y in range(int(cy - ry - 2), int(cy + ry + 3)):
                for x in range(int(cx - rx - 2), int(cx + rx + 3)):
                    v = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2
                    if 0.72 < v <= 1.0:
                        self.set(x, y, outline)
    def line(self, x0, y0, x1, y1, c):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.set(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)
    def rows(self, strs):
        for y, s in enumerate(strs):
            for x, ch in enumerate(s):
                if ch != ' ' and ch != '.':
                    self.set(x, y, int(ch))
    def tile(self, tx, ty):
        return [[self.p[ty * 8 + y][tx * 8 + x] for x in range(8)] for y in range(8)]
    def flip_h(self):
        out = Canvas(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                out.p[y][x] = self.p[y][self.w - 1 - x]
        return out

def tile8(strs):
    c = Canvas(8, 8)
    c.rows(strs)
    return c.tile(0, 0)

# ---------------------------------------------------------------- 5x7 font
FONT = {
'A':["01110","10001","10001","11111","10001","10001","10001"],
'B':["11110","10001","10001","11110","10001","10001","11110"],
'C':["01110","10001","10000","10000","10000","10001","01110"],
'D':["11110","10001","10001","10001","10001","10001","11110"],
'E':["11111","10000","10000","11110","10000","10000","11111"],
'F':["11111","10000","10000","11110","10000","10000","10000"],
'G':["01110","10001","10000","10111","10001","10001","01111"],
'H':["10001","10001","10001","11111","10001","10001","10001"],
'I':["01110","00100","00100","00100","00100","00100","01110"],
'J':["00111","00010","00010","00010","00010","10010","01100"],
'K':["10001","10010","10100","11000","10100","10010","10001"],
'L':["10000","10000","10000","10000","10000","10000","11111"],
'M':["10001","11011","10101","10101","10001","10001","10001"],
'N':["10001","11001","10101","10011","10001","10001","10001"],
'O':["01110","10001","10001","10001","10001","10001","01110"],
'P':["11110","10001","10001","11110","10000","10000","10000"],
'Q':["01110","10001","10001","10001","10101","10010","01101"],
'R':["11110","10001","10001","11110","10100","10010","10001"],
'S':["01111","10000","10000","01110","00001","00001","11110"],
'T':["11111","00100","00100","00100","00100","00100","00100"],
'U':["10001","10001","10001","10001","10001","10001","01110"],
'V':["10001","10001","10001","10001","10001","01010","00100"],
'W':["10001","10001","10001","10101","10101","11011","10001"],
'X':["10001","10001","01010","00100","01010","10001","10001"],
'Y':["10001","10001","01010","00100","00100","00100","00100"],
'Z':["11111","00001","00010","00100","01000","10000","11111"],
'0':["01110","10011","10101","10101","10101","11001","01110"],
'1':["00100","01100","00100","00100","00100","00100","01110"],
'2':["01110","10001","00001","00110","01000","10000","11111"],
'3':["11110","00001","00001","01110","00001","00001","11110"],
'4':["00010","00110","01010","10010","11111","00010","00010"],
'5':["11111","10000","11110","00001","00001","10001","01110"],
'6':["00110","01000","10000","11110","10001","10001","01110"],
'7':["11111","00001","00010","00100","01000","01000","01000"],
'8':["01110","10001","10001","01110","10001","10001","01110"],
'9':["01110","10001","10001","01111","00001","00010","01100"],
'.':["00000","00000","00000","00000","00000","01100","01100"],
',':["00000","00000","00000","00000","01100","00100","01000"],
'!':["00100","00100","00100","00100","00100","00000","00100"],
'?':["01110","10001","00001","00110","00100","00000","00100"],
'-':["00000","00000","00000","11111","00000","00000","00000"],
':':["00000","01100","01100","00000","01100","01100","00000"],
"'":["00100","00100","01000","00000","00000","00000","00000"],
'/':["00001","00010","00010","00100","01000","01000","10000"],
'x':["00000","00000","10001","01010","00100","01010","10001"],
}
FONT_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?-:'/x"

def font_tile(ch):
    rows = FONT[ch]
    t = [[0] * 8 for _ in range(8)]
    for y, r in enumerate(rows):
        for x, v in enumerate(r):
            if v == '1':
                t[y][x + 1] = 3
    return t

# ---------------------------------------------------------------- BG tiles
BG = {}   # name -> tile (8x8 of 0..3)
def _bg():
    BG['sky'] = tile8(["........"] * 8)
    BG['grass'] = tile8(["22222222", "21212121", "22222222", "33333333", "32323232", "33333333", "32333233", "33333333"])
    BG['dirt'] = tile8(["33333333", "32333233", "33333333", "33323333", "33333323", "32333333", "33333333", "33332333"])
    BG['brick'] = tile8(["22222222", "23333332", "23333332", "22222222", "33233323", "33233323", "22222222", "22222222"])
    BG['lava'] = tile8(["........", "..1..1..", ".111.11.", "22122122", "22222222", "32223222", "22222222", "23222322"])
    BG['coin'] = tile8(["........", "..3333..", ".311113.", ".311113.", ".311113.", ".311113.", "..3333..", "........"])
    BG['star'] = tile8(["...33...", "...33...", "3333333.", ".33333..", "..3333..", ".33.33..", ".3...3..", "........"])
    BG['trunk'] = tile8(["..2332..", "..2332..", "..2332..", "..2332..", "..2332..", "..2332..", "..2332..", "..2332.."])
    BG['leaf'] = tile8(["..2222..", ".222222.", "22322322", "22222222", "22232222", ".222222.", "..2222..", "........"])
    BG['cactus'] = tile8(["...22...", "2..22.2.", "2..22.2.", "222222.2", "...22222", "...22...", "...22...", "...22..."])
    BG['sand'] = tile8(["11111111", "11211111", "11111121", "22222222", "21222122", "22222222", "22212222", "22222222"])
    BG['sandfill'] = tile8(["22222222", "22212222", "22222222", "22222212", "21222222", "22222222", "22222122", "22222222"])
    BG['bld'] = tile8(["33333333", "32222223", "32222223", "32222223", "32222223", "32222223", "32222223", "33333333"])
    BG['window'] = tile8(["22222222", "21111112", "21111112", "21111112", "22222222", "22222222", "22222222", "22222222"])
    BG['cloud'] = tile8(["........", "...11...", "..1111..", ".111111.", "11111111", "........", "........", "........"])
    BG['spike'] = tile8(["........", "........", "...3....", "..333...", "..333.3.", "3.333.33", "33333333", "33333333"])
    BG['wall'] = tile8(["33333333", "32222223", "32333323", "32322323", "32322323", "32333323", "32222223", "33333333"])
    BG['metal'] = tile8(["33333333", "32222222", "32222222", "32222222", "32222222", "32222222", "32222222", "33333333"])
    BG['note'] = tile8(["...33...", "...3.3..", "...3..3.", "...3....", "..33....", ".333....", "..33....", "........"])
    BG['gear'] = tile8(["..3..3..", ".333333.", "33.22.33", "3..22..3", "3..22..3", "33.22.33", ".333333.", "..3..3.."])
    BG['hill'] = tile8(["........", "........", "........", "...22...", "..2222..", ".222222.", "22222222", "22222222"])
    BG['heart'] = tile8(["........", ".33.33..", "3333333.", "3333333.", ".33333..", "..333...", "...3....", "........"])
    BG['hudcoin'] = BG['coin']
    BG['hudstar'] = BG['star']
    BG['barrier'] = tile8(["3......3", "3......3", "3......3", "3......3", "3......3", "3......3", "3......3", "3......3"])
    BG['fill'] = tile8(["33333333"] * 8)
    BG['cityfill'] = tile8(["22222222", "22222222", "22222222", "22222222", "22222222", "22222222", "22222222", "22222222"])
_bg()

# order of BG tiles in VRAM
BG_ORDER = ['sky', 'grass', 'dirt', 'brick', 'lava', 'coin', 'star', 'trunk', 'leaf', 'cactus', 'sand', 'sandfill', 'bld', 'window',
            'cloud', 'spike', 'wall', 'metal', 'note', 'gear', 'hill', 'heart', 'barrier', 'fill', 'cityfill']
BG_INDEX = {n: i for i, n in enumerate(BG_ORDER)}
FONT_BASE = len(BG_ORDER)           # font tiles follow
def font_index(ch):
    if ch == ' ':
        return 0
    return FONT_BASE + FONT_CHARS.index(ch)
NUM_BG_TILES = FONT_BASE + len(FONT_CHARS)

# ---------------------------------------------------------------- Sprites
def pip_frame(frame):
    """8x16 Pip facing right. frame: 0 idle, 1 walk-a, 2 walk-b, 3 jump."""
    c = Canvas(8, 16)
    c.ellipse(4, 4, 3.6, 3.6, 1, 3)               # head (skin)
    c.rect(3, 5, 1, 1, 3); c.rect(5, 3, 1, 2, 3)   # eye and brow-ish
    c.rect(5, 5, 2, 1, 2)                          # nose/cheek
    c.rect(2, 8, 5, 4, 2)                          # shirt
    c.rect(1, 8, 1, 3, 3); c.rect(7, 8, 1, 3, 3)   # arms
    if frame == 1:
        c.rect(2, 12, 2, 3, 3); c.rect(5, 12, 2, 2, 3); c.set(6, 14, 3)
    elif frame == 2:
        c.rect(2, 12, 2, 2, 3); c.rect(5, 12, 2, 3, 3); c.set(2, 14, 3)
    elif frame == 3:
        c.rect(1, 12, 3, 2, 3); c.rect(5, 12, 2, 3, 3); c.set(1, 14, 3)
    else:
        c.rect(2, 12, 2, 3, 3); c.rect(5, 12, 2, 3, 3)
    c.rect(2, 15, 2, 1, 3); c.rect(5, 15, 2, 1, 3)
    return c

def pip_hat_frame():
    """Capt perched on Pip's head: 8x8 sprite drawn over the head top row (used as separate sprite)."""
    c = Canvas(8, 8)
    c.ellipse(4, 5, 3.6, 2.6, 2, 3)
    c.rect(0, 6, 8, 1, 3)
    c.set(3, 4, 1); c.set(5, 4, 1); c.set(3, 5, 3); c.set(5, 5, 3)
    return c

def hat_frame(f):
    c = Canvas(8, 8)
    if f == 0:
        c.ellipse(4, 4, 3.6, 2.8, 2, 3); c.rect(0, 5, 8, 1, 3); c.set(3, 3, 1); c.set(5, 3, 1)
    else:
        c.ellipse(4, 4, 2.2, 3.4, 2, 3); c.rect(3, 0, 2, 8, 3); c.set(4, 3, 1)
    return c

def walker_frame(f):
    c = Canvas(8, 8)
    c.ellipse(4, 4.2, 3.7, 3.2, 2, 3)
    c.rect(2, 3, 2, 2, 1); c.rect(5, 3, 2, 2, 1); c.set(3, 4, 3); c.set(5, 4, 3)
    c.rect(1, 2, 3, 1, 3); c.rect(5, 2, 3, 1, 3)
    if f == 0:
        c.rect(1, 7, 2, 1, 3); c.rect(5, 7, 2, 1, 3)
    else:
        c.rect(0, 7, 2, 1, 3); c.rect(6, 7, 2, 1, 3)
    return c

def flyer_frame(f):
    c = Canvas(8, 8)
    c.ellipse(4, 4, 2.2, 2.2, 3)
    c.set(3, 4, 1); c.set(5, 4, 1)
    if f == 0:
        c.line(0, 1, 2, 3, 2); c.line(7, 1, 5, 3, 2); c.rect(0, 0, 2, 1, 2); c.rect(6, 0, 2, 1, 2)
    else:
        c.line(0, 6, 2, 4, 2); c.line(7, 6, 5, 4, 2); c.rect(0, 6, 2, 1, 2); c.rect(6, 6, 2, 1, 2)
    return c

def boss_beetle():
    """24x24 scarab queen. Faces right."""
    c = Canvas(24, 24)
    c.ellipse(11, 14, 10.5, 8.5, 2, 3)            # shell
    c.line(11, 6, 11, 21, 3)                       # shell seam
    c.ellipse(20, 11, 3.5, 3.5, 3)                 # head
    c.set(21, 10, 1); c.set(22, 10, 1)
    c.line(19, 7, 22, 3, 3); c.line(22, 3, 23, 2, 3)   # antenna
    c.rect(18, 4, 4, 2, 1)                         # crown
    c.set(18, 3, 1); c.set(20, 3, 1); c.set(22, 3, 1)
    for i, x in enumerate((4, 9, 14)):
        c.line(x, 20, x - 2, 23, 3); c.line(x + 2, 20, x + 4, 23, 3)
    c.ellipse(8, 12, 2, 1.5, 1); c.ellipse(14, 12, 2, 1.5, 1)   # shell shine
    return c

def boss_baron():
    """24x24 Baron with top hat and key. Faces right."""
    c = Canvas(24, 24)
    c.rect(8, 0, 8, 7, 3); c.rect(6, 6, 12, 2, 3); c.rect(8, 5, 8, 1, 1)    # top hat
    c.ellipse(12, 12, 4.2, 4.0, 1, 3)              # face
    c.rect(10, 11, 2, 2, 3); c.rect(14, 11, 2, 2, 3); c.rect(10, 15, 5, 1, 3)  # eyes + mustache
    c.rect(5, 16, 14, 8, 3)                        # cape / body
    c.rect(7, 17, 10, 6, 2)
    c.rect(11, 17, 2, 6, 1)
    c.ellipse(3, 20, 3, 3, 1, 3); c.line(3, 17, 3, 12, 3); c.rect(1, 10, 5, 2, 3)  # key on the left
    return c

def projectile_frame(f):
    c = Canvas(8, 8)
    c.ellipse(4, 4, 2.6, 2.6, 3)
    c.set(3, 3, 1) if f == 0 else c.set(5, 5, 1)
    return c

def puff_frame():
    c = Canvas(8, 8)
    c.ellipse(4, 4, 3, 3, 1, 3)
    return c

def star_sprite():
    c = Canvas(8, 8)
    c.rows(BG_STAR if False else ["...33...", "...33...", "3333333.", ".33333..", "..3333..", ".33.33..", ".3...3..", "........"])
    return c

def tiles_2bpp(tile):
    """Convert 8x8 of 0..3 to GB 2bpp planar bytes (16)."""
    out = []
    for y in range(8):
        lo = hi = 0
        for x in range(8):
            v = tile[y][x]
            lo |= (v & 1) << (7 - x)
            hi |= ((v >> 1) & 1) << (7 - x)
        out += [lo, hi]
    return out

def split_tiles(canvas, flip=False):
    """Split a canvas into tiles in sprite order. For 8x16 frames: [top, bottom]. For NxM: row-major."""
    cv = canvas.flip_h() if flip else canvas
    tiles = []
    for ty in range(cv.h // 8):
        for tx in range(cv.w // 8):
            tiles.append(cv.tile(tx, ty))
    return tiles

# sprite sheet order (each entry: name, list of tiles)
def build_sprites():
    S = []
    def add(name, canvas):
        S.append((name, split_tiles(canvas)))
    for f in range(4):
        add("pip%d" % f, pip_frame(f))
    add("piphat", pip_hat_frame())
    add("hat0", hat_frame(0)); add("hat1", hat_frame(1))
    add("walk0", walker_frame(0)); add("walk1", walker_frame(1))
    add("fly0", flyer_frame(0)); add("fly1", flyer_frame(1))
    add("boss1", boss_beetle())
    add("boss2", boss_baron())
    add("proj0", projectile_frame(0)); add("proj1", projectile_frame(1))
    add("puff", puff_frame())
    add("star", star_sprite())
    return S

def sprite_layout():
    """Returns (flat tile list, {name: first_tile_index})."""
    flat, idx = [], {}
    for name, tiles in build_sprites():
        idx[name] = len(flat)
        flat += tiles
    return flat, idx

def bg_tiles():
    tiles = [BG[n] for n in BG_ORDER]
    for ch in FONT_CHARS:
        tiles.append(font_tile(ch))
    return tiles
