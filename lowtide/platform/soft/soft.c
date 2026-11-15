#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../../core/lt.h"
#include "soft.h"
typedef uint32_t u32;
/* ------------------------------------------------------------------ chunks */
static const u8 *blob;
static u16 nchunks;
static u32 chunk_off(u16 id) { const u8 *e = blob + 2 + id * 6; return e[0] | (e[1] << 8) | (e[2] << 16) | ((u32)e[3] << 24); }
static u16 chunk_len(u16 id) { const u8 *e = blob + 2 + id * 6; return e[4] | (e[5] << 8); }
u16 plat_chunk_size(u16 id) { return id < nchunks ? chunk_len(id) : 0; }
u16 plat_chunk_read(u16 id, u16 off, u8 *dst, u16 n) {
    u16 sz;
    if (id >= nchunks) return 0;
    sz = chunk_len(id);
    if (off >= sz) return 0;
    if (n > sz - off) n = sz - off;
    memcpy(dst, blob + chunk_off(id) + off, n);
    return n;
}
u16 plat_chunk(u16 id, u8 *dst, u16 max) { return plat_chunk_read(id, 0, dst, max); }

/* ------------------------------------------------------------------ PPU */
static u8 tiles[256][64];
static u8 bgmap[32 * 32], bgattr[32 * 32], winmap[32 * 32], winattr[32 * 32];
static struct { s16 x, y; u8 tile, attr; } oam[40];
static u32 pal[16][4];
static u8 scx, scy, winy = 144;
static s8 fade_lv;
static u8 dmg_mode, dmg_bgp = 0xE4, dmg_obp0 = 0xE4, dmg_obp1 = 0xE4;
static u16 palsrc[16][4];
static u32 fb[SW * SH];
static const u32 dmg_shade[4] = {0xFFE8F0C8, 0xFFA0B878, 0xFF587050, 0xFF181C18};

static u32 rgb555(u16 c) {
    u32 r = c & 31, g = (c >> 5) & 31, b = (c >> 10) & 31;
    return 0xFF000000u | ((r * 255 / 31) << 16) | ((g * 255 / 31) << 8) | (b * 255 / 31);
}
void plat_init(void) {}
void plat_vsync(void) {}
void plat_lcd(u8 on) { (void)on; }
void plat_tiles(u8 first, const u8 *src, u8 count) {
    u16 t, r, x;
    for (t = 0; t < count; t++) {
        u8 *d = tiles[(u8)(first + t)];
        for (r = 0; r < 8; r++) {
            u8 lo = src[t * 16 + r * 2], hi = src[t * 16 + r * 2 + 1];
            for (x = 0; x < 8; x++) d[r * 8 + x] = (((hi >> (7 - x)) & 1) << 1) | ((lo >> (7 - x)) & 1);
        }
    }
}
void plat_bg_set(u8 x, u8 y, u8 t, u8 a) { bgmap[(y & 31) * 32 + (x & 31)] = t; bgattr[(y & 31) * 32 + (x & 31)] = a; }
void plat_win_set(u8 x, u8 y, u8 t, u8 a) { winmap[(y & 31) * 32 + (x & 31)] = t; winattr[(y & 31) * 32 + (x & 31)] = a; }
void plat_bg_fill(u8 x, u8 y, u8 w, u8 h, u8 t, u8 a) { u8 i, j; for (j = 0; j < h; j++) for (i = 0; i < w; i++) plat_bg_set(x + i, y + j, t, a); }
void plat_win_fill(u8 x, u8 y, u8 w, u8 h, u8 t, u8 a) { u8 i, j; for (j = 0; j < h; j++) for (i = 0; i < w; i++) plat_win_set(x + i, y + j, t, a); }
void plat_scroll(u8 x, u8 y) { scx = x; scy = y; }
void plat_win_y(u8 y) { winy = y; }
void plat_pal(u8 idx, const u16 *c4) { int i; for (i = 0; i < 4; i++) { palsrc[idx & 15][i] = c4[i]; pal[idx & 15][i] = rgb555(c4[i]); } }
void plat_dmg_pal(u8 b, u8 o0, u8 o1) { dmg_bgp = b; dmg_obp0 = o0; dmg_obp1 = o1; }
void plat_fade(s8 l) { fade_lv = l; }
void plat_spr(u8 i, s16 x, s16 y, u8 tile, u8 attr) { if (i < 40) { oam[i].x = x; oam[i].y = y; oam[i].tile = tile; oam[i].attr = attr; } }

