/* LOWTIDE SDL2 backend: desktop, web (Emscripten), R36S. Implements the virtual 160x144 PPU,
   a 4-channel GB-style synth, input (keyboard/gamepad/touch) and save storage. */
#include <SDL.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "../../core/lt.h"
typedef uint32_t u32;
typedef uint64_t u64;

#include "../soft/soft.h"
extern const unsigned char lt_blob[];
extern const unsigned int lt_blob_len;
static SDL_AudioDeviceID adev;
static int audio_ok;
static int headless;
void SOFT_LOCK(void) { if (adev) SDL_LockAudioDevice(adev); }
void SOFT_UNLOCK(void) { if (adev) SDL_UnlockAudioDevice(adev); }
static void audio_cb(void *ud, Uint8 *stream, int len) {
    float tmp[2048];
    int n = len / 4, i;
    s16 *o = (s16 *)stream;
    (void)ud;
    if (n > 2048) n = 2048;
    soft_synth(tmp, n);
    for (i = 0; i < n; i++) {
        float v = tmp[i] * 32000.0f;
        if (v > 32767) v = 32767;
        if (v < -32768) v = -32768;
        o[i * 2] = o[i * 2 + 1] = (s16)v;
    }
}
static char savepath[512] = "lowtide.sav";
static void sram_load(void) {
    u8 buf[SOFT_SRAM_SZ];
    int n = 0;
    FILE *f = fopen(savepath, "rb");
    if (f) { n = (int)fread(buf, 1, SOFT_SRAM_SZ, f); fclose(f); }
    soft_sram_load(n ? buf : NULL, n);
}
void plat_sram_flush(void) {
    if (!soft_sram_take_dirty()) return;
    { FILE *f = fopen(savepath, "wb"); if (f) { fwrite(soft_sram_ptr(), 1, SOFT_SRAM_SZ, f); fclose(f); } }
}

/* ------------------------------------------------------------------ input */
static SDL_Window *win;
static SDL_Renderer *ren;
static SDL_Texture *tex;
static SDL_GameController *pad;
static u8 padkeys, touchkeys, scripted_keys, use_scripted;
static int touch_active;
static const SDL_Scancode defkeys[8][2] = {
    {SDL_SCANCODE_UP, SDL_SCANCODE_W}, {SDL_SCANCODE_DOWN, SDL_SCANCODE_S}, {SDL_SCANCODE_LEFT, SDL_SCANCODE_A},
    {SDL_SCANCODE_RIGHT, SDL_SCANCODE_D}, {SDL_SCANCODE_Z, SDL_SCANCODE_SPACE}, {SDL_SCANCODE_X, SDL_SCANCODE_BACKSPACE},
    {SDL_SCANCODE_RETURN, SDL_SCANCODE_C}, {SDL_SCANCODE_RSHIFT, SDL_SCANCODE_V}};
static int remap_btn = -1;
u8 plat_remap_busy(void) { return remap_btn >= 0; }
void plat_remap(u8 b) { remap_btn = b & 7; }
u8 plat_caps(void) {
    u8 c = PC_COLOR | PC_REMAP;
    c |= PC_QUIT;
#ifdef TARGET_R36S
    c &= ~PC_REMAP;
#endif
    return c;
}
void plat_quit(void) { exit(0); }
void plat_log(const char *s) { fprintf(stderr, "[lt] %s\n", s); }
u8 plat_keys(void) {
    const Uint8 *ks = SDL_GetKeyboardState(NULL);
    u8 k = 0;
    int b;
    if (use_scripted) return scripted_keys;
    for (b = 0; b < 8; b++) {
        if (ks[defkeys[b][0]] || ks[defkeys[b][1]]) k |= 1 << b;
        if (meta.keymap[b] && ks[meta.keymap[b]]) k |= 1 << b;
    }
    return k | padkeys | touchkeys;
}

