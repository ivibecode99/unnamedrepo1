#if defined(__SDCC)
#pragma bank 255
#endif
#include "lt.h"
/* Overworld: room loading, player movement/collision, entities, triggers, camera, block puzzles, encounters. */
#define MAXENT 14
#define PL 15            /* pseudo entity index for the player in scripted moves */
typedef struct { u8 kind, slot, x, y, dir, flags, gv, gval; u16 script; u8 vis, mdir, mleft, latch; } Ent;
static Ent ents[MAXENT];
static u8 nent, mw, mh, nplate, plate_var, mflags, menc, mrate, nmeta;
static u8 meta_t[48 * 6];
static u8 pxx, pyy, pdir, pframe, pstep, pmoving, steps_enc, running_b;
static u8 camx, camy, cam_follow = 1;
static u16 cur_chunk, cur_script_pending, pending_battle;
static u8 shake_t, shake_p, anim_t, pal_t;
static u8 map_music;
static u16 palbase[4];
u8 world_mode_flag;
static u8 pl_mleft, pl_mdir;

u16 world_cur_chunk(void) API { return cur_chunk; }
u16 world_take_script(void) API { u16 s = cur_script_pending; cur_script_pending = 0; return s; }
u16 world_take_battle(void) API { u16 b = pending_battle; pending_battle = 0; return b; }

static u16 map_chunk_id(u8 map) { u8 b[2]; plat_chunk_read(CH_MAPS, (u16)(map * 2), b, 2); return rd16(b); }

static u8 ent_visible(Ent *e) {
    if (!e->gv) return 1;
    return (u8)(((g.vars[e->gv] != 0) ? 1 : 0) ^ ((e->flags & 16) ? 1 : 0));
}
static u8 tile_flags(u8 tx, u8 ty) {
    u8 m;
    if (tx >= mw || ty >= mh) return 1;
    m = g_scene[MH_SIZE + ty * mw + tx];
    return meta_t[m * 6 + 5];
}
static u8 solid_px(u8 x, u8 y) { return (u8)(tile_flags((u8)(x >> 4), (u8)(y >> 4)) & 1); }

