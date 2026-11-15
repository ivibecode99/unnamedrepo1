#if defined(__SDCC)
#pragma bank 255
#endif
#include "lt.h"
/* SRAM layout: [0..7] header, [8..39] meta, slots at 64 + n*SLOT_SZ (struct copy + 16-bit sum) */
#define SLOT_SZ 330
#define SLOT0 64
static u16 sum(const u8 *p, u16 n) { u16 s = 0x5A5A; while (n--) s = (u16)((s << 1 | s >> 15) + *p++); return s; }

void meta_save(void) API {
    u8 h[4];
    h[0] = 'L'; h[1] = 'T'; h[2] = 1; h[3] = 0;
    meta.magic = 0xA7;
    plat_sram_write(0, h, 4);
    plat_sram_write(8, (const u8 *)&meta, sizeof(Meta));
    plat_sram_flush();
}
void save_init(void) API {
    u8 h[4], i;
    plat_sram_read(0, h, 4);
    if (h[0] == 'L' && h[1] == 'T' && h[2] == 1) {
        plat_sram_read(8, (u8 *)&meta, sizeof(Meta));
        if (meta.magic == 0xA7) return;
    }
    for (i = 0; i < sizeof(Meta); i++) ((u8 *)&meta)[i] = 0;
    meta.text_speed = 2; meta.vol = 6;
    meta_save();
    for (i = 0; i < 3; i++) save_erase(i);
}
u8 save_slot_used(u8 slot) API {
    u8 b[2];
    plat_sram_read((u16)(SLOT0 + slot * SLOT_SZ), b, 2);
    return b[0] == 'S' && b[1] == 'V';
}
void save_write(u8 slot) API {
    u16 base = (u16)(SLOT0 + slot * SLOT_SZ), s;
    u8 b[4];
    g.slot = slot;
    b[0] = 'S'; b[1] = 'V';
    s = sum((const u8 *)&g, sizeof(Game));
    wr16(b + 2, s);
    plat_sram_write(base, b, 4);
    plat_sram_write((u16)(base + 4), (const u8 *)&g, sizeof(Game));
    plat_sram_flush();
}
u8 save_read(u8 slot) API {
    u16 base = (u16)(SLOT0 + slot * SLOT_SZ), s;
    u8 b[4];
    if (!save_slot_used(slot)) return 0;
    plat_sram_read(base, b, 4);
    plat_sram_read((u16)(base + 4), (u8 *)&g, sizeof(Game));
    s = sum((const u8 *)&g, sizeof(Game));
    if (s != rd16(b + 2)) return 0;
    return 1;
}
void save_erase(u8 slot) API {
    u8 b[2];
    b[0] = 0; b[1] = 0;
    plat_sram_write((u16)(SLOT0 + slot * SLOT_SZ), b, 2);
    plat_sram_flush();
}
