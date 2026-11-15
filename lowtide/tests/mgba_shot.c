/* Headless mGBA harness: run a GB/GBC/GBA ROM with scripted input, dump PNG screenshots, WAV audio and
   optional memory peeks. Usage:
   mgba_shot rom [--frames N] [--keys file] [--shot F:path.png]... [--wav out.wav] [--sav file] [--model dmg|cgb]
   keys file: lines "frame hexmask" (GB bit layout: A=1 B=2 SELECT=4 START=8 RIGHT=16 LEFT=32 UP=64 DOWN=128) */
#include <mgba/core/core.h>
#include <mgba/core/blip_buf.h>
#include <mgba/core/config.h>
#include <mgba-util/vfs.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <zlib.h>

static void put32(uint8_t *p, uint32_t v) { p[0] = v >> 24; p[1] = v >> 16; p[2] = v >> 8; p[3] = v; }
static void chunk(FILE *f, const char *t, const uint8_t *d, uint32_t n) {
    uint8_t h[8]; uint32_t c;
    put32(h, n); memcpy(h + 4, t, 4); fwrite(h, 1, 8, f);
    if (n) fwrite(d, 1, n, f);
    c = crc32(0, (const uint8_t *)t, 4); c = crc32(c, d, n);
    put32(h, c); fwrite(h, 1, 4, f);
}
static void write_png(const char *path, const uint32_t *px, int w, int h, int stride, int scale) {
    int W = w * scale, H = h * scale, x, y;
    uint8_t *raw = malloc((size_t)(W * 3 + 1) * H), *p;
    uLongf zl; uint8_t *z; uint8_t ih[13] = {0};
    FILE *f = fopen(path, "wb");
    if (!f) return;
    p = raw;
    for (y = 0; y < H; y++) {
        *p++ = 0;
        for (x = 0; x < W; x++) { uint32_t c = px[(y / scale) * stride + x / scale]; *p++ = c & 255; *p++ = (c >> 8) & 255; *p++ = (c >> 16) & 255; }
    }
    zl = compressBound((uLong)(p - raw)); z = malloc(zl);
    compress2(z, &zl, raw, (uLong)(p - raw), 6);
    fwrite("\x89PNG\r\n\x1a\n", 1, 8, f);
    put32(ih, W); put32(ih + 4, H); ih[8] = 8; ih[9] = 2;
    chunk(f, "IHDR", ih, 13); chunk(f, "IDAT", z, (uint32_t)zl); chunk(f, "IEND", NULL, 0);
    fclose(f); free(raw); free(z);
}
typedef struct { int frame; unsigned mask; } Ev;
int main(int argc, char **argv) {
    const char *rom = NULL, *wav = NULL, *sav = NULL, *model = NULL;
    int frames = 120, nshots = 0, nev = 0, i, scale = 2;
    struct { int f; char path[256]; } shots[128];
    Ev *ev = calloc(100000, sizeof(Ev));
    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--frames")) frames = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--wav")) wav = argv[++i];
        else if (!strcmp(argv[i], "--sav")) sav = argv[++i];
        else if (!strcmp(argv[i], "--model")) model = argv[++i];
        else if (!strcmp(argv[i], "--scale")) scale = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--shot")) { char *c = strchr(argv[++i], ':'); *c = 0; shots[nshots].f = atoi(argv[i]); snprintf(shots[nshots].path, 256, "%s", c + 1); nshots++; }
        else if (!strcmp(argv[i], "--keys")) { FILE *f = fopen(argv[++i], "r"); int fr; unsigned m; while (f && fscanf(f, "%d %x", &fr, &m) == 2) { ev[nev].frame = fr; ev[nev].mask = m; nev++; } if (f) fclose(f); }
        else rom = argv[i];
    }
    if (!rom) { fprintf(stderr, "no rom\n"); return 1; }
    struct mCore *core = mCoreFind(rom);
    if (!core) { fprintf(stderr, "cannot find core for %s\n", rom); return 1; }
    core->init(core);
    mCoreInitConfig(core, NULL);
    if (model) mCoreConfigSetOverrideValue(&core->config, "gb.model", model);
    mCoreConfigSetValue(&core->config, "idleOptimization", "ignore");
    mCoreConfigSetIntValue(&core->config, "sgb.borders", 0);
    mCoreConfigSetIntValue(&core->config, "useCgbColors", 1);
    core->loadConfig(core, &core->config);
    unsigned w, h;
    core->desiredVideoDimensions(core, &w, &h);
    uint32_t *buf = calloc(w * h, 4);
    core->setVideoBuffer(core, (void *)buf, w);
    core->setAudioBufferSize(core, 2048);
    blip_set_rates(core->getAudioChannel(core, 0), core->frequency(core), 44100);
    blip_set_rates(core->getAudioChannel(core, 1), core->frequency(core), 44100);
    if (!mCoreLoadFile(core, rom)) { fprintf(stderr, "load failed\n"); return 1; }
    if (sav) { struct VFile *vf = VFileOpen(sav, O_RDWR | O_CREAT); if (vf) core->loadSave(core, vf); }
    core->reset(core);
    FILE *wf = NULL; uint32_t wbytes = 0;
    if (wav) { wf = fopen(wav, "wb"); uint8_t hdr[44] = {0}; fwrite(hdr, 1, 44, wf); }
    unsigned keys = 0; int ei = 0;
    int16_t abuf[4096 * 2];
    for (i = 0; i < frames; i++) {
        while (ei < nev && ev[ei].frame <= i) { keys = ev[ei].mask; ei++; }
        core->setKeys(core, keys);
        core->runFrame(core);
        if (wf) {
            int n = blip_read_samples(core->getAudioChannel(core, 0), abuf, 4096, 1);
            blip_read_samples(core->getAudioChannel(core, 1), abuf + 1, 4096, 1);
            fwrite(abuf, 4, n, wf); wbytes += n * 4;
        }
        for (int s = 0; s < nshots; s++) if (shots[s].f == i) write_png(shots[s].path, buf, w == 256 ? 160 : w, w == 256 ? 144 : h, w, scale);
    }
    if (wf) {
        uint8_t hdr[44]; uint32_t sr = 44100;
        memcpy(hdr, "RIFF", 4); *(uint32_t *)(hdr + 4) = 36 + wbytes; memcpy(hdr + 8, "WAVEfmt ", 8); *(uint32_t *)(hdr + 16) = 16;
        *(uint16_t *)(hdr + 20) = 1; *(uint16_t *)(hdr + 22) = 2; *(uint32_t *)(hdr + 24) = sr; *(uint32_t *)(hdr + 28) = sr * 4;
        *(uint16_t *)(hdr + 32) = 4; *(uint16_t *)(hdr + 34) = 16; memcpy(hdr + 36, "data", 4); *(uint32_t *)(hdr + 40) = wbytes;
        fseek(wf, 0, SEEK_SET); fwrite(hdr, 1, 44, wf); fclose(wf);
    }
    core->deinit(core);
    return 0;
}
