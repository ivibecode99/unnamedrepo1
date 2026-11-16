/* LOWTIDE Game Boy / Game Boy Color backend (GBDK-2020, MBC5 + battery SRAM). */
#include <gb/gb.h>
#include <gb/cgb.h>
#include <string.h>
#include "../../core/lt.h"

extern const unsigned char lt_dir[];       /* per chunk: bank, addr_lo, addr_hi, size_lo, size_hi */
extern const unsigned int lt_nchunks;

static u8 is_cgb, fade_lv;
static u16 palsrc[16][4];
static u8 dmg_b = 0xE4, dmg_o0 = 0xE4, dmg_o1 = 0xE4;

u16 plat_chunk_size(u16 id) {
    const unsigned char *e;
    if (id >= lt_nchunks) return 0;
    e = lt_dir + (unsigned)id * 5;
    return (u16)(e[3] | ((u16)e[4] << 8));
}
u16 plat_chunk_read(u16 id, u16 off, u8 *dst, u16 n) {
    const unsigned char *e;
    u16 sz, addr;
    u8 bank, old;
    if (id >= lt_nchunks) return 0;
    e = lt_dir + (unsigned)id * 5;
    bank = e[0]; addr = (u16)(e[1] | ((u16)e[2] << 8)); sz = (u16)(e[3] | ((u16)e[4] << 8));
    if (off >= sz) return 0;
    if (n > sz - off) n = (u16)(sz - off);
    old = CURRENT_BANK;
    SWITCH_ROM(bank);
    memcpy(dst, (const void *)(0x4000u + addr + off), n);
    SWITCH_ROM(old);
    return n;
}
u16 plat_chunk(u16 id, u8 *dst, u16 max) { return plat_chunk_read(id, 0, dst, max); }

void plat_init(void) {
    is_cgb = (_cpu == CGB_TYPE);
    if (is_cgb) cpu_fast();
    NR52_REG = 0x80; NR51_REG = 0xFF; NR50_REG = 0x77;
    ENABLE_RAM; SWITCH_RAM(0);
    LCDC_REG = LCDCF_OFF | LCDCF_BG8000 | LCDCF_BG9800 | LCDCF_WIN9C00 | LCDCF_OBJ8 | LCDCF_BGON | LCDCF_OBJON | LCDCF_WINON;
    WX_REG = 7; WY_REG = 144;
}
void plat_vsync(void) { wait_vbl_done(); }
void plat_lcd(u8 on) {
    if (on) { LCDC_REG |= LCDCF_ON; }
    else if (LCDC_REG & LCDCF_ON) { while (LY_REG != 144) {} LCDC_REG &= ~LCDCF_ON; }
}
void plat_tiles(u8 first, const u8 *src, u8 count) {
    set_data((uint8_t *)0x8000 + (unsigned)first * 16, src, (uint16_t)count * 16);
}
static void vram_wait(void) { while (STAT_REG & STATF_BUSY) {} }
void plat_bg_set(u8 x, u8 y, u8 t, u8 a) {
    volatile u8 *p = (volatile u8 *)(0x9800 + ((u16)(y & 31) << 5) + (x & 31));
    vram_wait(); *p = t;
    if (is_cgb) { VBK_REG = 1; vram_wait(); *p = a; VBK_REG = 0; }
}
void plat_win_set(u8 x, u8 y, u8 t, u8 a) {
    volatile u8 *p = (volatile u8 *)(0x9C00 + ((u16)(y & 31) << 5) + (x & 31));
    vram_wait(); *p = t;
    if (is_cgb) { VBK_REG = 1; vram_wait(); *p = a; VBK_REG = 0; }
}
void plat_bg_fill(u8 x, u8 y, u8 w, u8 h, u8 t, u8 a) { u8 i, j; for (j = 0; j < h; j++) for (i = 0; i < w; i++) plat_bg_set((u8)(x + i), (u8)(y + j), t, a); }
void plat_win_fill(u8 x, u8 y, u8 w, u8 h, u8 t, u8 a) { u8 i, j; for (j = 0; j < h; j++) for (i = 0; i < w; i++) plat_win_set((u8)(x + i), (u8)(y + j), t, a); }
void plat_scroll(u8 x, u8 y) { SCX_REG = x; SCY_REG = y; }
void plat_win_y(u8 y) { WY_REG = y; WX_REG = 7; }

