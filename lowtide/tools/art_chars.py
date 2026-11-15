"""Procedural characters: 16x16 overworld sprites, 32x32 face portraits (5 emotions), big battle sprites (2 frames)."""
import math, random
from pix import Canvas, pal_bytes

# ---------------------------------------------------------------- helpers
def ell(c, cx, cy, rx, ry, col=1, hi=True, rim=2):
    c.ellipse(cx, cy, rx, ry, rim)
    c.ellipse(cx, cy, max(rx - 1, 0), max(ry - 1, 0), col)
    if hi and rx > 3 and ry > 3:
        for y in range(int(cy - ry), int(cy)):
            for x in range(int(cx - rx), int(cx)):
                if c.get(x, y) == col and (x - cx) ** 2 + (y - cy) ** 2 > (min(rx, ry) * .55) ** 2 and (x - cx) ** 2 + (y - cy) ** 2 < (min(rx, ry) * .8) ** 2 and y < cy - ry * .25 and x < cx - rx * .15:
                    c.px(x, y, 0)
def rr(c, x, y, w, h, col=1, rim=2):
    c.rect(x, y, w, h, rim); c.rect(x + 1, y + 1, w - 2, h - 2, col)
    c.rect(x + 1, y + 1, w - 2, 1, 0) if h > 4 else None

# ---------------------------------------------------------------- overworld sprites (0 transp, 1 light, 2 mid, 3 dark)
def sp_kid(c, hat=True):
    c.ellipse(8, 5, 3, 3, 1); c.rect(5, 8, 6, 5, 2); c.rect(5, 13, 2, 2, 3); c.rect(9, 13, 2, 2, 3); c.rect(4, 9, 1, 3, 1); c.rect(11, 9, 1, 3, 1)
    if hat: c.rect(5, 1, 6, 2, 3); c.rect(4, 3, 8, 1, 3)
    c.px(7, 5, 3); c.px(9, 5, 3)
def sp_wick(c):
    c.ellipse(8, 9, 3, 4, 2); c.ellipse(8, 9, 2, 3, 1); c.px(8, 8, 0); c.px(8, 9, 0); c.rect(8, 3, 1, 3, 2); c.px(8, 2, 1); c.px(7, 6, 3); c.px(9, 6, 3)
def sp_crab(c):
    c.ellipse(8, 10, 5, 3, 1); c.rect(2, 5, 3, 3, 2); c.rect(11, 5, 3, 3, 2); c.rect(3, 8, 1, 2, 2); c.rect(12, 8, 1, 2, 2)
    for x in (4, 6, 9, 11): c.px(x, 13, 3); c.px(x, 14, 3)
    c.px(6, 8, 3); c.px(10, 8, 3); c.rect(6, 7, 1, 2, 3) if False else None
def sp_anem(c):
    c.rect(6, 8, 4, 6, 1); c.rect(5, 14, 6, 1, 2)
    for x in (3, 5, 7, 9, 11): c.rect(x, 2 + (x % 4), 2, 7 - (x % 4), 2); c.px(x, 1 + (x % 4), 0)
    c.px(7, 10, 3); c.px(9, 10, 3)
def sp_urch(c):
    c.ellipse(8, 9, 4, 4, 1)
    for a in range(0, 360, 30):
        x = 8 + 6.5 * math.cos(math.radians(a)); y = 9 + 6.5 * math.sin(math.radians(a)); c.line(8 + int(4 * math.cos(math.radians(a))), 9 + int(4 * math.sin(math.radians(a))), int(x), int(y), 2)
    c.px(6, 8, 3); c.px(10, 8, 3); c.rect(7, 11, 3, 1, 3)
def sp_eel(c):
    for y in range(2, 14): c.rect(6 + int(2 * math.sin(y / 2.0)), y, 3, 1, 1)
    c.ellipse(8, 3, 3, 2, 1); c.px(7, 3, 3); c.px(9, 3, 3); c.px(12, 1, 0); c.line(9, 1, 12, 1, 2)
def sp_jelly(c):
    c.ellipse(8, 6, 5, 4, 1); c.rect(3, 6, 10, 2, 1)
    for x in (4, 7, 10, 12): c.rect(x, 9, 1, 5, 2)
    c.px(6, 6, 3); c.px(10, 6, 3); c.px(6, 3, 0)
