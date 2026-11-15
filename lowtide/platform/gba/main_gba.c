/* LOWTIDE Game Boy Advance backend (bare metal, no libraries). 160x144 logical screen centred in 240x160. */
#include <stdint.h>
#include <string.h>
#include "../../core/lt.h"

typedef volatile uint16_t vu16; typedef volatile uint8_t vu8; typedef uint32_t u32;
#define R16(a) (*(vu16 *)(a))
#define DISPCNT R16(0x04000000)
#define BG0CNT R16(0x04000008)
#define BG1CNT R16(0x0400000A)
#define BG3CNT R16(0x0400000E)
#define BG0HOFS R16(0x04000010)
#define BG0VOFS R16(0x04000012)
#define BG1HOFS R16(0x04000014)
#define BG1VOFS R16(0x04000016)
#define WIN0H R16(0x04000040)
#define WIN1H R16(0x04000042)
#define WIN0V R16(0x04000044)
#define WIN1V R16(0x04000046)
#define WININ R16(0x04000048)
#define WINOUT R16(0x0400004A)
#define BLDCNT R16(0x04000050)
#define BLDY R16(0x04000054)
#define VCOUNT R16(0x04000006)
#define KEYINPUT R16(0x04000130)
#define WAITCNT R16(0x04000204)
#define BGPAL ((vu16 *)0x05000000)
#define OBJPAL ((vu16 *)0x05000200)
#define VRAM ((vu16 *)0x06000000)
#define OBJVRAM ((vu16 *)0x06010000)
#define OAM ((vu16 *)0x07000000)
#define SBLK_BG0 28
#define SBLK_BG1 29
#define SBLK_BG3 30
#define OFFX 40
#define OFFY 8

extern const unsigned char lt_blob[];
const char sram_id[] __attribute__((used)) = "SRAM_V113";

/* ---- chunks ---- */
static u32 chunk_off(u16 id) { const u8 *e = lt_blob + 2 + id * 6; return e[0] | (e[1] << 8) | (e[2] << 16) | ((u32)e[3] << 24); }
static u16 chunk_len(u16 id) { const u8 *e = lt_blob + 2 + id * 6; return (u16)(e[4] | (e[5] << 8)); }
u16 plat_chunk_size(u16 id) { u16 n = (u16)(lt_blob[0] | (lt_blob[1] << 8)); return id < n ? chunk_len(id) : 0; }
u16 plat_chunk_read(u16 id, u16 off, u8 *dst, u16 n) {
    u16 sz = plat_chunk_size(id);
    if (off >= sz) return 0;
    if (n > sz - off) n = (u16)(sz - off);
    memcpy(dst, lt_blob + chunk_off(id) + off, n);
    return n;
}
u16 plat_chunk(u16 id, u8 *dst, u16 max) { return plat_chunk_read(id, 0, dst, max); }

