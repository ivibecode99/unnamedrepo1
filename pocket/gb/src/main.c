/* Capt & Co. - Pocket Edition (Game Boy / Game Boy Color), GBDK-2020.
 * Original game. D-pad move, A jump, B throw Capt (boomerang hat), START pause.
 * 4 levels, 2 bosses, battery-backed save (MBC5+RAM+BATTERY). */
#include <gb/gb.h>
#include <gb/cgb.h>
#include <stdint.h>
#include <string.h>
#include "assets.h"
#include "levels.h"
#include "music_data.h"

#ifdef TARGET_GBC
#define IS_COLOR 1
#else
#define IS_COLOR 0
#endif

#define LH 18
#define MAXW 160
#define MAX_EN 12
#define GROUND_ROW 14

/* ------------------------------------------------------------------ state */
typedef enum { ST_TITLE, ST_PLAY } GameMode;
uint8_t lvl[MAXW * LH];
uint8_t lw, cur_level, cur_theme, cur_boss, arena0, arena1;
int16_t cam_x;
uint8_t drawn_tx;
uint8_t keys, prev_keys, pressed;
uint8_t char_tile[128];
uint16_t frame_count;

/* player (positions in 1/16 pixel) */
int16_t px, py, vx, vy;
uint8_t on_ground, facing, hp, max_hp, invuln, coyote, jbuf, anim;
uint16_t coins;
uint8_t level_done, player_dead;
/* hat */
int16_t hx, hy;
uint8_t hat_state, hat_dist, hat_bounced;   /* 0 idle on head, 1 out, 2 back */
int8_t hat_dir;
/* enemies */
int16_t ex[MAX_EN], ey[MAX_EN], ey0[MAX_EN];
int8_t edir[MAX_EN];
uint8_t etype[MAX_EN], ealive[MAX_EN], n_en;
/* boss */
int16_t bx, by;
int8_t bhp, bdir;
uint8_t bstate, btimer, bflash, bvuln, bactive, bdead, bphase;
uint8_t arena_locked, star_spawned;
/* projectiles */
int16_t prx[3], pry[3], prvx[3], prvy[3];
uint8_t pract[3];
/* save */
uint8_t save_reached, save_stars;
uint16_t save_coins;

static const int8_t sine[32] = { 0, 1, 2, 3, 4, 5, 5, 6, 6, 6, 5, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -5, -6, -6, -6, -5, -5, -4, -3, -2, -1 };

/* ------------------------------------------------------------------ helpers */
static void set_pal_bg(uint8_t theme) {
#ifdef TARGET_GBC
    set_bkg_palette(0, 5, bg_palettes[theme]);
    set_sprite_palette(0, 6, spr_palettes);
#else
    (void)theme;
    BGP_REG = 0xE4; OBP0_REG = 0xE4; OBP1_REG = 0xE4;
#endif
}

static void init_charmap(void) {
    uint8_t i;
    for (i = 0; i < 128; i++) char_tile[i] = 0;
    for (i = 0; FONT_CHARS[i]; i++) char_tile[(uint8_t)FONT_CHARS[i]] = FONT_BASE + i;
    char_tile[' '] = T_SKY;
}

static void set_tile_attr(uint8_t x, uint8_t y, uint8_t tile) {
#ifdef TARGET_GBC
    VBK_REG = 1;
    set_bkg_tile_xy(x, y, tile_palette[tile]);
    VBK_REG = 0;
#else
    (void)x; (void)y; (void)tile;
#endif
}

static void put_tile(uint8_t x, uint8_t y, uint8_t tile) {
    set_bkg_tile_xy(x & 31, y, tile);
    set_tile_attr(x & 31, y, tile);
}

static void print_at(uint8_t x, uint8_t y, const char *s) {
    while (*s) {
        put_tile(x++, y, char_tile[(uint8_t)*s]);
        s++;
    }
}

static void print_num(uint8_t x, uint8_t y, uint16_t v, uint8_t digits) {
    uint8_t i;
    for (i = digits; i > 0; i--) {
        put_tile(x + i - 1, y, char_tile['0' + (v % 10)]);
        v /= 10;
    }
}

static void clear_screen(void) {
    uint8_t x, y;
    for (y = 0; y < 32; y++)
        for (x = 0; x < 32; x++) put_tile(x, y, T_SKY);
}

static void hide_sprites(void) {
    uint8_t i;
    for (i = 0; i < 40; i++) move_sprite(i, 0, 0);
}

/* ------------------------------------------------------------------ sound */
uint8_t music_track, music_step, music_timer, music_on;
uint8_t sfx3_t, sfx3_kind, sfx4_t;

static void sound_init(void) {
    NR52_REG = 0x80; NR51_REG = 0xFF; NR50_REG = 0x77;
    /* triangle-ish wave for channel 3 */
    NR30_REG = 0x00;
    {
        static const uint8_t wave[16] = { 0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF, 0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10 };
        uint8_t i;
        for (i = 0; i < 16; i++) ((volatile uint8_t *)0xFF30)[i] = wave[i];
    }
    NR30_REG = 0x80;
}

