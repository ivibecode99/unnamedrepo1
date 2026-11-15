/*
 * Capt & Co. - Pocket Edition (Game Boy Advance), built with Butano (https://github.com/GValiente/butano).
 * Original game. D-pad move, A jump, B throw Capt (boomerang hat), START pause.
 * 4 levels, 2 bosses, battery-backed save (SRAM). Same levels/art as the GB and GBC versions.
 */
#include "bn_core.h"
#include "bn_keypad.h"
#include "bn_sram.h"
#include "bn_memory.h"
#include "bn_optional.h"
#include "bn_bg_tiles.h"
#include "bn_bg_palettes.h"
#include "bn_bg_palette_ptr.h"
#include "bn_regular_bg_ptr.h"
#include "bn_regular_bg_item.h"
#include "bn_regular_bg_map_ptr.h"
#include "bn_regular_bg_map_item.h"
#include "bn_regular_bg_map_cell_info.h"
#include "bn_sprite_ptr.h"

#include "bn_regular_bg_tiles_items_bg_tiles.h"
#include "bn_bg_palette_items_bg_pal.h"
#include "bn_sprite_items_pip.h"
#include "bn_sprite_items_piphat.h"
#include "bn_sprite_items_hat.h"
#include "bn_sprite_items_walker.h"
#include "bn_sprite_items_flyer.h"
#include "bn_sprite_items_boss1.h"
#include "bn_sprite_items_boss2.h"
#include "bn_sprite_items_proj.h"

#include "gba_data.h"