def sp_kelp(c):
    for x0 in (4, 8, 11):
        for y in range(1, 15): c.px(x0 + int(math.sin(y / 2.0 + x0)), y, 1 if x0 != 8 else 2)
    c.rect(6, 6, 5, 4, 1); c.px(7, 7, 3); c.px(9, 7, 3)
def sp_gull(c):
    c.ellipse(8, 9, 4, 4, 1); c.rect(8, 2, 4, 4, 1); c.rect(11, 3, 3, 1, 2); c.px(10, 3, 3); c.rect(2, 8, 4, 2, 2); c.rect(11, 8, 4, 2, 2); c.rect(6, 13, 1, 2, 3); c.rect(9, 13, 1, 2, 3)
def sp_turtle(c):
    c.ellipse(8, 9, 6, 4, 2); c.ellipse(8, 8, 4, 3, 1); c.rect(1, 9, 3, 3, 1); c.px(2, 9, 3); c.rect(4, 13, 2, 2, 3); c.rect(10, 13, 2, 2, 3); c.px(8, 7, 0); c.px(7, 8, 0)
def sp_clam(c):
    c.ellipse(8, 10, 6, 4, 2); c.ellipse(8, 10, 4, 2, 0); c.rect(2, 9, 12, 1, 3); c.px(7, 10, 3); c.px(9, 10, 3); c.ellipse(8, 5, 2, 2, 1); c.px(8, 5, 0)
def sp_angler(c):
    c.ellipse(7, 9, 5, 4, 1); c.px(5, 8, 3); c.px(5, 9, 0) if False else None; c.rect(12, 8, 3, 3, 2); c.px(8, 12, 3); c.line(5, 5, 8, 1, 2); c.line(8, 1, 12, 1, 2); c.ellipse(12, 2, 1, 1, 0)
    c.rect(3, 12, 2, 2, 2); c.rect(9, 12, 2, 2, 2)
def sp_golem(c):
    c.rect(4, 3, 8, 6, 1); c.rect(3, 9, 10, 5, 1); c.rect(1, 5, 3, 6, 2); c.rect(12, 5, 3, 6, 2); c.px(6, 5, 3); c.px(9, 5, 3); c.rect(4, 3, 8, 1, 0); c.rect(3, 9, 10, 1, 0)
def sp_bell(c):
    c.ellipse(8, 7, 5, 5, 1); c.rect(3, 9, 10, 3, 1); c.ellipse(8, 14, 1, 1, 2); c.px(6, 6, 3); c.px(10, 6, 3); c.rect(7, 1, 2, 2, 2)
def sp_moth(c):
    c.ellipse(8, 9, 2, 4, 2); c.ellipse(4, 7, 3, 4, 1); c.ellipse(12, 7, 3, 4, 1); c.px(7, 6, 3); c.px(9, 6, 3); c.px(8, 12, 0)
SPR = {'kid': sp_kid, 'wick': sp_wick, 'crab': sp_crab, 'anem': sp_anem, 'urch': sp_urch, 'eel': sp_eel, 'jelly': sp_jelly, 'kelp': sp_kelp,
       'gull': sp_gull, 'turtle': sp_turtle, 'clam': sp_clam, 'angler': sp_angler, 'golem': sp_golem, 'bell': sp_bell, 'moth': sp_moth}

def acc16(c, acc):
    if acc == 'hat': c.rect(4, 2, 8, 2, 3); c.rect(6, 0, 4, 2, 3)
    elif acc == 'crown': c.rect(5, 1, 6, 2, 0); c.px(5, 0, 0); c.px(8, 0, 0); c.px(10, 0, 0)
    elif acc == 'scarf': c.rect(4, 8, 8, 2, 0)
    elif acc == 'glasses': c.rect(5, 5, 6, 1, 3)
    elif acc == 'apron': c.rect(5, 10, 6, 4, 0)
    elif acc == 'cap': c.rect(4, 2, 8, 1, 3); c.rect(5, 1, 6, 1, 3)
    elif acc == 'lamp': c.ellipse(13, 10, 2, 2, 0); c.px(13, 10, 1)
def sprite16(spec, frame=0):
    c = Canvas(16, 16, 0)
    SPR[spec['sp']](c)
    acc16(c, spec.get('acc'))
    # outline
    base = c.copy(); c.outline(3)
    if frame: c = c.shift(0, 0)
    return c
