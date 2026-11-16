#if defined(__SDCC)
#pragma bank 255
#endif
#include "lt.h"
/* Text rendering on the window/BG layers and the typewriter dialogue box. */

static u8 uistr[800];
static u16 uioff[96];
static u8 uicount;

void ui_init(void) API {
    u16 sz = plat_chunk_size(CH_STRINGS), i, p;
    if (sz > sizeof uistr) sz = sizeof uistr;
    plat_chunk(CH_STRINGS, uistr, sz);
    uicount = uistr[0];
    p = 1;
    for (i = 0; i < uicount; i++) { uioff[i] = p; while (uistr[p]) p++; p++; }
}
const u8 *ui_str(u8 id) API { return id < uicount ? uistr + uioff[id] : (const u8 *)""; }

u8 ui_win_y = 144, ui_say_open_y = 96, ui_say_close_y = 144;
void ui_win(u8 y) API { ui_win_y = y; plat_win_y(y); }
void ui_hide_sprites(void) API { u8 i; for (i = 0; i < 40; i++) plat_spr(i, 0, 200, 0, 0); }
void ui_clear_win(void) API { plat_win_fill(0, 0, 32, 32, T_BLACK, P_UI); }

static u8 glyph(u8 c) { return (c >= 32 && c < 127) ? (u8)(T_FONT + c - 32) : T_FONT; }
void ui_print(u8 x, u8 y, const u8 *s) API {
    while (*s) { plat_win_set(x++, y, glyph(*s), P_UI); s++; }
}
void ui_print_bg(u8 x, u8 y, const u8 *s) API {
    while (*s) { plat_bg_set(x++, y, glyph(*s), P_UI); s++; }
}
void ui_num(u8 x, u8 y, u16 v, u8 digits) API {
    u8 i;
    for (i = 0; i < digits; i++) {
        u8 d = (u8)(v % 10);
        v /= 10;
        plat_win_set((u8)(x + digits - 1 - i), y, (u8)(T_FONT + 16 + d), P_UI);
        if (v == 0 && i + 1 < digits) { u8 j; for (j = (u8)(i + 1); j < digits; j++) plat_win_set((u8)(x + digits - 1 - j), y, T_FONT, P_UI); break; }
    }
}
static void box_gen(u8 x, u8 y, u8 w, u8 h, u8 bg) {
    u8 i, j;
    for (j = 0; j < h; j++)
        for (i = 0; i < w; i++) {
            u8 t;
            if (j == 0) t = i == 0 ? UI_TL : (i == w - 1 ? UI_TR : UI_T);
            else if (j == h - 1) t = i == 0 ? UI_BL : (i == w - 1 ? UI_BR : UI_B);
            else if (i == 0) t = UI_L;
            else if (i == w - 1) t = UI_R;
            else { if (bg) plat_bg_set((u8)(x + i), (u8)(y + j), T_BLACK, P_UI); else plat_win_set((u8)(x + i), (u8)(y + j), T_BLACK, P_UI); continue; }
            if (bg) plat_bg_set((u8)(x + i), (u8)(y + j), (u8)(T_UI + t), P_UI); else plat_win_set((u8)(x + i), (u8)(y + j), (u8)(T_UI + t), P_UI);
        }
}
void ui_box(u8 x, u8 y, u8 w, u8 h) API { box_gen(x, y, w, h, 0); }
void ui_box_bg(u8 x, u8 y, u8 w, u8 h) API { box_gen(x, y, w, h, 1); }

/* ---------------- dialogue box (window rows 0..5, shown at pixel row 96) ---------------- */
#define ST_IDLE 0
#define ST_TYPE 1
#define ST_PAGE 2
#define ST_END 3
static const u8 *sp, *inj;
static u8 sx, sy, sstate, stimer, sx0, swidth, sface, spk_blip, rush, spk_id, sarrow, semo;
static u16 sface_ch;