static void ent_load_all(void) {
    u8 i;
    u16 base = (u16)(MH_SIZE + mw * mh);
    nent = g_scene[MH_NENT]; if (nent > MAXENT) nent = MAXENT;
    for (i = 0; i < nent; i++) {
        const u8 *p = g_scene + base + i * ENT_SZ;
        Ent *e = &ents[i];
        e->kind = p[0]; e->slot = p[1]; e->x = p[2]; e->y = p[3]; e->dir = p[4]; e->flags = p[5]; e->gv = p[6]; e->gval = p[7];
        e->script = rd16(p + 8); e->mleft = 0; e->mdir = 0; e->latch = 0; e->vis = 1;
    }
}
static void gfx_load(void) {
    u8 i, j;
    u16 pc[4];
    u16 tc = rd16(g_scene + MH_TILES), pcg = rd16(g_scene + MH_PAL);
    if (tc) load_tiles(tc, T_MAP);
    for (i = 0; i < 6; i++) {
        plat_chunk_read(pcg, (u16)(i * 8), g_tmp, 8);
        for (j = 0; j < 4; j++) pc[j] = rd16(g_tmp + j * 2);
        plat_pal((u8)(P_ZONE + i), pc);
        if (i == 5) for (j = 0; j < 4; j++) palbase[j] = pc[j];
    }
    set_dmg(g_scene[MH_DMGBG], g_scene[MH_DMGOBJ], g_scene[MH_DMGOBJ]);
    /* player */
    plat_chunk_read(CH_PLAYER, 0, g_tmp, 8);
    for (j = 0; j < 4; j++) pc[j] = rd16(g_tmp + j * 2);
    plat_pal(P_PLAYER, pc);
    for (i = 0; i < 3; i++) { plat_chunk_read(CH_PLAYER, (u16)(8 + i * 128), g_tmp, 128); plat_tiles((u8)(T_PLAYER + i * 8), g_tmp, 8); }
    /* actors */
    for (i = 0; i < 6; i++) {
        u16 ac = rd16(g_scene + MH_ACTORS + i * 2);
        if (!ac) continue;
        plat_chunk_read(ac, 0, g_tmp, 8);
        for (j = 0; j < 4; j++) pc[j] = rd16(g_tmp + j * 2);
        plat_pal((u8)(P_ACTOR + i), pc);
        plat_chunk_read(ac, 8, g_tmp, 64);
        plat_tiles((u8)(T_ACTOR + i * 4), g_tmp, 4);
    }
}
static void draw_map(void) {
    u8 x, y;
    plat_bg_fill(0, 0, 32, 32, T_BLACK, P_UI);
    for (y = 0; y < mh; y++)
        for (x = 0; x < mw; x++) {
            const u8 *m = meta_t + g_scene[MH_SIZE + y * mw + x] * 6;
            u8 a = (u8)(P_ZONE + (m[4] & 7)), tx = (u8)(x * 2), ty = (u8)(y * 2);
            plat_bg_set(tx, ty, (u8)(T_MAP + m[0]), a);
            plat_bg_set((u8)(tx + 1), ty, (u8)(T_MAP + m[1]), a);
            plat_bg_set(tx, (u8)(ty + 1), (u8)(T_MAP + m[2]), a);
            plat_bg_set((u8)(tx + 1), (u8)(ty + 1), (u8)(T_MAP + m[3]), a);
        }
}
static void load_meta(void) {
    u16 mc = rd16(g_scene + MH_META), sz;
    u8 n;
    plat_chunk_read(mc, 0, g_tmp, 1);
    n = g_tmp[0]; if (n > 48) n = 48;
    sz = (u16)(n * 6);
    plat_chunk_read(mc, 1, meta_t, sz);
    nmeta = n;
}
static void read_header(void) {
    mw = g_scene[MH_W]; mh = g_scene[MH_H];
    mflags = g_scene[MH_FLAGS]; menc = g_scene[MH_ENC]; mrate = g_scene[MH_RATE];
    nplate = g_scene[MH_NPLATE]; plate_var = g_scene[MH_PLATEVAR];
    map_music = g_scene[MH_MUSIC];
}
void world_reload_chunk(void) API {
    plat_chunk(cur_chunk, g_scene, SCENE_MAX);
    read_header();
}
/* after battle/minigame the tile RAM was overwritten: full graphics restore without touching positions */
void world_restore(void) API {
    plat_lcd(0);
    load_tiles(CH_TILES_UI, 0);
    load_pal(CH_PAL_UI, P_UI, 1);
    world_reload_chunk();
    load_meta(); gfx_load(); draw_map();
    plat_lcd(1);
}
void world_load(u8 map, u8 px, u8 py, u8 dir) API {
    plat_lcd(0);
    ui_clear_win(); ui_win(144);
    cur_chunk = map_chunk_id(map);
    g.map = map;
    world_reload_chunk();
    load_tiles(CH_TILES_UI, 0);
    load_pal(CH_PAL_UI, P_UI, 1);
    load_meta(); gfx_load(); draw_map(); ent_load_all();
    pxx = (u8)(px * 16); pyy = (u8)(py * 16); pdir = dir; pframe = 0; pstep = 0; steps_enc = 0; pl_mleft = 0;
    g.px = px; g.py = py; g.dir = dir;
    {
        u8 i;
        for (i = 0; i < 40; i++) plat_spr(i, 0, 200, 0, 0);
    }
    cam_follow = 1;
    plat_lcd(1);
    if (map_music != 254) audio_play(map_music);
    cur_script_pending = 0;
    /* enter script runs through the VM */
    {
        u16 es = rd16(g_scene + MH_ENTER);
        if (es) cur_script_pending = es;
    }
}
void world_player_pos(u8 *x, u8 *y) API { *x = pxx; *y = pyy; }
void world_player_to(u8 x, u8 y) API { pxx = x; pyy = y; }
void world_ent_show(u8 idx, u8 on) API { if (idx < nent) { ents[idx].gv = 0; ents[idx].vis = on; ents[idx].flags |= 32; } }
void world_ent_set(u8 idx, u8 x, u8 y) API { if (idx == PL) { pxx = (u8)(x * 16); pyy = (u8)(y * 16); } else if (idx < nent) { ents[idx].x = (u8)(x * 16); ents[idx].y = (u8)(y * 16); } }
void world_ent_face(u8 idx, u8 d) API { if (idx == PL) pdir = d; else if (idx < nent) ents[idx].dir = d; }
u8 world_ent_move(u8 idx, u8 d, u8 n) API {
    if (idx == PL) { pl_mdir = d; pl_mleft = (u8)(n * 16); pdir = d; }
    else if (idx < nent) { ents[idx].mdir = d; ents[idx].mleft = (u8)(n * 16); ents[idx].dir = d; }
    return 0;
}
u8 world_busy(void) API {
    u8 i;
    if (pl_mleft) return 1;
    for (i = 0; i < nent; i++) if (ents[i].mleft) return 1;
    return 0;
}
void world_cam(u8 x, u8 y, u8 follow) API { camx = x; camy = y; cam_follow = follow; }
void world_shake(u8 f, u8 p) API { shake_t = f; shake_p = p; }

