#if defined(__SDCC)
#pragma bank 255
#endif
#include "lt.h"
#include "gen_strings.h"
/* Battle: command menu (ATTACK/LISTEN/ITEM/RELEASE), enemy turns driven by battle scripts, and the
   bullet box with parametric emitters. */
#if defined(__SDCC)
#define MAXB 16
#define DENS 5
#define HITR 4
#else
#define MAXB 40
#define DENS 8
#define HITR 3
#endif
#define BS_SCRIPT 0
#define BS_MENU 1
#define BS_LISTEN 2
#define BS_ITEM 3
#define BS_ATKBAR 4
#define BS_DODGE 5
#define BS_FINISH 6
#define BS_DEAD 7
#define BS_WAIT 8
#define BS_FLAVOR 9

typedef struct { u8 kind, ox, oy, speed, angle, spread, count, period, start, dur, param, gfx, timer, cnt, ang; } Em;
typedef struct { s16 x, y; s8 vx, vy; u8 age, gfx, beh, bnc; } Bul;
static Em em[4];
static Bul bl[MAXB];
static u8 nem, bs, bs_next, bmsel, bsub, bitem_n, result, spareable, pat_len_t, pat_dmg, atk_x, atk_dir, flags, nlisten, npat, boxw, boxh, tgtw, tgth, walt;
static u16 ehp, emax, gfx_chunk, bchunk, flavor_off, pat_frames, dodge_t;
static u8 ew, eh, eframes, eanim, atk_val, deadsel, resolved, shield_t, shield_cd, invuln, sx, sy;
static s16 soul_x, soul_y;
static u8 bx0, by0, box_step, flavor_shown, flavor_after;
u8 bt_wait;
extern u8 game_flag_title;
extern u8 vm_ctx;

static u8 name_buf[13];
static const u8 *EN(void) { u8 i; for (i = 0; i < 12; i++) name_buf[i] = g_scene[BH_NAME + i]; name_buf[12] = 0; return name_buf; }