/* ---- video ---- */
static u16 shadow_oam[128 * 4];
static u16 palsrc[16][4];
static s8 fade_lv;
static u8 win_y = 144, lcd_on;
static void dispcnt_update(void) {
    uint16_t d = 0x0000 | 0x0100 | 0x0200 | 0x1000 | 0x0040 | 0x2000 | 0x4000 | 0x0800;
    if (!lcd_on) d |= 0x80;
    DISPCNT = d;
}
void plat_init(void) {
    int i;
    WAITCNT = 0x4317;
    for (i = 0; i < 128; i++) { shadow_oam[i * 4] = 0x0200; shadow_oam[i * 4 + 1] = 0; shadow_oam[i * 4 + 2] = 0; }
    BG0CNT = 1 | (0 << 2) | (SBLK_BG0 << 8);
    BG1CNT = 0 | (0 << 2) | (SBLK_BG1 << 8);
    BG3CNT = 2 | (0 << 2) | (SBLK_BG3 << 8);
    WIN1H = (OFFX << 8) | (OFFX + 160); WIN1V = (OFFY << 8) | (OFFY + 144);
    WININ = (0x1 | 0x10) | ((0x1 | 0x10) << 8);   /* placeholder, updated by plat_win_y */
    WINOUT = 0x08;                                /* border layer (BG3) outside */
    *(vu16 *)0x04000084 = 0x80; *(vu16 *)0x04000080 = 0xFF77; *(vu16 *)0x04000082 = 2;
    for (i = 0; i < 1024; i++) { VRAM[(SBLK_BG3 * 0x800) / 2 + i] = 1; }
    BGPAL[0] = 0;
    lcd_on = 0; dispcnt_update();
}
void plat_lcd(u8 on) { lcd_on = on; dispcnt_update(); }
void plat_vsync(void) {
    int i;
    while (VCOUNT >= 160) {}
    while (VCOUNT < 160) {}
    for (i = 0; i < 128 * 4; i++) OAM[i] = shadow_oam[i];
}
void plat_tiles(u8 first, const u8 *src, u8 count) {
    u8 t, r, x;
    for (t = 0; t < count; t++) {
        u32 bgw[8], objw[8];
        for (r = 0; r < 8; r++) {
            u8 lo = src[t * 16 + r * 2], hi = src[t * 16 + r * 2 + 1];
            u32 bw = 0, ow = 0;
            for (x = 0; x < 8; x++) {
                u32 v = (u32)((((hi >> (7 - x)) & 1) << 1) | ((lo >> (7 - x)) & 1));
                bw |= (v + 1) << (x * 4);
                ow |= v << (x * 4);
            }
            bgw[r] = bw; objw[r] = ow;
        }
        {
            vu16 *bd = VRAM + (u32)(first + t) * 16, *od = OBJVRAM + (u32)(first + t) * 16;
            for (r = 0; r < 8; r++) {
                bd[r * 2] = (u16)bgw[r]; bd[r * 2 + 1] = (u16)(bgw[r] >> 16);
                od[r * 2] = (u16)objw[r]; od[r * 2 + 1] = (u16)(objw[r] >> 16);
            }
        }
    }
}
static u16 entry(u8 t, u8 a) { return (u16)(t | (((a >> 5) & 1) << 10) | (((a >> 6) & 1) << 11) | ((a & 7) << 12)); }
void plat_bg_set(u8 x, u8 y, u8 t, u8 a) { VRAM[(SBLK_BG0 * 0x800) / 2 + ((y & 31) << 5) + (x & 31)] = entry(t, a); }
void plat_win_set(u8 x, u8 y, u8 t, u8 a) { VRAM[(SBLK_BG1 * 0x800) / 2 + ((y & 31) << 5) + (x & 31)] = entry(t, a); }
void plat_bg_fill(u8 x, u8 y, u8 w, u8 h, u8 t, u8 a) { u8 i, j; for (j = 0; j < h; j++) for (i = 0; i < w; i++) plat_bg_set((u8)(x + i), (u8)(y + j), t, a); }
void plat_win_fill(u8 x, u8 y, u8 w, u8 h, u8 t, u8 a) { u8 i, j; for (j = 0; j < h; j++) for (i = 0; i < w; i++) plat_win_set((u8)(x + i), (u8)(y + j), t, a); }
void plat_scroll(u8 x, u8 y) { BG0HOFS = (u16)((x - OFFX) & 0x1FF); BG0VOFS = (u16)((y - OFFY) & 0x1FF); }
void plat_win_y(u8 y) {
    win_y = y;
    BG1HOFS = (u16)((-OFFX) & 0x1FF); BG1VOFS = (u16)((-(OFFY + y)) & 0x1FF);
    if (y >= 144) { WIN0H = 0; WIN0V = 0; WININ = (0x01 | 0x10) << 8; }
    else { WIN0H = (OFFX << 8) | (OFFX + 160); WIN0V = (u16)(((OFFY + y) << 8) | (OFFY + 144)); WININ = 0x02 | (((0x01 | 0x10)) << 8); }
}
static u16 blendc(u16 c, s8 lv) { (void)lv; return c; }
void plat_pal(u8 idx, const u16 *c4) {
    u8 i;
    idx &= 15;
    for (i = 0; i < 4; i++) {
        palsrc[idx][i] = c4[i];
        if (idx < 8) BGPAL[idx * 16 + 1 + i] = blendc(c4[i], 0);    /* BG: colours 1..4 (0 is transparent) */
        else OBJPAL[(idx - 8) * 16 + i] = blendc(c4[i], 0);          /* OBJ: colours 0..3 (0 transparent) */
    }
}
void plat_dmg_pal(u8 b, u8 o0, u8 o1) { (void)b; (void)o0; (void)o1; }
void plat_fade(s8 level) {
    if (level == fade_lv) return;
    fade_lv = level;
    if (level == 0) { BLDCNT = 0; BLDY = 0; }
    else { BLDCNT = (uint16_t)(((level > 0 ? 3 : 2) << 6) | 0x3F | 0x20); BLDY = (uint16_t)((level > 0 ? level : -level) * 2); }
}
void plat_spr(u8 i, s16 x, s16 y, u8 tile, u8 attr) {
    u16 *o = &shadow_oam[i * 4];
    if (i >= 128) return;
    if (x <= -8 || x >= 160 || y <= -8 || y >= 144) { o[0] = 0x0200; return; }
    o[0] = (u16)((y + OFFY) & 0xFF);
    o[1] = (u16)(((x + OFFX) & 0x1FF) | (((attr >> 5) & 1) << 12) | (((attr >> 6) & 1) << 13));
    o[2] = (u16)(tile | (0 << 10) | ((attr & 7) << 12));
}
/* ---- sound ---- */
void plat_snd_trig(u8 ch, u16 p, u8 env, u8 duty) {
    switch (ch & 3) {
    case 0: R16(0x04000060) = 0; R16(0x04000062) = (u16)(((u16)env << 8) | ((u16)duty << 6)); R16(0x04000064) = (u16)(0x8000 | p); break;
    case 1: R16(0x04000068) = (u16)(((u16)env << 8) | ((u16)duty << 6)); R16(0x0400006C) = (u16)(0x8000 | p); break;
    case 2: R16(0x04000070) = 0x80; R16(0x04000072) = (u16)(((u16)(env & 0x60)) << 8); R16(0x04000074) = (u16)(0x8000 | p); break;
    default: R16(0x04000078) = (u16)((u16)env << 8); R16(0x0400007C) = (u16)(0x8000 | (p & 0xFF)); break;
    }
}
void plat_snd_off(u8 ch) {
    switch (ch & 3) { case 0: R16(0x04000062) = 0; R16(0x04000064) = 0x8000; break; case 1: R16(0x04000068) = 0; R16(0x0400006C) = 0x8000; break;
    case 2: R16(0x04000070) = 0; break; default: R16(0x04000078) = 0; R16(0x0400007C) = 0x8000; break; }
}
void plat_snd_period(u8 ch, u16 p) {
    switch (ch & 3) { case 0: R16(0x04000064) = p; break; case 1: R16(0x0400006C) = p; break; case 2: R16(0x04000074) = p; break; default: break; }
}
void plat_snd_wave(const u8 *w) {
    int i;
    u16 was = R16(0x04000070);
    R16(0x04000070) = 0x40;            /* select bank 1 for writing, bank 0 plays */
    R16(0x04000070) = 0x00;
    for (i = 0; i < 8; i++) R16(0x04000090 + i * 2) = (u16)(w[i * 2] | (w[i * 2 + 1] << 8));
    R16(0x04000070) = was;
}
u8 plat_keys(void) {
    u16 k = (u16)(~KEYINPUT), r = 0;
    if (k & 1) r |= K_A; if (k & 2) r |= K_B; if (k & 4) r |= K_SELECT; if (k & 8) r |= K_START;
    if (k & 16) r |= K_RIGHT; if (k & 32) r |= K_LEFT; if (k & 64) r |= K_UP; if (k & 128) r |= K_DOWN;
    return (u8)r;
}
void plat_sram_read(u16 off, u8 *dst, u16 n) { u16 i; for (i = 0; i < n; i++) dst[i] = *(vu8 *)(0x0E000000u + off + i); }
void plat_sram_write(u16 off, const u8 *src, u16 n) { u16 i; for (i = 0; i < n; i++) *(vu8 *)(0x0E000000u + off + i) = src[i]; }
void plat_sram_flush(void) {}
u8 plat_caps(void) { return PC_COLOR; }
void plat_remap(u8 b) { (void)b; }
u8 plat_remap_busy(void) { return 0; }
void plat_log(const char *s) { (void)s; }
void plat_quit(void) {}

int main(void) {
    plat_init();
    core_init();
    for (;;) {
        plat_vsync();
        core_frame();
    }
}
