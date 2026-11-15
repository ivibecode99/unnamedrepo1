#if defined(__SDCC)
#pragma bank 255
#endif
#include "lt.h"
#include "gen_strings.h"
/* Gameplay layer: new game/continue, pause menu, items, shops, naming, save points, endings, credits. */

extern u8 game_flag_title;
#define P_WORLD 0
#define P_MENU 1
#define P_SHOP 2
#define P_NAME 3
#define P_SAVE 4
#define P_ENDING 5
#define P_CREDITS 6
#define P_ITEMSEL 7
static u8 pmode, menu_cur, menu_sub, shop_id, shop_n, shop_cur, shop_ents[8], shop_msg;
static u8 name_cur, name_len, save_cur, end_id;
static u16 credits_y, credits_off, credits_sz;
static u8 stats_open;

void game_init(void) API {}

/* ---------- items ---------- */
/* item table: 14 bytes each: name[10], type, value, price(2) */
static void item_read(u8 id, u8 *dst) { plat_chunk_read(CH_ITEMS, (u16)(1 + (u16)(id - 1) * 14), dst, 14); }
void item_name_print(u8 x, u8 y, u8 id) API {
    u8 b[14], i;
    item_read(id, b);
    for (i = 0; i < 10 && b[i]; i++) plat_win_set((u8)(x + i), y, (u8)(T_FONT + b[i] - 32), P_UI);
}
u8 item_add(u8 id) API { u8 i; for (i = 0; i < 8; i++) if (!g.inv[i]) { g.inv[i] = id; return 1; } return 0; }
u8 item_has(u8 id) API { u8 i; for (i = 0; i < 8; i++) if (g.inv[i] == id) return 1; return 0; }
void item_remove(u8 id) API { u8 i; for (i = 0; i < 8; i++) if (g.inv[i] == id) { g.inv[i] = 0; return; } }
void items_use(u8 idx) API {
    u8 n = 0, i, id = 0, b[14];
    for (i = 0; i < 8; i++) if (g.inv[i]) { if (n == idx) { id = g.inv[i]; n = i; break; } n++; }
    if (!id) return;
    item_read(id, b);
    if (b[10] == 0) { u16 h = (u16)(g.hp + b[11]); g.hp = (u8)(h > g.maxhp ? g.maxhp : h); audio_sfx(13); g.inv[n] = 0; }
    else if (b[10] == 2) { g.vars[V_BT_FLAG0 + 7] = id; g.inv[n] = 0; }   /* gift item: consumed, recorded for scripts */
}
void recalc_stats(void) API {
    u8 lv = (u8)(1 + (g.exp / 12 > 9 ? 9 : g.exp / 12));
    u8 bonus = (u8)((g.vars[V_SPARES] > 20 ? 20 : g.vars[V_SPARES]) + (g.vars[V_BOSSSPARES] > 5 ? 5 : g.vars[V_BOSSSPARES]) * 2);
    u8 mh = (u8)(20 + (lv - 1) * 3 + bonus);
    if (mh > 99) mh = 99;
    if (mh > g.maxhp) { g.hp = (u8)(g.hp + (mh - g.maxhp)); g.maxhp = mh; }
    g.lv = lv;
}
u8 moral(void) API {
    if (g.vars[V_KILLS] == 0 && g.vars[V_BOSSKILLS] == 0) return 0;
    if (g.vars[V_KILLS] >= 6 || g.vars[V_BOSSKILLS] >= 2) return 2;
    return 1;
}

