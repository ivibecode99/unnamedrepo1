#if defined(__SDCC)
#pragma bank 255
#endif
#include "lt.h"
#include "gen_strings.h"
/* Two light mini-games: 0 = rhythm lantern lighting (LEFT / A / RIGHT), 1 = cargo sorting (LEFT = round, RIGHT = spiky). */
#define NN 24
static u8 mid, t_notes[NN], lane[NN], done[NN], score, hits, total, phase, wt, spawned, cur_lane_flash;
static u16 frame, seed;
static u8 rnd8(void) { seed = (u16)(seed * 25173u + 13849u); return (u8)(seed >> 8); }
static u8 crate_y, crate_type, crate_alive, crate_n, speed;

void mg_start(u8 id) API {
    u8 i;
    plat_lcd(0);
    mid = id; frame = 0; score = 0; hits = 0; phase = 0; wt = 0; spawned = 0; seed = (u16)(id * 777 + 31);
    load_tiles(CH_TILES_UI, 0); load_pal(CH_PAL_UI, P_UI, 1);
    { u16 pc[4]; plat_chunk_read(CH_BSPR, 0, g_tmp, 16); for (i = 0; i < 4; i++) pc[i] = rd16(g_tmp + i * 2); plat_pal(P_BULLET, pc); for (i = 0; i < 4; i++) pc[i] = rd16(g_tmp + 8 + i * 2); plat_pal(P_SOUL, pc); }
    plat_chunk_read(CH_BSPR, 16, g_tmp, 256); plat_tiles(T_BSPR, g_tmp, 16);
    plat_bg_fill(0, 0, 32, 32, T_BLACK, P_UI);
    ui_win(144); plat_scroll(0, 0);
    for (i = 0; i < 40; i++) plat_spr(i, 0, 200, 0, 0);
    set_dmg(0xE4, 0xE4, 0xE4);
    audio_play(mid == 0 ? 21 : 22);
    if (mid == 0) {
        u16 t = 40;
        total = NN;
        for (i = 0; i < NN; i++) { t_notes[i] = (u8)(t / 4); lane[i] = (u8)(rnd8() % 3); done[i] = 0; t = (u16)(t + 22 + (rnd8() & 15)); }
        ui_print_bg(3, 1, ui_str(S_TAP));
        ui_print_bg(3, 16, (const u8 *)"<    A     >");
    } else {
        total = 20; crate_alive = 0; crate_n = 0; speed = 2;
        ui_print_bg(3, 1, ui_str(S_SORT));
        ui_print_bg(1, 16, (const u8 *)"ROUND         SPIKY");
    }
    plat_lcd(1);
}
static void hud(void) {
    u8 d[8];
    d[0] = (u8)('0' + hits / 10); d[1] = (u8)('0' + hits % 10); d[2] = '/'; d[3] = (u8)('0' + total / 10); d[4] = (u8)('0' + total % 10); d[5] = 0;
    ui_print_bg(7, 3, d);
}
u8 mg_tick(void) API {
    u8 i;
    frame++;
    if (phase == 1) {
        if (++wt == 1) {
            u8 r = (u8)(hits * 100 / total);
            g.vars[V_R] = (u8)(r >= 80 ? 2 : r >= 45 ? 1 : 0);
            ui_print_bg(4, 8, g.vars[V_R] == 2 ? ui_str(S_PERFECT) : g.vars[V_R] == 1 ? ui_str(S_GOOD) : ui_str(S_MISS));
        }
        if (wt > 90 || (wt > 20 && (g_pressed & K_A))) {
            for (i = 0; i < 40; i++) plat_spr(i, 0, 200, 0, 0);
            audio_stop();
            return 1;
        }
        return 0;
    }
    if (mid == 0) {
        /* notes fall: y = (frame - spawn_frame*?) ; note i spawns at t_notes[i]*4 and hits line at +64 frames */
        u8 spr = 0;
        u8 pressed_lane = 255;
        if (g_pressed & K_LEFT) pressed_lane = 0; else if (g_pressed & K_A) pressed_lane = 1; else if (g_pressed & K_RIGHT) pressed_lane = 2;
        for (i = 0; i < NN; i++) {
            s16 age = (s16)frame - (s16)((u16)t_notes[i] * 4);
            s16 y;
            if (done[i] || age < 0) continue;
            y = (s16)(age * 2);              /* hit line at y = 128 -> age 64 */
            if (pressed_lane == lane[i] && age > 52 && age < 76) { done[i] = 1; hits++; pressed_lane = 255; audio_sfx(10); hud(); continue; }
            if (age > 80) { done[i] = 2; hud(); continue; }
            plat_spr(spr++, (s16)(40 + lane[i] * 40), y, T_BSPR, (u8)(P_SOUL - 8));
        }
        while (spr < 12) plat_spr(spr++, 0, 200, 0, 0);
        { u8 all = 1; for (i = 0; i < NN; i++) if (!done[i]) all = 0; if (all) phase = 1; }
        if (pressed_lane != 255) audio_sfx(14);
        for (i = 0; i < 3; i++) plat_spr((u8)(20 + i), (s16)(40 + i * 40), 128, (u8)(T_BSPR + 6), (u8)(P_BULLET - 8));
    } else {
        if (!crate_alive) {
            if (crate_n >= total) { phase = 1; return 0; }
            if ((frame & 31) == 0) { crate_alive = 1; crate_y = 8; crate_type = (u8)(rnd8() & 1); crate_n++; if (speed < 5 && (crate_n % 6) == 0) speed++; }
        } else {
            crate_y = (u8)(crate_y + speed / 2 + 1);
            plat_spr(0, 76, crate_y, (u8)(T_BSPR + (crate_type ? 7 : 6)), (u8)(P_BULLET - 8));
            if ((g_pressed & (K_LEFT | K_RIGHT)) && crate_y > 40) {
                u8 want = (u8)((g_pressed & K_RIGHT) ? 1 : 0);
                if (want == crate_type) { hits++; audio_sfx(10); } else audio_sfx(14);
                crate_alive = 0; plat_spr(0, 0, 200, 0, 0); hud();
            } else if (crate_y > 124) { crate_alive = 0; plat_spr(0, 0, 200, 0, 0); audio_sfx(14); }
        }
    }
    return 0;
}