static u32 colour(u8 pi, u8 idx, u8 obj, u8 obpsel) {
    if (dmg_mode) {
        u8 reg = obj ? (obpsel ? dmg_obp1 : dmg_obp0) : dmg_bgp;
        return dmg_shade[(reg >> (idx * 2)) & 3];
    }
    return pal[pi][idx];
}
static u32 shadec(u32 c) {
    if (fade_lv == 0) return c;
    {
        int l = fade_lv < 0 ? -fade_lv : fade_lv;
        int r = (c >> 16) & 255, g = (c >> 8) & 255, b = c & 255;
        int tgt = fade_lv > 0 ? 0 : 255;
        r += (tgt - r) * l / 8; g += (tgt - g) * l / 8; b += (tgt - b) * l / 8;
        return 0xFF000000u | (r << 16) | (g << 8) | b;
    }
}
static void render(void) {
    int x, y, i;
    static u8 bgcol[SW];
    for (y = 0; y < SH; y++) {
        for (x = 0; x < SW; x++) {
            u8 idx, pi, attr, t;
            u32 c;
            u8 mx = (u8)(x + scx), my = (u8)(y + scy);
            int off = (my >> 3) * 32 + (mx >> 3);
            int px = mx & 7, py = my & 7;
            int usewin = (y >= winy);
            if (usewin) {
                int wy = y - winy;
                if (wy < 32 * 8) {
                    off = (wy >> 3) * 32 + (x >> 3);
                    px = x & 7; py = wy & 7;
                    t = winmap[off]; attr = winattr[off];
                } else { t = 1; attr = 0; }
            } else { t = bgmap[off]; attr = bgattr[off]; }
            if (attr & 0x20) px = 7 - px;
            if (attr & 0x40) py = 7 - py;
            idx = tiles[t][py * 8 + px];
            pi = attr & 7;
            c = colour(pi, idx, 0, 0);
            fb[y * SW + x] = c;
            bgcol[x] = usewin ? 99 : idx;
        }
        if (y < winy) {
            for (i = 39; i >= 0; i--) {
                int sy = y - oam[i].y;
                if (sy < 0 || sy >= 8) continue;
                for (x = 0; x < 8; x++) {
                    int sx = oam[i].x + x, px = x, py = sy;
                    u8 idx;
                    if (sx < 0 || sx >= SW) continue;
                    if (oam[i].attr & 0x20) px = 7 - px;
                    if (oam[i].attr & 0x40) py = 7 - py;
                    idx = tiles[oam[i].tile][py * 8 + px];
                    if (!idx) continue;
                    fb[y * SW + sx] = colour(8 + (oam[i].attr & 7), idx, 1, (oam[i].attr >> 4) & 1);
                }
            }
        }
        for (x = 0; x < SW; x++) fb[y * SW + x] = shadec(fb[y * SW + x]);
    }
}

/* ------------------------------------------------------------------ audio synth */
typedef struct {
    int on;
    u16 period; u8 env, duty, vol, estep, etimer, dirup;
    u32 phase; /* 16.16-ish accumulator in samples */
    u16 lfsr; u8 noisep;
} Chan;
static Chan ch[4];
static u8 wave[32];