def sprite16_pal(spec):
    a, b, d = spec['pal']
    return [0, a, b, d]

# ---------------------------------------------------------------- faces 32x32 (bg 3, head 0/1/2)
EYE = {  # species -> (eye_y, eye_dx, size)
 'kid': (14, 6, 2), 'wick': (15, 5, 2), 'crab': (13, 7, 2), 'anem': (15, 6, 2), 'urch': (15, 6, 2), 'eel': (12, 5, 2), 'jelly': (14, 6, 2),
 'kelp': (14, 6, 2), 'gull': (12, 6, 2), 'turtle': (14, 6, 2), 'clam': (17, 7, 2), 'angler': (14, 7, 3), 'golem': (13, 6, 2), 'bell': (14, 6, 2), 'moth': (14, 6, 2)}
def head(c, sp):
    if sp == 'kid': ell(c, 16, 16, 11, 11, 1); c.rect(6, 6, 20, 3, 2) if False else None
    elif sp == 'wick': ell(c, 16, 19, 9, 11, 2); ell(c, 16, 19, 6, 8, 1); c.line(16, 8, 16, 3, 2); ell(c, 16, 3, 2, 2, 0, hi=False)
    elif sp == 'crab': ell(c, 16, 18, 14, 9, 1); ell(c, 5, 7, 4, 4, 2); ell(c, 27, 7, 4, 4, 2); c.line(10, 10, 10, 6, 2); c.line(22, 10, 22, 6, 2)
    elif sp == 'anem':
        ell(c, 16, 20, 8, 9, 1)
        for i, x in enumerate((4, 9, 14, 19, 24)): c.rect(x, 3 + (i % 2) * 3, 4, 14 - (i % 2) * 3, 2); c.px(x + 1, 3 + (i % 2) * 3, 0)
    elif sp == 'urch':
        ell(c, 16, 17, 9, 9, 1)
        for a in range(0, 360, 20): c.line(16 + int(9 * math.cos(math.radians(a))), 17 + int(9 * math.sin(math.radians(a))), 16 + int(14 * math.cos(math.radians(a))), 17 + int(14 * math.sin(math.radians(a))), 2)
    elif sp == 'eel': ell(c, 16, 14, 8, 10, 1); c.rect(9, 20, 14, 10, 1); c.line(22, 6, 28, 2, 2); ell(c, 28, 3, 2, 2, 0, hi=False)
    elif sp == 'jelly': ell(c, 16, 13, 13, 10, 1); c.rect(3, 13, 26, 4, 1); [c.rect(x, 18, 2, 10, 2) for x in (5, 11, 17, 23)]
    elif sp == 'kelp':
        for x0 in (6, 16, 24):
            for y in range(0, 32): c.px(x0 + int(2 * math.sin(y / 3.0 + x0)), y, 2); c.px(x0 + 1 + int(2 * math.sin(y / 3.0 + x0)), y, 2)
        ell(c, 16, 15, 8, 9, 1)
    elif sp == 'gull': ell(c, 14, 16, 10, 11, 1); c.rect(22, 11, 8, 4, 2); c.rect(22, 11, 8, 1, 0)
    elif sp == 'turtle': ell(c, 16, 17, 11, 10, 1); c.rect(8, 3, 16, 4, 2); ell(c, 16, 4, 8, 3, 2)
    elif sp == 'clam': ell(c, 16, 20, 14, 8, 2); ell(c, 16, 20, 11, 5, 0); ell(c, 16, 10, 7, 7, 1)
    elif sp == 'angler': ell(c, 14, 17, 12, 10, 1); c.line(10, 7, 14, 1, 2); c.line(14, 1, 26, 1, 2); ell(c, 27, 3, 3, 3, 0, hi=False); c.rect(20, 20, 9, 3, 2)
    elif sp == 'golem': rr(c, 6, 4, 20, 22, 1); c.rect(6, 4, 20, 2, 0)
    elif sp == 'bell': ell(c, 16, 14, 12, 11, 1); c.rect(4, 17, 24, 6, 1); c.rect(14, 24, 4, 4, 2)
    elif sp == 'moth': ell(c, 16, 17, 6, 10, 2); ell(c, 7, 12, 6, 8, 1); ell(c, 25, 12, 6, 8, 1)