static void step_dir(u8 d, u8 *x, u8 *y, u8 n) {
    if (d == 0) *y = (u8)(*y + n); else if (d == 1) *y = (u8)(*y - n); else if (d == 2) *x = (u8)(*x - n); else *x = (u8)(*x + n);
}
/* blocked test for a 16x16 sprite at (x,y) with feet hitbox; who = index to ignore */
static u8 ent_solid_at(u8 x, u8 y, u8 who) {
    u8 i;
    for (i = 0; i < nent; i++) {
        Ent *e = &ents[i];
        if (i == who) continue;
        if (!(e->kind == EK_NPC || e->kind == EK_BLOCK || e->kind == EK_CHEST || e->kind == EK_SAVE || e->kind == EK_DOOR)) continue;
        if (!(e->flags & 32 ? e->vis : ent_visible(e))) continue;
        if (x + 13 > e->x + 1 && x + 3 < e->x + 15 && y + 15 > e->y + 6 && y + 10 < e->y + 16) return 1;
    }
    return 0;
}
static u8 blocked(u8 x, u8 y, u8 who) {
    /* player hitbox x+3..x+12, y+10..y+15 */
    if (solid_px((u8)(x + 3), (u8)(y + 10)) || solid_px((u8)(x + 12), (u8)(y + 10)) || solid_px((u8)(x + 3), (u8)(y + 15)) || solid_px((u8)(x + 12), (u8)(y + 15))) return 1;
    if (x > 240 || y > 240) return 1;
    return ent_solid_at(x, y, who);
}
static u8 block_free(Ent *b, u8 i, u8 nx, u8 ny) {
    u8 k;
    if (solid_px((u8)(nx + 2), (u8)(ny + 2)) || solid_px((u8)(nx + 13), (u8)(ny + 2)) || solid_px((u8)(nx + 2), (u8)(ny + 13)) || solid_px((u8)(nx + 13), (u8)(ny + 13))) return 0;
    for (k = 0; k < nent; k++) {
        Ent *e = &ents[k];
        if (k == i || !(e->kind == EK_NPC || e->kind == EK_BLOCK || e->kind == EK_CHEST || e->kind == EK_SAVE || e->kind == EK_DOOR)) continue;
        if (!ent_visible(e)) continue;
        if (nx + 14 > e->x + 2 && nx + 2 < e->x + 14 && ny + 14 > e->y + 2 && ny + 2 < e->y + 14) return 0;
    }
    (void)b;
    return 1;
}
static void try_move_player(u8 d, u8 spd) {
    u8 nx = pxx, ny = pyy, k;
    for (k = 0; k < spd; k++) {
        nx = pxx; ny = pyy;
        step_dir(d, &nx, &ny, 1);
        if (blocked(nx, ny, 255)) {
            /* try to push a block */
            u8 i;
            for (i = 0; i < nent; i++) {
                Ent *e = &ents[i];
                u8 bx, by;
                if (e->kind != EK_BLOCK || !ent_visible(e)) continue;
                if (nx + 13 > e->x + 1 && nx + 3 < e->x + 15 && ny + 15 > e->y + 6 && ny + 10 < e->y + 16) {
                    bx = e->x; by = e->y; step_dir(d, &bx, &by, 1);
                    if (block_free(e, i, bx, by)) { e->x = bx; e->y = by; nx = pxx; ny = pyy; step_dir(d, &nx, &ny, 1); if (!blocked(nx, ny, 255)) { pxx = nx; pyy = ny; pmoving = 1; } }
                    break;
                }
            }
            /* slide along walls */
            if (d < 2) { u8 sx = pxx, sy = pyy; if (!blocked((u8)(pxx - 1), pyy, 255) && blocked(nx, ny, 255) && blocked(pxx, (u8)(d ? pyy - 1 : pyy + 1), 255)) { (void)sx; (void)sy; } }
            continue;
        }
        pxx = nx; pyy = ny; pmoving = 1;
    }
}
static void plates_check(void) {
    u8 i, k, ok = 1;
    if (!nplate) return;
    {
        u16 base = (u16)(MH_SIZE + mw * mh + nent * ENT_SZ);
        for (i = 0; i < nplate; i++) {
            u8 tx = g_scene[base + i * 2], ty = g_scene[base + i * 2 + 1], cov = 0;
            for (k = 0; k < nent; k++) if (ents[k].kind == EK_BLOCK && (u8)((ents[k].x + 8) >> 4) == tx && (u8)((ents[k].y + 8) >> 4) == ty) cov = 1;
            if (!cov) ok = 0;
        }
    }
    if (ok && !g.vars[plate_var]) { g.vars[plate_var] = 1; audio_sfx(10); }
}
static void ent_rect_touch_player(Ent *e, u8 w, u8 h, u8 *inside) {
    u8 cx = (u8)(pxx + 8), cy = (u8)(pyy + 12);
    *inside = (u8)((u16)cx >= e->x && (u16)cx < (u16)e->x + w && (u16)cy >= e->y && (u16)cy < (u16)e->y + h);
}
static u16 find_interact(void) {
    u8 px2 = (u8)(pxx + 8), py2 = (u8)(pyy + 12), i;
    u8 fx = px2, fy = py2;
    step_dir(pdir, &fx, &fy, 11);
    for (i = 0; i < nent; i++) {
        Ent *e = &ents[i];
        if (!(e->kind == EK_NPC || e->kind == EK_SPOT || e->kind == EK_CHEST || e->kind == EK_SAVE)) continue;
        if (!(e->flags & 32 ? e->vis : ent_visible(e))) continue;
        if (!e->script) continue;
        if ((u16)fx >= e->x && (u16)fx < (u16)e->x + 16 && (u16)fy >= e->y && (u16)fy < (u16)e->y + 16) {
            if (e->kind == EK_NPC) { u8 d = pdir; e->dir = (u8)(d == 0 ? 1 : d == 1 ? 0 : d == 2 ? 3 : 2); }
            return e->script;
        }
    }
    return 0;
}
void world_tick(void) API {
    u8 i, spd, d = 255;
    anim_t++;
    /* scripted movement */
    if (pl_mleft) { step_dir(pl_mdir, &pxx, &pyy, 1); pl_mleft--; pmoving = 1; }
    for (i = 0; i < nent; i++) if (ents[i].mleft) { step_dir(ents[i].mdir, &ents[i].x, &ents[i].y, 1); ents[i].mleft--; }
    if (world_mode_flag) return;   /* scripted: no player control */
    pmoving = 0;
    spd = (g_keys & K_B) ? 2 : 1;
    if (g_keys & K_UP) d = 1; else if (g_keys & K_DOWN) d = 0; else if (g_keys & K_LEFT) d = 2; else if (g_keys & K_RIGHT) d = 3;
    if (d != 255 && !pl_mleft) {
        u8 ox = pxx, oy = pyy;
        pdir = d;
        try_move_player(d, spd);
        if (pxx != ox || pyy != oy) {
            pstep = (u8)(pstep + spd);
            if (pstep >= 8) { pstep = 0; pframe ^= 1; }
            /* random encounters on flagged tiles */
            if (mrate && (tile_flags((u8)((pxx + 8) >> 4), (u8)((pyy + 12) >> 4)) & 4)) {
                if (++steps_enc >= (u8)(mrate * 4 + 24)) {
                    steps_enc = 0;
                    if ((rnd() & 3) != 0) {
                        u8 b[8];
                        plat_chunk_read(CH_ENC, (u16)(menc * 8), b, 8);
                        { u8 n = 0, pick; for (i = 0; i < 4; i++) if (rd16(b + i * 2)) n++; if (n) { pick = (u8)(rnd() % n); pending_battle = rd16(b + pick * 2); } }
                    }
                }
            }
        }
    }
    if (g_pressed & K_A) { u16 s = find_interact(); if (s) cur_script_pending = s; }
    /* zones, touch-enemies */
    for (i = 0; i < nent; i++) {
        Ent *e = &ents[i];
        u8 in;
        if (!(e->flags & 32 ? e->vis : ent_visible(e))) { e->latch = 0; continue; }
        if (e->kind == EK_ZONE) {
            ent_rect_touch_player(e, (u8)(e->slot * 8), (u8)(e->dir * 8), &in);
            if (in && !e->latch && e->script) { e->latch = 1; cur_script_pending = e->script; }
            else if (!in) e->latch = 0;
        } else if (e->kind == EK_ENEMY && e->script) {
            ent_rect_touch_player(e, 16, 16, &in);
            if (in) cur_script_pending = e->script;
        }
    }
    plates_check();
}
static void spr_big(u8 *oi, s16 sx, s16 sy, u8 tile0, u8 pal, u8 flip) {
    u8 a = (u8)(pal | (flip ? 0x20 : 0));
    plat_spr((*oi)++, sx, sy, (u8)(tile0 + (flip ? 1 : 0)), a);
    plat_spr((*oi)++, (s16)(sx + 8), sy, (u8)(tile0 + (flip ? 0 : 1)), a);
    plat_spr((*oi)++, sx, (s16)(sy + 8), (u8)(tile0 + (flip ? 3 : 2)), a);
    plat_spr((*oi)++, (s16)(sx + 8), (s16)(sy + 8), (u8)(tile0 + (flip ? 2 : 3)), a);
}
extern u8 ui_win_y;
void world_draw(void) API {
    u8 oi = 0, i, bob;
    s16 sx, sy;
    u8 wy = ui_win_y;
    u8 cx, cy, scx, scy;
    /* camera */
    if (cam_follow) {
        s16 c = (s16)pxx + 8 - 80;
        if (c < 0) c = 0; if (c > (s16)mw * 16 - 160) c = (s16)mw * 16 - 160; if (c < 0) c = 0;
        camx = (u8)c;
        c = (s16)pyy + 8 - 72;
        if (c < 0) c = 0; if (c > (s16)mh * 16 - 144) c = (s16)mh * 16 - 144; if (c < 0) c = 0;
        camy = (u8)c;
    }
    cx = camx; cy = camy; scx = cx; scy = cy;
    if (shake_t) { shake_t--; scx = (u8)(cx + (rnd() % (shake_p * 2 + 1)) - shake_p); scy = (u8)(cy + (rnd() % (shake_p * 2 + 1)) - shake_p); }
    plat_scroll(scx, scy);
    /* water shimmer */
    if ((mflags & 2) && ((anim_t & 15) == 0)) { u16 c[4]; u8 k = (u8)((anim_t >> 4) % 3); c[0] = palbase[0]; c[1] = palbase[1 + k]; c[2] = palbase[1 + (k + 1) % 3]; c[3] = palbase[1 + (k + 2) % 3]; plat_pal((u8)(P_ZONE + 5), c); }
    /* player */
    sx = (s16)pxx - cx; sy = (s16)pyy - cy;
    if (sy + 8 <= wy) {
        u8 base, flip = 0;
        if (pdir == 0) base = 0; else if (pdir == 1) base = 8; else { base = 16; flip = (u8)(pdir == 3); }
        spr_big(&oi, sx, sy, (u8)(T_PLAYER + base + (pmoving ? pframe * 4 : 0)), 0, flip);
    } else { for (i = 0; i < 4; i++) plat_spr(oi++, 0, 200, 0, 0); }
    /* entities */
    for (i = 0; i < nent; i++) {
        Ent *e = &ents[i];
        u8 k = e->kind;
        if (!(k == EK_NPC || k == EK_BLOCK || k == EK_CHEST || k == EK_SAVE || k == EK_ENEMY || k == EK_DOOR)) continue;
        if (oi > 36) break;
        if (!(e->flags & 32 ? e->vis : ent_visible(e))) continue;
        sx = (s16)e->x - cx; sy = (s16)e->y - cy;
        if (sx <= -16 || sx >= 160 || sy <= -16 || sy >= 144 || sy + 8 > wy) continue;
        bob = (u8)(((anim_t >> 5) + i) & 1);
        spr_big(&oi, sx, (s16)(sy + (k == EK_NPC || k == EK_ENEMY ? bob : 0)), (u8)(T_ACTOR + e->slot * 4), (u8)(1 + e->slot), (u8)((k == EK_NPC && e->dir == 3) ? 1 : 0));
    }
    while (oi < 40) plat_spr(oi++, 0, 200, 0, 0);
}

#ifndef __SDCC
#include <stdio.h>
void world_dbg(char *o) API {
    u8 i; char *p = o;
    p += sprintf(p, "W %d %d %d %d %d %d ", g.map, mw, mh, pxx, pyy, pdir);
    for (i = 0; i < (u8)(mw * mh); i++) p += sprintf(p, "%d", meta_t[g_scene[MH_SIZE + i] * 6 + 5] & 1);
    p += sprintf(p, " %d", nent);
    for (i = 0; i < nent; i++) p += sprintf(p, " %d,%d,%d,%d,%d,%d", ents[i].kind, ents[i].x, ents[i].y, (ents[i].flags & 32) ? ents[i].vis : ent_visible(&ents[i]), ents[i].slot, ents[i].dir);
}
#endif