static void say_clear_text(void) { plat_win_fill(1, 1, 18, 4, T_BLACK, P_UI); if (sface) { /* redraw face */ u8 i, j; for (j = 0; j < 4; j++) for (i = 0; i < 4; i++) plat_win_set((u8)(1 + i), (u8)(1 + j), (u8)(T_FACE + j * 4 + i), P_FACE); } sx = sx0; sy = 1; }
static void face_load(u8 emo) {
    u8 buf[16];
    (void)buf;
    if (!sface_ch) return;
    plat_chunk_read(sface_ch, (u16)(8 + (u16)emo * 256), g_tmp, 256);
    plat_tiles(T_FACE, g_tmp, 16);
}
void ui_say_begin(u8 spk, u8 emo) API {
    u8 e[16], i;
    u16 c[4];
    spk_id = spk; sface_ch = 0; sface = 0; spk_blip = 40;
    if (spk) {
        plat_chunk_read(CH_SPEAKERS, (u16)spk * 16, e, 16);
        spk_blip = e[0];
        sface_ch = rd16(e + 2);
        if (sface_ch && e[1]) {
            sface = 1;
            plat_chunk_read(sface_ch, 0, g_tmp, 8);
            for (i = 0; i < 4; i++) c[i] = rd16(g_tmp + i * 2);
            plat_pal(P_FACE, c);
            face_load(emo);
        }
    }
    sx0 = sface ? 6 : 1; swidth = sface ? 13 : 18;
    ui_box(0, 0, 20, 6);
    say_clear_text();
    ui_win(ui_say_open_y);
    sstate = ST_IDLE; semo = emo;
}
void ui_say_text(const u8 *txt) API { sp = txt; inj = 0; sstate = ST_TYPE; stimer = 0; rush = 0; plat_win_set(18, 4, T_BLACK, P_UI); }
static u8 tdelay(void) { switch (meta.text_speed) { case 0: return 0; case 1: return 1; case 3: return 3; default: return 2; } }
u8 ui_say_tick(void) API {
    if (sstate == ST_TYPE) {
        if (g_pressed & (K_A | K_B)) rush = 1;
        if (stimer) { stimer--; if (!rush) return 0; stimer = 0; }
        for (;;) {
            u8 c;
            if (inj) { c = *inj; if (!c) { inj = 0; continue; } inj++; if (c != ' ') audio_blip(spk_blip); plat_win_set(sx++, sy, glyph(c), P_UI); if (!rush && tdelay()) { stimer = (u8)(tdelay() - 1); return 0; } continue; }
            c = *sp;
            if (c == 0) { sstate = ST_END; sarrow = 0; return 0; }
            sp++;
            if (c == 0x0A) { sy++; sx = sx0; continue; }
            if (c == 0x0C) { sstate = ST_PAGE; sarrow = 0; return 0; }
            if (c == 0x01) { if (!rush) { stimer = 10; return 0; } continue; }
            if (c == 0x02) { if (!rush) { stimer = 28; return 0; } continue; }
            if (c == 0x03) { semo = *sp++; face_load(semo); continue; }
            if (c == 0x04) { inj = g.name; continue; }
            plat_win_set(sx++, sy, glyph(c), P_UI);
            if (c != ' ' && (sx & 1)) audio_blip(spk_blip);
            if (!rush && tdelay()) { stimer = (u8)(tdelay() - 1); return 0; }
        }
    }
    if (sstate == ST_PAGE || sstate == ST_END) {
        sarrow++;
        plat_win_set(18, 4, (sarrow & 32) ? T_BLACK : (u8)(T_UI + UI_ARROW), P_UI);
        if (g_pressed & K_A) {
            plat_win_set(18, 4, T_BLACK, P_UI);
            if (sstate == ST_PAGE) { say_clear_text(); sstate = ST_TYPE; rush = 0; stimer = 0; return 0; }
            sstate = ST_IDLE;
            return 1;
        }
    }
    return 0;
}
void ui_say_end(void) API { ui_win(ui_say_close_y); }

#ifndef __SDCC
u8 ui_dbg_state(void) API { return sstate; }
void ui_dbg_text(char *o) API { int i; for (i = 0; i < 24; i++) o[i] = sp ? (char)(sp[i] >= 32 && sp[i] < 127 ? sp[i] : '.') : '?'; o[24] = 0; }
#endif
