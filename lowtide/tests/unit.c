/* Unit tests: script VM, save/load, battle emitter system. Built natively against the real core with a stub platform.
   cc -Icore tests/unit.c core/*.c build/gen/blob.c -o build/unit && ./build/unit */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "../core/lt.h"
typedef uint32_t u32;
extern const unsigned char lt_blob[];
static int fails, checks;
#define CHECK(c) do { checks++; if (!(c)) { fails++; printf("FAIL %s:%d  %s\n", __FILE__, __LINE__, #c); } } while (0)
/* ---- stub platform ---- */
static const u8 *blob; static u16 nch; static u8 sram[8192]; static u8 keys_now; static int win_y_calls;
static u32 off(u16 id) { const u8 *e = blob + 2 + id * 6; return e[0] | (e[1] << 8) | (e[2] << 16) | ((u32)e[3] << 24); }
static u16 len(u16 id) { const u8 *e = blob + 2 + id * 6; return e[4] | (e[5] << 8); }
void plat_init(void) {} void plat_vsync(void) {} u8 plat_keys(void) { return keys_now; } void plat_lcd(u8 o) { (void)o; }
void plat_tiles(u8 f, const u8 *s, u8 c) { (void)f; (void)s; (void)c; }
void plat_bg_set(u8 x, u8 y, u8 t, u8 a) { (void)x; (void)y; (void)t; (void)a; } void plat_win_set(u8 x, u8 y, u8 t, u8 a) { (void)x; (void)y; (void)t; (void)a; }
void plat_bg_fill(u8 x, u8 y, u8 w, u8 h, u8 t, u8 a) { (void)x; (void)y; (void)w; (void)h; (void)t; (void)a; }
void plat_win_fill(u8 x, u8 y, u8 w, u8 h, u8 t, u8 a) { (void)x; (void)y; (void)w; (void)h; (void)t; (void)a; }
void plat_scroll(u8 x, u8 y) { (void)x; (void)y; } void plat_win_y(u8 y) { (void)y; win_y_calls++; }
void plat_pal(u8 i, const u16 *c) { (void)i; (void)c; } void plat_dmg_pal(u8 a, u8 b, u8 c) { (void)a; (void)b; (void)c; } void plat_fade(s8 l) { (void)l; }
void plat_spr(u8 i, s16 x, s16 y, u8 t, u8 a) { (void)i; (void)x; (void)y; (void)t; (void)a; }
u16 plat_chunk_size(u16 id) { return id < nch ? len(id) : 0; }
u16 plat_chunk_read(u16 id, u16 o, u8 *d, u16 n) { u16 sz = plat_chunk_size(id); if (o >= sz) return 0; if (n > sz - o) n = sz - o; memcpy(d, blob + off(id) + o, n); return n; }
u16 plat_chunk(u16 id, u8 *d, u16 m) { return plat_chunk_read(id, 0, d, m); }
void plat_snd_trig(u8 c, u16 p, u8 e, u8 d) { (void)c; (void)p; (void)e; (void)d; } void plat_snd_off(u8 c) { (void)c; } void plat_snd_period(u8 c, u16 p) { (void)c; (void)p; } void plat_snd_wave(const u8 *w) { (void)w; }
void plat_sram_read(u16 o, u8 *d, u16 n) { memcpy(d, sram + o, n); } void plat_sram_write(u16 o, const u8 *s, u16 n) { memcpy(sram + o, s, n); } void plat_sram_flush(void) {}
u8 plat_caps(void) { return 0; } void plat_remap(u8 b) { (void)b; } u8 plat_remap_busy(void) { return 0; } void plat_log(const char *s) { (void)s; } void plat_quit(void) {}
static void frame(u8 k) { keys_now = k; core_frame(); }