static void music_start(uint8_t t) { music_track = t; music_step = 0; music_timer = 0; music_on = 1; }
static void music_stop(void) { music_on = 0; NR12_REG = 0; NR22_REG = 0; NR14_REG = 0x80; NR24_REG = 0x80; }

static void music_update(void) {
    uint8_t n;
    uint16_t f;
    if (!music_on) return;
    if (music_timer++ < 7) return;
    music_timer = 0;
    n = track_lead[music_track][music_step];
    if (n) {
        f = note_freq[n - 1];
        NR11_REG = 0x80; NR12_REG = 0x74; NR13_REG = (uint8_t)f; NR14_REG = 0x80 | (uint8_t)(f >> 8);
    }
    n = track_bass[music_track][music_step];
    if (n) {
        f = note_freq[n - 1];
        NR21_REG = 0x40; NR22_REG = 0x83; NR23_REG = (uint8_t)f; NR24_REG = 0x80 | (uint8_t)(f >> 8);
    }
    music_step = (music_step + 1) & (TRACK_STEPS - 1);
}

#define SFX_JUMP 1
#define SFX_COIN 2
#define SFX_HIT 3
#define SFX_THROW 4
#define SFX_HURT 5
#define SFX_STAR 6
#define SFX_BOSS 7

static void sfx_ch3(uint16_t f) {
    NR32_REG = 0x20; NR33_REG = (uint8_t)f; NR34_REG = 0x80 | (uint8_t)(f >> 8);
}
static void sfx_noise(uint8_t env, uint8_t poly) {
    NR41_REG = 0x00; NR42_REG = env; NR43_REG = poly; NR44_REG = 0x80;
}

static void sfx(uint8_t k) {
    switch (k) {
    case SFX_JUMP: sfx3_kind = 1; sfx3_t = 10; sfx_ch3(1500); break;
    case SFX_COIN: sfx3_kind = 2; sfx3_t = 12; sfx_ch3(1850); break;
    case SFX_STAR: sfx3_kind = 3; sfx3_t = 40; sfx_ch3(1600); break;
    case SFX_HIT: sfx_noise(0xA1, 0x35); break;
    case SFX_THROW: sfx_noise(0x61, 0x10); break;
    case SFX_HURT: sfx_noise(0xF3, 0x55); sfx3_kind = 4; sfx3_t = 12; sfx_ch3(900); break;
    case SFX_BOSS: sfx_noise(0xF4, 0x66); break;
    }
}

static void sfx_update(void) {
    if (sfx3_t) {
        sfx3_t--;
        switch (sfx3_kind) {
        case 1: sfx_ch3(1500 + (10 - sfx3_t) * 30); break;
        case 2: if (sfx3_t == 6) sfx_ch3(1950); break;
        case 3: if ((sfx3_t & 7) == 0) sfx_ch3(1600 + (40 - sfx3_t) * 8); break;
        case 4: sfx_ch3(900 - (12 - sfx3_t) * 40); break;
        }
        if (!sfx3_t) NR32_REG = 0x00;
    }
}

/* ------------------------------------------------------------------ level data */
static uint8_t tile_at(int16_t tx, int16_t ty) {
    if (ty < 0 || ty >= LH) return T_SKY;
    if (tx < 0 || tx >= lw) return T_WALL;
    return lvl[(uint16_t)tx * LH + (uint8_t)ty];
}

static uint8_t solid_px(int16_t x, int16_t y) {
    if (x < 0) return 1;
    if (y < 0) return 0;
    return tile_class[tile_at(x >> 3, y >> 3)] & 1;
}

static uint8_t rect_solid(int16_t x0, int16_t y0, int16_t x1, int16_t y1) {
    int16_t x, y;
    for (y = y0 & ~7; y <= y1; y += 8)
        for (x = x0 & ~7; x <= x1; x += 8)
            if (solid_px(x, y)) return 1;
    return 0;
}

static void draw_column(int16_t tx) {
    uint8_t buf[LH], at[LH], y;
    if (tx < 0 || tx >= lw) return;
    for (y = 0; y < LH; y++) buf[y] = lvl[(uint16_t)tx * LH + y];
    set_bkg_tiles(tx & 31, 0, 1, LH, buf);
#ifdef TARGET_GBC
    for (y = 0; y < LH; y++) at[y] = tile_palette[buf[y]];
    VBK_REG = 1;
    set_bkg_tiles(tx & 31, 0, 1, LH, at);
    VBK_REG = 0;
#else
    (void)at;
#endif
}

static void set_lvl_tile(int16_t tx, int16_t ty, uint8_t t) {
    if (tx < 0 || tx >= lw || ty < 0 || ty >= LH) return;
    lvl[(uint16_t)tx * LH + (uint8_t)ty] = t;
    if (tx >= (cam_x >> 3) - 1 && tx <= (cam_x >> 3) + 21) put_tile(tx, ty, t);
}