/* ---------- drawing helpers ---------- */
static void draw_enemy(u8 frame) {
    u8 x, y, x0 = (u8)((20 - ew) / 2);
    for (y = 0; y < eh; y++)
        for (x = 0; x < ew; x++) plat_bg_set((u8)(x0 + x), y, (u8)(T_ENEMY + frame * ew * eh + y * ew + x), P_ZONE);
}
static void load_enemy_gfx(u16 chunk) {
    u8 hdr[16], j;
    u16 pc[4];
    plat_chunk_read(chunk, 0, hdr, 16);
    ew = hdr[0]; eh = hdr[1]; eframes = hdr[2];
    for (j = 0; j < 4; j++) pc[j] = rd16(hdr + 8 + j * 2);
    plat_pal(P_ZONE, pc);
    {
        u16 sz = plat_chunk_size(chunk), off = 16, t = T_ENEMY;
        while (off < sz) {
            u16 n = sz - off;
            if (n > 512) n = 512;
            plat_chunk_read(chunk, off, g_tmp, n);
            plat_tiles((u8)t, g_tmp, (u8)(n / 16));
            t = (u16)(t + n / 16); off = (u16)(off + n);
        }
    }
    gfx_chunk = chunk;
}
static void hp_draw(u8 win, u8 y) {
    u8 i, fill = (u8)((u16)g.hp * 40 / (g.maxhp ? g.maxhp : 1));  /* 0..40 px over 5 tiles */
    void (*dummy)(void) = 0; (void)dummy;
    for (i = 0; i < 5; i++) {
        u8 f = fill > (u8)(i * 8) ? (u8)(fill - i * 8) : 0;
        if (f > 8) f = 8;
        if (win) plat_win_set((u8)(9 + i), y, (u8)(T_UI + UI_HP0 + f), P_UI); else plat_bg_set((u8)(9 + i), y, (u8)(T_UI + UI_HP0 + f), P_UI);
    }
}
static void status_draw(u8 win, u8 y) {
    /* "LV 1 HP ##### 20/20" */
    const u8 *t;
    u8 i;
    if (win) { for (i = 0; i < 20; i++) plat_win_set(i, y, T_BLACK, P_UI); } else for (i = 0; i < 20; i++) plat_bg_set(i, y, T_BLACK, P_UI);
    t = ui_str(S_LV);
    if (win) { ui_print(1, y, t); ui_num(4, y, g.lv, 2); ui_print(7, y, ui_str(S_HP)); } else { u8 d[3]; ui_print_bg(1, y, t); d[0] = (u8)('0' + g.lv / 10); d[1] = (u8)('0' + g.lv % 10); d[2] = 0; ui_print_bg(4, y, d); ui_print_bg(7, y, ui_str(S_HP)); }
    hp_draw(win, y);
    if (win) { ui_num(15, y, g.hp, 2); plat_win_set(17, y, (u8)(T_FONT + '/' - 32), P_UI); ui_num(18, y, g.maxhp, 2); }
    else { /* BG numbers via manual */
        u8 d[3]; d[0] = (u8)('0' + g.hp / 10); d[1] = (u8)('0' + g.hp % 10); d[2] = 0;
        ui_print_bg(15, y, d); plat_bg_set(17, y, (u8)(T_FONT + '/' - 32), P_UI);
        d[0] = (u8)('0' + g.maxhp / 10); d[1] = (u8)('0' + g.maxhp % 10); ui_print_bg(18, y, d);
    }
}
static void panel_open(void) {
    ui_clear_win();
    ui_say_open_y = 56; ui_say_close_y = 56;
    ui_win(56);
    ui_box(0, 0, 20, 6);
    status_draw(1, 9);
}
static void cmd_draw(void) {
    u8 i;
    ui_print(3, 6, ui_str(S_ATTACK)); ui_print(12, 6, ui_str(S_ITEM));
    ui_print(3, 7, ui_str(S_LISTEN)); ui_print(12, 7, ui_str(S_RELEASE));
    for (i = 0; i < 4; i++) plat_win_set((u8)((i & 1) ? 11 : 2), (u8)(6 + (i >> 1)), i == bmsel ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
}
static void flavor_print(void) {
    const u8 *p;
    u8 x = 1, y = 1;
    plat_win_fill(1, 1, 18, 4, T_BLACK, P_UI);
    if (!flavor_off) return;
    p = g_scene + flavor_off;
    while (*p) { if (*p == 0x0A) { y++; x = 1; } else if (*p >= 32 && x < 19) { plat_win_set(x++, y, (u8)(T_FONT + *p - 32), P_UI); } p++; }
}
static void box_draw(void) {
    u8 x0t = (u8)((160 - boxw * 8) / 16 * 2 / 2), y0t, w = boxw, h = boxh;
    u8 i, j;
    x0t = (u8)((20 - w) / 2);
    y0t = (u8)(11 - h / 2);
    /* clear battle area rows 7..15 */
    for (j = 7; j < 16; j++) for (i = 0; i < 20; i++) plat_bg_set(i, j, T_BLACK, P_UI);
    ui_box_bg((u8)(x0t - 1), (u8)(y0t - 1), (u8)(w + 2), (u8)(h + 2));
    bx0 = (u8)(x0t * 8); by0 = (u8)(y0t * 8);
}
static void sprites_off(void) { u8 i; for (i = 0; i < 40; i++) plat_spr(i, 0, 200, 0, 0); }

/* ---------- setup ---------- */
void battle_start(u16 chunk) API {
    u8 i;
    u16 pc[4];
    bchunk = chunk;
    fx_fade(8, 1); while (fx_busy()) { fx_tick(); plat_vsync(); }
    plat_lcd(0);
    audio_stop();
    plat_chunk(chunk, g_scene, SCENE_MAX);
    vm_ctx = 1; vm_set_chunk(chunk); vm_ctx = 0;
    load_tiles(CH_TILES_UI, 0);
    load_pal(CH_PAL_UI, P_UI, 1);
    plat_chunk_read(CH_BSPR, 0, g_tmp, 16);
    for (i = 0; i < 4; i++) pc[i] = rd16(g_tmp + i * 2); plat_pal(P_BULLET, pc);
    for (i = 0; i < 4; i++) pc[i] = rd16(g_tmp + 8 + i * 2); plat_pal(P_SOUL, pc);
    plat_chunk_read(CH_BSPR, 16, g_tmp, 256); plat_tiles(T_BSPR, g_tmp, 16);
    plat_bg_fill(0, 0, 32, 32, T_BLACK, P_UI);
    load_enemy_gfx(rd16(g_scene + BH_GFX));
    draw_enemy(0);
    flags = g_scene[BH_FLAGS]; ehp = rd16(g_scene + BH_HP); emax = ehp;
    nlisten = g_scene[BH_NLISTEN]; npat = g_scene[BH_NPAT];
    set_dmg(0xE4, 0xE4, 0xE4);
    for (i = V_BT_TURN; i < V_BT_FLAG0 + 8; i++) g.vars[i] = 0;
    spareable = 0; flavor_off = 0; bmsel = 0; resolved = 0; shield_cd = 0; invuln = 0; eanim = 0;
    boxw = 12; boxh = 5; tgtw = 12; tgth = 5;
    sprites_off();
    status_draw(0, 17);
    panel_open();
    plat_scroll(0, 0);
    plat_lcd(1);
    audio_play(g_scene[BH_MUSIC]);
    fx_fade(0, 2);
    audio_sfx(16);
    bs = BS_SCRIPT; bs_next = BS_MENU;
    vm_ctx = 1; vm_start(rd16(g_scene + BH_INTRO)); vm_ctx = 0;
}
u8 battle_running(void) API { return 1; }

/* ---------- emitters / bullets ---------- */
static void pattern_load(u8 n) {
    u16 po = rd16(g_scene + BH_PAT + 0);
    u16 o = rd16(g_scene + po + n * 2);
    const u8 *p = g_scene + o;
    u8 i, j;
    pat_frames = (u16)(p[0] * 4); tgtw = p[1]; tgth = p[2]; pat_dmg = p[3]; nem = p[4];
    if (nem > 4) nem = 4;
    for (i = 0; i < nem; i++) {
        const u8 *q = p + 5 + i * 12;
        em[i].kind = q[0]; em[i].ox = q[1]; em[i].oy = q[2]; em[i].speed = q[3]; em[i].angle = q[4]; em[i].spread = q[5];
        em[i].count = q[6]; em[i].period = q[7]; em[i].start = q[8]; em[i].dur = q[9]; em[i].param = q[10]; em[i].gfx = q[11];
        em[i].timer = em[i].start; em[i].cnt = 0; em[i].ang = 0;
    }
    for (j = 0; j < MAXB; j++) bl[j].gfx = 255;
}
static void spawn(s16 px, s16 py, u8 ang, u8 spd, u8 gfx) {
    u8 i;
    s16 vx, vy;
    for (i = 0; i < MAXB; i++) if (bl[i].gfx == 255) break;
    if (i == MAXB) return;
    if (meta.assist) spd = (u8)(spd * 7 / 10);
    vx = (s16)(((s16)icos(ang) * spd) >> 7); vy = (s16)(((s16)isin(ang) * spd) >> 7);
    bl[i].x = (s16)(px * 16); bl[i].y = (s16)(py * 16); bl[i].vx = (s8)vx; bl[i].vy = (s8)vy; bl[i].age = 0;
    bl[i].gfx = (u8)(gfx & 15); bl[i].beh = (u8)(gfx >> 4); bl[i].bnc = 0;
}
static u8 eff_count(u8 c) { u16 n = (u16)(c * DENS / 8); return (u8)(n ? n : 1); }
static void em_fire(Em *e) {
    u8 n = eff_count(e->count), k, a;
    s16 ox = (s16)bx0 + (s16)((u16)e->ox * (boxw * 8) / 256), oy = (s16)by0 + (s16)((u16)e->oy * (boxh * 8) / 256);
    s16 cx = soul_x + 4, cy = soul_y + 4;
    s16 bwp = (s16)boxw * 8, bhp = (s16)boxh * 8;
    switch (e->kind) {
    case 0: { u8 base = iatan((s16)(cy - oy), (s16)(cx - ox)); for (k = 0; k < n; k++) { a = (u8)(base - e->spread / 2 + (n > 1 ? (u16)e->spread * k / (n - 1) : 0)); spawn((s16)(ox - 4), (s16)(oy - 4), a, e->speed, e->gfx); } } break;
    case 1: for (k = 0; k < n; k++) { a = (u8)(e->angle + (e->spread == 255 ? (u16)256 * k / n : (n > 1 ? (u16)e->spread * k / (n - 1) : 0)) - (e->spread == 255 ? 0 : e->spread / 2)); spawn((s16)(ox - 4), (s16)(oy - 4), a, e->speed, e->gfx); } break;
    case 2: for (k = 0; k < n; k++) spawn((s16)(bx0 + rnd() % (u8)(bwp - 8)), (s16)(by0 - 6), (u8)(64 + (rnd() & 7) - 4 + (e->spread ? (rnd() % e->spread) - e->spread / 2 : 0)), e->speed, e->gfx); break;
    case 3: { u8 base = (u8)(e->angle + (((s16)isin((u8)(e->cnt * e->param)) * e->spread) >> 7)); for (k = 0; k < n; k++) spawn((s16)(ox - 4), (s16)(oy - 4), (u8)(base + (n > 1 ? k * 6 : 0)), e->speed, e->gfx); e->cnt++; } break;
    case 4: { u8 base = (u8)(e->angle + e->cnt * e->param); for (k = 0; k < n; k++) spawn((s16)(ox - 4), (s16)(oy - 4), (u8)(base + (u16)256 * k / n), e->speed, e->gfx); e->cnt++; } break;
    case 5: { u8 gap = (u8)(rnd() % (n > 3 ? n - 2 : 1)); for (k = 0; k < n; k++) { if (k == gap || k == gap + 1) continue; if (e->angle == 64) spawn((s16)(bx0 + (s16)k * (bwp - 8) / (n > 1 ? n - 1 : 1)), (s16)(by0 - 6), 64, e->speed, e->gfx); else if (e->angle == 192) spawn((s16)(bx0 + (s16)k * (bwp - 8) / (n > 1 ? n - 1 : 1)), (s16)(by0 + bhp - 2), 192, e->speed, e->gfx); else if (e->angle == 0) spawn((s16)(bx0 - 6), (s16)(by0 + (s16)k * (bhp - 8) / (n > 1 ? n - 1 : 1)), 0, e->speed, e->gfx); else spawn((s16)(bx0 + bwp - 2), (s16)(by0 + (s16)k * (bhp - 8) / (n > 1 ? n - 1 : 1)), 128, e->speed, e->gfx); } } break;
    case 6: for (k = 0; k < n; k++) { if (e->angle < 64) spawn((s16)(bx0 - 6), (s16)(by0 + rnd() % (u8)(bhp - 8)), (u8)(e->angle + (rnd() & 7) - 4), e->speed, e->gfx); else spawn((s16)(bx0 + bwp - 2), (s16)(by0 + rnd() % (u8)(bhp - 8)), (u8)(128 + (rnd() & 7) - 4), e->speed, e->gfx); } break;
    case 7: { u8 base = (u8)(e->cnt * 16); for (k = 0; k < n; k++) { a = (u8)(base + (u16)256 * k / n); spawn((s16)(cx - 4 + ((s16)icos(a) * e->param) / 127), (s16)(cy - 4 + ((s16)isin(a) * e->param) / 127), (u8)(a + 128), e->speed, e->gfx); } e->cnt++; } break;
    default: break;
    }
    (void)oy; (void)a;
}
static void soul_reset(void) {
    soul_x = (s16)(bx0 + boxw * 4 - 4); soul_y = (s16)(by0 + boxh * 4 - 4);
}
static void dodge_begin(u8 n) {
    u8 i;
    pattern_load(n);
    tgtw = tgtw ? tgtw : 12; tgth = tgth ? tgth : 5;
    bs = BS_DODGE; dodge_t = 0; shield_t = 0; invuln = 0; walt = 0;
    boxw = tgtw; boxh = tgth;
    ui_win(144);
    box_draw();
    soul_reset();
    for (i = 0; i < 40; i++) plat_spr(i, 0, 200, 0, 0);
    g.vars[V_BT_HITS] = 0; g.vars[V_BT_SHIELD] = 0; g.vars[V_BT_MOVED] = 0;
}
static void dodge_end(void) {
    u8 i;
    for (i = 0; i < 40; i++) plat_spr(i, 0, 200, 0, 0);
    for (i = 8; i < 16; i++) { /* clear battle area */ }
    plat_bg_fill(0, 7, 20, 9, T_BLACK, P_UI);
    ui_win(56);
    status_draw(1, 9);
    bs = BS_SCRIPT;
    g.vars[V_BT_TURN]++;
}
static void dodge_tick(void) {
    u8 i, k, spd = 1, moved = 0;
    s16 dx = 0, dy = 0;
    dodge_t++;
    /* box tween handled instantly at dodge_begin (shape per pattern) */
    /* soul movement: 1px/frame, +1 every other frame */
    spd = (u8)(1 + ((dodge_t & 1) ? 1 : 0));
    if (g_keys & K_LEFT) dx = -spd; if (g_keys & K_RIGHT) dx = spd; if (g_keys & K_UP) dy = -spd; if (g_keys & K_DOWN) dy = spd;
    if (dx || dy) { moved = 1; g.vars[V_BT_MOVED] = 1; }
    soul_x += dx; soul_y += dy;
    if (soul_x < bx0) soul_x = bx0; if (soul_x > bx0 + boxw * 8 - 8) soul_x = (s16)(bx0 + boxw * 8 - 8);
    if (soul_y < by0) soul_y = by0; if (soul_y > by0 + boxh * 8 - 8) soul_y = (s16)(by0 + boxh * 8 - 8);
    (void)moved;
    /* shield */
    if (shield_cd) shield_cd--;
    if (shield_t) shield_t--;
    if ((g_pressed & K_B) && !shield_t && !shield_cd) { shield_t = 14; shield_cd = (u8)(meta.assist ? 36 : 56); audio_sfx(4); }
    if (invuln) invuln--;
    /* emitters */
    for (i = 0; i < nem; i++) {
        Em *e = &em[i];
        if (dodge_t < e->start) continue;
        if (e->dur && dodge_t > (u16)(e->start + e->dur * 2)) continue;
        if (e->timer) { e->timer--; continue; }
        e->timer = e->period ? (u8)(e->period - 1) : 0;
        em_fire(e);
    }
    /* bullets */
    for (i = 0; i < MAXB; i++) {
        Bul *b = &bl[i];
        s16 px, py, ddx, ddy;
        u8 r;
        if (b->gfx == 255) continue;
        b->age++;
        if (b->beh == 1 && (b->age & 3) == 0 && b->vy < 60) b->vy++;
        if (b->beh == 4 && (b->age & 7) == 0) { if (soul_x * 16 > b->x) { if (b->vx < 14) b->vx++; } else if (b->vx > -14) b->vx--; if (soul_y * 16 > b->y) { if (b->vy < 14) b->vy++; } else if (b->vy > -14) b->vy--; }
        b->x += b->vx; b->y += b->vy;
        if (b->beh == 2) b->x += (s16)(isin((u8)(b->age * 6)) >> 4);
        px = (s16)(b->x >> 4); py = (s16)(b->y >> 4);
        if (b->beh == 3 && b->bnc < 4) {
            if (px < bx0 || px > bx0 + boxw * 8 - 8) { b->vx = (s8)-b->vx; b->bnc++; }
            if (py < by0 || py > by0 + boxh * 8 - 8) { b->vy = (s8)-b->vy; b->bnc++; }
        }
        if (px < bx0 - 24 || px > bx0 + boxw * 8 + 24 || py < by0 - 24 || py > by0 + boxh * 8 + 24 || (b->beh == 5 && b->age > 90)) { b->gfx = 255; continue; }
        ddx = (s16)(px + 4 - (soul_x + 4)); ddy = (s16)(py + 4 - (soul_y + 4));
        if (shield_t && ddx > -10 && ddx < 10 && ddy > -10 && ddy < 10) { b->gfx = 255; g.vars[V_BT_SHIELD]++; audio_sfx(5); continue; }
        r = HITR;
        if (b->gfx == 4) { if ((ddx < -5 || ddx > 5) || (ddy < -(r - 1) || ddy > (r - 1))) continue; }
        else if (ddx < -r || ddx > r || ddy < -r || ddy > r) continue;
        if (!invuln) {
            u8 dmg = pat_dmg ? pat_dmg : g_scene[BH_ATK];
            if (meta.assist && dmg > 1) dmg--;
            if (dmg >= g.hp) g.hp = 0; else g.hp = (u8)(g.hp - dmg);
            invuln = 40; g.vars[V_BT_HITS]++;
            audio_sfx(3); world_shake(8, 2);
            if (!meta.no_flash) fx_flash(6);
            b->gfx = 255;
            status_draw(0, 17);
            if (g.hp == 0) { bs = BS_DEAD; deadsel = 0; return; }
        }
    }
    /* draw */
    {
        u8 inv_blink = (u8)(invuln && (invuln & 4));
        plat_spr(0, soul_x, soul_y, (u8)(T_BSPR + (invuln ? 1 : 0)), (u8)(P_SOUL - 8));
        if (inv_blink) plat_spr(0, 0, 200, 0, 0);
        if (shield_t) {
            s16 sx2 = (s16)(soul_x - 4), sy2 = (s16)(soul_y - 4);
            plat_spr(1, sx2, sy2, (u8)(T_BSPR + 2), (u8)(P_BULLET - 8)); plat_spr(2, (s16)(sx2 + 8), sy2, (u8)(T_BSPR + 3), (u8)(P_BULLET - 8));
            plat_spr(3, sx2, (s16)(sy2 + 8), (u8)(T_BSPR + 4), (u8)(P_BULLET - 8)); plat_spr(4, (s16)(sx2 + 8), (s16)(sy2 + 8), (u8)(T_BSPR + 5), (u8)(P_BULLET - 8));
        } else for (k = 1; k < 5; k++) plat_spr(k, 0, 200, 0, 0);
        for (i = 0; i < MAXB; i++) {
            if (bl[i].gfx == 255) plat_spr((u8)(8 + i), 0, 200, 0, 0);
            else plat_spr((u8)(8 + i), (s16)(bl[i].x >> 4), (s16)(bl[i].y >> 4), (u8)(T_BSPR + 6 + bl[i].gfx), (u8)(P_BULLET - 8));
        }
    }
    /* finished when pattern time has elapsed */
    if (dodge_t >= pat_frames) {
        u8 any = 0;
        for (i = 0; i < MAXB; i++) if (bl[i].gfx != 255) any = 1;
        if (!any || dodge_t > pat_frames + 90) dodge_end();
    }
}

/* ---------- script ops from VM ---------- */
void battle_cmd(u8 op, u8 a, u8 b) API {
    switch (op) {
    case 0x24: flavor_off = (u16)(a | ((u16)b << 8)); flavor_shown = 0; break;
    case 0x25: dodge_begin(a); break;
    case 0x26: tgtw = a; tgth = b; boxw = a; boxh = b; break;
    case 0x28: spareable = a; break;
    case 0x29: if (ehp > a) ehp -= a; else ehp = 1; break;
    case 0x2B: result = a; bs = BS_FINISH; break;
    case 0x33: load_enemy_gfx((u16)(a | ((u16)b << 8))); draw_enemy(0); break;
    case 0x3B: g.vars[V_BT_FLAG0 + (a & 7)] = 1; break;
    }
}

/* ---------- main state machine ---------- */
static void finish(u8 res) {
    g.vars[V_LASTBT] = res;
    if (res == 0) {
        u16 x = g_scene[BH_EXP];
        if (flags & 1) { if (g.vars[V_BOSSKILLS] < 255) g.vars[V_BOSSKILLS]++; } else if (g.vars[V_KILLS] < 255) g.vars[V_KILLS]++;
        g.exp = (u16)(g.exp + x);
    } else if (res == 1) {
        if (flags & 1) { if (g.vars[V_BOSSSPARES] < 255) g.vars[V_BOSSSPARES]++; } else if (g.vars[V_SPARES] < 255) g.vars[V_SPARES]++;
    }
    g.gold = (u16)(g.gold + rd16(g_scene + BH_GOLD));
    recalc_stats();
}
static void list_draw(u8 listen) {
    u8 i, n = listen ? nlisten : bitem_n;
    plat_win_fill(1, 1, 18, 4, T_BLACK, P_UI);
    for (i = 0; i < n; i++) {
        u8 x = (u8)(3 + (i & 1) * 9), y = (u8)(1 + (i >> 1));
        if (listen) { u8 j; for (j = 0; j < 10; j++) { u8 c = g_scene[BH_LISTEN + i * 12 + j]; if (!c) break; plat_win_set((u8)(x + j), y, (u8)(T_FONT + c - 32), P_UI); } }
        else item_name_print(x, y, g.inv[i]);
        plat_win_set((u8)(x - 1), y, i == bsub ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
    }
}
static void flavor_begin(u8 after) {
    ui_say_open_y = 56; ui_say_close_y = 56;
    ui_hide_sprites();
    ui_win(56);
    ui_say_begin(0, 0);
    ui_say_text(g_scene + flavor_off);
    flavor_shown = 1; flavor_after = after; bs = BS_FLAVOR;
    cmd_draw(); status_draw(1, 9);
}
static void begin_menu(void) {
    bs = BS_MENU; bmsel = bmsel & 3;
    ui_say_open_y = 56; ui_say_close_y = 56;
    ui_win(56);
    ui_box(0, 0, 20, 6);
    if (flavor_off && !flavor_shown) { flavor_begin(BS_MENU); return; }
    cmd_draw();
    status_draw(1, 9);
}
static void start_turn(void) {
    bs = BS_SCRIPT; bs_next = BS_MENU;
    vm_ctx = 1; vm_start(rd16(g_scene + BH_TURN)); vm_ctx = 0;
}
u8 battle_tick(void) API {
    u8 i;
    if (invuln && bs != BS_DODGE) invuln = 0;
    if (bs == BS_DODGE) { dodge_tick(); if (bs == BS_DEAD) goto dead_init; return 0; }
    if (bs == BS_SCRIPT) {
        if (vm_running_ctx(1)) { vm_ctx = 1; vm_tick(); vm_ctx = 0; return 0; }
        if (bs == BS_SCRIPT) {
            if (bs_next == BS_FINISH) { if (flavor_off && !flavor_shown) { flavor_begin(BS_FINISH); return 0; } bs = BS_FINISH; } else if (bs_next == 100) { start_turn(); return 0; } else { begin_menu(); }
        }
        if (bs != BS_FINISH) return 0;
    }
    if (bs == BS_FINISH) {
        finish(result);
        fx_fade(8, 2); while (fx_busy()) { fx_tick(); plat_vsync(); }
        sprites_off(); ui_say_open_y = 96; ui_say_close_y = 144; ui_win(144);
        return 1;
    }
    if (bs == BS_FLAVOR) {
        if ((++eanim & 31) == 0 && eframes > 1) draw_enemy((u8)((eanim >> 5) & 1));
        if (ui_say_tick()) { if (flavor_after == BS_FINISH) bs = BS_FINISH; else { bs = BS_MENU; cmd_draw(); } }
        return 0;
    }
    /* idle animation */
    if ((++eanim & 31) == 0 && eframes > 1) draw_enemy((u8)((eanim >> 5) & 1));
    switch (bs) {
    case BS_MENU:
        if (g_pressed & K_LEFT) { bmsel &= 2; if (bmsel == 0 && 0) bmsel = 0; bmsel = (u8)(bmsel & 2); audio_sfx(0); cmd_draw(); }
        if (g_pressed & K_RIGHT) { bmsel = (u8)((bmsel & 2) | 1); audio_sfx(0); cmd_draw(); }
        if (g_pressed & K_UP) { bmsel &= 1; audio_sfx(0); cmd_draw(); }
        if (g_pressed & K_DOWN) { bmsel |= 2; audio_sfx(0); cmd_draw(); }
        if ((g_pressed & K_SELECT) && !(flags & 2)) { audio_sfx(14); if (!(flags & 1)) { fx_fade(8, 2); while (fx_busy()) { fx_tick(); plat_vsync(); } result = 2; g.vars[V_LASTBT] = 2; sprites_off(); ui_say_open_y = 96; ui_say_close_y = 144; ui_win(144); return 1; } }
        if (g_pressed & K_A) {
            audio_sfx(1);
            if (bmsel == 0) { /* ATTACK */ bs = BS_ATKBAR; atk_x = 8; atk_dir = 1; plat_win_fill(1, 1, 18, 4, T_BLACK, P_UI); for (i = 0; i < 18; i++) plat_win_set((u8)(1 + i), 3, (u8)(T_FONT + (i == 9 ? '|' : '-') - 32), P_UI); }
            else if (bmsel == 1) { /* ITEM */ bitem_n = 0; for (i = 0; i < 8; i++) if (g.inv[i]) bitem_n++; if (!bitem_n) { audio_sfx(14); } else { bs = BS_ITEM; bsub = 0; list_draw(0); } }
            else if (bmsel == 2) { /* LISTEN */ bs = BS_LISTEN; bsub = 0; list_draw(1); }
            else { /* RELEASE */
                if (spareable) { vm_ctx = 1; bs = BS_SCRIPT; bs_next = BS_FINISH; result = 1; vm_start(rd16(g_scene + BH_SPARED)); vm_ctx = 0; audio_sfx(9); }
                else { bs = BS_SCRIPT; bs_next = 100; vm_ctx = 1; vm_start(rd16(g_scene + BH_REFUSE)); vm_ctx = 0; }
            }
        }
        break;
    case BS_LISTEN:
        if (g_pressed & K_B) { begin_menu(); break; }
        if (g_pressed & K_LEFT) { if (bsub & 1) bsub--; list_draw(1); }
        if (g_pressed & K_RIGHT) { if (!(bsub & 1) && bsub + 1 < nlisten) bsub++; list_draw(1); }
        if (g_pressed & K_UP) { if (bsub >= 2) bsub -= 2; audio_sfx(0); list_draw(1); }
        if (g_pressed & K_DOWN) { if (bsub + 2 < nlisten) bsub += 2; audio_sfx(0); list_draw(1); }
        if (g_pressed & K_A) {
            u16 lab = rd16(g_scene + BH_LISTEN + bsub * 12 + 10);
            audio_sfx(1);
            g.vars[V_BT_ACTS]++; if (g.vars[V_LISTEN] < 255) g.vars[V_LISTEN]++;
            bs = BS_SCRIPT; bs_next = 100; flavor_off = 0;
            vm_ctx = 1; vm_start(lab); vm_ctx = 0;
        }
        break;
    case BS_ITEM:
        if (g_pressed & K_B) { begin_menu(); break; }
        if (g_pressed & K_LEFT) { if (bsub & 1) bsub--; list_draw(0); }
        if (g_pressed & K_RIGHT) { if (!(bsub & 1) && bsub + 1 < bitem_n) bsub++; list_draw(0); }
        if (g_pressed & K_UP) { if (bsub >= 2) bsub -= 2; list_draw(0); }
        if (g_pressed & K_DOWN) { if (bsub + 2 < bitem_n) bsub += 2; list_draw(0); }
        if (g_pressed & K_A) { items_use(bsub); flavor_off = 0; status_draw(1, 9); bs = BS_SCRIPT; bs_next = 100; start_turn(); }
        break;
    case BS_ATKBAR: {
        u8 mult, dist;
        atk_x = (u8)(atk_x + atk_dir * 3);
        if (atk_x >= 148) atk_dir = (u8)-1; if (atk_x <= 8) atk_dir = 1;
        plat_spr(0, atk_x, 56 + 24 - 4, T_BSPR, (u8)(P_SOUL - 8));
        if (g_pressed & K_A) {
            u16 dmg;
            dist = (u8)(atk_x > 80 ? atk_x - 80 : 80 - atk_x);
            mult = (u8)(dist > 72 ? 8 : (72 - dist) * 100 / 72 + 8);
            sprites_off();
            dmg = (u16)((4 + g.lv * 2) * mult / 100);
            if (flags & 4) dmg = 0;
            audio_sfx(8);
            world_shake(6, 2);
            if (dmg >= ehp) {
                ehp = 0;
                bs = BS_SCRIPT; bs_next = BS_FINISH; result = 0;
                vm_ctx = 1; vm_start(rd16(g_scene + BH_WIN)); vm_ctx = 0;
            } else { ehp = (u16)(ehp - dmg); flavor_off = 0; g.vars[V_BT_ACTS]++; start_turn(); }
        }
        if (g_pressed & K_B) { sprites_off(); begin_menu(); }
        break;
    }
    case BS_DEAD: goto dead_init;
    default: break;
    }
    return 0;
dead_init:
    {
        static u8 dead_state, dead_t;
        if (bs != BS_DEAD) return 0;
        if (!dead_state) {
            dead_state = 1; dead_t = 0; sprites_off(); audio_stop(); audio_sfx(17); fx_fade(0, 1);
            ui_win(0); ui_clear_win(); ui_print(1, 5, ui_str(S_GAMEOVER)); ui_print(5, 9, ui_str(S_RETRY)); ui_print(5, 11, ui_str(S_TITLE)); deadsel = 0;
        }
        for (i = 0; i < 2; i++) plat_win_set(3, (u8)(9 + i * 2), i == deadsel ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
        if (dead_t < 40) { dead_t++; return 0; }   /* ignore held dodge keys so the game-over choice can't be hit by accident */
        if (g_pressed & (K_UP | K_DOWN)) deadsel ^= 1;
        if (g_pressed & K_A) {
            dead_state = 0;
            g.hp = g.maxhp;
            if (deadsel == 0) { battle_start(bchunk); }
            else { game_flag_title = 2; bs = BS_FINISH; result = 2; sprites_off(); ui_win(144); return 1; }
        }
        return 0;
    }
}

#ifndef __SDCC
#include <stdio.h>
void battle_dbg(char *o) API {
    u8 i; char *p = o;
    p += sprintf(p, "B %d %d %d %d %d %d %d %d %d %d %d %d", bs, bmsel, bsub, spareable, ehp, soul_x, soul_y, shield_cd, invuln, atk_x, nlisten, bitem_n);
    p += sprintf(p, " %d,%d,%d,%d", bx0, by0, boxw, boxh);
    for (i = 0; i < MAXB; i++) if (bl[i].gfx != 255) p += sprintf(p, " %d,%d,%d,%d", bl[i].x >> 4, bl[i].y >> 4, bl[i].vx, bl[i].vy);
}
int battle_dbg_nbullets(void) API { int n = 0, i; for (i = 0; i < MAXB; i++) if (bl[i].gfx != 255) n++; return n; }
#endif