/* ---------- new game / continue ---------- */
void game_start_new(void) API {
    u16 i;
    u8 *p = (u8 *)&g;
    for (i = 0; i < sizeof(Game); i++) p[i] = 0;
    g.hp = 20; g.maxhp = 20; g.lv = 1;
    g.name[0] = 'K'; g.name[1] = 'I'; g.name[2] = 'D';
    g.vars[V_NG] = meta.ng; g.vars[V_PREV_ENDING] = meta.prev_end;
    g.vars[V_USER] = meta.prev_moral;      /* user var 0 mirrors previous run's morality */
    if (meta.ng) { g.gold = 30; item_add(1); }
    g_mode = M_PLAY; pmode = P_WORLD;
    game_flag_title = 0;
    audio_stop();
    ui_say_open_y = 96; ui_say_close_y = 144;
    /* prologue chunk is content chunk id stored in CH_MAPS entry 255? -> map 0 runs its enter script */
    world_mode_flag = 0;
    play_start_map(0, 0, 0, 0);
}
void play_start_map(u8 map, u8 x, u8 y, u8 d) API {
    u8 sx = x, sy = y;
    u8 b[4];
    if (map == 0 && x == 0 && y == 0) { plat_chunk_read(CH_MAPS, 510, b, 4); sx = b[0]; sy = b[1]; d = b[2]; }
    world_load(map, sx, sy, d);
    vm_ctx = 0;
    vm_set_chunk(world_cur_chunk());
    {
        u16 es = world_take_script();
        if (es) vm_start(es);
    }
}
void game_continue(void) API {
    u8 x, y;
    recalc_stats();
    g_mode = M_PLAY; pmode = P_WORLD; game_flag_title = 0;
    ui_say_open_y = 96; ui_say_close_y = 144; world_mode_flag = 0;
    x = g.px; y = g.py;
    world_load(g.map, x, y, g.dir);
    vm_ctx = 0;
    vm_set_chunk(world_cur_chunk());
    (void)world_take_script();
}