/* touch button layout (window coordinates) */
static int ww = 640, wh = 480;
static struct { int x, y, w, h; u8 key; const char *lbl; } tb[8];
static void touch_layout(void) {
    int u = wh < ww ? wh / 6 : ww / 5;
    int by = wh - u * 3 - u / 2;
    tb[0] = (typeof(tb[0])){u, by, u, u, K_UP, "^"};
    tb[1] = (typeof(tb[0])){u, by + 2 * u, u, u, K_DOWN, "v"};
    tb[2] = (typeof(tb[0])){0, by + u, u, u, K_LEFT, "<"};
    tb[3] = (typeof(tb[0])){2 * u, by + u, u, u, K_RIGHT, ">"};
    tb[4] = (typeof(tb[0])){ww - u * 3 / 2, by + u, u * 3 / 2, u, K_A, "A"};
    tb[5] = (typeof(tb[0])){ww - u * 3, by + 2 * u, u * 3 / 2, u, K_B, "B"};
    tb[6] = (typeof(tb[0])){ww / 2 - u * 2, wh - u / 2 - u / 3, u * 2, u / 2, K_START, "ST"};
    tb[7] = (typeof(tb[0])){ww / 2, wh - u / 2 - u / 3, u * 2, u / 2, K_SELECT, "SE"};
}
static void touch_update(float fx, float fy, int down, SDL_FingerID id, int *held) {
    (void)id; (void)held;
    (void)fx; (void)fy; (void)down;
}
static SDL_FingerID fingers_id[10]; static int fingers_x[10], fingers_y[10], fingers_n;
static void touch_recalc(void) {
    int i, f;
    touchkeys = 0;
    for (f = 0; f < fingers_n; f++)
        for (i = 0; i < 8; i++) {
            int m = tb[i].w / 3;
            if (fingers_x[f] >= tb[i].x - m && fingers_x[f] < tb[i].x + tb[i].w + m && fingers_y[f] >= tb[i].y - m && fingers_y[f] < tb[i].y + tb[i].h + m)
                touchkeys |= tb[i].key;
        }
}

/* ------------------------------------------------------------------ test hooks */
typedef struct { int frame; u8 mask; } KeyEv;
static KeyEv *kev; static int nkev;
static struct { int frame; char path[256]; } shots[64]; static int nshots;
static int dbg_map = -1, dbg_x, dbg_y, dbg_d, dbg_n;
static u8 dbg_idx[64], dbg_val[64];
static int bridge;
static int max_frames = -1, cur_frame, dumpstate;
static int scale_out = 1;

/* ------------------------------------------------------------------ main loop */
static int running = 1;
static u64 lastt; static double acc;
static void present(void) {
    int sc, vx, vy, vw, vh, i;
    SDL_Rect dst;
    SDL_GetRendererOutputSize(ren, &ww, &wh);
    touch_layout();
    sc = ww / SW < wh / SH ? ww / SW : wh / SH;
    if (touch_active && wh > ww) { sc = ww / SW; }
    if (sc < 1) sc = 1;
#ifdef TARGET_R36S
    sc = 3;
#endif
    vw = SW * sc; vh = SH * sc; vx = (ww - vw) / 2; vy = touch_active && wh > ww ? 8 : (wh - vh) / 2;
    dst.x = vx; dst.y = vy; dst.w = vw; dst.h = vh;
    SDL_UpdateTexture(tex, NULL, soft_fb(), SW * 4);
    SDL_SetRenderDrawColor(ren, 0, 0, 0, 255);
    SDL_RenderClear(ren);
    SDL_RenderCopy(ren, tex, NULL, &dst);
    if (touch_active) {
        SDL_SetRenderDrawBlendMode(ren, SDL_BLENDMODE_BLEND);
        for (i = 0; i < 8; i++) {
            SDL_Rect r = {tb[i].x + 4, tb[i].y + 4, tb[i].w - 8, tb[i].h - 8};
            SDL_SetRenderDrawColor(ren, 255, 255, 255, (touchkeys & tb[i].key) ? 120 : 45);
            SDL_RenderFillRect(ren, &r);
        }
    }
    SDL_RenderPresent(ren);
}

