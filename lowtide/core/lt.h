/* LOWTIDE core - shared types and API. Portable C99 (also compiles with SDCC for Game Boy). */
#ifndef LT_H
#define LT_H
#include "layout.h"

typedef unsigned char u8;
typedef signed char s8;
typedef unsigned short u16;
typedef signed short s16;

/* On Game Boy the core is split across ROM banks, so cross-file calls are __banked. */
#if defined(__SDCC)
#define API __banked
#define CONSTMEM const
#else
#define API
#define CONSTMEM const
#endif

#define NULL0 ((void*)0)

/* ---------- input bits ---------- */
#define K_UP 0x01
#define K_DOWN 0x02
#define K_LEFT 0x04
#define K_RIGHT 0x08
#define K_A 0x10
#define K_B 0x20
#define K_START 0x40
#define K_SELECT 0x80

/* ---------- platform layer (implemented by each backend, never banked) ---------- */
void plat_init(void);
void plat_vsync(void);                       /* present frame + wait for next */
u8   plat_keys(void);                        /* held keys */
void plat_lcd(u8 on);
void plat_tiles(u8 first, const u8 *src, u8 count); /* 2bpp planar GB format, 16 bytes/tile */
void plat_bg_set(u8 x, u8 y, u8 tile, u8 attr);
void plat_win_set(u8 x, u8 y, u8 tile, u8 attr);
void plat_bg_fill(u8 x, u8 y, u8 w, u8 h, u8 tile, u8 attr);
void plat_win_fill(u8 x, u8 y, u8 w, u8 h, u8 tile, u8 attr);
void plat_scroll(u8 x, u8 y);
void plat_win_y(u8 y);                       /* window layer visible from pixel row y; >=144 hides */
void plat_pal(u8 idx, const u16 *c4);        /* idx 0-7 BG, 8-15 OBJ, RGB555 */
void plat_dmg_pal(u8 bgp, u8 obp0, u8 obp1);
void plat_fade(s8 level);                    /* -8 (white) .. 0 .. +8 (black) */
void plat_spr(u8 i, s16 x, s16 y, u8 tile, u8 attr); /* screen coords of top-left; y>=144 or x<=-8 hides */
u16  plat_chunk(u16 id, u8 *dst, u16 max);   /* copy chunk to RAM, returns size */
u16  plat_chunk_size(u16 id);
u16  plat_chunk_read(u16 id, u16 off, u8 *dst, u16 n); /* copy n bytes at offset */
void plat_snd_trig(u8 ch, u16 period, u8 env, u8 duty);
void plat_snd_off(u8 ch);
void plat_snd_period(u8 ch, u16 period);
void plat_snd_wave(const u8 *w16);
void plat_sram_read(u16 off, u8 *dst, u16 n);
void plat_sram_write(u16 off, const u8 *src, u16 n);
void plat_sram_flush(void);
u8   plat_caps(void);                        /* PC_* bits */
void plat_remap(u8 btn);                     /* begin capture of next key for button index 0..7 */
u8   plat_remap_busy(void);
void plat_log(const char *s);
void plat_quit(void);
#define PC_COLOR 1
#define PC_REMAP 2
#define PC_QUIT 4

/* ---------- core API (called by backends) ---------- */
void core_init(void) API;
void core_frame(void) API;     /* one 60Hz logic+render step */

/* ---------- shared core modules ---------- */
#include "core.h"
#endif