static u16 blend(u16 c, u8 lv) {
    /* lv bit7 = white direction */
    u8 neg = lv & 0x80, l = lv & 0x7F;
    s16 r = c & 31, g = (c >> 5) & 31, b = (c >> 10) & 31, t = neg ? 31 : 0;
    r += ((t - r) * l) / 8; g += ((t - g) * l) / 8; b += ((t - b) * l) / 8;
    return (u16)(r | (g << 5) | (b << 10));
}
static void pal_apply(u8 idx) {
    u16 c[4]; u8 i, lv = fade_lv;
    for (i = 0; i < 4; i++) c[i] = lv ? blend(palsrc[idx][i], lv) : palsrc[idx][i];
    if (idx < 8) set_bkg_palette(idx, 1, c); else set_sprite_palette((u8)(idx - 8), 1, c);
}
void plat_pal(u8 idx, const u16 *c4) {
    u8 i;
    idx &= 15;
    for (i = 0; i < 4; i++) palsrc[idx][i] = c4[i];
    if (is_cgb) pal_apply(idx);
}
static u8 dmg_fade(u8 reg, u8 lv) {
    u8 k = (u8)(((lv & 0x7F) + 2) / 3), out = 0, i;
    for (i = 0; i < 4; i++) {
        s8 v = (s8)((reg >> (i * 2)) & 3);
        if (lv & 0x80) v -= k; else v += k;
        if (v < 0) v = 0; if (v > 3) v = 3;
        out |= (u8)(v << (i * 2));
    }
    return out;
}
static void dmg_apply(void) { BGP_REG = dmg_fade(dmg_b, fade_lv); OBP0_REG = dmg_fade(dmg_o0, fade_lv); OBP1_REG = dmg_fade(dmg_o1, fade_lv); }
void plat_dmg_pal(u8 b, u8 o0, u8 o1) { dmg_b = b; dmg_o0 = o0; dmg_o1 = o1; if (!is_cgb) dmg_apply(); }
void plat_fade(s8 level) {
    u8 nv = level < 0 ? (u8)(0x80 | (u8)(-level)) : (u8)level, i;
    if (nv == fade_lv) return;
    fade_lv = nv;
    if (is_cgb) for (i = 0; i < 16; i++) pal_apply(i); else dmg_apply();
}
void plat_spr(u8 i, s16 x, s16 y, u8 tile, u8 attr) {
    if (x <= -8 || x >= 160 || y <= -8 || y >= 144) { move_sprite(i, 0, 0); return; }
    set_sprite_tile(i, tile);
    set_sprite_prop(i, attr);
    move_sprite(i, (u8)(x + 8), (u8)(y + 16));
}
/* ----- sound ----- */
void plat_snd_trig(u8 ch, u16 p, u8 env, u8 duty) {
    switch (ch & 3) {
    case 0: NR10_REG = 0; NR11_REG = (u8)(duty << 6); NR12_REG = env; NR13_REG = (u8)p; NR14_REG = (u8)(0x80 | (p >> 8)); break;
    case 1: NR21_REG = (u8)(duty << 6); NR22_REG = env; NR23_REG = (u8)p; NR24_REG = (u8)(0x80 | (p >> 8)); break;
    case 2: NR30_REG = 0x80; NR31_REG = 0; NR32_REG = (u8)(env & 0x60); NR33_REG = (u8)p; NR34_REG = (u8)(0x80 | (p >> 8)); break;
    default: NR41_REG = 0; NR42_REG = env; NR43_REG = (u8)p; NR44_REG = 0x80; break;
    }
}
void plat_snd_off(u8 ch) {
    switch (ch & 3) { case 0: NR12_REG = 0; NR14_REG = 0x80; break; case 1: NR22_REG = 0; NR24_REG = 0x80; break; case 2: NR30_REG = 0; break; default: NR42_REG = 0; NR44_REG = 0x80; break; }
}
void plat_snd_period(u8 ch, u16 p) {
    switch (ch & 3) { case 0: NR13_REG = (u8)p; NR14_REG = (u8)(p >> 8); break; case 1: NR23_REG = (u8)p; NR24_REG = (u8)(p >> 8); break; case 2: NR33_REG = (u8)p; NR34_REG = (u8)(p >> 8); break; default: break; }
}
void plat_snd_wave(const u8 *w) {
    u8 i, was = NR30_REG;
    NR30_REG = 0;
    for (i = 0; i < 16; i++) ((volatile u8 *)0xFF30)[i] = w[i];
    NR30_REG = was ? was : 0;
}
/* ----- input ----- */
u8 plat_keys(void) {
    u8 j = joypad(), k = 0;
    if (j & J_UP) k |= K_UP; if (j & J_DOWN) k |= K_DOWN; if (j & J_LEFT) k |= K_LEFT; if (j & J_RIGHT) k |= K_RIGHT;
    if (j & J_A) k |= K_A; if (j & J_B) k |= K_B; if (j & J_START) k |= K_START; if (j & J_SELECT) k |= K_SELECT;
    return k;
}
/* ----- save (battery SRAM at 0xA000) ----- */
void plat_sram_read(u16 off, u8 *dst, u16 n) { memcpy(dst, (const void *)(0xA000u + off), n); }
void plat_sram_write(u16 off, const u8 *src, u16 n) { memcpy((void *)(0xA000u + off), src, n); }
void plat_sram_flush(void) {}
u8 plat_caps(void) { return is_cgb ? PC_COLOR : 0; }
void plat_remap(u8 b) { (void)b; }
u8 plat_remap_busy(void) { return 0; }
void plat_log(const char *s) { (void)s; }
void plat_quit(void) {}

void main(void) {
    plat_init();
    core_init();
#ifdef LT_PROFILE
    {
        u8 n = 0; u16 t0 = (u16)sys_time;
        volatile u8 *prof = (volatile u8 *)0xBF00;
        while (1) {
            wait_vbl_done();
            core_frame();
            if (++n == 100) { u16 el = (u16)((u16)sys_time - t0); prof[0] = (u8)el; prof[1] = (u8)(el >> 8); prof[3]++; n = 0; t0 = (u16)sys_time; }
        }
    }
#else
    while (1) {
        wait_vbl_done();
        core_frame();
    }
#endif
}