static void frame_step(void) {
    SDL_Event e;
    while (SDL_PollEvent(&e)) {
        switch (e.type) {
        case SDL_QUIT: running = 0; break;
        case SDL_KEYDOWN:
            if (remap_btn >= 0 && !e.key.repeat) {
                if (e.key.keysym.scancode < 256 && e.key.keysym.scancode != SDL_SCANCODE_ESCAPE) meta.keymap[remap_btn] = (u8)e.key.keysym.scancode;
                remap_btn = -1;
            } else if (e.key.keysym.sym == SDLK_F11 || (e.key.keysym.sym == SDLK_RETURN && (e.key.keysym.mod & KMOD_ALT))) {
                SDL_SetWindowFullscreen(win, (SDL_GetWindowFlags(win) & SDL_WINDOW_FULLSCREEN_DESKTOP) ? 0 : SDL_WINDOW_FULLSCREEN_DESKTOP);
            } else if (e.key.keysym.sym == SDLK_F12) { soft_write_png("lowtide_shot.png", 3); }
            break;
        case SDL_CONTROLLERDEVICEADDED: if (!pad) pad = SDL_GameControllerOpen(e.cdevice.which); break;
        case SDL_CONTROLLERDEVICEREMOVED: if (pad) { SDL_GameControllerClose(pad); pad = NULL; } break;
        case SDL_FINGERDOWN: case SDL_FINGERMOTION: {
            int f, found = -1;
            touch_active = 1;
            for (f = 0; f < fingers_n; f++) if (fingers_id[f] == e.tfinger.fingerId) found = f;
            if (found < 0 && fingers_n < 10) { found = fingers_n++; fingers_id[found] = e.tfinger.fingerId; }
            if (found >= 0) { fingers_x[found] = (int)(e.tfinger.x * ww); fingers_y[found] = (int)(e.tfinger.y * wh); }
            touch_recalc();
        } break;
        case SDL_FINGERUP: {
            int f;
            for (f = 0; f < fingers_n; f++) if (fingers_id[f] == e.tfinger.fingerId) {
                fingers_id[f] = fingers_id[fingers_n - 1]; fingers_x[f] = fingers_x[fingers_n - 1]; fingers_y[f] = fingers_y[fingers_n - 1]; fingers_n--; break;
            }
            touch_recalc();
        } break;
        }
    }
    padkeys = 0;
    if (pad) {
#define B(btn) SDL_GameControllerGetButton(pad, btn)
        if (B(SDL_CONTROLLER_BUTTON_DPAD_UP)) padkeys |= K_UP;
        if (B(SDL_CONTROLLER_BUTTON_DPAD_DOWN)) padkeys |= K_DOWN;
        if (B(SDL_CONTROLLER_BUTTON_DPAD_LEFT)) padkeys |= K_LEFT;
        if (B(SDL_CONTROLLER_BUTTON_DPAD_RIGHT)) padkeys |= K_RIGHT;
        if (B(SDL_CONTROLLER_BUTTON_A)) padkeys |= K_A;
        if (B(SDL_CONTROLLER_BUTTON_B)) padkeys |= K_B;
        if (B(SDL_CONTROLLER_BUTTON_X)) padkeys |= K_B;
        if (B(SDL_CONTROLLER_BUTTON_START)) padkeys |= K_START;
        if (B(SDL_CONTROLLER_BUTTON_BACK)) padkeys |= K_SELECT;
        {
            int ax = SDL_GameControllerGetAxis(pad, SDL_CONTROLLER_AXIS_LEFTX), ay = SDL_GameControllerGetAxis(pad, SDL_CONTROLLER_AXIS_LEFTY);
            if (ax < -12000) padkeys |= K_LEFT; if (ax > 12000) padkeys |= K_RIGHT;
            if (ay < -12000) padkeys |= K_UP; if (ay > 12000) padkeys |= K_DOWN;
        }
    }
    if (bridge) {
        char line[64];
        for (;;) {
            if (!fgets(line, sizeof line, stdin)) { running = 0; return; }
            if (line[0] == 'S') { char *nl = strchr(line, '\n'); if (nl) *nl = 0; soft_render(); soft_write_png(line + 2, 3); printf("SHOT\n"); fflush(stdout); continue; }
            break;
        }
        if (line[0] == 'Q') { running = 0; return; }
        scripted_keys = (u8)strtol(line, NULL, 16); use_scripted = 1; nkev = 0;
    }
    if (use_scripted) {
        int i;
        for (i = 0; i < nkev; i++) if (kev[i].frame <= cur_frame) scripted_keys = kev[i].mask;
    }
    soft_master = meta.vol ? meta.vol / 8.0f * 0.6f : 0.0f;
    if (meta.magic != 0xA7) soft_master = 0.4f;
    core_frame();
    soft_render();
    if (!headless) present();
    {
        int i;
        for (i = 0; i < nshots; i++) if (shots[i].frame == cur_frame) soft_write_png(shots[i].path, scale_out);
    }
    if (bridge) {
        char buf[8192], t[1024];
        play_dbg(t); printf("%s\n", t); vars_dbg(buf); printf("%s\n", buf);
        vm_dbg(t); printf("%s\n", t);
        world_dbg(buf); printf("%s\n", buf);
        battle_dbg(buf); printf("%s\n", buf);
        mg_dbg(t); printf("%s\nU %d\n", t, ui_dbg_state()); ui_dbg_text(t); printf("T %s\nEND\n", t);
        fflush(stdout);
    }
    cur_frame++;
    if (max_frames >= 0 && cur_frame >= max_frames) running = 0;
}