namespace {

constexpr int LH = data::level_h;
constexpr int MAX_EN = 12;
constexpr int GROUND_ROW = 14;
constexpr int VOFF = 8;                    // level is 144 px tall, screen 160: shift down 8
constexpr int SCREEN_W = 240;

// ------------------------------------------------------------------ BG maps
struct bg_map_64x32 {
    alignas(int) bn::regular_bg_map_cell cells[64 * 32];
    bn::regular_bg_map_item item;
    bg_map_64x32() : item(cells[0], bn::size(64, 32)) { bn::memory::clear(cells); }
    void set(int x, int y, int tile) {
        bn::regular_bg_map_cell_info info(cells[item.cell_index(x & 63, y)]);
        info.set_tile_index(tile);
        info.set_palette_id(data::tile_palette[tile]);
        cells[item.cell_index(x & 63, y)] = info.cell();
    }
};
struct bg_map_32x32 {
    alignas(int) bn::regular_bg_map_cell cells[32 * 32];
    bn::regular_bg_map_item item;
    bg_map_32x32() : item(cells[0], bn::size(32, 32)) { bn::memory::clear(cells); }
    void set(int x, int y, int tile, int pal = -1) {
        bn::regular_bg_map_cell_info info(cells[item.cell_index(x & 31, y & 31)]);
        info.set_tile_index(tile);
        info.set_palette_id(pal >= 0 ? pal : data::tile_palette[tile]);
        cells[item.cell_index(x & 31, y & 31)] = info.cell();
    }
};
constexpr int HUD_PAL = 5;

bg_map_64x32* game_map = nullptr;
bg_map_32x32* ui_map = nullptr;
bn::optional<bn::regular_bg_ptr> game_bg;
bn::optional<bn::regular_bg_ptr> ui_bg;
bn::optional<bn::regular_bg_map_ptr> game_bg_map;
bn::optional<bn::regular_bg_map_ptr> ui_bg_map;
bool game_dirty = false, ui_dirty = false;

// ------------------------------------------------------------------ game state (mirrors the GB version)
int lvl[160 * LH];
int lw, cur_level, cur_theme, cur_boss, arena0, arena1;
int cam_x, drawn_tx;
int px, py, vx, vy;                       // 1/16 px
bool on_ground, facing = true;
int hp, max_hp = 3, invuln, coyote, jbuf, anim;
unsigned coins;
bool level_done, player_dead;
int hx, hy, hat_state, hat_dist, hat_dir; bool hat_bounced;
int ex[MAX_EN], ey[MAX_EN], ey0[MAX_EN], edir[MAX_EN], etype[MAX_EN], n_en;
bool ealive[MAX_EN];
int bx, by, bhp, bdir, bstate, btimer, bflash, bphase;
bool bvuln, bactive, bdead, arena_locked, star_spawned;
int prx[3], pry[3], prvx[3], prvy[3]; bool pract[3];
int save_reached, save_stars; unsigned save_coins;
unsigned frame_count;

const int sine_tab[32] = { 0, 1, 2, 3, 4, 5, 5, 6, 6, 6, 5, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -5, -6, -6, -6, -5, -5, -4, -3, -2, -1 };

// ------------------------------------------------------------------ sprites
bn::optional<bn::sprite_ptr> s_pip, s_hathead, s_hat, s_boss1, s_boss2, s_en[MAX_EN], s_proj[3];

template<typename Item>
void make(bn::optional<bn::sprite_ptr>& s, const Item& item) {
    s = item.create_sprite(0, 0);
    s->set_bg_priority(1);
    s->set_visible(false);
}

void place(bn::optional<bn::sprite_ptr>& s, int sx, int sy, int w, int h) {
    if(!s) return;
    if(sx < -w || sx > SCREEN_W || sy < -h || sy > 160) { s->set_visible(false); return; }
    s->set_visible(true);
    s->set_position(sx + w / 2 - SCREEN_W / 2, sy + h / 2 - 80);
}

void hide(bn::optional<bn::sprite_ptr>& s) { if(s) s->set_visible(false); }

void hide_all_sprites() {
    hide(s_pip); hide(s_hathead); hide(s_hat); hide(s_boss1); hide(s_boss2);
    for(auto& e : s_en) hide(e);
    for(auto& p : s_proj) hide(p);
}

// ------------------------------------------------------------------ text / UI
int char_tile(char c) {
    if(c == ' ') return data::T_SKY;
    for(int i = 0; data::font_chars[i]; ++i)
        if(data::font_chars[i] == c) return data::font_base + i;
    return data::T_SKY;
}

void ui_clear() {
    for(int y = 0; y < 32; ++y) for(int x = 0; x < 32; ++x) ui_map->set(x, y, data::T_SKY);
    ui_dirty = true;
}

void print_at(int x, int y, const char* s) {
    while(*s) ui_map->set(x++, y, char_tile(*s++));
    ui_dirty = true;
}

void flush_maps() {
    if(game_dirty && game_bg_map) { game_bg_map->reload_cells_ref(); game_dirty = false; }
    if(ui_dirty && ui_bg_map) { ui_bg_map->reload_cells_ref(); ui_dirty = false; }
}

void frame() {            // one vsync with map uploads and BG scroll
    flush_maps();
    bn::core::update();
    ++frame_count;
}

// ------------------------------------------------------------------ level helpers
int tile_at(int tx, int ty) {
    if(ty < 0 || ty >= LH) return data::T_SKY;
    if(tx < 0 || tx >= lw) return data::T_WALL;
    return lvl[tx * LH + ty];
}
bool solid_px(int x, int y) {
    if(x < 0) return true;
    if(y < 0) return false;
    return data::tile_class[tile_at(x >> 3, y >> 3)] & 1;
}
bool rect_solid(int x0, int y0, int x1, int y1) {
    for(int y = y0 & ~7; y <= y1; y += 8)
        for(int x = x0 & ~7; x <= x1; x += 8)
            if(solid_px(x, y)) return true;
    return false;
}

void draw_column(int tx) {
    if(tx < 0 || tx >= lw) return;
    for(int y = 0; y < LH; ++y) game_map->set(tx, y, lvl[tx * LH + y]);
    // two filler rows below the level so the screen is covered: repeat the bottom tile
    game_map->set(tx, LH, lvl[tx * LH + LH - 1]);
    game_map->set(tx, LH + 1, lvl[tx * LH + LH - 1]);
    game_dirty = true;
}

void set_lvl_tile(int tx, int ty, int t) {
    if(tx < 0 || tx >= lw || ty < 0 || ty >= LH) return;
    lvl[tx * LH + ty] = t;
    int c0 = cam_x >> 3;
    if(tx >= c0 - 1 && tx <= c0 + 31) { game_map->set(tx, ty, t); game_dirty = true; }
}

// ------------------------------------------------------------------ save (SRAM)
struct save_t { char magic[4]; uint8_t reached, stars; uint16_t coins; uint8_t sum; };
uint8_t save_sum() { return uint8_t(0x5A + save_reached * 7 + save_stars * 13 + uint8_t(save_coins) + uint8_t(save_coins >> 8) * 3); }

void save_write() {
    save_t s{};
    s.magic[0] = 'C'; s.magic[1] = 'P'; s.magic[2] = 'T'; s.magic[3] = '1';
    s.reached = uint8_t(save_reached); s.stars = uint8_t(save_stars); s.coins = uint16_t(save_coins); s.sum = save_sum();
    bn::sram::write(s);
}
bool save_load() {
    save_t s{};
    bn::sram::read(s);
    bool ok = false;
    if(s.magic[0] == 'C' && s.magic[1] == 'P' && s.magic[2] == 'T' && s.magic[3] == '1') {
        save_reached = s.reached; save_stars = s.stars; save_coins = s.coins;
        if(s.sum == save_sum() && save_reached < data::num_levels + 1) ok = true;
    }
    if(!ok) { save_reached = 0; save_stars = 0; save_coins = 0; }
    return ok;
}

// ------------------------------------------------------------------ screens
void set_palette(int theme) {
    const auto& tp = data::theme_pals[theme];
    bn::bg_palette_ptr pal = game_bg->palette();
    for(int b = 0; b < 5; ++b) for(int i = 0; i < 4; ++i) pal.set_color(b * 16 + i, tp.bank[b][i]);
    for(int i = 1; i < 4; ++i) pal.set_color(HUD_PAL * 16 + i, bn::color(31, 31, 31));
    bn::bg_palettes::set_transparent_color(tp.bank[0][0]);
}

void wait_a() {
    while(true) {
        frame();
        if(bn::keypad::a_pressed() || bn::keypad::start_pressed()) return;
    }
}

void text_page(const char* l0, const char* l1, const char* l2, const char* l3, const char* l4) {
    hide_all_sprites();
    game_bg->set_visible(false);
    ui_clear();
    print_at(1, 3, l0); print_at(1, 6, l1); print_at(1, 9, l2); print_at(1, 12, l3); print_at(1, 15, l4);
    print_at(10, 18, "PRESS A");
    wait_a();
    ui_clear();
    game_bg->set_visible(true);
}

void draw_hud() {
    for(int x = 0; x < 30; ++x) ui_map->set(x, 19, data::T_SKY);
    for(int i = 0; i < max_hp; ++i) ui_map->set(i, 19, i < hp ? data::T_HEART : data::T_SKY);
    ui_map->set(8, 19, data::T_COIN);
    ui_map->set(9, 19, char_tile('x'), HUD_PAL);
    ui_map->set(10, 19, char_tile(char('0' + (coins / 100) % 10)), HUD_PAL);
    ui_map->set(11, 19, char_tile(char('0' + (coins / 10) % 10)), HUD_PAL);
    ui_map->set(12, 19, char_tile(char('0' + coins % 10)), HUD_PAL);
    ui_map->set(15, 19, data::T_STAR);
    ui_map->set(16, 19, char_tile('x'), HUD_PAL);
    ui_map->set(17, 19, char_tile(char('0' + save_stars % 10)), HUD_PAL);
    ui_map->set(20, 19, char_tile('L'), HUD_PAL);
    ui_map->set(21, 19, char_tile(char('0' + cur_level + 1)), HUD_PAL);
    ui_dirty = true;
}

// ------------------------------------------------------------------ gameplay
void hurt_player() {
    if(invuln || player_dead) return;
    if(hp) --hp;
    invuln = 90;
    vy = -36; vx = facing ? -20 : 20;
    if(hp == 0) player_dead = true;
    draw_hud();
}

void spawn_projectile(int x, int y, int vxx, int vyy) {
    for(int i = 0; i < 3; ++i) if(!pract[i]) { pract[i] = true; prx[i] = x; pry[i] = y; prvx[i] = vxx; prvy[i] = vyy; return; }
}

void load_level(int n) {
    const data::level_info& li = data::levels[n];
    cur_level = n;
    lw = li.w; cur_theme = li.theme; cur_boss = li.boss; arena0 = li.arena0; arena1 = li.arena1;
    for(int i = 0; i < lw * LH; ++i) lvl[i] = li.tiles[i];
    bn::memory::clear(game_map->cells);
    set_palette(cur_theme);
    cam_x = 0; drawn_tx = 0;
    for(int i = 0; i <= 32; ++i) { draw_column(i); drawn_tx = i; }
    px = 3 * 8 * 16; py = (GROUND_ROW - 2) * 8 * 16; vx = vy = 0; facing = true; on_ground = false; invuln = 0;
    hat_state = 0; level_done = false; player_dead = false; hp = max_hp;
    n_en = li.n_enemies; if(n_en > MAX_EN) n_en = MAX_EN;
    for(int i = 0; i < n_en; ++i) {
        ex[i] = li.enemies[i].x * 8; ey[i] = li.enemies[i].y * 8; ey0[i] = ey[i];
        etype[i] = li.enemies[i].type; ealive[i] = true; edir[i] = -1;
    }
    for(int i = 0; i < 3; ++i) pract[i] = false;
    bactive = false; bdead = false; arena_locked = false; star_spawned = false; bhp = 0;
    if(li.boss) {
        bx = (arena1 - 6) * 8; by = (GROUND_ROW - 3) * 8; bdir = -1; bstate = 0; btimer = 0; bvuln = false; bflash = 0; bphase = 0;
        bhp = li.boss == 1 ? 5 : 8;
        if(li.boss == 2) by = 56;
    }
    game_bg->set_visible(true);
    ui_clear();
    draw_hud();
}

void kill_enemy(int i) { ealive[i] = false; ++coins; draw_hud(); }

void collect_tiles(int x0, int y0, int x1, int y1) {
    for(int ty = y0 >> 3; ty <= (y1 >> 3); ++ty)
        for(int tx = x0 >> 3; tx <= (x1 >> 3); ++tx) {
            int c = data::tile_class[tile_at(tx, ty)];
            if(c & 4) { set_lvl_tile(tx, ty, data::T_SKY); ++coins; draw_hud(); }
            if((c & 8) && !level_done) level_done = true;
        }
}

void boss_hit() {
    if(!bvuln || bdead || bflash) return;
    --bhp; bflash = 40;
    if(bhp <= 0) { bdead = true; btimer = 90; bvuln = false; }
    else if(cur_boss == 1 && bhp <= 2) bphase = 1;
    else if(cur_boss == 2) bphase = bhp <= 3 ? 2 : (bhp <= 6 ? 1 : 0);
}

void update_boss() {
    int ppx = px >> 4, ppy = py >> 4;
    if(!cur_boss) return;
    if(!arena_locked && !bdead && ppx > arena0 * 8 + 24) {
        arena_locked = true; bactive = true; bstate = 0; btimer = 60;
        for(int i = 0; i < GROUND_ROW; ++i) { set_lvl_tile(arena0, i, data::T_BARRIER); set_lvl_tile(arena0 + 21, i, data::T_BARRIER); }
    }
    if(!arena_locked) return;
    int bmin = (arena0 + 2) * 8, bmax = (arena0 + 19) * 8;
    if(bflash) --bflash;
    if(bdead) {
        if(btimer) --btimer;
        if(!btimer && !star_spawned) {
            star_spawned = true; bactive = false;
            set_lvl_tile(arena0 + 11, GROUND_ROW - 2, data::T_STAR);
            for(int i = 0; i < GROUND_ROW; ++i) set_lvl_tile(arena0, i, data::T_SKY);
        }
        return;
    }
    if(cur_boss == 1) {                        // Scarabella the beetle queen
        switch(bstate) {
        case 0: if(btimer) --btimer; else { bstate = 1; btimer = 100; } break;
        case 1:
            bdir = ppx > bx + 8 ? 1 : -1;
            if(frame_count & 1) bx += bdir;
            if(bphase && (frame_count & 63) == 0) spawn_projectile(bx + 12, by + 8, bdir * 24, -30);
            if(btimer) --btimer; else { bstate = 2; btimer = 40; }
            break;
        case 2: bx += (frame_count & 2) ? 1 : -1; if(btimer) --btimer; else { bstate = 3; bdir = ppx > bx + 8 ? 1 : -1; } break;
        case 3:
            bx += bdir * 3;
            if(bx < bmin || bx > bmax) { bx = bx < bmin ? bmin : bmax; bstate = 4; btimer = 110; bvuln = true; }
            break;
        case 4: bvuln = true; if(btimer) --btimer; else { bvuln = false; bstate = 1; btimer = 100; } break;
        }
    } else {                                   // Baron Von Grumblebelt
        switch(bstate) {
        case 0: if(btimer) --btimer; else { bstate = 1; btimer = 200; } break;
        case 1:
            bx += (ppx > bx + 8 ? 1 : -1) * ((frame_count & 3) == 0 ? 1 : 0) + sine_tab[(frame_count >> 2) & 31] / 3 * int(frame_count & 1);
            if(bx < bmin) bx = bmin;
            if(bx > bmax) bx = bmax;
            by = 48 + sine_tab[(frame_count >> 2) & 31];
            bdir = ppx > bx + 8 ? 1 : -1;
            if(frame_count % unsigned(70 - bphase * 18) == 0) {
                spawn_projectile(bx + 8, by + 20, 0, 12);
                if(bphase >= 2) spawn_projectile(bx + 4, by + 20, -12, 10);
            }
            if(btimer) --btimer; else { bstate = 2; btimer = 40; }
            break;
        case 2: by += 4; if(by >= (GROUND_ROW - 3) * 8) { by = (GROUND_ROW - 3) * 8; bstate = 3; btimer = 100; bvuln = true; } break;
        case 3: bvuln = true; if(btimer) --btimer; else { bvuln = false; bstate = 4; } break;
        case 4: by -= 2; if(by <= 56) { by = 56; bstate = 1; btimer = 190; } break;
        }
    }
    if(!bdead) {
        int dx1 = ppx + 1, dx2 = ppx + 6, dy1 = ppy + 2, dy2 = ppy + 15;
        if(dx2 > bx + 2 && dx1 < bx + 22 && dy2 > by + 2 && dy1 < by + 24) {
            if(vy > 0 && dy2 < by + 12) { if(bvuln) boss_hit(); vy = -44; }
            else if(!bvuln) hurt_player();
        }
        if(hat_state && hx + 8 > bx && hx < bx + 24 && hy + 8 > by && hy < by + 24) {
            if(bvuln) boss_hit();
            hat_state = 2;
        }
    }
}

void update_projectiles() {
    int ppx = px >> 4, ppy = py >> 4;
    for(int i = 0; i < 3; ++i) {
        if(!pract[i]) continue;
        prx[i] += prvx[i] >> 3; pry[i] += prvy[i] >> 3;
        if(cur_boss == 1) prvy[i] += 2;
        if(prx[i] < 0 || prx[i] > lw * 8 || pry[i] > 150 || pry[i] < -8 || solid_px(prx[i] + 4, pry[i] + 4)) { pract[i] = false; continue; }
        if(prx[i] + 6 > ppx + 1 && prx[i] + 2 < ppx + 6 && pry[i] + 6 > ppy + 2 && pry[i] + 2 < ppy + 15) { pract[i] = false; hurt_player(); }
    }
}

void update_hat() {
    int ppx = px >> 4, ppy = py >> 4;
    if(bn::keypad::b_pressed() && hat_state == 0) {
        hat_state = 1; hat_dist = 0; hat_bounced = false;
        hat_dir = facing ? 1 : -1;
        hx = ppx + (facing ? 6 : -6); hy = ppy + 4;
    }
    if(!hat_state) return;
    if(hat_state == 1) {
        hx += hat_dir * 3; hat_dist += 3;
        if(hat_dist >= 60 || solid_px(hx + 4, hy + 4)) hat_state = 2;
    } else {
        int tx2 = ppx, ty2 = ppy + 4;
        if(hx < tx2 - 2) hx += 4; else if(hx > tx2 + 2) hx -= 4;
        if(hy < ty2 - 2) hy += 3; else if(hy > ty2 + 2) hy -= 3;
        if(hx > tx2 - 6 && hx < tx2 + 6 && hy > ty2 - 8 && hy < ty2 + 8) hat_state = 0;
    }
    int tx = (hx + 4) >> 3, ty = (hy + 4) >> 3;
    if(data::tile_class[tile_at(tx, ty)] & 4) { set_lvl_tile(tx, ty, data::T_SKY); ++coins; draw_hud(); }
    for(int i = 0; i < n_en; ++i)
        if(ealive[i] && hx + 8 > ex[i] && hx < ex[i] + 8 && hy + 8 > ey[i] && hy < ey[i] + 8) kill_enemy(i);
    if(hat_state && !hat_bounced && vy > 0 && ppy + 16 > hy && ppy + 12 < hy + 6 && ppx + 6 > hx && ppx + 1 < hx + 8) { vy = -40; hat_bounced = true; }
}

void update_enemies() {
    int ppx = px >> 4, ppy = py >> 4;
    for(int i = 0; i < n_en; ++i) {
        if(!ealive[i]) continue;
        if(ex[i] - cam_x < -40 || ex[i] - cam_x > 280) continue;
        if(etype[i] == 0) {
            if(frame_count & 1) {
                int nx = ex[i] + edir[i];
                int front = edir[i] > 0 ? nx + 8 : nx - 1;
                if(solid_px(front, ey[i] + 4) || !solid_px(front, ey[i] + 9)) edir[i] = -edir[i];
                else ex[i] = nx;
            }
        } else {
            if(frame_count & 1) ex[i] += ppx > ex[i] ? 1 : -1;
            ey[i] = ey0[i] + sine_tab[(frame_count >> 2) & 31];
            edir[i] = ppx > ex[i] ? 1 : -1;
        }
        if(ppx + 6 > ex[i] && ppx + 1 < ex[i] + 8 && ppy + 15 > ey[i] && ppy + 2 < ey[i] + 8) {
            if(vy > 0 && ppy + 15 < ey[i] + 6) { kill_enemy(i); vy = -38; }
            else hurt_player();
        }
    }
}

void update_player() {
    int ppx = px >> 4, ppy = py >> 4;
    bool left = bn::keypad::left_held(), right = bn::keypad::right_held();
    if(player_dead) return;
    if(invuln) --invuln;
    if(left && !right) { vx -= 3; facing = false; }
    else if(right && !left) { vx += 3; facing = true; }
    else if(vx > 0) { vx -= 3; if(vx < 0) vx = 0; }
    else if(vx < 0) { vx += 3; if(vx > 0) vx = 0; }
    if(vx > 24) vx = 24;
    if(vx < -24) vx = -24;
    if(vy >= 0) on_ground = rect_solid(ppx + 1, ppy + 16, ppx + 6, ppy + 16);
    if(bn::keypad::a_pressed()) jbuf = 6;
    if(jbuf) --jbuf;
    if(on_ground) coyote = 5; else if(coyote) --coyote;
    if(jbuf && coyote) { vy = -58; jbuf = 0; coyote = 0; on_ground = false; }
    if(on_ground && vy >= 0) vy = 0;
    else {
        if(vy < 0 && !bn::keypad::a_held()) vy += 8; else vy += 4;
        if(vy > 64) vy = 64;
    }
    int nx = px + vx;
    int edge = (nx >> 4) + (vx > 0 ? 6 : 1);
    if(vx != 0 && rect_solid(edge, ppy + 3, edge, ppy + 15)) vx = 0; else px = nx;
    ppx = px >> 4;
    int ny = py + vy;
    if(vy > 0) {
        edge = (ny >> 4) + 15;
        if(rect_solid(ppx + 1, edge, ppx + 6, edge)) { py = ((edge & ~7) - 16) << 4; vy = 0; on_ground = true; }
        else { py = ny; on_ground = false; }
    } else if(vy < 0) {
        edge = (ny >> 4) + 2;
        if(rect_solid(ppx + 1, edge, ppx + 6, edge)) vy = 0; else py = ny;
        on_ground = false;
    }
    ppy = py >> 4;
    for(int ty = (ppy + 4) >> 3; ty <= (ppy + 15) >> 3; ++ty)
        for(int tx = (ppx + 1) >> 3; tx <= (ppx + 6) >> 3; ++tx)
            if(data::tile_class[tile_at(tx, ty)] & 2) hurt_player();
    collect_tiles(ppx + 1, ppy + 2, ppx + 6, ppy + 15);
    if(ppy > 175) { hp = 0; player_dead = true; draw_hud(); }
    ++anim;
}

void update_camera() {
    int maxc = lw * 8 - SCREEN_W;
    int target;
    if(arena_locked) target = (arena0 + 11) * 8 - SCREEN_W / 2;
    else target = (px >> 4) - 104;
    if(!arena_locked && target < cam_x) target = cam_x;
    if(target > maxc) target = maxc;
    if(target < 0) target = 0;
    if(arena_locked) { if(cam_x < target) cam_x += 2; if(cam_x > target) cam_x -= 2; }
    else cam_x = target;
    while(drawn_tx < (cam_x >> 3) + 32 && drawn_tx < lw - 1) { ++drawn_tx; draw_column(drawn_tx); }
    game_bg->set_position(136 - (cam_x & 511), 48 + VOFF);
}

void draw_sprites() {
    int ppx = px >> 4, ppy = py >> 4;
    bool blink = invuln && (frame_count & 2);
    if(blink) { hide(s_pip); hide(s_hathead); }
    else {
        int fr = !on_ground ? 3 : (vx != 0 ? ((anim & 8) ? 1 : 2) : 0);
        s_pip->set_tiles(bn::sprite_items::pip.tiles_item(), fr);
        s_pip->set_horizontal_flip(!facing);
        place(s_pip, ppx - cam_x, ppy + VOFF, 8, 16);
        if(hat_state == 0) { s_hathead->set_horizontal_flip(!facing); place(s_hathead, ppx - cam_x, ppy - 3 + VOFF, 8, 8); }
        else hide(s_hathead);
    }
    if(hat_state) { s_hat->set_tiles(bn::sprite_items::hat.tiles_item(), (frame_count & 4) ? 1 : 0); place(s_hat, hx - cam_x, hy + VOFF, 8, 8); }
    else hide(s_hat);
    for(int i = 0; i < MAX_EN; ++i) {
        if(i < n_en && ealive[i]) {
            const auto& it = etype[i] ? bn::sprite_items::flyer : bn::sprite_items::walker;
            (void)it;
            s_en[i]->set_tiles(etype[i] ? bn::sprite_items::flyer.tiles_item() : bn::sprite_items::walker.tiles_item(), (frame_count & 8) ? 1 : 0);
            s_en[i]->set_horizontal_flip(edir[i] > 0);
            place(s_en[i], ex[i] - cam_x, ey[i] + VOFF, 8, 8);
        } else hide(s_en[i]);
    }
    hide(s_boss1); hide(s_boss2);
    if(bactive && !(bdead && (frame_count & 2))) {
        auto& bs = cur_boss == 1 ? s_boss1 : s_boss2;
        bs->set_horizontal_flip(bdir <= 0);
        place(bs, bx - 4 - cam_x, by - 8 + VOFF, 32, 32);
    }
    for(int i = 0; i < 3; ++i) {
        if(pract[i]) { s_proj[i]->set_tiles(bn::sprite_items::proj.tiles_item(), (frame_count & 4) ? 1 : 0); place(s_proj[i], prx[i] - cam_x, pry[i] + VOFF, 8, 8); }
        else hide(s_proj[i]);
    }
}

// returns true when the level was completed
bool play_level(int n) {
    load_level(n);
    bool paused = false;
    while(true) {
        frame();
        if(bn::keypad::start_pressed()) { paused = !paused; if(paused) print_at(12, 9, "PAUSED"); else { for(int i = 12; i < 18; ++i) ui_map->set(i, 9, data::T_SKY); ui_dirty = true; } }
        if(paused) continue;
        update_player();
        update_hat();
        update_enemies();
        update_boss();
        update_projectiles();
        update_camera();
        draw_sprites();
        if((frame_count & 7) == 0) draw_hud();
        if(level_done) return true;
        if(player_dead) { for(int k = 0; k < 60; ++k) frame(); return false; }
    }
}

void show_title(bool has_save) {
    hide_all_sprites();
    game_bg->set_visible(false);
    set_palette(0);
    ui_clear();
    print_at(9, 4, "CAPT AND CO");
    print_at(8, 6, "POCKET EDITION");
    print_at(7, 17, "ORIGINAL GAME");
    int choice = 0;
    unsigned blink = 0;
    // little hero + enemy on a grass strip
    for(int x = 0; x < 30; ++x) { ui_map->set(x, 13, data::T_GRASS); ui_map->set(x, 14, data::T_DIRT); ui_map->set(x, 15, data::T_DIRT); }
    ui_map->set(4, 12, data::T_TRUNK); ui_map->set(4, 11, data::T_LEAF); ui_map->set(3, 11, data::T_LEAF); ui_map->set(5, 11, data::T_LEAF);
    s_pip->set_tiles(bn::sprite_items::pip.tiles_item(), 0);
    place(s_pip, 112, 13 * 8 - 16 + 0, 8, 16);
    s_hathead->set_horizontal_flip(false);
    place(s_hathead, 112, 13 * 8 - 19, 8, 8);
    s_en[0]->set_tiles(bn::sprite_items::walker.tiles_item(), 0);
    place(s_en[0], 150, 13 * 8 - 8, 8, 8);
    while(true) {
        frame(); ++blink;
        if(has_save) {
            if(bn::keypad::up_pressed() || bn::keypad::down_pressed()) choice ^= 1;
            print_at(11, 9, choice == 0 ? ">CONTINUE" : " CONTINUE");
            print_at(11, 10, choice == 1 ? ">NEW GAME" : " NEW GAME");
        } else {
            print_at(10, 9, (blink & 32) ? "           " : "PRESS START");
        }
        if(bn::keypad::start_pressed() || bn::keypad::a_pressed()) break;
    }
    if(!has_save || choice == 1) { save_reached = 0; save_stars = 0; save_coins = 0; }
}

void story_intro() {
    text_page("LONG AGO A SONG", "HELD THE WORLD", "TOGETHER. EVERY", "NOTE WAS A STAR.", "");
    text_page("BARON GRUMBLEBELT", "STOLE THEM ALL FOR", "HIS GIANT MUSIC", "BOX. THAT RASCAL!", "");
    text_page("CAPT: PIP WAKE UP!", "PIP: FIVE MORE", "MINUTES...", "CAPT: NO. HAT BOSS", "SAYS GO!");
}

}  // namespace