/* ---------- pause menu ---------- */
void menu_pause(void) API {
    pmode = P_MENU; menu_cur = 0; menu_sub = 0; stats_open = 0;
    ui_clear_win(); ui_win(0);
}
static void menu_draw(void) {
    u8 i, n;
    ui_clear_win();
    ui_box(0, 0, 8, 9);
    ui_print(2, 1, ui_str(S_ITEMS)); ui_print(2, 3, ui_str(S_STATS)); ui_print(2, 5, ui_str(S_OPTIONS)); ui_print(2, 7, ui_str(S_RESUME));
    for (i = 0; i < 4; i++) plat_win_set(1, (u8)(1 + i * 2), (menu_sub == 0 && i == menu_cur) ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
    ui_box(8, 0, 12, 9);
    ui_print(9, 1, ui_str(S_LV)); ui_num(12, 1, g.lv, 2);
    ui_print(9, 3, ui_str(S_HP)); ui_num(12, 3, g.hp, 2); ui_print(14, 3, (const u8 *)"/"); ui_num(15, 3, g.maxhp, 2);
    ui_print(9, 5, ui_str(S_GOLD)); ui_num(14, 5, g.gold, 4);
    ui_print(9, 7, ui_str(S_PLAYTIME)); ui_num(14, 7, (u16)(g.secs / 60), 3);
    ui_box(0, 9, 20, 9);
    n = 0;
    for (i = 0; i < 8; i++) if (g.inv[i]) { item_name_print((u8)(3 + (n & 1) * 9), (u8)(10 + (n >> 1) * 2), g.inv[i]); n++; }
    if (menu_sub == 1) { u8 k; for (k = 0; k < 8; k++) plat_win_set((u8)(2 + (k & 1) * 9), (u8)(10 + (k >> 1) * 2), (k == menu_cur && k < n) ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI); }
}
u8 menu_tick(void) API {
    static u8 first;
    if (!first || pmode != P_MENU) { first = 1; menu_draw(); }
    if (menu_sub == 0) {
        if (g_pressed & K_UP) { menu_cur = menu_cur ? (u8)(menu_cur - 1) : 3; audio_sfx(0); menu_draw(); }
        if (g_pressed & K_DOWN) { menu_cur = menu_cur < 3 ? (u8)(menu_cur + 1) : 0; audio_sfx(0); menu_draw(); }
        if (g_pressed & (K_B | K_START)) { first = 0; ui_win(144); return 1; }
        if (g_pressed & K_A) {
            audio_sfx(1);
            if (menu_cur == 0) { menu_sub = 1; menu_cur = 0; menu_draw(); }
            else if (menu_cur == 3) { first = 0; ui_win(144); return 1; }
            else if (menu_cur == 2) { first = 0; game_options_open(); return 0; }
        }
    } else {
        u8 n = 0, i;
        for (i = 0; i < 8; i++) if (g.inv[i]) n++;
        if (g_pressed & K_B) { menu_sub = 0; menu_cur = 0; menu_draw(); }
        if (g_pressed & K_UP) { if (menu_cur >= 2) menu_cur -= 2; menu_draw(); }
        if (g_pressed & K_DOWN) { if (menu_cur + 2 < n) menu_cur += 2; menu_draw(); }
        if (g_pressed & K_LEFT) { if (menu_cur & 1) menu_cur--; menu_draw(); }
        if (g_pressed & K_RIGHT) { if (!(menu_cur & 1) && menu_cur + 1 < n) menu_cur++; menu_draw(); }
        if (g_pressed & K_A) { if (menu_cur < n) { items_use(menu_cur); menu_draw(); } }
    }
    return 0;
}

/* ---------- shop ---------- */
void shop_open(u8 id) API {
    u8 b[10], i;
    plat_chunk_read(CH_SHOPS, (u16)(id * 10), b, 10);
    shop_n = b[0]; for (i = 0; i < 8; i++) shop_ents[i] = b[1 + i];
    shop_cur = 0; shop_msg = 0;
    pmode = P_SHOP;
    ui_clear_win(); ui_win(0);
}
static void shop_draw(void) {
    u8 i, b[14];
    ui_clear_win(); ui_box(0, 0, 20, 18);
    ui_print(8, 1, ui_str(S_BUY));
    ui_print(2, 15, ui_str(S_GOLD)); ui_num(7, 15, g.gold, 4);
    for (i = 0; i < shop_n; i++) {
        u8 y = (u8)(3 + i * 2);
        item_name_print(3, y, shop_ents[i]);
        item_read(shop_ents[i], b);
        ui_num(15, y, rd16(b + 12), 3);
        plat_win_set(2, y, i == shop_cur ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
    }
    ui_print(3, (u8)(3 + shop_n * 2), ui_str(S_SELL));
    plat_win_set(2, (u8)(3 + shop_n * 2), shop_cur == shop_n ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
    if (shop_msg == 1) ui_print(2, 13, ui_str(S_NOMONEY));
    if (shop_msg == 2) ui_print(2, 13, ui_str(S_FULL));
}
u8 shop_tick(void) API {
    static u8 first;
    if (!first) { first = 1; shop_draw(); }
    if (g_pressed & K_UP) { shop_cur = shop_cur ? (u8)(shop_cur - 1) : shop_n; audio_sfx(0); shop_msg = 0; shop_draw(); }
    if (g_pressed & K_DOWN) { shop_cur = shop_cur < shop_n ? (u8)(shop_cur + 1) : 0; audio_sfx(0); shop_msg = 0; shop_draw(); }
    if (g_pressed & K_B) { first = 0; ui_win(144); pmode = P_WORLD; return 1; }
    if (g_pressed & K_A) {
        if (shop_cur == shop_n) { first = 0; ui_win(144); pmode = P_WORLD; return 1; }
        {
            u8 b[14];
            item_read(shop_ents[shop_cur], b);
            if (g.gold < rd16(b + 12)) { shop_msg = 1; audio_sfx(14); }
            else if (!item_add(shop_ents[shop_cur])) { shop_msg = 2; audio_sfx(14); }
            else { g.gold = (u16)(g.gold - rd16(b + 12)); shop_msg = 0; audio_sfx(12); }
            shop_draw();
        }
    }
    return 0;
}

/* ---------- naming ---------- */
static const u8 *name_chars(void) { return (const u8 *)"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"; }
void name_enter(void) API { name_cur = 0; name_len = 0; { u8 i; for (i = 0; i < 8; i++) g.name[i] = 0; } ui_clear_win(); ui_win(0); }
static void name_draw(void) {
    u8 i, n = 0;
    ui_clear_win();
    ui_print(2, 0, ui_str(S_NAMEPROMPT));
    for (i = 0; i < 6; i++) plat_win_set((u8)(7 + i), 2, g.name[i] ? (u8)(T_FONT + g.name[i] - 32) : (u8)(T_FONT + '_' - 32), P_UI);
    {
        u8 r, cc;
        const u8 *ch = name_chars();
        for (r = 0; r < 7; r++) for (cc = 0; cc < 9; cc++) {
            u8 idx = (u8)(r * 9 + cc);
            if (idx < 62) { plat_win_set((u8)(2 + cc * 2), (u8)(5 + r * 2), (u8)(T_FONT + ch[idx] - 32), P_UI); plat_win_set((u8)(1 + cc * 2), (u8)(5 + r * 2), idx == name_cur ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI); }
        }
    }
    ui_print(3, 3, (const u8 *)"START=OK B=DEL");
    (void)n;
}
u8 name_tick(void) API {
    static u8 first;
    if (!first) { first = 1; name_draw(); }
    if (g_pressed & K_LEFT) { name_cur = name_cur ? (u8)(name_cur - 1) : 61; name_draw(); }
    if (g_pressed & K_RIGHT) { name_cur = name_cur < 61 ? (u8)(name_cur + 1) : 0; name_draw(); }
    if (g_pressed & K_UP) { name_cur = (u8)(name_cur >= 9 ? name_cur - 9 : name_cur); name_draw(); }
    if (g_pressed & K_DOWN) { name_cur = (u8)(name_cur + 9 < 62 ? name_cur + 9 : name_cur); name_draw(); }
    if (g_pressed & K_A) { if (name_len < 6) { g.name[name_len++] = name_chars()[name_cur]; audio_sfx(0); name_draw(); } }
    if (g_pressed & K_B) { if (name_len) { g.name[--name_len] = 0; name_draw(); } }
    if (g_pressed & K_START) {
        if (!name_len) { g.name[0] = 'K'; g.name[1] = 'I'; g.name[2] = 'D'; }
        first = 0; ui_win(144); audio_sfx(1); return 1;
    }
    return 0;
}

/* ---------- save point ---------- */
void save_menu_open(void) API {
    save_cur = 0;
    ui_clear_win(); ui_win(0);
    g.hp = g.maxhp;
    audio_sfx(6);
}
static void save_draw(void) {
    u8 i;
    ui_clear_win(); ui_box(0, 0, 20, 18);
    ui_print(7, 1, ui_str(S_SAVE));
    for (i = 0; i < 3; i++) {
        u8 y = (u8)(4 + i * 3);
        ui_print(4, y, ui_str(S_SLOT)); ui_num(9, y, (u16)(i + 1), 1);
        ui_print(11, y, ui_str(save_slot_used(i) ? S_PLAYTIME : S_EMPTY));
        plat_win_set(2, y, i == save_cur ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
    }
    ui_print(4, 13, ui_str(S_BACK));
    plat_win_set(2, 13, save_cur == 3 ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
}
u8 save_menu_tick(void) API {
    static u8 first, done;
    if (!first) { first = 1; done = 0; save_draw(); }
    if (done) {
        if (g_pressed & (K_A | K_B)) { first = 0; ui_win(144); return 1; }
        return 0;
    }
    if (g_pressed & K_UP) { save_cur = save_cur ? (u8)(save_cur - 1) : 3; audio_sfx(0); save_draw(); }
    if (g_pressed & K_DOWN) { save_cur = save_cur < 3 ? (u8)(save_cur + 1) : 0; audio_sfx(0); save_draw(); }
    if (g_pressed & K_B) { first = 0; ui_win(144); return 1; }
    if (g_pressed & K_A) {
        if (save_cur == 3) { first = 0; ui_win(144); return 1; }
        {
            u8 wx, wy;
            world_player_pos(&wx, &wy);
            g.px = (u8)((wx + 8) >> 4); g.py = (u8)((wy + 8) >> 4);
        }
        save_write(save_cur);
        ui_clear_win(); ui_box(0, 6, 20, 5);
        ui_print(1, 8, ui_str(S_SAVED));
        audio_sfx(6);
        done = 1;
    }
    return 0;
}

/* ---------- endings + credits ---------- */
void game_ending(u8 id) API {
    /* ending scripts are run by the script (chunk); this op shows the credits roll afterwards */
    end_id = id; pmode = P_CREDITS;
    ui_clear_win(); ui_win(0);
    credits_y = 0; credits_off = 0; credits_sz = plat_chunk_size(CH_CREDITS);
    { u8 i; for (i = 0; i < 40; i++) plat_spr(i, 0, 200, 0, 0); }
    plat_bg_fill(0, 0, 32, 32, T_BLACK, P_UI);
    plat_scroll(0, 0);
    meta.endings |= (u8)(1 << (id - 1)); meta.ng++; meta.prev_end = id; meta.prev_moral = moral();
    meta_save();
}
static u8 credits_tick(void) {
    static u8 t;
    t++;
    if ((t & 1) == 0) {
        credits_y++;
        if ((credits_y & 7) == 0) {
            /* shift window map up a row by redrawing: simplest = print next line at bottom and scroll via text redraw */
        }
    }
    {
        u16 base = (u16)(credits_y / 8);
        u8 row;
        static u16 lastbase = 0xFFFF;
        if (base != lastbase) {
            lastbase = base;
            plat_chunk_read(CH_CREDITS, 0, g_scene, SCENE_MAX);
            for (row = 0; row < 18; row++) {
                u16 ln = (u16)(base + row), p = 0, cnt = 0;
                u8 x = 0;
                plat_win_fill(0, row, 20, 1, T_BLACK, P_UI);
                while (p < credits_sz && cnt < ln) { if (g_scene[p] == 0x0A) cnt++; p++; }
                if (cnt == ln) {
                    u8 len = 0;
                    while (p + len < credits_sz && g_scene[p + len] != 0x0A && len < 20) len++;
                    x = (u8)((20 - len) / 2);
                    { u8 k; for (k = 0; k < len; k++) plat_win_set((u8)(x + k), row, (u8)(T_FONT + g_scene[p + k] - 32), P_UI); }
                }
            }
        }
        if (base > 130 || (g_pressed & K_START && credits_y > 40)) { lastbase = 0xFFFF; return 1; }
    }
    return 0;
}

/* ---------- main per-frame play dispatcher ---------- */
static u16 rnd_battle;
void game_play_frame(void) API {
    u16 s;
    static u8 secs_t;
    if (game_flag_title == 2) { game_flag_title = 0; vm_stop(); pmode = P_WORLD; game_title(); return; }
    if (++secs_t >= 60) { secs_t = 0; if (g.secs < 65000) g.secs++; }
    if (pmode == P_CREDITS) {
        if (credits_tick()) { pmode = P_WORLD; vm_stop(); game_title(); }
        return;
    }
    if (pmode == P_MENU) { if (menu_tick()) pmode = P_WORLD; return; }
    if (pmode == P_ENDING) {
        /* random-encounter battle in progress */
        if (battle_tick()) {
            world_restore(); pmode = P_WORLD;
            if (game_flag_title == 2) return;
        }
        return;
    }
    if (vm_running()) {
        world_mode_flag = 1;
        vm_tick();
        if (!vm_running()) world_mode_flag = 0;
        if (!vm_fullscreen()) { world_tick(); if (pmode == P_WORLD) world_draw(); }
        return;
    }
    world_mode_flag = 0;
    world_tick();
    s = world_take_script();
    if (s) { vm_ctx = 0; vm_start(s); world_mode_flag = 1; }
    else {
        u16 b = world_take_battle();
        if (b) { rnd_battle = b; battle_start(b); pmode = P_ENDING; return; }
    }
    if (g_pressed & K_START) { menu_pause(); return; }
    if (g_pressed & K_SELECT) { menu_pause(); menu_sub = 1; return; }
    world_draw();
}

/* test hook: jump straight into a map with preset variables (used by headless tests and the playthrough bot) */
void game_debug_apply(u8 map, u8 x, u8 y, u8 d, u8 n, const u8 *idx, const u8 *val) API {
    u8 i;
    game_start_new();
    for (i = 0; i < n; i++) g.vars[idx[i]] = val[i];
    world_load(map, x, y, d);
    vm_ctx = 0; vm_set_chunk(world_cur_chunk()); vm_stop();
    (void)world_take_script();
    g_mode = M_PLAY;
}