void plat_snd_trig(u8 c, u16 period, u8 env, u8 duty) {
    Chan *k = &ch[c & 3];
    SOFT_LOCK();
    k->on = 1; k->period = period; k->env = env; k->duty = duty & 3;
    k->vol = env >> 4; k->dirup = (env >> 3) & 1; k->estep = env & 7; k->etimer = 0;
    if (c == 2) { k->vol = (env >> 5) & 3; } /* wave: 0 mute,1 100%,2 50%,3 25% */
    if (c == 3) { k->lfsr = 0x7FFF; k->noisep = (u8)period; }
    SOFT_UNLOCK();
}
void plat_snd_off(u8 c) { SOFT_LOCK(); ch[c & 3].on = 0; SOFT_UNLOCK(); }
void plat_snd_period(u8 c, u16 p) { SOFT_LOCK(); ch[c & 3].period = p; SOFT_UNLOCK(); }
void plat_snd_wave(const u8 *w) {
    int i;
    SOFT_LOCK();
    for (i = 0; i < 16; i++) { wave[i * 2] = w[i] >> 4; wave[i * 2 + 1] = w[i] & 15; }
    SOFT_UNLOCK();
}
int soft_rate = 44100;
float soft_master = 0.5f;
void soft_synth(float *out, int n) {
    static u32 envacc;
    int i;
    for (i = 0; i < n; i++) {
        float mix = 0;
        int c;
        /* envelopes tick at 64 Hz */
        envacc += 64;
        if (envacc >= AUDIO_RATE) {
            envacc -= AUDIO_RATE;
            for (c = 0; c < 4; c++) if (c != 2 && ch[c].on && ch[c].estep) {
                if (++ch[c].etimer >= ch[c].estep) {
                    ch[c].etimer = 0;
                    if (ch[c].dirup) { if (ch[c].vol < 15) ch[c].vol++; }
                    else if (ch[c].vol > 0) ch[c].vol--;
                }
            }
        }
        for (c = 0; c < 4; c++) {
            Chan *k = &ch[c];
            float s = 0;
            if (!k->on) continue;
            if (c < 2) {
                float f = 131072.0f / (2048 - (k->period & 2047));
                static const float duties[4] = {0.125f, 0.25f, 0.5f, 0.75f};
                k->phase += (u32)(f * 65536.0f / AUDIO_RATE * 8.0f);
                s = ((k->phase & 0x7FFFF) / 524288.0f) < duties[k->duty] ? 1.0f : -1.0f;
                s *= k->vol / 15.0f;
            } else if (c == 2) {
                float f = 65536.0f / (2048 - (k->period & 2047));
                int sh, smp;
                k->phase += (u32)(f * 65536.0f / AUDIO_RATE * 32.0f);
                smp = wave[(k->phase >> 16) & 31];
                sh = k->vol == 0 ? 4 : k->vol - 1;
                s = ((smp >> sh) / 7.5f) - 1.0f;
                if (k->vol == 0) s = 0;
                s *= 0.9f;
            } else {
                int sh = k->noisep >> 4, r = k->noisep & 7;
                float f = 524288.0f / (r ? r : 0.5f) / (float)(1 << (sh + 1));
                u32 inc = (u32)(f * 65536.0f / AUDIO_RATE);
                u32 old = k->phase;
                k->phase += inc;
                {
                    u32 steps = (k->phase >> 16) - (old >> 16);
                    while (steps--) {
                        u16 x = (k->lfsr ^ (k->lfsr >> 1)) & 1;
                        k->lfsr = (k->lfsr >> 1) | (x << 14);
                        if (k->noisep & 8) k->lfsr = (k->lfsr & ~0x40) | (x << 6);
                    }
                }
                s = (k->lfsr & 1) ? -1.0f : 1.0f;
                s *= k->vol / 15.0f;
            }
            mix += s;
        }
        out[i] = mix * 0.18f * soft_master;
    }
}
/* offline render for tests: render N frames' worth after the caller drives audio */


