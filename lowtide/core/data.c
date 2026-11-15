#if defined(__SDCC)
#pragma bank 255
#endif
#include "lt.h"

u8 g_scene[SCENE_MAX];
u8 g_tmp[SCRATCH_MAX];
u8 g_music[MUSIC_MAX];
u8 g_keys, g_pressed;
Game g;
Meta meta;

u16 rd16(const u8 *p) API { return (u16)(p[0] | ((u16)p[1] << 8)); }
void wr16(u8 *p, u16 v) API { p[0] = (u8)v; p[1] = (u8)(v >> 8); }
u8 str_len(const u8 *s) API { u8 n = 0; while (s[n]) n++; return n; }

/* load raw 2bpp tile data from a chunk into tile slots starting at 'first' (all of the chunk) */
void load_tiles(u16 chunk, u8 first) API {
    u16 sz = plat_chunk_size(chunk), off = 0;
    u8 t = first;
    while (off < sz) {
        u16 n = sz - off;
        if (n > SCRATCH_MAX) n = (SCRATCH_MAX / 16) * 16;
        n = plat_chunk_read(chunk, off, g_tmp, n);
        if (!n) break;
        plat_tiles(t, g_tmp, (u8)(n / 16));
        t = (u8)(t + n / 16);
        off += n;
    }
}
/* palette chunk: n palettes of 4 x RGB555 (8 bytes) */
void load_pal(u16 chunk, u8 first_slot, u8 n) API {
    u8 i;
    u16 c[4];
    for (i = 0; i < n; i++) {
        u8 j;
        plat_chunk_read(chunk, (u16)(i * 8), g_tmp, 8);
        for (j = 0; j < 4; j++) c[j] = rd16(g_tmp + j * 2);
        plat_pal((u8)(first_slot + i), c);
    }
}
void set_dmg(u8 bgp, u8 obp0, u8 obp1) API { plat_dmg_pal(bgp, obp0, obp1); }
