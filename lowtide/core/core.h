/* LOWTIDE core internal API. Included via lt.h */
#ifndef CORE_H
#define CORE_H

/* ---- state ---- */
typedef struct {
    u8 vars[256];
    u16 gold;
    u16 exp;
    u8 hp, maxhp, lv;
    u8 inv[8];
    u8 map, px, py, dir;
    u8 name[8];
    u16 secs;
    u8 slot;
} Game;
extern Game g;

typedef struct {         /* persistent meta + options (SRAM) */
    u8 magic;
    u8 endings;          /* bit0 peace bit1 neutral bit2 fight bit3 true */
    u8 ng;               /* completed runs */
    u8 prev_end;         /* last ending 1..4 */
    u8 prev_moral;       /* 0 kind 1 mixed 2 violent */
    u8 text_speed;       /* 0 instant 1 fast 2 normal 3 slow */
    u8 no_flash;
    u8 assist;           /* slow-dodge */
    u8 keymap[8];
    u8 vol;
    u8 seen_bits;        /* bit0 intro seen */
    u8 reserved[3];
} Meta;
extern Meta meta;

extern u8 g_scene[SCENE_MAX];
extern u8 g_tmp[SCRATCH_MAX];
extern u8 g_music[MUSIC_MAX];
extern u8 g_keys, g_pressed;       /* held, newly pressed this frame */

/* math / rng */
u8 rnd(void) API;
void rnd_seed(u16 s) API;
s8 isin(u8 a) API;
s8 icos(u8 a) API;
u8 iatan(s16 dy, s16 dx) API;      /* 0..255 angle, 0=right 64=down */

/* data / gfx helpers */
void load_tiles(u16 chunk, u8 first) API;       /* chunk is raw 2bpp tiles */
void load_pal(u16 chunk, u8 first_slot, u8 n) API;
void set_dmg(u8 bgp, u8 obp0, u8 obp1) API;
u16 rd16(const u8 *p) API;
void wr16(u8 *p, u16 v) API;
u8 str_len(const u8 *s) API;

/* text / UI (window layer) */
void ui_init(void) API;
void ui_clear_win(void) API;
void ui_win(u8 y) API;
void ui_hide_sprites(void) API;
extern u8 ui_win_y, ui_say_open_y, ui_say_close_y;
u16 world_take_script(void) API;
u16 world_take_battle(void) API;
u16 world_cur_chunk(void) API;
void world_restore(void) API;
void world_player_pos(u8 *x, u8 *y) API;
void ui_print(u8 x, u8 y, const u8 *s) API;          /* window layer */
void ui_print_bg(u8 x, u8 y, const u8 *s) API;       /* BG layer */
void ui_num(u8 x, u8 y, u16 v, u8 digits) API;
void ui_box(u8 x, u8 y, u8 w, u8 h) API;             /* window layer frame, interior black */
void ui_box_bg(u8 x, u8 y, u8 w, u8 h) API;
const u8 *ui_str(u8 id) API;                         /* UI string from strings chunk */
void ui_say_begin(u8 spk, u8 face) API;
void ui_say_text(const u8 *txt) API;                 /* start typewriter on text (copied ptr into scene) */
u8 ui_say_tick(void) API;                            /* returns 1 when finished all pages */
void ui_say_end(void) API;
u8 ui_menu(const u8 **items, u8 n, u8 x, u8 y, u8 w, u8 start) API; /* unused */
void blip(u8 spk) API;

/* script VM */
void vm_start(u16 ip) API;
void vm_start_chunk(u16 chunk) API;
u8 vm_running(void) API;
void vm_tick(void) API;
extern u8 vm_ctx;                 /* 0 world, 1 battle */

/* audio */
void audio_init(void) API;
void audio_play(u8 id) API;
void audio_stop(void) API;
void audio_tick(void) API;
void audio_layers(u8 mask) API;   /* bit per channel enabled */
void audio_sfx(u8 id) API;
void audio_blip(u8 pitch) API;
u8 audio_cur(void) API;
void audio_fadeout(void) API;

/* world */
void world_init(void) API;
void world_load(u8 map, u8 px, u8 py, u8 dir) API;
void world_tick(void) API;
void world_draw(void) API;
u8 world_busy(void) API;
void world_ent_show(u8 idx, u8 on) API;
void world_ent_set(u8 idx, u8 x, u8 y) API;
void world_ent_face(u8 idx, u8 dir) API;
u8 world_ent_move(u8 idx, u8 dir, u8 n) API;      /* start scripted move; poll world_busy */
void world_cam(u8 x, u8 y, u8 follow) API;
void world_reload_chunk(void) API;                /* after battle: reload map chunk w/o resetting position */
void world_player_to(u8 x, u8 y) API;
void world_set_mapchunk(u16 ch) API;
void world_shake(u8 frames, u8 power) API;
extern u8 world_mode_flag;

/* battle */
void battle_start(u16 chunk) API;
u8 battle_tick(void) API;       /* 1 when done */
u8 battle_running(void) API;
void battle_cmd(u8 op, u8 a, u8 b) API;  /* script ops */
extern u8 bt_wait;

/* minigames */
void mg_start(u8 id) API;
u8 mg_tick(void) API;

/* save */
void save_init(void) API;
u8 save_slot_used(u8 slot) API;
void save_write(u8 slot) API;
u8 save_read(u8 slot) API;
void save_erase(u8 slot) API;
void meta_save(void) API;
void new_game(void) API;

/* game */
void game_init(void) API;
void items_use(u8 idx) API;
u8 item_add(u8 id) API;
u8 item_has(u8 id) API;
void item_remove(u8 id) API;
u8 moral(void) API;             /* 0 kind 1 mixed 2 violent */
void fx_flash(u8 n) API;
void fx_fade(s8 target, u8 speed) API;
u8 fx_busy(void) API;
void fx_tick(void) API;
void shake_tick_apply(u8 *sx, u8 *sy) API;
void shop_open(u8 id) API;
u8 shop_tick(void) API;
void game_ending(u8 id) API;
void menu_pause(void) API;
u8 menu_tick(void) API;
void name_enter(void) API;
u8 name_tick(void) API;
void save_menu_open(void) API;
u8 save_menu_tick(void) API;
#define M_PLAY 3
extern u8 g_mode;
void game_start_new(void) API;
void game_continue(void) API;
void game_play_frame(void) API;
void game_title(void) API;
void recalc_stats(void) API;
void game_debug_battle(u16 chunk) API;
void game_debug_apply(u8 map, u8 x, u8 y, u8 d, u8 n, const u8 *idx, const u8 *val) API;
void game_options_open(void) API;
void item_name_print(u8 x, u8 y, u8 id) API;
u8 vm_running_ctx(u8 c) API;
u8 vm_fullscreen(void) API;
void vm_set_chunk(u16 c) API;
u16 vm_get_chunk(void) API;
void vm_stop(void) API;
void play_start_map(u8 map, u8 x, u8 y, u8 d) API;
#ifndef __SDCC
void vm_dbg(char *o) API; u8 ui_dbg_state(void) API; void ui_dbg_text(char *o) API; void world_dbg(char *o) API; void battle_dbg(char *o) API; void mg_dbg(char *o) API; void play_dbg(char *o) API; void vars_dbg(char *o) API;
int battle_dbg_nbullets(void) API;
#endif
#endif