/* ---- save storage buffer ---- */
static u8 sram[SOFT_SRAM_SZ];
static int sram_dirty;
void soft_sram_load(const u8 *src, int n) { memset(sram, 0xFF, sizeof sram); if (src) memcpy(sram, src, n < SOFT_SRAM_SZ ? n : SOFT_SRAM_SZ); }
const u8 *soft_sram_ptr(void) { return sram; }
int soft_sram_take_dirty(void) { int d = sram_dirty; sram_dirty = 0; return d; }
void plat_sram_read(u16 off, u8 *dst, u16 n) { if (off + n <= SOFT_SRAM_SZ) memcpy(dst, sram + off, n); }
void plat_sram_write(u16 off, const u8 *src, u16 n) { if (off + n <= SOFT_SRAM_SZ) { memcpy(sram + off, src, n); sram_dirty = 1; } }
void soft_blob(const unsigned char *b) { blob = b; nchunks = (u16)(b[0] | (b[1] << 8)); }
void soft_set_dmg(int on) { dmg_mode = on; }
const u32 *soft_fb(void) { return fb; }
void soft_render(void) { render(); }
/* tiny PNG writer (stored deflate) */
static u32 crctab[256];
static void crcinit(void) { u32 n, k; for (n = 0; n < 256; n++) { u32 c = n; for (k = 0; k < 8; k++) c = (c & 1) ? 0xEDB88320u ^ (c >> 1) : c >> 1; crctab[n] = c; } }
static u32 crc32b(u32 c, const u8 *b, size_t n) { size_t i; c = ~c; for (i = 0; i < n; i++) c = crctab[(c ^ b[i]) & 255] ^ (c >> 8); return ~c; }
static void put32(u8 *p, u32 v) { p[0] = v >> 24; p[1] = v >> 16; p[2] = v >> 8; p[3] = v; }
static void chunkw(FILE *f, const char *type, const u8 *d, u32 n) {
    u8 h[8]; u32 c; put32(h, n); memcpy(h + 4, type, 4); fwrite(h, 1, 8, f);
    if (n) fwrite(d, 1, n, f);
    c = crc32b(0, (const u8 *)type, 4); c = ~crc32b(~0u ^ 0, d, 0) ? c : c;
    { u32 cc = crc32b(0, (const u8 *)type, 4); /* continue */ size_t i; cc = ~cc; for (i = 0; i < n; i++) cc = crctab[(cc ^ d[i]) & 255] ^ (cc >> 8); cc = ~cc; put32(h, cc); fwrite(h, 1, 4, f); }
}
void soft_write_png(const char *path, int scale) {
    int w = SW * scale, h = SH * scale, x, y;
    size_t raw = (size_t)(w * 3 + 1) * h, pos = 0, bp;
    u8 *r = malloc(raw), *z; u32 a = 1, b = 0; size_t zl, i;
    FILE *f = fopen(path, "wb");
    u8 ihdr[13] = {0};
    if (!f) return;
    crcinit();
    for (y = 0; y < h; y++) {
        r[pos++] = 0;
        for (x = 0; x < w; x++) { u32 c = fb[(y / scale) * SW + x / scale]; r[pos++] = c >> 16; r[pos++] = c >> 8; r[pos++] = c; }
    }
    zl = 2 + raw + (raw / 65535 + 1) * 5 + 4;
    z = malloc(zl); bp = 0; z[bp++] = 0x78; z[bp++] = 1;
    for (i = 0; i < raw; i += 65535) {
        size_t n = raw - i > 65535 ? 65535 : raw - i;
        z[bp++] = (i + n >= raw); z[bp++] = n & 255; z[bp++] = n >> 8; z[bp++] = ~n & 255; z[bp++] = (~n >> 8) & 255;
        memcpy(z + bp, r + i, n); bp += n;
    }
    for (i = 0; i < raw; i++) { a = (a + r[i]) % 65521; b = (b + a) % 65521; }
    put32(z + bp, (b << 16) | a); bp += 4;
    fwrite("\x89PNG\r\n\x1a\n", 1, 8, f);
    put32(ihdr, w); put32(ihdr + 4, h); ihdr[8] = 8; ihdr[9] = 2;
    chunkw(f, "IHDR", ihdr, 13); chunkw(f, "IDAT", z, (u32)bp); chunkw(f, "IEND", NULL, 0);
    fclose(f); free(r); free(z);
}

