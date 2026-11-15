#!/usr/bin/env python3
"""Generates GBDK sources (assets.c/h, levels.c/h, music.c) + ASCII level dumps from the shared generators."""
import os, math, random, sys
sys.path.insert(0, os.path.dirname(__file__))
import art, levels

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "gb", "src")
SHARED = os.path.join(ROOT, "shared", "levels")
os.makedirs(SRC, exist_ok=True); os.makedirs(SHARED, exist_ok=True)

def rgb(r, g, b):  # 8-bit -> GBC 15-bit
    return ((b >> 3) << 10) | ((g >> 3) << 5) | (r >> 3)

# BG palettes per theme: [terrain(4), coin(4), hazard(4), text(4), star(4)]
THEME_PAL = {
    "forest": [(200, 236, 255), (110, 200, 90), (60, 130, 60), (40, 60, 40)],
    "desert": [(255, 240, 200), (245, 215, 120), (205, 150, 70), (110, 70, 40)],
    "city":   [(200, 215, 245), (150, 175, 215), (90, 110, 160), (30, 40, 80)],
    "castle": [(70, 40, 100), (130, 90, 170), (90, 60, 130), (20, 10, 40)],
}
COIN = [(0, 0, 0), (255, 235, 90), (230, 170, 20), (110, 60, 0)]
HAZ = [(0, 0, 0), (255, 120, 60), (220, 50, 40), (90, 10, 20)]

STAR = [(0, 0, 0), (255, 245, 150), (255, 210, 40), (120, 70, 0)]

def pal_line(cols):
    return ", ".join("0x%04X" % rgb(*c) for c in cols)

def bg_pal_for(theme):
    t = THEME_PAL[theme]
    pal0 = [t[0], t[1], t[2], t[3]]
    text = [t[0], t[3], t[3], t[3]]
    return [pal0, [t[0]] + COIN[1:], [t[0]] + HAZ[1:], text, [t[0]] + STAR[1:]]

SPR_PAL = [
    [(0, 0, 0), (255, 214, 170), (60, 120, 240), (40, 30, 70)],       # Pip
    [(0, 0, 0), (255, 255, 255), (170, 90, 200), (50, 20, 70)],       # enemies
    [(0, 0, 0), (255, 215, 80), (40, 170, 160), (30, 40, 70)],        # boss1 (beetle)
    [(0, 0, 0), (255, 255, 255), (232, 54, 90), (110, 20, 50)],       # hat / projectile
    [(0, 0, 0), (255, 220, 190), (110, 70, 170), (30, 20, 50)],       # boss2 (baron)
    [(0, 0, 0), (255, 245, 150), (255, 210, 40), (120, 70, 0)],       # star
]

# tile -> palette table
def tile_pal(i):
    name = art.BG_ORDER[i] if i < len(art.BG_ORDER) else None
    if name is None:
        return 3
    if name in ("coin",):
        return 1
    if name in ("lava", "spike"):
        return 2
    if name in ("star",):
        return 4
    if name in ("heart",):
        return 2
    return 0

SOLID = {"grass", "dirt", "brick", "sand", "sandfill", "bld", "window", "wall", "metal", "cityfill", "fill", "barrier"}
HAZARD = {"lava", "spike"}

def flat(tiles):
    out = []
    for t in tiles:
        out += art.tiles_2bpp(t)
    return out

def carr(name, data, typ="uint8_t", per=16, fmt="0x%02X"):
    lines = []
    for i in range(0, len(data), per):
        lines.append("    " + ", ".join(fmt % v for v in data[i:i + per]))
    return "const %s %s[] = {\n%s\n};\n" % (typ, name, ",\n".join(lines))

