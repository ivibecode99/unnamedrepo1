#if defined(__SDCC)
#pragma bank 255
#endif
#include "lt.h"
/* Script VM. Two contexts: 0 = world, 1 = battle. Bytecode lives in g_scene (loaded chunk). */
#define W_NONE 0
#define W_SAY 1
#define W_FRAMES 2
#define W_MOVE 3
#define W_CHOICE 4
#define W_FADE 5
#define W_BATTLE 6
#define W_SHOP 7
#define W_SAVE 8
#define W_MG 9
#define W_NAME 10
#define W_END 11
#define W_BTLINE 12

typedef struct { u16 ip, stack[4], chunk; u8 sp, wait, waitv, active, tb; u8 cvar, cn, ccur; u16 cptr; } Vm;
static Vm vms[2];
u8 vm_ctx;
static u8 pending_ending;
u8 game_flag_title;

u8 vm_fullscreen(void) API { u8 w = vms[0].wait; return vms[0].active && (w == W_BATTLE || w == W_SHOP || w == W_SAVE || w == W_MG || w == W_NAME || w == W_END); }
u8 vm_running(void) API { return vms[vm_ctx].active; }
u8 vm_running_ctx(u8 c) API { return vms[c].active; }
void vm_start(u16 ip) API { Vm *v = &vms[vm_ctx]; v->ip = ip; v->sp = 0; v->wait = W_NONE; v->active = 1; v->tb = 0; }
void vm_start_chunk(u16 chunk) API {
    Vm *v = &vms[vm_ctx];
    plat_chunk(chunk, g_scene, SCENE_MAX);
    v->chunk = chunk; vm_start(0);
}
void vm_set_chunk(u16 c) API { vms[vm_ctx].chunk = c; }
u16 vm_get_chunk(void) API { return vms[vm_ctx].chunk; }
void vm_stop(void) API { vms[vm_ctx].active = 0; }

static void tb_close(Vm *v) { if (v->tb) { ui_say_end(); v->tb = 0; } }
static u8 cmp(u8 a, u8 op, u8 b) {
    switch (op) { case 0: return a == b; case 1: return a != b; case 2: return a < b; case 3: return a > b; case 4: return a <= b; default: return a >= b; }
}
static void choice_draw(Vm *v) {
    const u8 *p = g_scene + v->cptr;
    u8 i, x = 6;
    plat_win_fill(1, 1, 18, 4, T_BLACK, P_UI);
    if (ui_win_y == 144) return;
    for (i = 0; i < v->cn; i++) {
        ui_print(x, (u8)(1 + i), p);
        while (*p) p++;
        p++;
        plat_win_set(5, (u8)(1 + i), i == v->ccur ? (u8)(T_UI + UI_CURSOR) : T_BLACK, P_UI);
    }
}
void world_ent_op(u8 op, u8 a, u8 b, u8 c) API { (void)op; (void)a; (void)b; (void)c; }