static void decode_level(uint8_t n) {
    const LevelInfo *li = &level_info[n];
    uint16_t i = 0, o = 0;
    uint8_t cnt, t, k;
    while (i < li->rle_len) {
        cnt = li->rle[i++];
        t = li->rle[i++];
        for (k = 0; k < cnt; k++) lvl[o++] = t;
    }
    lw = li->w; cur_theme = li->theme; cur_boss = li->boss; arena0 = li->arena_x0; arena1 = li->arena_x1;
}

/* ------------------------------------------------------------------ save */
#define SAVE_BASE ((volatile uint8_t *)0xA000)
static uint8_t save_sum(void) { return (uint8_t)(0x5A + save_reached * 7 + save_stars * 13 + (uint8_t)save_coins + (uint8_t)(save_coins >> 8) * 3); }

static void save_write(void) {
    ENABLE_RAM; SWITCH_RAM(0);
    SAVE_BASE[0] = 'C'; SAVE_BASE[1] = 'P'; SAVE_BASE[2] = 'T'; SAVE_BASE[3] = '1';
    SAVE_BASE[4] = save_reached; SAVE_BASE[5] = save_stars;
    SAVE_BASE[6] = (uint8_t)save_coins; SAVE_BASE[7] = (uint8_t)(save_coins >> 8);
    SAVE_BASE[8] = save_sum();
    DISABLE_RAM;
}

uint8_t dbg_raw[9];
static uint8_t save_load(void) {
    uint8_t ok = 0, q;
    ENABLE_RAM; SWITCH_RAM(0);
    for (q = 0; q < 9; q++) dbg_raw[q] = SAVE_BASE[q];
    if (SAVE_BASE[0] == 'C' && SAVE_BASE[1] == 'P' && SAVE_BASE[2] == 'T' && SAVE_BASE[3] == '1') {
        save_reached = SAVE_BASE[4]; save_stars = SAVE_BASE[5];
        save_coins = SAVE_BASE[6] | ((uint16_t)SAVE_BASE[7] << 8);
        if (SAVE_BASE[8] == save_sum() && save_reached < NUM_LEVELS + 1) ok = 1;
    }
    DISABLE_RAM;
    if (!ok) { save_reached = 0; save_stars = 0; save_coins = 0; }
    return ok;
}

/* ------------------------------------------------------------------ screens */
static void wait_a(void) {
    do { vsync(); prev_keys = keys; keys = joypad(); music_update(); sfx_update(); } while (!((keys & (J_A | J_START)) && !(prev_keys & (J_A | J_START))));
}

static void text_page(const char *l0, const char *l1, const char *l2, const char *l3, const char *l4) {
    DISPLAY_OFF;
    HIDE_WIN;
    move_bkg(0, 0);
    clear_screen();
    hide_sprites();
    print_at(1, 3, l0); print_at(1, 5, l1); print_at(1, 7, l2); print_at(1, 9, l3); print_at(1, 11, l4);
    print_at(4, 16, "PRESS A");
    DISPLAY_ON;
    wait_a();
}

static void draw_hud(void) {
    uint8_t i, buf[20], at[20];
    for (i = 0; i < 20; i++) { buf[i] = T_SKY; at[i] = 3; }
    for (i = 0; i < max_hp; i++) { buf[i] = i < hp ? T_HEART : T_SKY; at[i] = 2; }
    buf[6] = T_COIN; at[6] = 1;
    buf[7] = char_tile['x'];
    buf[8] = char_tile['0' + (coins / 100) % 10];
    buf[9] = char_tile['0' + (coins / 10) % 10];
    buf[10] = char_tile['0' + coins % 10];
    buf[12] = T_STAR; at[12] = 4;
    buf[13] = char_tile['x']; buf[14] = char_tile['0' + save_stars % 10];
    buf[16] = char_tile['L']; buf[17] = char_tile['0' + (cur_level + 1)];
    if (bactive && !bdead) {
        buf[15] = T_NOTE;
    }
    set_win_tiles(0, 0, 20, 1, buf);
#ifdef TARGET_GBC
    VBK_REG = 1;
    set_win_tiles(0, 0, 20, 1, at);
    VBK_REG = 0;
#endif
}

/* ------------------------------------------------------------------ sprites */
static void spr(uint8_t n, uint8_t tile, int16_t x, int16_t y, uint8_t prop) {
    set_sprite_tile(n, tile);
    set_sprite_prop(n, prop);
    if (x < -8 || x > 168 || y < -16 || y > 160) { move_sprite(n, 0, 0); return; }
    move_sprite(n, (uint8_t)(x + 8), (uint8_t)(y + 16));
}

#define OAM_PIP 0
#define OAM_HATHEAD 2
#define OAM_HAT 3
#define OAM_EN 4
#define OAM_BOSS 16
#define OAM_PROJ 25
#define OAM_FX 28