def face32(spec, emo):
    """emo: 0 neutral 1 happy 2 sad 3 angry 4 surprised"""
    c = Canvas(32, 32, 3)
    sp = spec['sp']
    head(c, sp)
    ey, dx, sz = EYE.get(sp, (14, 6, 2)); cx = 16
    if sp in ('gull',): cx = 14
    for s in (-1, 1):
        x = cx + s * dx
        if emo == 1: c.px(x - 2, ey + 1, 3); c.px(x - 1, ey, 3); c.px(x, ey, 3); c.px(x + 1, ey, 3); c.px(x + 2, ey + 1, 3)
        elif emo == 4: c.ellipse(x, ey, 2, 3, 3); c.px(x, ey, 0)
        else:
            c.rect(x - 1, ey - 1, sz, sz + 1, 3); c.px(x - 1, ey - 1, 0)
        if emo == 2: c.line(x - s * 3, ey - 4 - (0 if s < 0 else 0), x + s * 2, ey - 6 + (0), 3) if False else (c.px(x - 2, ey - 4 + (1 if s > 0 else 0), 3), c.px(x - 1, ey - 5, 3), c.px(x, ey - 5, 3), c.px(x + 1, ey - 4, 3), c.px(x + 2, ey - 3 + (0 if s < 0 else 0), 3))
        if emo == 3: c.line(x - 3, ey - 5 + (0 if s > 0 else 3), x + 3, ey - 5 + (3 if s > 0 else 0), 3)
    my = ey + 7
    if sp == 'clam': my = 20
    if sp == 'gull': 
        my = ey + 8
    if emo == 0: c.rect(cx - 2, my, 5, 1, 3)
    elif emo == 1: c.rect(cx - 3, my, 7, 1, 3); c.px(cx - 4, my - 1, 3); c.px(cx + 4, my - 1, 3)
    elif emo == 2: c.rect(cx - 2, my, 5, 1, 3); c.px(cx - 3, my + 1, 3); c.px(cx + 3, my + 1, 3)
    elif emo == 3: [c.px(cx - 3 + i, my + (i % 2), 3) for i in range(7)]
    else: c.ellipse(cx, my, 2, 2, 3)
    acc = spec.get('acc')
    if acc == 'hat': c.rect(6, 2, 20, 4, 3); c.rect(10, 0, 12, 3, 3); c.rect(6, 5, 20, 1, 2)
    elif acc == 'crown': [c.rect(8 + i * 5, 1, 3, 5, 0) for i in range(4)]; c.rect(8, 5, 18, 2, 0)
    elif acc == 'glasses': c.frame(cx - dx - 4, ey - 3, 8, 7, 3); c.frame(cx + dx - 4, ey - 3, 8, 7, 3); c.rect(cx - 2, ey, 4, 1, 3)
    elif acc == 'scarf': c.rect(6, 27, 20, 4, 0); c.rect(6, 27, 20, 1, 1)
    elif acc == 'cap': c.rect(7, 4, 18, 2, 3); c.rect(9, 2, 14, 3, 3)
    elif acc == 'apron': c.rect(8, 29, 16, 3, 0)
    elif acc == 'lamp': ell(c, 27, 26, 4, 4, 0, hi=False); c.px(27, 26, 1)
    return c
def face_pal(spec):
    a, b, d = spec['pal']
    return [a, b, d, '#0C0B14']
EMOS = ['neutral', 'happy', 'sad', 'angry', 'surprised']

# ---------------------------------------------------------------- big enemy art (bg 3; 0 highlight 1 body 2 shade)
def big_dustcrab(t):
    c = Canvas(48, 32, 3)
    ell(c, 24, 20, 16, 9, 1); lift = 4 if t else 0
    ell(c, 6, 9 - lift, 5, 5, 2); ell(c, 42, 9 - lift, 5, 5, 2); c.line(8, 13 - lift, 12, 18, 2); c.line(40, 13 - lift, 36, 18, 2)
    c.rect(6, 7 - lift, 2, 2, 3) if False else None
    for x in (11, 17, 31, 37): c.rect(x, 27, 2, 4, 2); c.rect(x, 28 + t, 2, 2, 2)
    c.rect(18, 8, 2, 8, 2); c.rect(28, 8, 2, 8, 2); ell(c, 19, 8, 3, 3, 0, hi=False); ell(c, 29, 8, 3, 3, 0, hi=False); c.px(19, 8, 3); c.px(29, 8, 3)
    c.rect(20, 23, 8, 1, 2); return c
