/* Shared software PPU + 4-channel synth used by the SDL and web backends. */
#ifndef SOFT_H
#define SOFT_H
#define SW 160
#define SH 144
extern int soft_rate;
#define AUDIO_RATE soft_rate
#define SOFT_SRAM_SZ 8192
void SOFT_LOCK(void);
void SOFT_UNLOCK(void);
extern float soft_master;
void soft_synth(float *out, int n);
void soft_blob(const unsigned char *b);
void soft_set_dmg(int on);
const uint32_t *soft_fb(void);
void soft_render(void);
void soft_sram_load(const unsigned char *src, int n);
const unsigned char *soft_sram_ptr(void);
int soft_sram_take_dirty(void);
void soft_write_png(const char *path, int scale);
#endif
