#!/usr/bin/env python3
"""Contact sheets: overworld sprites + faces + enemies, rendered with their real palettes. usage: sheet.py outdir"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'content'))
from pix import Canvas, save_png, hexc, c555_to_rgb
import art_chars as AC
import fontdata
def rgb(c): return c555_to_rgb(hexc(c))
def render(cv, pal, scale, transparent=False, bg=(24, 22, 40)):
    rows = []
    for y in range(cv.h):
        r = []
        for x in range(cv.w):
            v = cv.p[y][x]; col = bg if (transparent and v == 0) else rgb(pal[v])
            r += [col] * scale
        rows += [r] * scale
    return rows
def paste(sheet, rows, x0, y0):
    for j, r in enumerate(rows):
        for i, px in enumerate(r):
            if 0 <= y0 + j < len(sheet) and 0 <= x0 + i < len(sheet[0]): sheet[y0 + j][x0 + i] = px
def label(sheet, text, x, y):
    c = fontdata.text_canvas(text[:14], ink=1, bg=0)
    paste(sheet, render(c, ['#181628', '#E8E0C8', '#000', '#000'], 1), x, y)
ENEMY_ZONE = {'dustcrab': 0, 'spitwink': 1, 'lampfly': 1, 'ruffle': 1, 'skiff': 1, 'barnabee': 2, 'rustmite': 2, 'brass': 2, 'brinebell': 3, 'saltling': 3, 'choir': 3,
              'gloamfin': 4, 'lumen': 4, 'paperclam': 5, 'quill': 5, 'echo': 6, 'marrow': 6, 'marrow2': 6, 'marrow3': 6}
ZONE_NAMES = ['Prologue - Dry Shore', 'Zone 1 - Coralline (teal reef)', 'Zone 2 - Ballast Row (amber hull)', 'Zone 3 - Rimeton (salt ruins)', 'Zone 4 - Glimmer Hollow (violet depths)', 'Zone 5 - Archive of Tides', 'Finale - Hollow Light']
def zone_sheet(out, z, chars, enemies):
    cw, chh = 112, 100; cols = 6
    rows_c = (len(chars) + cols - 1) // cols
    ecw = 140
    h = 14 + max(rows_c, 1) * chh + (160 if enemies else 0)
    W_ = cols * cw
    sheet = [[(24, 22, 40)] * W_ for _ in range(h)]
    label(sheet, ZONE_NAMES[z], 4, 2)
    for i, (n, spec) in enumerate(chars):
        x0 = (i % cols) * cw + 4; y0 = 14 + (i // cols) * chh
        label(sheet, n, x0, y0)
        paste(sheet, render(AC.sprite16(spec), AC.sprite16_pal(spec), 3, True), x0, y0 + 10)
        for e in range(4):
            paste(sheet, render(AC.face32(spec, e), AC.face_pal(spec), 1), x0 + 52 + (e % 2) * 34, y0 + 10 + (e // 2) * 34)
    y0 = 14 + max(rows_c, 1) * chh + 4
    for i, n in enumerate(enemies):
        paste(sheet, render(AC.BIG[n](0), ['#F4EBD0', '#9AA0B0', '#4C4A68', '#0C0B14'], 2), 4 + i * ecw, y0 + 10)
        label(sheet, n, 4 + i * ecw, y0)
    save_png(os.path.join(out, f'zone{z}_sprites.png'), sheet)
def main(out):
    os.makedirs(out, exist_ok=True)
    import cast
    from world import W
    for z in range(7):
        chars = [(n, sp) for n, sp in W.cast_.items() if sp['zone'] == z]
        zone_sheet(out, z, chars, [n for n, zz in ENEMY_ZONE.items() if zz == z])
    print('wrote', out)
if __name__ == '__main__': main(sys.argv[1])
