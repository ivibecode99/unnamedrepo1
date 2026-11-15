#if defined(__SDCC)
#pragma bank 255
#endif
#include "lt.h"
#include "gen_strings.h"
/* Top-level state machine: title, options, slot select, hands off to world/battle/etc. */

#define M_TITLE 0
#define M_OPTIONS 1
#define M_SLOTS 2

u8 g_mode;
#define mode g_mode
static u8 tstate, tcur, frame_ctr, prevk, opt_cur, opt_remap, opt_from, slot_cur, slot_erase;
static s8 fade_cur, fade_tgt, fade_spd;
static u8 flash_n;

void fx_fade(s8 target, u8 speed) API { fade_tgt = target; fade_spd = speed ? speed : 1; }
u8 fx_busy(void) API { return fade_cur != fade_tgt; }
void fx_flash(u8 n) API { if (!meta.no_flash) flash_n = n; }
void fx_tick(void) API {
    static u8 t;
    if (fade_cur != fade_tgt) {
        if (++t >= (u8)fade_spd) { t = 0; if (fade_cur < fade_tgt) fade_cur++; else fade_cur--; }
    }
    if (flash_n) { flash_n--; plat_fade((s8)(-(s8)(flash_n > 8 ? 8 : flash_n) / 2 - (fade_cur < 0 ? 0 : 0))); }
    else plat_fade(fade_cur);
}

/* ---------- common list drawing ---------- */
static void win_open(u8 y) { ui_clear_win(); ui_win(y); }