def big_spitwink(t):
    c = Canvas(48, 40, 3)
    ell(c, 24, 26, 18, 10, 1); ell(c, 14, 14, 5, 5, 0, rim=2); ell(c, 34, 14, 5, 5, 0, rim=2); c.px(14, 14 + t, 3); c.px(34, 14 + t, 3); c.rect(13, 14, 3, 2, 3) if False else None
    c.rect(34, 29, 12, 3 + 3 * t, 2); c.rect(36, 30, 8, 1 + 3 * t, 3); c.rect(6, 34, 8, 3, 2); c.rect(30, 34, 10, 3, 2)
    for x in range(10, 30, 5): c.px(x, 22, 2); c.px(x + 1, 24, 2)
    return c
def big_lampfly(t):
    c = Canvas(40, 40, 3); w = 3 if t else 0
    ell(c, 20, 22, 4, 10, 2); ell(c, 20, 30, 5, 6, 0, hi=False); ell(c, 20, 30, 3, 4, 1, hi=False, rim=0)
    ell(c, 9, 14 - w, 8, 10 + w, 1); ell(c, 31, 14 - w, 8, 10 + w, 1); ell(c, 20, 12, 5, 5, 1)
    c.px(18, 11, 3); c.px(22, 11, 3); c.line(18, 7, 14, 2 + w, 2); c.line(22, 7, 26, 2 + w, 2); return c
def big_barnabee(t):
    c = Canvas(40, 40, 3)
    for cx, cy, r in ((10, 28, 7), (30, 28, 7), (20, 20, 10), (20, 32, 6)):
        c.ellipse(cx, cy, r, r, 2); c.ellipse(cx, cy, r - 1, r - 2, 1); c.rect(cx - 2, cy - r + 2, 4, 2, 0)
    c.rect(14, 19, 12, 2 + 2 * t, 3); c.px(16, 16, 0); c.px(24, 16, 0); c.rect(15, 15, 2, 2, 3); c.rect(23, 15, 2, 2, 3) if False else None
    return c
def big_rustmite(t):
    c = Canvas(48, 40, 3); b = 1 if t else 0
    c.rect(10, 8 + b, 28, 24, 2); c.rect(11, 9 + b, 26, 22, 1); c.rect(10, 8 + b, 28, 3, 0); c.rect(14, 14 + b, 3, 8, 2); c.rect(30, 20 + b, 4, 6, 2)
    ell(c, 24, 8 + b, 12, 3, 0, hi=False)
    ell(c, 24, 34, 12, 5, 2); c.rect(8, 30, 6, 5, 2); c.rect(34, 30, 6, 5, 2); c.px(20, 36, 3)
    c.rect(18, 20 + b, 3, 3, 3); c.rect(28, 20 + b, 3, 3, 3); return c
def big_brinebell(t):
    c = Canvas(40, 48, 3); s = 1 if t else -1
    ell(c, 20, 20, 15, 14, 1); c.rect(5, 20, 31, 12, 1); c.rect(4, 31, 33, 3, 2)
    for x in (9, 18, 27): c.rect(x, 4, 3, 4, 0)
    ell(c, 20 + 2 * s, 40, 4, 4, 2); c.rect(19 + 2 * s, 32, 2, 4, 2)
    c.rect(14, 17, 3, 4, 3); c.rect(25, 17, 3, 4, 3); c.rect(17, 25, 7, 1 + t, 3); return c
def big_saltling(t):
    c = Canvas(40, 48, 3)
    rr(c, 10, 4, 20, 16, 1); rr(c, 7, 20, 26, 20, 1); rr(c, 0, 22 - 2 * t, 8, 14, 2); rr(c, 32, 22 + 2 * t, 8, 14, 2); rr(c, 10, 40, 8, 8, 2); rr(c, 22, 40, 8, 8, 2)
    c.rect(14, 10, 4, 4, 3); c.rect(23, 10, 4, 4, 3); c.rect(16, 15, 9, 1, 3)
    for x, y in ((12, 26), (22, 30), (28, 24)): c.px(x, y, 0); c.px(x + 1, y, 0)
    return c
