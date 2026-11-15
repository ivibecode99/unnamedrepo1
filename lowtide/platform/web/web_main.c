/* LOWTIDE web backend: Emscripten, no SDL. Canvas 2D presentation, WebAudio synth, localStorage saves,
   keyboard / Gamepad API / touch handled in shell.html and read here as a key bitmask. */
#include <emscripten.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>
#include "../../core/lt.h"
#include "../soft/soft.h"
typedef uint32_t u32;
extern const unsigned char lt_blob[];

void SOFT_LOCK(void) {}
void SOFT_UNLOCK(void) {}

EM_JS(int, js_keys, (void), { return (window.ltKeys | 0) & 255; });
EM_JS(void, js_present, (const void *p), {
    var c = window.ltCtx; if (!c) return;
    var src = new Uint8Array(HEAPU8.buffer, p, 160 * 144 * 4);
    var d = window.ltImg.data, i;
    for (i = 0; i < 160 * 144 * 4; i += 4) { d[i] = src[i + 2]; d[i + 1] = src[i + 1]; d[i + 2] = src[i]; d[i + 3] = 255; }
    c.putImageData(window.ltImg, 0, 0);
});
EM_JS(void, js_save, (const char *hex), { try { localStorage.setItem("lowtide_sav", UTF8ToString(hex)); } catch (e) {} });
EM_JS(char *, js_load, (void), {
    var s = ""; try { s = localStorage.getItem("lowtide_sav") || ""; } catch (e) {}
    var n = lengthBytesUTF8(s) + 1; var p = _malloc(n); stringToUTF8(s, p, n); return p; });
EM_JS(void, js_remap, (int b), { window.ltRemap = b; });
EM_JS(int, js_remap_busy, (void), { return window.ltRemap >= 0 ? 1 : 0; });
EM_JS(int, js_keymap_get, (int b), { return (window.ltKeymapSet && window.ltKeymapSet[b]) | 0; });

EMSCRIPTEN_KEEPALIVE void web_audio_fill(float *out, int n, int rate) { soft_rate = rate; soft_synth(out, n); }

u8 plat_keys(void) { return (u8)js_keys(); }
u8 plat_caps(void) { return PC_COLOR | PC_REMAP; }
void plat_remap(u8 b) { js_remap(b); }
u8 plat_remap_busy(void) { return (u8)js_remap_busy(); }
void plat_log(const char *s) { emscripten_log(0, "%s", s); }
void plat_quit(void) {}
void plat_sram_flush(void) {
    if (!soft_sram_take_dirty()) return;
    {
        static char hex[SOFT_SRAM_SZ * 2 + 1];
        const u8 *p = soft_sram_ptr(); int i;
        for (i = 0; i < SOFT_SRAM_SZ; i++) sprintf(hex + i * 2, "%02x", p[i]);
        js_save(hex);
    }
}
static double last_t, acc;
static void frame(void) {
    double now = emscripten_get_now();
    int steps = 0, b;
    acc += (now - last_t) / 1000.0; last_t = now;
    if (acc > 0.25) acc = 0.25;
    while (acc >= 1.0 / 60.0 && steps < 3) {
        acc -= 1.0 / 60.0; steps++;
        for (b = 0; b < 8; b++) { int k = js_keymap_get(b); if (k) meta.keymap[b] = (u8)k; }
        soft_master = meta.vol ? meta.vol / 8.0f * 0.6f : 0.0f;
        core_frame();
    }
    if (steps) { soft_render(); js_present(soft_fb()); }
}
int main(void) {
    static u8 buf[SOFT_SRAM_SZ];
    char *h = (char *)js_load();
    int i, n = (int)(strlen(h) / 2);
    for (i = 0; i < n && i < SOFT_SRAM_SZ; i++) { unsigned v; sscanf(h + i * 2, "%2x", &v); buf[i] = (u8)v; }
    soft_blob(lt_blob);
    soft_sram_load(n ? buf : NULL, n);
    plat_init();
    core_init();
    last_t = emscripten_get_now();
    emscripten_set_main_loop(frame, 0, 1);
    return 0;
}