/* ---------- title ---------- */
static void title_draw_map(void) {
    u8 x, y;
    u16 pc[4];
    u8 i, j;
    plat_lcd(0);
    load_tiles(CH_TILES_UI, 0);
    load_pal(CH_PAL_UI, P_UI, 1);
    for (i = 1; i < 4; i++) {
        plat_chunk_read(CH_TITLE, (u16)(i * 8), g_tmp, 8);
        for (j = 0; j < 4; j++) pc[j] = rd16(g_tmp + j * 2);
        plat_pal(i, pc);
    }
    {
        u16 off = 32 + 720, nt = (plat_chunk_size(CH_TITLE) - off) / 16, done = 0;
        while (done < nt) {
            u16 n = nt - done;
            if (n > 32) n = 32;
            plat_chunk_read(CH_TITLE, (u16)(off + done * 16), g_tmp, (u16)(n * 16));
            plat_tiles((u8)(T_MAP + done), g_tmp, (u8)n);
            done += n;
        }
    }
    for (y = 0; y < 18; y++) {
        plat_chunk_read(CH_TITLE, (u16)(32 + y * 20), g_tmp, 20);
        plat_chunk_read(CH_TITLE, (u16)(32 + 360 + y * 20), g_tmp + 32, 20);
        for (x = 0; x < 20; x++) plat_bg_set(x, y, (u8)(T_MAP + g_tmp[x]), g_tmp[32 + x]);
    }
    {
        u16 bp[4];
        plat_chunk_read(CH_BSPR, 0, g_tmp, 16);
        for (j = 0; j < 4; j++) bp[j] = rd16(g_tmp + j * 2);
        plat_pal(P_BULLET, bp);
        for (j = 0; j < 4; j++) bp[j] = rd16(g_tmp + 8 + j * 2);
        plat_pal(P_SOUL, bp);
        plat_chunk_read(CH_BSPR, 16, g_tmp, 256);
        plat_tiles(T_BSPR, g_tmp, 16);
    }
    for (i = 0; i < 40; i++) plat_spr(i, 0, 200, 0, 0);
    plat_scroll(0, 0);
    ui_clear_win();
    ui_win(144);
    set_dmg(0xE4, 0xE4, 0xE4);
    plat_lcd(1);
}
static void title_menu_draw(void) {
    ui_clear_win();
    ui_box(3, 0, 14, 9);
    ui_print(6, 2, ui_str(S_NEWGAME));
    ui_print(6, 4, ui_str(S_CONTINUE));
    ui_print(6, 6, ui_str(S_OPTIONS));
}
static void title_init(void) {
    mode = M_TITLE; tstate = 0; tcur = 0; frame_ctr = 0;
    title_draw_map();
    audio_play(0);
    fade_cur = 8; fx_fade(0, 3);
}
static void options_draw(void);
static void slots_draw(void);
static void title_tick(void) {
    u8 i, wx, wy;
    frame_ctr++;
    /* the stray light bobs over the dunes */
    wx = (u8)(40 + (isin((u8)(frame_ctr * 2)) >> 2)); wy = (u8)(92 + (isin((u8)(frame_ctr * 3)) >> 4));
    plat_spr(0, (s16)wx + 60, wy, T_BSPR, P_SOUL - 8);
    (void)i;
    if (tstate == 0) {
        if ((frame_ctr & 32) == 0) ui_print_bg(4, 14, ui_str(S_PRESS));
        else plat_bg_fill(4, 14, 11, 1, T_BLACK, P_UI);
        if (g_pressed & (K_START | K_A)) { audio_sfx(1); tstate = 1; title_menu_draw(); ui_win(80); }
        return;
    }
    if (tstate == 1) {
        for (i = 0; i < 3; i++) plat_win_set(5, (u8)(2 + i * 2), i == tcur ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
        if (g_pressed & K_UP) { tcur = tcur ? (u8)(tcur - 1) : 2; audio_sfx(0); }
        if (g_pressed & K_DOWN) { tcur = tcur < 2 ? (u8)(tcur + 1) : 0; audio_sfx(0); }
        if (g_pressed & K_B) { tstate = 0; ui_win(144); }
        if (g_pressed & K_A) {
            audio_sfx(1);
            if (tcur == 2) { mode = M_OPTIONS; opt_cur = 0; opt_remap = 255; opt_from = 0; win_open(0); options_draw(); }
            else if (tcur == 1) { mode = M_SLOTS; slot_cur = 0; slot_erase = 0; win_open(0); slots_draw(); }
            else { game_start_new(); }
        }
    }
}

/* ---------- options ---------- */
static const u8 *speed_str(void) { return ui_str((u8)(meta.text_speed == 0 ? S_INSTANT : meta.text_speed == 1 ? S_FAST : meta.text_speed == 2 ? S_NORMAL : S_SLOW)); }
static void options_draw(void) {
    u8 n = 0, caps = plat_caps();
    ui_clear_win();
    ui_box(0, 0, 20, 18);
    ui_print(5, 1, ui_str(S_OPTIONS));
    ui_print(3, 4, ui_str(S_TXTSPD)); ui_print(14, 4, speed_str());
    ui_print(3, 6, ui_str(S_FLASH)); ui_print(14, 6, ui_str(meta.no_flash ? S_ON : S_OFF));
    ui_print(3, 8, ui_str(S_ASSIST)); ui_print(14, 8, ui_str(meta.assist ? S_ON : S_OFF));
    ui_print(3, 10, ui_str(S_VOLUME)); ui_num(14, 10, meta.vol, 1);
    if (caps & PC_REMAP) { ui_print(3, 12, ui_str(S_KEYS)); n = 1; }
    ui_print(3, (u8)(12 + n * 2), ui_str(S_BACK));
    for (n = 0; n < 6; n++) plat_win_set(2, (u8)(4 + n * 2), n == opt_cur ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
}
static void remap_draw(void) {
    static const char *nm[8] = {"UP", "DOWN", "LEFT", "RIGHT", "A OK", "B BACK", "START", "SELECT"};
    u8 i;
    ui_clear_win(); ui_box(0, 0, 20, 18);
    ui_print(4, 1, ui_str(S_KEYS));
    for (i = 0; i < 8; i++) ui_print(5, (u8)(3 + i * 1 + (i > 3)), (const u8 *)nm[i]);
    ui_print(5, 14, ui_str(S_BACK));
    for (i = 0; i < 9; i++) plat_win_set(3, (u8)(3 + i + (i > 3 && i < 8)), (i == opt_remap) ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
    /* simple listing: show whether a custom key set */
    for (i = 0; i < 8; i++) if (meta.keymap[i]) ui_num(15, (u8)(3 + i + (i > 3)), meta.keymap[i], 3);
}
void game_options_open(void) API { mode = M_OPTIONS; opt_cur = 0; opt_remap = 255; opt_from = M_PLAY; win_open(0); options_draw(); }
static void options_leave(void) { meta_save(); win_open(144); if (opt_from == M_PLAY) { mode = M_PLAY; } else { mode = M_TITLE; tstate = 1; ui_win(80); title_menu_draw(); } }
static void options_tick(void) {
    u8 ncount = (plat_caps() & PC_REMAP) ? 6 : 5, last = (u8)(ncount - 1);
    if (opt_remap < 8) { /* capturing */
        remap_draw(); ui_print(4, 16, ui_str(S_PRESSKEY));
        if (!plat_remap_busy()) { opt_remap = 100; remap_draw(); }
        return;
    }
    if (opt_remap == 100 || opt_remap == 101 || opt_remap == 102) { /* remap list (cursor idx in slot_cur) */
        if (g_pressed & K_UP) { slot_cur = slot_cur ? (u8)(slot_cur - 1) : 8; audio_sfx(0); }
        if (g_pressed & K_DOWN) { slot_cur = slot_cur < 8 ? (u8)(slot_cur + 1) : 0; audio_sfx(0); }
        opt_remap = 100;
        {
            u8 i;
            for (i = 0; i < 9; i++) plat_win_set(3, (u8)(3 + i + (i > 3 && i < 8)), (i == slot_cur) ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
        }
        if (g_pressed & K_B) { opt_remap = 255; options_draw(); return; }
        if (g_pressed & K_A) {
            if (slot_cur == 8) { opt_remap = 255; options_draw(); meta_save(); }
            else { plat_remap(slot_cur); opt_remap = 0; }
        }
        return;
    }
    if (g_pressed & K_UP) { opt_cur = opt_cur ? (u8)(opt_cur - 1) : last; audio_sfx(0); }
    if (g_pressed & K_DOWN) { opt_cur = opt_cur < last ? (u8)(opt_cur + 1) : 0; audio_sfx(0); }
    if (g_pressed & (K_LEFT | K_RIGHT | K_A)) {
        s8 d = (g_pressed & K_LEFT) ? -1 : 1;
        if (opt_cur == 0) meta.text_speed = (u8)((meta.text_speed + 4 + d) & 3);
        else if (opt_cur == 1) meta.no_flash ^= 1;
        else if (opt_cur == 2) meta.assist ^= 1;
        else if (opt_cur == 3) { if (d > 0 && meta.vol < 8) meta.vol++; else if (d < 0 && meta.vol > 0) meta.vol--; }
        else if (opt_cur == 4 && ncount == 6) { if (g_pressed & K_A) { opt_remap = 100; slot_cur = 0; remap_draw(); return; } }
        else if (opt_cur == last && (g_pressed & K_A)) { options_leave(); return; }
        audio_sfx(0);
        options_draw();
    }
    if (g_pressed & K_B) { options_leave(); }
}

/* ---------- slots (continue) ---------- */
static void slots_draw(void) {
    u8 i;
    ui_clear_win(); ui_box(0, 0, 20, 18);
    ui_print(5, 1, ui_str(S_CONTINUE));
    for (i = 0; i < 3; i++) {
        u8 y = (u8)(4 + i * 3);
        ui_print(4, y, ui_str(S_SLOT)); ui_num(9, y, (u16)(i + 1), 1);
        if (save_slot_used(i)) { ui_print(11, y, (const u8 *)"SAVED"); }
        else ui_print(11, y, ui_str(S_EMPTY));
    }
    ui_print(4, 13, ui_str(S_BACK));
    for (i = 0; i < 4; i++) plat_win_set(2, (u8)(i == 3 ? 13 : 4 + i * 3), i == slot_cur ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
}
static void slots_tick(void) {
    if (g_pressed & K_UP) { slot_cur = slot_cur ? (u8)(slot_cur - 1) : 3; audio_sfx(0); slots_draw(); }
    if (g_pressed & K_DOWN) { slot_cur = slot_cur < 3 ? (u8)(slot_cur + 1) : 0; audio_sfx(0); slots_draw(); }
    if (g_pressed & K_B) { mode = M_TITLE; tstate = 1; title_menu_draw(); ui_win(80); }
    if (g_pressed & K_A) {
        if (slot_cur == 3) { mode = M_TITLE; tstate = 1; title_menu_draw(); ui_win(80); return; }
        if (save_slot_used(slot_cur) && save_read(slot_cur)) { audio_sfx(1); game_continue(); }
        else audio_sfx(14);
    }
}

void core_init(void) API {
    save_init();
    ui_init();
    audio_init();
    rnd_seed(0x1234);
    game_init();
    title_init();
#ifdef LT_BOOT_MAP
    game_debug_apply(LT_BOOT_MAP, LT_BOOT_X, LT_BOOT_Y, LT_BOOT_D, 0, 0, 0);
#endif
}
void game_title(void) API { title_init(); }
void core_frame(void) API {
    u8 k = plat_keys();
    g_pressed = k & (u8)~prevk;
    prevk = k; g_keys = k;
    frame_ctr = (u8)frame_ctr;
    fx_tick();
    audio_tick();
    switch (mode) {
    case M_TITLE: title_tick(); break;
    case M_OPTIONS: options_tick(); break;
    case M_SLOTS: slots_tick(); break;
    default: game_play_frame(); break;
    }
}