def big_gloamfin(t):
    c = Canvas(48, 40, 3)
    ell(c, 22, 26, 17, 11, 1); c.rect(34, 24, 12, 5 + t * 2, 2); ell(c, 14, 22, 4, 4, 0, hi=False); c.px(13, 22, 3)
    c.line(14, 16, 18, 4, 2); c.line(18, 4, 34, 4 + t, 2); ell(c, 36, 6 + t, 4, 4, 0, hi=False); ell(c, 36, 6 + t, 2, 2, 1, hi=False, rim=0)
    for x in range(32, 46, 3): c.px(x, 26, 0); c.px(x + 1, 28 + t, 0)
    c.rect(10, 34, 5, 4, 2); c.rect(26, 35, 8, 3, 2); return c
def big_paperclam(t):
    c = Canvas(48, 40, 3)
    ell(c, 24, 28, 20, 9, 2); ell(c, 24, 28, 16, 6, 0, hi=False); ell(c, 24, 14 - t, 9, 8, 1)
    c.rect(20, 12 - t, 2, 3, 3); c.rect(27, 12 - t, 2, 3, 3); c.rect(21, 18 - t, 7, 1, 3)
    c.rect(38, 4, 7, 9, 0); c.frame(38, 4, 7, 9, 2); c.rect(40, 7 + t, 3, 1, 3); return c
