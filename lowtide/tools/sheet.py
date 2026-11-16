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
def main(out):
    os.makedirs(out, exist_ok=True)
    import cast
    from world import W
    names = list(W.cast_.items())
    # sprites + faces
    cols = 6; cw, ch = 112, 190
    rowsn = (len(names) + cols - 1) // cols
    sheet = [[(24, 22, 40)] * (cols * cw) for _ in range(rowsn * ch)]
    for i, (n, spec) in enumerate(names):
        x0 = (i % cols) * cw + 4; y0 = (i // cols) * ch + 4
        label(sheet, n, x0, y0)
        sp = AC.sprite16(spec); paste(sheet, render(sp, AC.sprite16_pal(spec), 3, True), x0, y0 + 12)
        for e in (0, 1, 2, 3):
            f = AC.face32(spec, e); fp = AC.face_pal(spec)
            paste(sheet, render(f, fp, 1), x0 + e * 0, y0 + 12)  # placeholder (overwritten below)
        f0 = AC.face32(spec, 0); paste(sheet, render(f0, AC.face_pal(spec), 2), x0, y0 + 64)
        f1 = AC.face32(spec, 3); paste(sheet, render(f1, AC.face_pal(spec), 1), x0 + 70, y0 + 64)
    save_png(os.path.join(out, 'sheet_characters.png'), sheet)
    # enemies
    en = list(AC.BIG.items()); cols = 5; cw, ch = 200, 150
    rowsn = (len(en) + cols - 1) // cols
    sheet = [[(24, 22, 40)] * (cols * cw) for _ in range(rowsn * ch)]
    for i, (n, fn) in enumerate(en):
        x0 = (i % cols) * cw + 4; y0 = (i // cols) * ch + 4
        label(sheet, n, x0, y0)
        paste(sheet, render(fn(0), ['#F4EBD0', '#9AA0B0', '#4C4A68', '#0C0B14'], 2), x0, y0 + 12)
    save_png(os.path.join(out, 'sheet_enemies.png'), sheet)
if __name__ == '__main__': main(sys.argv[1])