def gen_assets():
    bg = flat(art.bg_tiles())
    spr_tiles, spr_idx = art.sprite_layout()
    sp = flat(spr_tiles)
    h = ["#ifndef ASSETS_H", "#define ASSETS_H", "#include <stdint.h>", ""]
    h.append("#define NUM_BG_TILES %d" % art.NUM_BG_TILES)
    h.append("#define NUM_SPR_TILES %d" % len(spr_tiles))
    h.append("#define FONT_BASE %d" % art.FONT_BASE)
    h.append("#define FONT_CHARS \"%s\"" % art.FONT_CHARS.replace("\\", "\\\\").replace("\"", "\\\""))
    for n, i in art.BG_INDEX.items():
        h.append("#define T_%s %d" % (n.upper(), i))
    for n, i in spr_idx.items():
        h.append("#define S_%s %d" % (n.upper(), i))
    h.append("extern const uint8_t bg_tiles[];")
    h.append("extern const uint8_t spr_tiles[];")
    h.append("extern const uint8_t tile_class[NUM_BG_TILES];   /* bit0 solid, bit1 hazard, bit2 coin, bit3 star */")
    h.append("extern const uint8_t tile_palette[NUM_BG_TILES];")
    h.append("extern const uint16_t bg_palettes[4][5 * 4];")
    h.append("extern const uint16_t spr_palettes[6 * 4];")
    h.append("#endif")
    open(os.path.join(SRC, "assets.h"), "w").write("\n".join(h) + "\n")
    c = ['#include "assets.h"', ""]
    c.append(carr("bg_tiles", bg))
    c.append(carr("spr_tiles", sp))
    cls = []
    for i in range(art.NUM_BG_TILES):
        v = 0
        if i < len(art.BG_ORDER):
            n = art.BG_ORDER[i]
            if n in SOLID: v |= 1
            if n in HAZARD: v |= 2
            if n == "coin": v |= 4
            if n == "star": v |= 8
        cls.append(v)
    c.append(carr("tile_class", cls, per=32, fmt="%d"))
    c.append(carr("tile_palette", [tile_pal(i) for i in range(art.NUM_BG_TILES)], per=32, fmt="%d"))
    c.append("const uint16_t bg_palettes[4][5 * 4] = {")
    for th in ["forest", "desert", "city", "castle"]:
        c.append("    { " + ", ".join(pal_line(p) for p in bg_pal_for(th)) + " },")
    c.append("};")
    c.append("const uint16_t spr_palettes[6 * 4] = { " + ", ".join(pal_line(p) for p in SPR_PAL) + " };")
    open(os.path.join(SRC, "assets.c"), "w").write("\n".join(c) + "\n")

def gen_levels():
    lvls = levels.all_levels()
    h = ["#ifndef LEVELS_H", "#define LEVELS_H", "#include <stdint.h>", "#define NUM_LEVELS %d" % len(lvls),
         "typedef struct { uint8_t type, x, y; } EnemySpawn;",
         "typedef struct { const char *name; const uint8_t *rle; uint16_t rle_len; uint8_t w; uint8_t theme; uint8_t boss; uint8_t music; uint8_t n_enemies; const EnemySpawn *enemies; uint8_t arena_x0, arena_x1; uint8_t goal_x, goal_y; uint8_t coins; } LevelInfo;",
         "extern const LevelInfo level_info[NUM_LEVELS];", "#endif"]
    open(os.path.join(SRC, "levels.h"), "w").write("\n".join(h) + "\n")
    c = ['#include "levels.h"', '#include "assets.h"', ""]
    for i, lv in enumerate(lvls):
        r = lv.rle()
        c.append(carr("lvl%d_rle" % i, r, per=24, fmt="%d"))
        en = ", ".join("{%d,%d,%d}" % e for e in lv.enemies) or "{0,0,0}"
        c.append("static const EnemySpawn lvl%d_en[] = { %s };" % (i, en))
        with open(os.path.join(SHARED, "level%d.txt" % (i + 1)), "w") as f:
            f.write("# %s  (theme=%s w=%d)\n" % (lv.spec["name"], lv.spec["theme"], lv.w))
            f.write(lv.ascii() + "\n")
    c.append("const LevelInfo level_info[NUM_LEVELS] = {")
    th_idx = {"forest": 0, "desert": 1, "city": 2, "castle": 3}
    for i, lv in enumerate(lvls):
        s = lv.spec
        c.append('    { "%s", lvl%d_rle, %d, %d, %d, %d, %d, %d, lvl%d_en, %d, %d, %d, %d, %d },' % (
            s["name"], i, len(lv.rle()), lv.w, th_idx[s["theme"]], s["boss"], s["music"], len(lv.enemies), i,
            lv.arena[0], lv.arena[1], lv.goal[0], lv.goal[1], min(lv.coins, 255)))
    c.append("};")
    open(os.path.join(SRC, "levels.c"), "w").write("\n".join(c) + "\n")
    return lvls