static void draw_sprites(void) {
    uint8_t i, flip, pf, t, k;
    int16_t sx, sy;
    int16_t ppx = px >> 4, ppy = py >> 4;
    /* Pip */
    flip = facing ? 0 : S_FLIPX;
    t = S_PIP0;
    if (!on_ground) t = S_PIP3;
    else if (vx != 0) t = (anim & 8) ? S_PIP1 : S_PIP2;
    pf = 0;
    if (invuln && (frame_count & 2)) {
        move_sprite(OAM_PIP, 0, 0); move_sprite(OAM_PIP + 1, 0, 0); move_sprite(OAM_HATHEAD, 0, 0);
    } else {
        spr(OAM_PIP, t, ppx - cam_x, ppy, flip | pf);
        spr(OAM_PIP + 1, t + 1, ppx - cam_x, ppy + 8, flip | pf);
        if (hat_state == 0) spr(OAM_HATHEAD, S_PIPHAT, ppx - cam_x, ppy - 3, flip | 3);
        else move_sprite(OAM_HATHEAD, 0, 0);
    }
    /* thrown hat */
    if (hat_state) spr(OAM_HAT, (frame_count & 4) ? S_HAT1 : S_HAT0, hx - cam_x, hy, 3);
    else move_sprite(OAM_HAT, 0, 0);
    /* enemies */
    for (i = 0; i < MAX_EN && i < 12; i++) {
        if (i >= 12) break;
        if (i < n_en && ealive[i] && ex[i] - cam_x > -16 && ex[i] - cam_x < 176 && (OAM_EN + i) < OAM_BOSS) {
            k = (frame_count & 8) ? 1 : 0;
            spr(OAM_EN + i, (etype[i] ? S_FLY0 : S_WALK0) + k, ex[i] - cam_x, ey[i], 1 | (edir[i] > 0 ? S_FLIPX : 0));
        } else if (OAM_EN + i < OAM_BOSS) move_sprite(OAM_EN + i, 0, 0);
    }
    /* boss: 3x3 sprites */
    if (bactive && !(bdead && (frame_count & 2))) {
        uint8_t r, c, tile0 = (cur_boss == 1) ? S_BOSS1 : S_BOSS2;
        uint8_t bf = (bflash && (frame_count & 2)) ? 0 : 1;
        for (r = 0; r < 3; r++) for (c = 0; c < 3; c++) {
            uint8_t cc = (bdir > 0) ? c : 2 - c;
            spr(OAM_BOSS + r * 3 + c, tile0 + r * 3 + c, bx + cc * 8 - cam_x, by + r * 8, (cur_boss == 1 ? 2 : 4) | (bdir > 0 ? 0 : S_FLIPX));
            (void)bf;
        }
    } else {
        for (i = 0; i < 9; i++) move_sprite(OAM_BOSS + i, 0, 0);
    }
    for (i = 0; i < 3; i++) {
        if (pract[i]) spr(OAM_PROJ + i, (frame_count & 4) ? S_PROJ0 : S_PROJ1, prx[i] - cam_x, pry[i], 3);
        else move_sprite(OAM_PROJ + i, 0, 0);
    }
    (void)sx; (void)sy;
}

/* ------------------------------------------------------------------ test hook
 * The emulator test-suite (pocket/tests/test_gb.py) queues (address, value) pokes here;
 * they are applied at a frame boundary so tests can teleport Pip deterministically. */
uint16_t dbg_addr[16];
uint8_t dbg_val[16];
uint8_t dbg_n;
static void apply_pokes(void) {
    uint8_t i, n = dbg_n;
    for (i = 0; i < n; i++) *(volatile uint8_t *)dbg_addr[i] = dbg_val[i];
    dbg_n = 0;
}

/* ------------------------------------------------------------------ gameplay */
static void hurt_player(void) {
    if (invuln || player_dead) return;
    if (hp) hp--;
    invuln = 90;
    vy = -36; vx = facing ? -20 : 20;
    sfx(SFX_HURT);
    if (hp == 0) player_dead = 1;
}

static void spawn_projectile(int16_t x, int16_t y, int16_t vxx, int16_t vyy) {
    uint8_t i;
    for (i = 0; i < 3; i++) if (!pract[i]) { pract[i] = 1; prx[i] = x; pry[i] = y; prvx[i] = vxx; prvy[i] = vyy; return; }
}

static void load_level(uint8_t n) {
    uint8_t i;
    const LevelInfo *li;
    cur_level = n;
    DISPLAY_OFF;
    decode_level(n);
    li = &level_info[n];
    cam_x = 0; drawn_tx = 0;
    clear_screen();
    set_pal_bg(cur_theme);
    set_bkg_data(0, NUM_BG_TILES, bg_tiles);
    set_sprite_data(0, NUM_SPR_TILES, spr_tiles);
    for (i = 0; i <= 20; i++) { draw_column(i); drawn_tx = i; }
    move_bkg(0, 0);
    px = 3 * 8 * 16; py = (GROUND_ROW - 2) * 8 * 16; vx = vy = 0; facing = 1; on_ground = 0; invuln = 0;
    hat_state = 0; level_done = 0; player_dead = 0; hp = max_hp;
    n_en = li->n_enemies; if (n_en > MAX_EN) n_en = MAX_EN;
    for (i = 0; i < n_en; i++) {
        ex[i] = li->enemies[i].x * 8; ey[i] = li->enemies[i].y * 8; ey0[i] = ey[i];
        etype[i] = li->enemies[i].type; ealive[i] = 1; edir[i] = -1;
    }
    for (i = 0; i < 3; i++) pract[i] = 0;
    bactive = 0; bdead = 0; arena_locked = 0; star_spawned = 0; bhp = 0;
    if (li->boss) {
        bx = (arena1 - 6) * 8; by = (GROUND_ROW - 3) * 8; bdir = -1; bstate = 0; btimer = 0; bvuln = 0; bflash = 0; bphase = 0;
        bhp = li->boss == 1 ? 5 : 8;
        if (li->boss == 2) by = 56;
    }
    SHOW_BKG; SHOW_SPRITES;
    LCDC_REG |= LCDCF_WIN9C00;
    move_win(7, 136);
    SHOW_WIN;
    draw_hud();
    DISPLAY_ON;
    music_start(li->music);
}