def big_echo(t):
    c = Canvas(40, 48, 3)
    ell(c, 20, 18, 10, 11, 1); c.rect(10, 22, 20, 22, 1)
    for x in range(10, 30, 5): c.rect(x, 44 - 2 * ((x // 5 + t) % 2), 3, 4, 3)
    c.rect(14, 15, 4, 5, 3); c.rect(23, 15, 4, 5, 3); c.rect(16, 26, 9, 1, 3)
    ell(c, 20, 34, 4, 4, 0, hi=False); c.px(20, 34, 1)
    return c
def big_ruffle(t):
    c = Canvas(56, 48, 3); s = 2 if t else 0
    ell(c, 28, 34, 12, 13, 1)
    for i, x in enumerate(range(3, 51, 6)):
        h = 20 - abs(i - 4) * 2; c.rect(x, 8 + abs(i - 4) * 2 + (s if i % 2 else 0), 5, h, 2); c.rect(x + 1, 9 + abs(i - 4) * 2 + (s if i % 2 else 0), 2, h - 3, 0)
    c.rect(21, 28, 4, 5, 3); c.rect(31, 28, 4, 5, 3); c.rect(23, 38, 10, 2 + t, 3); c.rect(22, 20, 12, 2, 0)
    return c
def big_brass(t):
    c = Canvas(64, 48, 3); up = 6 if t else 0
    ell(c, 32, 30, 20, 12, 1); ell(c, 8, 16 - up, 7, 7, 2); ell(c, 56, 16 - up, 7, 7, 2); c.line(12, 21 - up, 20, 28, 2); c.line(52, 21 - up, 44, 28, 2)
    c.rect(20, 8, 24, 4, 0); c.rect(24, 3, 16, 5, 0); c.frame(24, 3, 16, 9, 2); c.rect(30, 5, 4, 2, 2)
    c.rect(24, 22, 5, 5, 3); c.rect(37, 22, 5, 5, 3); c.rect(26, 33, 12, 2 + t, 3)
    for x in (14, 24, 40, 50): c.rect(x, 41, 3, 6, 2)
    c.rect(26, 40, 12, 3, 0); return c
def big_choir(t):
    c = Canvas(64, 48, 3)
    for i, x in enumerate((2, 24, 46)):
        rr(c, x + 3, 2 + 4 * (i == 1) - t * (i % 2), 14, 14, 1); rr(c, x, 18 + 4 * (i == 1), 20, 26 - 4 * (i == 1), 1)
        c.rect(x + 6, 7 + 4 * (i == 1), 3, 3, 3); c.rect(x + 12, 7 + 4 * (i == 1), 3, 3, 3); c.ellipse(x + 10, 13 + 4 * (i == 1), 2, 2 + t, 3)
    return c
def big_lumen(t):
    c = Canvas(64, 48, 3)
    ell(c, 30, 30, 24, 14, 1); c.rect(46, 28, 16, 8 + t * 3, 2); ell(c, 18, 24, 5, 5, 0, hi=False); c.px(17, 24, 3)
    c.line(18, 17, 24, 4, 2); c.line(24, 4, 44, 3, 2)
    ell(c, 46, 4 + t, 5, 5, 0, hi=False); ell(c, 46, 4 + t, 3, 3, 1, hi=False, rim=0); ell(c, 46, 4 + t, 1, 1, 0, hi=False, rim=0)
    for x in range(48, 62, 3): c.px(x, 30, 0); c.px(x + 1, 33 + t, 0)
    for x in (10, 24, 38): c.rect(x, 42, 6, 5, 2)
    return c
def big_quill(t):
    c = Canvas(64, 48, 3)
    ell(c, 32, 34, 26, 11, 2); ell(c, 32, 34, 22, 8, 0, hi=False); ell(c, 32, 20 - t, 12, 11, 1)
    c.ellipse(32, 20 - t, 12, 11, 2) if False else None
    c.frame(24, 17 - t, 7, 6, 3); c.frame(34, 17 - t, 7, 6, 3); c.rect(31, 19 - t, 4, 1, 3); c.rect(29, 27 - t, 7, 1, 3)
    c.rect(50, 2, 10, 14, 0); c.frame(50, 2, 10, 14, 2); [c.rect(52, 5 + i * 3, 6, 1, 3) for i in range(4)]
    c.line(54, 30, 62, 22 - 3 * t, 2); return c
def big_marrow(t, phase=0):
    c = Canvas(64, 48, 3)
    ell(c, 32, 28, 22, 15, 2); ell(c, 32, 26, 17, 11, 1)
    for a in range(0, 360, 60): c.px(32 + int(11 * math.cos(math.radians(a))), 26 + int(8 * math.sin(math.radians(a))), 0)
    ell(c, 8, 24, 7, 7, 1); c.px(6, 23, 3); c.px(10, 23, 3); c.rect(6, 28, 5, 1, 3)
    c.rect(30, 2, 3, 9, 2); gl = 6 + 2 * t + phase
    ell(c, 31, 6, gl // 2 + 1, gl // 2 + 1, 0, hi=False); c.px(31, 6, 1)
    for x in (14, 26, 38, 48): c.rect(x, 40, 5, 7, 2)
    if phase >= 1:
        for x, y in ((4, 4), (58, 6), (6, 40), (58, 42)): ell(c, x, y, 2, 2, 0, hi=False)
    if phase >= 2:
        c.line(0, 0, 63, 47, 2) if False else None
        for i in range(6): c.px(10 + i * 9, 12 + (i * 5) % 9, 0)
    return c
def big_skiff(t):
    c = Canvas(40, 40, 3)
    ell(c, 18, 24, 12, 10, 1); c.px(13, 22, 3); c.rect(24, 24, 10, 3 + t, 2)
    c.line(12, 15, 17, 4, 2); c.line(17, 4, 30, 3, 2); ell(c, 31, 4 + t, 3, 3, 0, hi=False); c.rect(8, 33, 4, 5, 2); c.rect(22, 33, 4, 5, 2)
    c.rect(11, 12, 14, 3, 3); return c
BIG = {'dustcrab': big_dustcrab, 'spitwink': big_spitwink, 'lampfly': big_lampfly, 'barnabee': big_barnabee, 'rustmite': big_rustmite,
       'brinebell': big_brinebell, 'saltling': big_saltling, 'gloamfin': big_gloamfin, 'paperclam': big_paperclam, 'echo': big_echo,
       'ruffle': big_ruffle, 'brass': big_brass, 'choir': big_choir, 'lumen': big_lumen, 'quill': big_quill, 'marrow': lambda t: big_marrow(t, 0),
       'marrow2': lambda t: big_marrow(t, 1), 'marrow3': lambda t: big_marrow(t, 2), 'skiff': big_skiff}

def enemy_chunk(name, pal):
    f0 = BIG[name](0); f1 = BIG[name](1)
    w, h = f0.w // 8, f0.h // 8
    data = bytes([w, h, 2, 0]) + b'\0' * 4 + pal_bytes(pal) + f0.tiles() + f1.tiles()
    return data, (w, h)