/* returns after starting an op that waits; loops through instantaneous ops */
void vm_tick(void) API {
    Vm *v = &vms[vm_ctx];
    u8 guard = 0;
    while (v->active && guard < 100) {
        const u8 *S = g_scene;
        u8 op;
        guard++;
        /* ---- waits ---- */
        switch (v->wait) {
        case W_SAY:
            if (ui_say_tick()) { v->wait = W_NONE; } else return;
            break;
        case W_FRAMES: if (v->waitv) { v->waitv--; return; } v->wait = W_NONE; break;
        case W_MOVE: if (world_busy()) return; v->wait = W_NONE; break;
        case W_FADE: if (fx_busy()) return; v->wait = W_NONE; break;
        case W_CHOICE:
            if (g_pressed & K_UP) { v->ccur = v->ccur ? (u8)(v->ccur - 1) : (u8)(v->cn - 1); audio_sfx(0); choice_draw(v); }
            if (g_pressed & K_DOWN) { v->ccur = (u8)(v->ccur + 1 < v->cn ? v->ccur + 1 : 0); audio_sfx(0); choice_draw(v); }
            if (g_pressed & K_A) { g.vars[v->cvar] = v->ccur; audio_sfx(1); plat_win_fill(1, 1, 18, 4, T_BLACK, P_UI); v->wait = W_NONE; }
            else return;
            break;
        case W_BATTLE:
            if (battle_tick()) {
                world_restore();
                plat_chunk(v->chunk, g_scene, SCENE_MAX);
                fx_fade(0, 2);
                v->wait = W_NONE;
                break;
            }
            return;
        case W_SHOP: if (shop_tick()) { v->wait = W_NONE; } else return; break;
        case W_SAVE: if (save_menu_tick()) { v->wait = W_NONE; } else return; break;
        case W_MG: if (mg_tick()) { v->wait = W_NONE; world_restore(); plat_chunk(v->chunk, g_scene, SCENE_MAX); } else return; break;
        case W_NAME: if (name_tick()) { v->wait = W_NONE; } else return; break;
        case W_END: return;
        default: break;
        }
        if (v->wait != W_NONE) continue;
        S = g_scene;
        op = S[v->ip++];
        switch (op) {
        case 0x00: tb_close(v); v->active = 0; if (vm_ctx == 0 && v->chunk != world_cur_chunk()) { world_reload_chunk(); v->chunk = world_cur_chunk(); } return;
        case 0x01: {
            u8 spk = S[v->ip], emo = S[v->ip + 1];
            const u8 *t = S + v->ip + 2;
            v->ip = (u16)(v->ip + 2);
            while (S[v->ip]) v->ip++;
            v->ip++;
            ui_say_begin(spk, emo);
            ui_say_text(t);
            v->tb = 1; v->wait = W_SAY;
            return;
        }
        case 0x02: g.vars[S[v->ip]] = S[v->ip + 1]; v->ip += 2; break;
        case 0x03: g.vars[S[v->ip]] = (u8)(g.vars[S[v->ip]] + (s8)S[v->ip + 1]); v->ip += 2; break;
        case 0x04: { u8 r = cmp(g.vars[S[v->ip]], S[v->ip + 1], S[v->ip + 2]); u16 t = rd16(S + v->ip + 3); v->ip += 5; if (r) v->ip = t; } break;
        case 0x05: v->ip = rd16(S + v->ip); break;
        case 0x06: { u16 t = rd16(S + v->ip); v->ip += 2; if (v->sp < 4) v->stack[v->sp++] = v->ip; v->ip = t; } break;
        case 0x07: if (v->sp) v->ip = v->stack[--v->sp]; else { tb_close(v); v->active = 0; if (vm_ctx == 0 && v->chunk != world_cur_chunk()) { world_reload_chunk(); v->chunk = world_cur_chunk(); } return; } break;
        case 0x08: {
            v->cvar = S[v->ip]; v->cn = S[v->ip + 1]; v->cptr = (u16)(v->ip + 2); v->ccur = 0;
            v->ip += 2;
            { u8 i; for (i = 0; i < v->cn; i++) { while (S[v->ip]) v->ip++; v->ip++; } }
            choice_draw(v); v->wait = W_CHOICE; return;
        }
        case 0x09: {
            u8 m = S[v->ip], x = S[v->ip + 1], y = S[v->ip + 2], d = S[v->ip + 3];
            u16 es;
            v->ip += 4;
            tb_close(v);
            fx_fade(8, 1); while (fx_busy()) { fx_tick(); plat_vsync(); }
            world_load(m, x, y, d);
            v->chunk = world_cur_chunk(); v->sp = 0;
            es = world_take_script();
            fx_fade(0, 2);
            if (es) v->ip = es; else { v->active = 0; return; }
            break;
        }
        case 0x0A: v->waitv = S[v->ip++]; v->wait = W_FRAMES; tb_close(v); break;
        case 0x0B: { u8 d = S[v->ip++]; fx_fade(d ? 0 : 8, 3); v->wait = W_FADE; } break;
        case 0x0C: world_shake(S[v->ip], S[v->ip + 1]); v->ip += 2; break;
        case 0x0D: audio_play(S[v->ip++]); break;
        case 0x0E: audio_sfx(S[v->ip++]); break;
        case 0x0F: {
            u16 ch = rd16(S + v->ip);
            v->ip += 2;
            tb_close(v);
            battle_start(ch);
            v->wait = W_BATTLE;
            return;
        }
        case 0x10: tb_close(v); shop_open(S[v->ip++]); v->wait = W_SHOP; return;
        case 0x11: if (!item_add(S[v->ip++])) { /* full */ } else audio_sfx(12); break;
        case 0x12: item_remove(S[v->ip++]); break;
        case 0x13: { u8 it = S[v->ip]; u16 t = rd16(S + v->ip + 1); v->ip += 3; if (item_has(it)) v->ip = t; } break;
        case 0x14: tb_close(v); save_menu_open(); v->wait = W_SAVE; return;
        case 0x15: tb_close(v); mg_start(S[v->ip++]); v->wait = W_MG; return;
        case 0x16: world_ent_show(S[v->ip], S[v->ip + 1]); v->ip += 2; break;
        case 0x17: world_ent_move(S[v->ip], S[v->ip + 1], S[v->ip + 2]); v->ip += 3; v->wait = W_MOVE; tb_close(v); break;
        case 0x18: world_ent_face(S[v->ip], S[v->ip + 1]); v->ip += 2; break;
        case 0x19: world_ent_set(S[v->ip], S[v->ip + 1], S[v->ip + 2]); v->ip += 3; break;
        case 0x1A: { s16 d = (s16)(S[v->ip] | (S[v->ip + 1] << 8)); v->ip += 2; if (d < 0 && (u16)(-d) > g.gold) g.gold = 0; else g.gold = (u16)(g.gold + d); } break;
        case 0x1B: tb_close(v); pending_ending = S[v->ip++]; game_ending(pending_ending); v->wait = W_END; return;
        case 0x1C: g.hp = g.maxhp; break;
        case 0x1D: { u16 c = rd16(S + v->ip); tb_close(v); plat_chunk(c, g_scene, SCENE_MAX); v->chunk = c; v->ip = 0; v->sp = 0; } break;
        case 0x1E: tb_close(v); name_enter(); v->wait = W_NAME; return;
        case 0x1F: fx_flash(S[v->ip++]); break;
        case 0x20: tb_close(v); break;
        case 0x21: g.vars[S[v->ip]] = g.vars[S[v->ip + 1]]; v->ip += 2; break;
        case 0x22: g.vars[S[v->ip]] = (u8)(g.vars[S[v->ip]] + g.vars[S[v->ip + 1]]); v->ip += 2; break;
        case 0x23: g.vars[S[v->ip]] = (u8)(rnd() % S[v->ip + 1]); v->ip += 2; break;
        case 0x24: battle_cmd(0x24, (u8)(v->ip & 255), (u8)(v->ip >> 8)); while (S[v->ip]) v->ip++; v->ip++; break;
        case 0x25: battle_cmd(0x25, S[v->ip++], 0); return;
        case 0x26: battle_cmd(0x26, S[v->ip], S[v->ip + 1]); v->ip += 2; break;
        case 0x27: audio_layers(S[v->ip++]); break;
        case 0x28: battle_cmd(0x28, S[v->ip++], 0); break;
        case 0x29: battle_cmd(0x29, S[v->ip++], 0); break;
        case 0x2B: battle_cmd(0x2B, S[v->ip++], 0); tb_close(v); v->active = 0; return;
        case 0x2D: world_cam((u8)(S[v->ip] * 16), (u8)(S[v->ip + 1] * 16), S[v->ip + 2]); v->ip += 3; break;
        case 0x2F: { u8 n = S[v->ip++]; g.maxhp = (u8)(g.maxhp + n); g.hp = (u8)(g.hp + n); } break;
        case 0x33: battle_cmd(0x33, S[v->ip], S[v->ip + 1]); v->ip += 2; break;
        case 0x37: tb_close(v); game_flag_title = 2; v->active = 0; return;
        case 0x38: meta.endings |= S[v->ip++]; meta_save(); break;
        case 0x39: { u8 m = S[v->ip]; u16 t = rd16(S + v->ip + 1); v->ip += 3; if (meta.endings & m) v->ip = t; } break;
        case 0x3A: world_mode_flag = S[v->ip++]; break;
        case 0x3B: battle_cmd(0x3B, S[v->ip++], 0); break;
        case 0x3E: {
            u8 m = S[v->ip], x = S[v->ip + 1], y = S[v->ip + 2], d = S[v->ip + 3];
            u16 saved = v->chunk;
            v->ip += 4;
            tb_close(v);
            fx_fade(8, 1); while (fx_busy()) { fx_tick(); plat_vsync(); }
            world_load(m, x, y, d);
            (void)world_take_script();
            plat_chunk(saved, g_scene, SCENE_MAX);
            v->chunk = saved;
            fx_fade(0, 2);
            break;
        }
        case 0x3D: { u8 n = S[v->ip]; u16 t = rd16(S + v->ip + 1); v->ip += 3; if (g.gold >= n) v->ip = t; } break;
        case 0x3C: g.vars[S[v->ip]] = (u8)(g.vars[S[v->ip]] + 1 > 255 ? 255 : g.vars[S[v->ip]] + 1); v->ip++; break;
        default: v->active = 0; return;
        }
    }
}

#ifndef __SDCC
#include <stdio.h>
void vm_dbg(char *o) API { sprintf(o, "V %d %d %d %d", vms[0].active, vms[0].wait, vms[1].active, vms[0].chunk); }
#endif