static void usage_parse(int argc, char **argv) {
    int i;
    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--headless")) headless = 1;
        else if (!strcmp(argv[i], "--warp") && i + 4 < argc) { dbg_map = atoi(argv[++i]); dbg_x = atoi(argv[++i]); dbg_y = atoi(argv[++i]); dbg_d = atoi(argv[++i]); }
        else if (!strcmp(argv[i], "--var") && i + 1 < argc && dbg_n < 64) { int a, b; if (sscanf(argv[++i], "%d=%d", &a, &b) == 2) { dbg_idx[dbg_n] = (u8)a; dbg_val[dbg_n++] = (u8)b; } }
        else if (!strcmp(argv[i], "--bridge")) bridge = 1;
        else if (!strcmp(argv[i], "--dmg")) soft_set_dmg(1);
        else if (!strcmp(argv[i], "--frames") && i + 1 < argc) max_frames = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--sav") && i + 1 < argc) snprintf(savepath, sizeof savepath, "%s", argv[++i]);
        else if (!strcmp(argv[i], "--scale") && i + 1 < argc) scale_out = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--seed") && i + 1 < argc) rnd_seed((u16)atoi(argv[++i]));
        else if (!strcmp(argv[i], "--shot") && i + 1 < argc && nshots < 64) {
            char *c = strchr(argv[++i], ':');
            if (c) { *c = 0; shots[nshots].frame = atoi(argv[i]); snprintf(shots[nshots].path, 256, "%s", c + 1); nshots++; }
        } else if (!strcmp(argv[i], "--keys") && i + 1 < argc) {
            FILE *f = fopen(argv[++i], "r"); int fr, m;
            kev = malloc(sizeof(KeyEv) * 100000);
            while (f && fscanf(f, "%d %x", &fr, &m) == 2) { kev[nkev].frame = fr; kev[nkev].mask = (u8)m; nkev++; }
            if (f) fclose(f);
            use_scripted = 1;
        }
    }
}

int main(int argc, char **argv) {
    SDL_AudioSpec want, have;
    Uint32 initf = SDL_INIT_VIDEO | SDL_INIT_AUDIO | SDL_INIT_GAMECONTROLLER;
    int i;
    soft_blob(lt_blob);
    for (i = 1; i < argc; i++) if (!strcmp(argv[i], "--headless")) { headless = 1; }
    if (headless) { SDL_setenv("SDL_VIDEODRIVER", "dummy", 1); SDL_setenv("SDL_AUDIODRIVER", "dummy", 1); }
#ifdef TARGET_R36S
    { char *e = SDL_getenv("LT_SAVE_DIR"); if (e) snprintf(savepath, sizeof savepath, "%s/lowtide.sav", e); }
#endif
    if (SDL_Init(initf) != 0) { initf &= ~SDL_INIT_GAMECONTROLLER; if (SDL_Init(initf) != 0) { fprintf(stderr, "SDL: %s\n", SDL_GetError()); return 1; } }
    SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "0");
    win = SDL_CreateWindow("LOWTIDE", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 640, 576,
#ifdef TARGET_R36S
        SDL_WINDOW_FULLSCREEN_DESKTOP
#else
        SDL_WINDOW_RESIZABLE | SDL_WINDOW_ALLOW_HIGHDPI
#endif
    );
    ren = SDL_CreateRenderer(win, -1, headless ? SDL_RENDERER_SOFTWARE : SDL_RENDERER_ACCELERATED);
    if (!ren) ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_SOFTWARE);
    tex = SDL_CreateTexture(ren, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, SW, SH);
    SDL_ShowCursor(0);
    memset(&want, 0, sizeof want);
    want.freq = AUDIO_RATE; want.format = AUDIO_S16SYS; want.channels = 2; want.samples = 1024; want.callback = audio_cb;
    if (!headless) { adev = SDL_OpenAudioDevice(NULL, 0, &want, &have, 0); if (adev) { audio_ok = 1; SDL_PauseAudioDevice(adev, 0); } }
    sram_load();
    usage_parse(argc, argv);
    plat_init();
    core_init();
    if (dbg_map >= 0) game_debug_apply((u8)dbg_map, (u8)dbg_x, (u8)dbg_y, (u8)dbg_d, (u8)dbg_n, dbg_idx, dbg_val);
    lastt = SDL_GetPerformanceCounter();
    while (running) {
        if (headless) { frame_step(); continue; }
        {
            u64 now = SDL_GetPerformanceCounter();
            acc += (double)(now - lastt) / SDL_GetPerformanceFrequency();
            lastt = now;
            if (acc > 0.25) acc = 0.25;
            if (acc >= 1.0 / 60.0) { acc -= 1.0 / 60.0; frame_step(); } else SDL_Delay(1);
        }
    }
    plat_sram_flush();
    if (dumpstate) {}
    (void)touch_update; (void)audio_ok; (void)lt_blob_len;
    SDL_Quit();
    return 0;
}