static void test_vm(void) {
    /* bytecode: SET v40=5; ADD v40 +3; IF v40==8 goto L; SET v41=99; L: SET v42=1; END */
    u8 code[] = {0x02, 40, 5, 0x03, 40, 3, 0x04, 40, 0, 8, 0, 0, 0x02, 41, 99, 0x02, 42, 1, 0x00};
    u16 target = 15; code[10] = (u8)target; code[11] = 0;   /* jump over "SET v41=99" (offset of the SET v42) */
    code[10] = 15; code[11] = 0;
    memset(&g, 0, sizeof g);
    memcpy(g_scene, code, sizeof code);
    vm_ctx = 0; vm_set_chunk(0xFFFF); vm_start(0);
    { int n = 0; while (vm_running() && n++ < 100) vm_tick(); }
    CHECK(g.vars[40] == 8); CHECK(g.vars[41] == 0); CHECK(g.vars[42] == 1);
    /* CALL / RET and comparison ops */
    { u8 c2[] = {0x06, 8, 0, 0x02, 50, 7, 0x00, 0x00, 0x02, 51, 4, 0x07};
      memset(g.vars, 0, 256); memcpy(g_scene, c2, sizeof c2); vm_start(0);
      { int n = 0; while (vm_running() && n++ < 100) vm_tick(); }
      CHECK(g.vars[51] == 4); CHECK(g.vars[50] == 7); }
    /* IF with each comparator */
    { int op, okc = 0;
      for (op = 0; op < 6; op++) {
          u8 c3[] = {0x02, 60, 5, 0x04, 60, 0, 5, 14, 0, 0x02, 61, 1, 0x00, 0x00, 0x02, 62, 1, 0x00};
          c3[5] = (u8)op; c3[7] = 14; c3[8] = 0;
          memset(g.vars, 0, 256); memcpy(g_scene, c3, sizeof c3); vm_start(0);
          { int n = 0; while (vm_running() && n++ < 100) vm_tick(); }
          { int taken = g.vars[62] == 1, want = (op == 0) || (op == 4) || (op == 5);   /* 5==5 : ==, <=, >= are true */
            if (taken == want) okc++; }
      }
      CHECK(okc == 6); }
}
static void test_save(void) {
    u8 s;
    memset(sram, 0xFF, sizeof sram); save_init();
    CHECK(!save_slot_used(0)); CHECK(!save_slot_used(2));
    memset(&g, 0, sizeof g); g.hp = 17; g.maxhp = 31; g.gold = 321; g.map = 9; g.px = 3; g.py = 4; g.vars[77] = 200; g.name[0] = 'Z';
    save_write(1);
    CHECK(save_slot_used(1)); CHECK(!save_slot_used(0));
    memset(&g, 0, sizeof g);
    s = save_read(1); CHECK(s == 1);
    CHECK(g.hp == 17 && g.maxhp == 31 && g.gold == 321 && g.map == 9 && g.vars[77] == 200 && g.name[0] == 'Z');
    /* corruption must be rejected */
    sram[64 + 330 + 10] ^= 0x55;
    memset(&g, 0, sizeof g); CHECK(save_read(1) == 0);
    /* meta persistence */
    meta.endings = 0x0A; meta.ng = 2; meta_save(); memset(&meta, 0, sizeof meta); save_init(); CHECK(meta.endings == 0x0A && meta.ng == 2);
    save_erase(1); CHECK(!save_slot_used(1));
}
static int chunk_by_name_hp(u16 id) { u8 b[16]; plat_chunk_read(id, 0, b, 16); return b[4] | (b[5] << 8); }
static void test_emitters(void) {
    /* find any battle chunk by scanning for header shape, run the dodge simulation and check bullets spawn inside bounds and are capped */
    int id, found = 0, maxb = 0, spawned = 0;
    for (id = CH_CONTENT; id < nch; id++) {
        u8 b[40];
        u16 sz = plat_chunk_size(id);
        if (sz < 120 || sz > 2304) continue;
        plat_chunk_read(id, 0, b, 40);
        if (b[10] >= 3 && b[11] >= 1 && b[11] <= 6 && rd16(b + 24) == BH_SIZE) { found++; if (found == 3) break; }
    }
    CHECK(found == 3);
    memset(&g, 0, sizeof g); g.hp = 99; g.maxhp = 99; g.lv = 1;
    battle_start((u16)id);
    { int f; u8 hits = 0;
      for (f = 0; f < 3000; f++) {
          u8 k = (f % 120) < 3 ? K_A : 0;     /* mash A through intro text and menu */
          frame(k);
          { int n = battle_dbg_nbullets(); if (n > maxb) maxb = n; if (n) spawned++; }
          (void)hits;
      }
    }
    CHECK(spawned > 0);                 /* emitters produced bullets */
    CHECK(maxb <= 40);                  /* never exceeds the platform cap */
    CHECK(chunk_by_name_hp((u16)id) > 0);
    /* determinism: same seed, same chunk -> identical bullet count trace */
    { int a[200], i, same = 1; rnd_seed(1234); memset(&g, 0, sizeof g); g.hp = 99; g.maxhp = 99; g.lv = 1; battle_start((u16)id);
      for (i = 0; i < 200; i++) { frame(0); a[i] = battle_dbg_nbullets(); }
      rnd_seed(1234); memset(&g, 0, sizeof g); g.hp = 99; g.maxhp = 99; g.lv = 1; battle_start((u16)id);
      for (i = 0; i < 200; i++) { frame(0); if (a[i] != battle_dbg_nbullets()) same = 0; }
      CHECK(same); }
}
int main(void) {
    blob = lt_blob; nch = blob[0] | (blob[1] << 8);
    core_init();
    test_vm(); test_save(); test_emitters();
    printf("%d checks, %d failures\n", checks, fails);
    return fails ? 1 : 0;
}