static void kill_enemy(uint8_t i) {
    ealive[i] = 0;
    sfx(SFX_HIT);
    coins++;
}

static void collect_tiles(int16_t x0, int16_t y0, int16_t x1, int16_t y1) {
    int16_t tx, ty;
    uint8_t c;
    for (ty = y0 >> 3; ty <= (y1 >> 3); ty++)
        for (tx = x0 >> 3; tx <= (x1 >> 3); tx++) {
            c = tile_class[tile_at(tx, ty)];
            if (c & 4) { set_lvl_tile(tx, ty, T_SKY); coins++; sfx(SFX_COIN); draw_hud(); }
            if ((c & 8) && !level_done) { level_done = 1; }
        }
}

static void boss_hit(void) {
    if (!bvuln || bdead || bflash) return;
    bhp--;
    bflash = 40;
    sfx(SFX_BOSS);
    if (bhp <= 0) {
        bdead = 1; btimer = 90; bvuln = 0;
    } else if (cur_boss == 1 && bhp <= 2) bphase = 1;
    else if (cur_boss == 2) bphase = (bhp <= 3) ? 2 : (bhp <= 6 ? 1 : 0);
}

static void update_boss(void) {
    int16_t ppx = px >> 4, ppy = py >> 4, bmin, bmax;
    uint8_t i;
    if (!cur_boss) return;
    /* trigger: lock the arena when Pip enters */
    if (!arena_locked && !bdead && ppx > arena0 * 8 + 24) {
        arena_locked = 1; bactive = 1; bstate = 0; btimer = 60;
        for (i = 0; i < GROUND_ROW; i++) { set_lvl_tile(arena0, i, T_BARRIER); set_lvl_tile(arena0 + 21, i, T_BARRIER); }
        music_start(cur_boss == 1 ? 3 : 3);
        sfx(SFX_BOSS);
    }
    if (!arena_locked) return;
    bmin = (arena0 + 2) * 8; bmax = (arena0 + 19) * 8;
    if (bflash) bflash--;
    if (bdead) {
        if (btimer) btimer--;
        if (!btimer && !star_spawned) {
            star_spawned = 1; bactive = 0;
            set_lvl_tile(arena0 + 11, GROUND_ROW - 2, T_STAR);
            sfx(SFX_STAR);
            for (i = 0; i < GROUND_ROW; i++) { set_lvl_tile(arena0, i, T_SKY); }
        }
        return;
    }
    if (cur_boss == 1) {                 /* Scarabella the beetle queen */
        switch (bstate) {
        case 0: if (btimer) btimer--; else { bstate = 1; btimer = 100; } break;
        case 1:                         /* stalk Pip */
            bdir = (ppx > bx + 8) ? 1 : -1;
            if (frame_count & 1) bx += bdir;
            if (bphase && (frame_count & 63) == 0) spawn_projectile(bx + 12, by + 8, bdir * 24, -30);
            if (btimer) btimer--; else { bstate = 2; btimer = 40; }
            break;
        case 2: bx += ((frame_count & 2) ? 1 : -1) ; if (btimer) btimer--; else { bstate = 3; bdir = (ppx > bx + 8) ? 1 : -1; sfx(SFX_BOSS); } break;
        case 3:                         /* charge */
            bx += bdir * 3;
            if (bx < bmin || bx > bmax) { bx = bx < bmin ? bmin : bmax; bstate = 4; btimer = 110; bvuln = 1; sfx(SFX_HIT); }
            break;
        case 4: bvuln = 1; if (btimer) btimer--; else { bvuln = 0; bstate = 1; btimer = 100; } break;
        }
    } else {                             /* Baron Von Grumblebelt */
        uint8_t sp = bphase ? 2 : 1;
        switch (bstate) {
        case 0: if (btimer) btimer--; else { bstate = 1; btimer = 200; } break;
        case 1:                         /* hover and drop notes */
            bx += ((frame_count >> 1) & 1) ? 0 : 0;
            bx += ((int16_t)sine[(frame_count >> 2) & 31]) / 2 * sp / 3 * ((frame_count & 1) ? 1 : 0) + ((ppx > bx + 8) ? 1 : -1) * ((frame_count & 3) == 0 ? 1 : 0);
            if (bx < bmin) bx = bmin; if (bx > bmax) bx = bmax;
            by = 48 + sine[(frame_count >> 2) & 31];
            bdir = (ppx > bx + 8) ? 1 : -1;
            if ((frame_count % (uint8_t)(70 - bphase * 18)) == 0) {
                spawn_projectile(bx + 8, by + 20, 0, 12);
                if (bphase >= 2) { spawn_projectile(bx + 4, by + 20, -12, 10); }
            }
            if (btimer) btimer--; else { bstate = 2; btimer = 40; }
            break;
        case 2: by += 4; if (by >= (GROUND_ROW - 3) * 8) { by = (GROUND_ROW - 3) * 8; bstate = 3; btimer = 100; bvuln = 1; sfx(SFX_HIT); } break;
        case 3: bvuln = 1; if (btimer) btimer--; else { bvuln = 0; bstate = 4; } break;
        case 4: by -= 2; if (by <= 56) { by = 56; bstate = 1; btimer = 190; } break;
        }
        if (bstate == 1 || bstate == 4) {
            /* nothing: horizontal tracking handled above */
        }
        (void)sp;
    }
    /* boss body vs Pip */
    if (!bdead) {
        int16_t dx1 = ppx + 1, dx2 = ppx + 6, dy1 = ppy + 2, dy2 = ppy + 15;
        if (dx2 > bx + 2 && dx1 < bx + 22 && dy2 > by + 2 && dy1 < by + 24) {
            if (vy > 0 && dy2 < by + 12) { if (bvuln) boss_hit(); vy = -44; }
            else if (!bvuln) hurt_player();
        }
        /* hat vs boss */
        if (hat_state && hx + 8 > bx && hx < bx + 24 && hy + 8 > by && hy < by + 24) {
            if (bvuln) boss_hit();
            hat_state = 2;
        }
    }
}