# ------------------------------------------------------------ music
def midi_freq_reg(m):
    f = 440.0 * 2 ** ((m - 69) / 12.0)
    return max(0, min(2047, int(round(2048 - 131072.0 / f))))

SCALES = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10], "dorian": [0, 2, 3, 5, 7, 9, 10], "harm": [0, 2, 3, 5, 7, 8, 11]}
TRACKS = [("major", 62, [0, 5, 3, 4], 11), ("dorian", 57, [0, 1, 0, 6], 22), ("major", 60, [0, 3, 4, 3], 33), ("harm", 52, [0, 5, 6, 4], 44)]

def gen_music():
    out = ['#include "music_data.h"', ""]
    hdr = ["#ifndef MUSIC_DATA_H", "#define MUSIC_DATA_H", "#include <stdint.h>", "#define NOTE_MIN 36", "#define NOTE_COUNT 61", "#define TRACK_STEPS 64", "#define NUM_TRACKS %d" % len(TRACKS),
           "extern const uint16_t note_freq[NOTE_COUNT];", "extern const uint8_t track_lead[NUM_TRACKS][TRACK_STEPS];", "extern const uint8_t track_bass[NUM_TRACKS][TRACK_STEPS];", "#endif"]
    open(os.path.join(SRC, "music_data.h"), "w").write("\n".join(hdr) + "\n")
    out.append("const uint16_t note_freq[NOTE_COUNT] = { " + ", ".join(str(midi_freq_reg(36 + i)) for i in range(61)) + " };")
    leads, basses = [], []
    for scale, root, prog, seed in TRACKS:
        rng = random.Random(seed)
        sc = SCALES[scale]
        def deg(d, base):
            return base + sc[d % 7] + 12 * (d // 7)
        motif = []
        d = 4
        for i in range(8):
            d = max(0, min(9, d + rng.randint(-2, 2)))
            motif.append(d)
        lead, bass = [], []
        for bar in range(4):
            chord = prog[bar % 4]
            for st in range(16):
                i = bar * 16 + st
                if st in (0, 3, 6, 8, 10, 12, 14):
                    k = [0, 3, 6, 8, 10, 12, 14].index(st)
                    m = deg(motif[(k + bar * 2) % 8] + (2 if bar == 2 else 0), root + 12)
                    lead.append(m - 36 + 1)
                else:
                    lead.append(0)
                if st % 4 == 0:
                    bass.append(deg(chord, root - 12) - 36 + 1)
                else:
                    bass.append(0)
        leads.append(lead); basses.append(bass)
    out.append("const uint8_t track_lead[NUM_TRACKS][TRACK_STEPS] = {\n" + ",\n".join("  { " + ", ".join(map(str, l)) + " }" for l in leads) + "\n};")
    out.append("const uint8_t track_bass[NUM_TRACKS][TRACK_STEPS] = {\n" + ",\n".join("  { " + ", ".join(map(str, l)) + " }" for l in basses) + "\n};")
    open(os.path.join(SRC, "music_data.c"), "w").write("\n".join(out) + "\n")

if __name__ == "__main__":
    gen_assets()
    lv = gen_levels()
    gen_music()
    print("generated for", len(lv), "levels")
