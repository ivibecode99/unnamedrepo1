"""Fixed art: font + UI tiles, battle sprites (soul/shield/bullets), title screen."""
import struct, math
from pix import Canvas, pal_bytes, canvas_png
from fontdata import glyph_canvas, G
import chunks as CHK
L = CHK.LAYOUT

UI_PAL = ['#F4EBD0', '#8C93B0', '#3C3A5C', '#0C0B14']

def grid(rows, cmap=None):
    cmap = cmap or {'.': 0, '1': 1, '2': 2, '3': 3}
    c = Canvas(len(rows[0]), len(rows))
    for y, r in enumerate(rows):
        for x, ch in enumerate(r): c.p[y][x] = cmap[ch]
    return c

def ui_tiles():
    tiles = []
    def t(rows): return grid(rows).tile(0, 0)
    bg = lambda: [[3] * 8 for _ in range(8)]
    def mk(fn):
        c = Canvas(8, 8, 3); fn(c); return c.tile(0, 0)
    def hl(c, y0, x0, x1):
        for y in (y0, y0 + 1):
            for x in range(x0, x1 + 1): c.px(x, y, 0)
    def vl(c, x0, y0, y1):
        for x in (x0, x0 + 1):
            for y in range(y0, y1 + 1): c.px(x, y, 0)
    TL = mk(lambda c: (hl(c, 3, 3, 7), vl(c, 3, 3, 7), c.px(3, 3, 3)))
    T = mk(lambda c: hl(c, 3, 0, 7))
    TR = mk(lambda c: (hl(c, 3, 0, 4), vl(c, 3, 3, 7), c.px(4, 3, 3)))
    Lt = mk(lambda c: vl(c, 3, 0, 7))
    R = mk(lambda c: vl(c, 3, 0, 7))
    BL = mk(lambda c: (hl(c, 3, 3, 7), vl(c, 3, 0, 4), c.px(3, 4, 3)))
    B = mk(lambda c: hl(c, 3, 0, 7))
    BR = mk(lambda c: (hl(c, 3, 0, 4), vl(c, 3, 0, 4), c.px(4, 4, 3)))
    arrow = grid(['33333333', '33333333', '30000003', '33000033', '33300333', '33330333', '33333333', '33333333'], {'0': 0, '3': 3}).tile(0, 0)
    cursor = grid(['33333333', '33033333', '33003333', '33000333', '33000033', '33000333', '33003333', '33033333'], {'0': 0, '3': 3}).tile(0, 0)
    heart = grid(['33303333', '33001333', '33001133', '30011113', '30011113', '30011113', '33000133', '33333333'], {'0': 0, '1': 1, '3': 3}).tile(0, 0)
    hp = []
    for k in range(9):
        c = Canvas(8, 8, 3)
        for x in range(8):
            for y in range(2, 6): c.px(x, y, 0 if x < k else 2)
        hp.append(c.tile(0, 0))
    tiles = [TL, T, TR, Lt, R, BL, B, BR, arrow, cursor, heart] + hp
    while len(tiles) < 31: tiles.append(Canvas(8, 8, 3).tile(0, 0))
    return tiles

def font_tiles():
    return [glyph_canvas(chr(32 + i)).tile(0, 0) for i in range(95)]