static void update_projectiles(void) {
    uint8_t i;
    int16_t ppx = px >> 4, ppy = py >> 4;
    for (i = 0; i < 3; i++) {
        if (!pract[i]) continue;
        prx[i] += prvx[i] >> 3; pry[i] += prvy[i] >> 3;
        if (cur_boss == 1) prvy[i] += 2;
        if (prx[i] < 0 || prx[i] > lw * 8 || pry[i] > 150 || pry[i] < -8 || solid_px(prx[i] + 4, pry[i] + 4)) { pract[i] = 0; continue; }
        if (prx[i] + 6 > ppx + 1 && prx[i] + 2 < ppx + 6 && pry[i] + 6 > ppy + 2 && pry[i] + 2 < ppy + 15) { pract[i] = 0; hurt_player(); }
    }
}

static void update_hat(void) {
    int16_t ppx = px >> 4, ppy = py >> 4, tx, ty;
    uint8_t i;
    if (pressed & J_B && hat_state == 0) {
        hat_state = 1; hat_dist = 0; hat_bounced = 0;
        hat_dir = facing ? 1 : -1;
        hx = ppx + (facing ? 6 : -6); hy = ppy + 4;
        sfx(SFX_THROW);
    }
    if (!hat_state) return;
    if (hat_state == 1) {
        hx += hat_dir * 3; hat_dist += 3;
        if (hat_dist >= 60 || solid_px(hx + 4, hy + 4)) hat_state = 2;
    } else {
        int16_t tx2 = ppx, ty2 = ppy + 4;
        if (hx < tx2 - 2) hx += 4; else if (hx > tx2 + 2) hx -= 4;
        if (hy < ty2 - 2) hy += 3; else if (hy > ty2 + 2) hy -= 3;
        if (hx > tx2 - 6 && hx < tx2 + 6 && hy > ty2 - 8 && hy < ty2 + 8) { hat_state = 0; sfx(SFX_THROW); }
    }
    /* hat picks up coins and hits enemies */
    tx = (hx + 4) >> 3; ty = (hy + 4) >> 3;
    if (tile_class[tile_at(tx, ty)] & 4) { set_lvl_tile(tx, ty, T_SKY); coins++; sfx(SFX_COIN); draw_hud(); }
    for (i = 0; i < n_en; i++) {
        if (ealive[i] && hx + 8 > ex[i] && hx < ex[i] + 8 && hy + 8 > ey[i] && hy < ey[i] + 8) { kill_enemy(i); draw_hud(); }
    }
    /* hat bounce: land on the flying hat */
    if (hat_state && !hat_bounced && vy > 0 && ppy + 16 > hy && ppy + 12 < hy + 6 && ppx + 6 > hx && ppx + 1 < hx + 8) {
        vy = -40; hat_bounced = 1; sfx(SFX_JUMP);
    }
}