int main() {
    bn::core::init();
    bn::bg_tiles::set_allow_offset(false);
    game_map = new bg_map_64x32();
    ui_map = new bg_map_32x32();
    {
        bn::regular_bg_item game_item(bn::regular_bg_tiles_items::bg_tiles, bn::bg_palette_items::bg_pal, game_map->item);
        game_bg = game_item.create_bg(0, 0);
        game_bg_map = game_bg->map();
        game_bg->set_priority(2);
        bn::regular_bg_item ui_item(bn::regular_bg_tiles_items::bg_tiles, bn::bg_palette_items::bg_pal, ui_map->item);
        ui_bg = ui_item.create_bg(0, 0);
        ui_bg_map = ui_bg->map();
        ui_bg->set_priority(0);
        ui_bg->set_position(8, 48);
    }
    bn::bg_tiles::set_allow_offset(true);
    make(s_pip, bn::sprite_items::pip);
    make(s_hathead, bn::sprite_items::piphat);
    make(s_hat, bn::sprite_items::hat);
    make(s_boss1, bn::sprite_items::boss1);
    make(s_boss2, bn::sprite_items::boss2);
    for(auto& e : s_en) make(e, bn::sprite_items::walker);
    for(auto& p : s_proj) make(p, bn::sprite_items::proj);

    bool has_save = save_load();
    while(true) {
        show_title(has_save);
        int lv = save_reached;
        if(lv >= data::num_levels) lv = data::num_levels - 1;
        coins = save_coins;
        if(!has_save || lv == 0) story_intro();
        while(lv < data::num_levels) {
            const data::level_info& li = data::levels[lv];
            char numbuf[10] = { 'L', 'E', 'V', 'E', 'L', ' ', char('1' + lv), 0 };
            if(li.boss == 1) text_page(numbuf, li.name, "", "MADAME SCARABELLA:", "MY HAIR!! HOW DARE");
            else if(li.boss == 2) text_page(numbuf, li.name, "", "BARON: WIND THE KEY!", "HE IS VERY SERIOUS");
            else text_page(numbuf, li.name, "", "A JUMP  B HAT", "GRAB THE STAR!");
            if(play_level(lv)) {
                ++save_stars;
                if(lv + 1 > save_reached) save_reached = lv + 1;
                save_coins = coins;
                save_write();
                has_save = true;
                hide_all_sprites();
                text_page("STAR GET!", "", "NICE JOB PIP!", "", "");
                ++lv;
            } else {
                coins = save_coins;
                text_page("OOPS!", "", "CAPT SAYS TRY", "AGAIN. WITH SNACKS.", "");
            }
        }
        text_page("THE MUSIC BOX IS", "QUIET... THEN A NEW", "FRIENDLIER TUNE", "BEGINS TO PLAY.", "");
        text_page("THE END", "THANKS FOR PLAYING!", "", "CAPT: SNACKS NOW.", "");
        save_reached = 0; save_stars = 0; save_write();
        has_save = false;
    }
}