BS = {  # battle sprites, 8x8 each. colours: 0 transparent, 1 light, 2 mid, 3 dark
 'soul': ['...11...', '..1221..', '..1221..', '.122221.', '.122221.', '.122221.', '..2222..', '...22...'],
 'soulhit': ['........', '...22...', '..2222..', '..2332..', '..2332..', '..2222..', '...22...', '........'],
 'ring0': ['....1111', '..112222', '.1222...', '.122....', '12......', '12......', '12......', '12......'],
}
def battle_tiles():
    tiles = []
    soul = grid(['...22...', '..2112..', '.211112.', '.211112.', '.211112.', '..2112..', '..2112..', '...22...'], {'.': 0, '1': 1, '2': 2, '3': 3})
    # flame colours via SOUL palette: 1 yellow-white core, 2 orange edge
    soul2 = grid(['...2....', '..212...', '.21112..', '.211112.', '.211112.', '.211112.', '..2112..', '...22...'])
    # shield: 16x16 ring as 4 tiles (tl,tr,bl,br)
    sh = Canvas(16, 16)
    for a in range(0, 360, 3):
        x = 8 + 7.2 * math.cos(math.radians(a)); y = 8 + 7.2 * math.sin(math.radians(a))
        sh.px(int(x), int(y), 1)
    for a in range(0, 360, 7):
        x = 8 + 6.2 * math.cos(math.radians(a)); y = 8 + 6.2 * math.sin(math.radians(a))
        sh.px(int(round(x)), int(round(y)), 2)
    shield = [sh.tile(0, 0), sh.tile(1, 0), sh.tile(0, 1), sh.tile(1, 1)]
    orb = grid(['..1111..', '.122221.', '12222221', '12222221', '12222221', '12222221', '.122221.', '..1111..'])
    orb = grid(['........', '..1111..', '.112211.', '.122221.', '.122221.', '.112211.', '..1111..', '........'])
    spike = grid(['...11...', '...11...', '..1221..', '..1221..', '.122221.', '.122221.', '..1221..', '...11...'])
    bubble = grid(['..1111..', '.1....1.', '1..11..1', '1.1....1', '1......1', '1......1', '.1....1.', '..1111..'])
    note = grid(['....111.', '....1221', '....12.1', '....1...', '..111...', '.12221..', '.12221..', '..111...'])
    bar = grid(['........', '........', '11111111', '12222221', '12222221', '11111111', '........', '........'])
    star = grid(['...11...', '...11...', '1111111.', '.11221..', '..122...', '.12..21.', '.1....1.', '........'])
    star = grid(['...11...', '...11...', '.111111.', '11122111', '.111111.', '..1111..', '.11..11.', '11....11'])
    coin = grid(['..1111..', '.122221.', '12211221', '12211221', '12211221', '12211221', '.122221.', '..1111..'])
    drop = grid(['...11...', '...11...', '..1221..', '..1221..', '.122221.', '.122221.', '.122221.', '..1111..'])
    return [soul2.tile(0, 0), soulhit_tile(), *shield, orb.tile(0, 0), spike.tile(0, 0), bubble.tile(0, 0), note.tile(0, 0), bar.tile(0, 0), star.tile(0, 0), coin.tile(0, 0), drop.tile(0, 0), blank_tile(), blank_tile(), blank_tile(), blank_tile()]
def soulhit_tile(): return grid(['........', '...22...', '..2222..', '.222222.', '.222222.', '..2222..', '...22...', '........']).tile(0, 0)
def blank_tile(): return Canvas(8, 8, 0).tile(0, 0)