static void update_enemies(void) {
    uint8_t i;
    int16_t ppx = px >> 4, ppy = py >> 4;
    for (i = 0; i < n_en; i++) {
        if (!ealive[i]) continue;
        if (ex[i] - cam_x < -40 || ex[i] - cam_x > 200) continue;
        if (etype[i] == 0) {
            if (frame_count & 1) {
                int16_t nx = ex[i] + edir[i];
                int16_t front = edir[i] > 0 ? nx + 8 : nx - 1;
                if (solid_px(front, ey[i] + 4) || !solid_px(front, ey[i] + 9)) edir[i] = -edir[i];
                else ex[i] = nx;
            }
        } else {
            if (frame_count & 1) ex[i] += (ppx > ex[i]) ? 1 : -1;
            ey[i] = ey0[i] + sine[(frame_count >> 2) & 31];
            edir[i] = (ppx > ex[i]) ? 1 : -1;
        }
        /* vs Pip */
        if (ppx + 6 > ex[i] && ppx + 1 < ex[i] + 8 && ppy + 15 > ey[i] && ppy + 2 < ey[i] + 8) {
            if (vy > 0 && ppy + 15 < ey[i] + 6) { kill_enemy(i); vy = -38; draw_hud(); }
            else hurt_player();
        }
    }
}

void update_player(void) {
    int16_t ppx = px >> 4, ppy = py >> 4, nx, ny, edge;
    uint8_t left = keys & J_LEFT, right = keys & J_RIGHT;
    if (player_dead) return;
    if (invuln) invuln--;
    /* horizontal */
    if (left && !right) { vx -= 3; facing = 0; }
    else if (right && !left) { vx += 3; facing = 1; }
    else if (vx > 0) { vx -= 3; if (vx < 0) vx = 0; }
    else if (vx < 0) { vx += 3; if (vx > 0) vx = 0; }
    if (vx > 24) vx = 24;
    if (vx < -24) vx = -24;
    /* ground probe (stable standing: no gravity while supported) */
    if (vy >= 0) on_ground = rect_solid(ppx + 1, ppy + 16, ppx + 6, ppy + 16);
    /* jump (with coyote + buffer) */
    if (pressed & J_A) jbuf = 6;
    if (jbuf) jbuf--;
    if (on_ground) coyote = 5; else if (coyote) coyote--;
    if (jbuf && coyote) { vy = -58; jbuf = 0; coyote = 0; on_ground = 0; sfx(SFX_JUMP); }
    /* gravity */
    if (on_ground && vy >= 0) vy = 0;
    else {
        if (vy < 0 && !(keys & J_A)) vy += 8; else vy += 4;
        if (vy > 64) vy = 64;
    }
    /* move X */
    nx = px + vx;
    edge = (nx >> 4) + (vx > 0 ? 6 : 1);
    if (vx != 0 && rect_solid(edge, ppy + 3, edge, ppy + 15)) vx = 0; else px = nx;
    ppx = px >> 4;
    /* move Y */
    ny = py + vy;
    if (vy > 0) {
        edge = (ny >> 4) + 15;
        if (rect_solid(ppx + 1, edge, ppx + 6, edge)) {
            py = (int16_t)((edge & ~7) - 16) << 4; vy = 0; on_ground = 1;
        } else { py = ny; on_ground = 0; }
    } else if (vy < 0) {
        edge = (ny >> 4) + 2;
        if (rect_solid(ppx + 1, edge, ppx + 6, edge)) vy = 0; else py = ny;
        on_ground = 0;
    }
    ppy = py >> 4;
    /* hazards, pickups */
    {
        int16_t tx, ty;
        for (ty = (ppy + 4) >> 3; ty <= (ppy + 15) >> 3; ty++)
            for (tx = (ppx + 1) >> 3; tx <= (ppx + 6) >> 3; tx++)
                if (tile_class[tile_at(tx, ty)] & 2) hurt_player();
    }
    collect_tiles(ppx + 1, ppy + 2, ppx + 6, ppy + 15);
    if (ppy > 150) { hp = 0; player_dead = 1; sfx(SFX_HURT); }
    anim++;
}

static void update_camera(void) {
    int16_t target, maxc = (int16_t)lw * 8 - 160;
    if (arena_locked) target = arena0 * 8 + 8;
    else target = (px >> 4) - 72;
    if (target < cam_x && !arena_locked) target = cam_x;
    if (target > maxc) target = maxc;
    if (target < 0) target = 0;
    if (arena_locked) { if (cam_x < target) cam_x += 2; if (cam_x > target) cam_x -= 2; }
    else cam_x = target;
    while ((int16_t)drawn_tx < (cam_x >> 3) + 20 && drawn_tx < lw - 1) { drawn_tx++; draw_column(drawn_tx); }
    move_bkg((uint8_t)cam_x, 0);
}

/* returns 1 when level completed, 0 when player died */
static uint8_t play_level(uint8_t n) {
    uint8_t paused = 0;
    load_level(n);
    while (1) {
        vsync();
        prev_keys = keys; keys = joypad(); pressed = keys & ~prev_keys;
        frame_count++;
        music_update(); sfx_update();
        apply_pokes();
        if (pressed & J_START) {
            paused = !paused;
            if (paused) { print_at(0, 0, ""); }
        }
        if (paused) continue;
        update_player();
        update_hat();
        update_enemies();
        update_boss();
        update_projectiles();
        update_camera();
        draw_sprites();
        if (frame_count % 8 == 0) draw_hud();
        if (level_done) { return 1; }
        if (player_dead) {
            music_stop();
            sfx(SFX_HURT);
            {
                uint8_t k;
                for (k = 0; k < 60; k++) { vsync(); sfx_update(); }
            }
            return 0;
        }
    }
}

static void show_title(uint8_t has_save) {
    uint8_t choice = 0, blink = 0;
    DISPLAY_OFF;
    HIDE_WIN;
    move_bkg(0, 0);
    set_pal_bg(0);
    set_bkg_data(0, NUM_BG_TILES, bg_tiles);
    set_sprite_data(0, NUM_SPR_TILES, spr_tiles);
    clear_screen();
    hide_sprites();
    print_at(5, 3, "CAPT AND CO");
    print_at(4, 5, "POCKET EDITION");
    print_at(5, 15, "ORIGINAL GAME");
    {
        uint8_t x;
        for (x = 0; x < 20; x++) { put_tile(x, 12, T_GRASS); put_tile(x, 13, T_DIRT); }
        put_tile(3, 11, T_TRUNK); put_tile(3, 10, T_LEAF); put_tile(2, 10, T_LEAF); put_tile(4, 10, T_LEAF);
        put_tile(16, 11, T_HILL);
    }
    SHOW_BKG; SHOW_SPRITES;
    DISPLAY_ON;
    spr(0, S_PIP0, 70, 96, 0); spr(1, S_PIP0 + 1, 70, 104, 0);
    spr(2, S_PIPHAT, 70, 93, 3);
    spr(3, S_WALK0, 110, 104, 1);
    music_start(0);
    while (1) {
        vsync();
        prev_keys = keys; keys = joypad(); pressed = keys & ~prev_keys;
        music_update(); sfx_update(); blink++;
        if (has_save) {
            if (pressed & (J_UP | J_DOWN)) choice ^= 1;
            print_at(6, 8, choice == 0 ? ">CONTINUE" : " CONTINUE");
            print_at(6, 9, choice == 1 ? ">NEW GAME" : " NEW GAME");
        } else {
            print_at(5, 8, (blink & 32) ? "           " : "PRESS START");
        }
        if (pressed & (J_START | J_A)) break;
    }
    if (!has_save) { save_reached = 0; save_stars = 0; save_coins = 0; }
    else if (choice == 1) { save_reached = 0; save_stars = 0; save_coins = 0; }
}

static void story_intro(void) {
    text_page("LONG AGO A SONG", "HELD THE WORLD", "TOGETHER. EVERY", "NOTE WAS A STAR.", "");
    text_page("BARON GRUMBLEBELT", "STOLE THEM ALL FOR", "HIS GIANT MUSIC", "BOX. THAT RASCAL!", "");
    text_page("CAPT: PIP WAKE UP!", "PIP: FIVE MORE", "MINUTES...", "CAPT: NO. HAT BOSS", "SAYS GO!");
}

int main(void) {
    uint8_t lv, has_save, result;
    init_charmap();
    sound_init();
    SPRITES_8x8;
    max_hp = 3;
    has_save = save_load();
    while (1) {
        show_title(has_save);
        lv = save_reached;
        if (lv >= NUM_LEVELS) lv = NUM_LEVELS - 1;
        coins = save_coins;
        if (!has_save || lv == 0) story_intro();
        while (lv < NUM_LEVELS) {
            const LevelInfo *li = &level_info[lv];
            char numbuf[10];
            numbuf[0] = 'L'; numbuf[1] = 'E'; numbuf[2] = 'V'; numbuf[3] = 'E'; numbuf[4] = 'L'; numbuf[5] = ' '; numbuf[6] = '1' + lv; numbuf[7] = 0;
            if (li->boss == 1) text_page(numbuf, li->name, "", "MADAME SCARABELLA:", "MY HAIR!! HOW DARE");
            else if (li->boss == 2) text_page(numbuf, li->name, "", "BARON: WIND THE KEY!", "HE IS VERY SERIOUS");
            else text_page(numbuf, li->name, "", "A JUMP  B HAT", "GRAB THE STAR!");
            result = play_level(lv);
            if (result) {
                save_stars++;
                if (lv + 1 > save_reached) save_reached = lv + 1;
                save_coins = coins;
                save_write();
                has_save = 1;
                music_stop();
                sfx(SFX_STAR);
                text_page("STAR GET!", "", "NICE JOB PIP!", "", "");
                lv++;
            } else {
                coins = save_coins;
                text_page("OOPS!", "", "CAPT SAYS TRY", "AGAIN. WITH SNACKS.", "");
            }
        }
        text_page("THE MUSIC BOX IS", "QUIET... THEN A NEW", "FRIENDLIER TUNE", "BEGINS TO PLAY.", "");
        text_page("THE END", "THANKS FOR PLAYING!", "", "CAPT: SNACKS NOW.", "");
        save_reached = 0; save_stars = 0; save_write();
        has_save = 0;
    }
    return 0;
}