def title_art(ch):
    """20x18 tile title screen assembled from <=64 unique tiles."""
    uniq = []; idx = {}
    def T(cv):  # cv 8x8 canvas -> tile index
        b = cv.tile(0, 0)
        if b not in idx: idx[b] = len(uniq); uniq.append(b)
        return idx[b]
    W, H = 20, 18
    tmap = [[0] * W for _ in range(H)]; amap = [[0] * W for _ in range(H)]
    import random
    rnd = random.Random(7)
    # sky bands (palette 1): idx3 deep, dither to 2, 1
    def solid(v): return Canvas(8, 8, v)
    def dither(a, b, k):
        c = Canvas(8, 8, a)
        for y in range(8):
            for x in range(8):
                if (x + y * 2 + k) % 4 == 0: c.px(x, y, b)
        return c
    def starry(base, pts):
        c = Canvas(8, 8, base)
        for x, y in pts: c.px(x, y, 0)
        return c
    stars = [starry(3, [(2, 3)]), starry(3, [(6, 1), (1, 6)]), starry(3, [(4, 5)])]
    for y in range(0, 9):
        for x in range(W):
            if y < 3: cv = stars[(x * 7 + y * 3) % 5] if (x * 7 + y * 3) % 5 < 3 and (x + y) % 2 == 0 else solid(3)
            elif y < 5: cv = dither(3, 2, 0) if (x + y) % 3 == 0 else solid(3)
            elif y < 7: cv = solid(2) if (x * 3 + y) % 5 else dither(2, 3, 0)
            elif y == 7: cv = solid(2)
            else: cv = dither(2, 1, 0)
            tmap[y][x] = T(cv); amap[y][x] = 1
    lg = Canvas(112, 16)
    for i, chh in enumerate('LOWTIDE'):
        g = Canvas(5, 7)
        for y, r in enumerate(G[chh][:7]):
            for x in range(5):
                if r & (0x10 >> x): g.px(x, y, 1)
        big = g.scale(2)
        cell = Canvas(16, 16)
        for y in range(big.h):
            for x in range(big.w):
                if big.p[y][x]:
                    cell.px(x + 3, y + 1, 9)
        for y in range(big.h):
            for x in range(big.w):
                if big.p[y][x] and cell.get(x + 4, y + 2) == 0 and not big.get(x + 1, y + 1):
                    cell.px(x + 4, y + 2, 2)
        lg.blit(cell, i * 16, 0)
    lg.outline(3, diag=True)
    for yy in range(16):
        for xx in range(112):
            if lg.p[yy][xx] == 9: lg.p[yy][xx] = 0
            elif lg.p[yy][xx] == 0: lg.p[yy][xx] = 3
    for y in range(2):
        for x in range(14):
            cv = lg.crop(x * 8, y * 8, 8, 8)
            tmap[2 + y][3 + x] = T(cv); amap[2 + y][3 + x] = 2
    def dune(k):
        c = Canvas(8, 8, 3)
        for x in range(8):
            top = int(2 + 1.5 * math.sin((x + k * 8) / 6.0))
            for y in range(top, 8): c.px(x, y, 2 if y < top + 2 else 1)
        return c
    for y in range(9, 18):
        for x in range(W):
            if y == 9: cv = dune(x % 4)
            elif y == 10: cv = dither(2, 1, 0)
            elif y < 14: cv = solid(1) if (x + y) % 4 else dither(1, 0, 0)
            else: cv = dither(1, 0, 0) if y < 16 else dither(1, 0, 1)
            tmap[y][x] = T(cv); amap[y][x] = 3
    mast = Canvas(16, 32, 0)
    mast.rect(7, 0, 2, 30, 3); mast.rect(2, 6, 12, 2, 3); mast.rect(4, 14, 8, 2, 3)
    mast.line(8, 0, 2, 10, 3); mast.line(8, 0, 14, 9, 3); mast.rect(0, 28, 16, 4, 3)
    for ty in range(4):
        for tx in range(2):
            cv = mast.crop(tx * 8, ty * 8, 8, 8)
            gx, gy = 14 + tx, 5 + ty
            base = [[3] * 8 for _ in range(8)]
            ub = uniq[tmap[gy][gx]]
            for r in range(8):
                lo, hi = ub[r * 2], ub[r * 2 + 1]
                for xx in range(8): base[r][xx] = (((hi >> (7 - xx)) & 1) << 1) | ((lo >> (7 - xx)) & 1)
            out = Canvas(8, 8)
            for yy in range(8):
                for xx in range(8):
                    out.p[yy][xx] = 3 if cv.p[yy][xx] == 3 else base[yy][xx]
            tmap[gy][gx] = T(out)
            amap[gy][gx] = 1 if gy < 9 else 3
    assert len(uniq) <= 64, len(uniq)
    pal = [
        ['#26324F', '#3A4C7A', '#16203A', '#0A1024'],      # 0 spare
        ['#8FB8D8', '#4C6EA0', '#27365F', '#10162E'],       # 1 sky: idx0 star, 1, 2 deep, 3 darkest  (index order light->dark)
        ['#FFF2C8', '#F2A33C', '#B2542A', '#14122A'],       # 2 logo: cream, amber, rust, navy
        ['#E8C88C', '#C0905A', '#7A5240', '#1C1A30'],       # 3 sand: light, mid, shadow, dark
    ]
    data = bytearray()
    for p in pal: data += pal_bytes(p)
    for r in tmap: data += bytes(r)
    for r in amap: data += bytes(r)
    for t in uniq: data += t
    return bytes(data), len(uniq)

def build(ch):
    tiles = [blank_tile(), Canvas(8, 8, 3).tile(0, 0)] + font_tiles() + ui_tiles()
    assert len(tiles) == 128
    ch.fixed(L['CH_TILES_UI'], b''.join(tiles), 'ui_tiles')
    ch.fixed(L['CH_PAL_UI'], pal_bytes(UI_PAL), 'ui_pal')
    # CH_BSPR: 2 palettes (bullet, soul) then 16 tiles
    bp = pal_bytes(['#000000', '#BFF3FF', '#4FB3D9', '#16405E']) + pal_bytes(['#000000', '#FFF3B0', '#FF8A2A', '#B8321C'])
    ch.fixed(L['CH_BSPR'], bp + b''.join(battle_tiles()), 'battle_sprites')
    data, n = title_art(ch)
    ch.fixed(L['CH_TITLE'], data, 'title')
    print(f'  title: {n} unique tiles')
