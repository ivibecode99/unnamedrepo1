#if defined(__SDCC)
#pragma bank 255
#endif
#include "lt.h"
/* 4-channel (2 pulse, wave, noise) tracker-style music + sfx driver. Same data on every platform. */

static CONSTMEM u16 ptab[85] = {
  44,44,157,263,363,457,547,631,711,786,
  856,923,986,1046,1102,1155,1205,1253,1297,1339,
  1379,1417,1452,1486,1517,1547,1575,1602,1627,1650,
  1673,1694,1714,1732,1750,1767,1783,1798,1812,1825,
  1837,1849,1860,1871,1881,1890,1899,1907,1915,1923,
  1930,1936,1943,1949,1954,1959,1964,1969,1974,1978,
  1982,1985,1989,1992,1995,1998,2001,2004,2006,2009,
  2011,2013,2015,2017,2018,2020,2022,2023,2025,2026,
  2027,2028,2029,2030,2031
};
/* drums -> NR43 + envelope */
static CONSTMEM u8 drum_nr43[8] = {0x93, 0x43, 0x20, 0x20, 0x31, 0x73, 0x10, 0x53};
static CONSTMEM u8 drum_env[8] = {0xF1, 0xC2, 0x61, 0x93, 0xA4, 0xB2, 0x41, 0x71};
static CONSTMEM u8 waves[4][16] = {
  {0x01,0x23,0x45,0x67,0x89,0xAB,0xCD,0xEF,0xFE,0xDC,0xBA,0x98,0x76,0x54,0x32,0x10},
  {0x01,0x12,0x23,0x34,0x45,0x56,0x67,0x78,0x89,0x9A,0xAB,0xBC,0xCD,0xDE,0xEF,0xF0},
  {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00},
  {0x00,0x44,0xAA,0xEE,0xFF,0xEE,0xAA,0x44,0x00,0x44,0xAA,0xEE,0xFF,0xEE,0xAA,0x44}
};

typedef struct {
    u16 pc, loop, ret;
    u8 timer, env, duty, vib, vp, note, wave, on;
} Voice;
static Voice mv[4];
static Voice sv[4];          /* sfx voices */
static u8 sfx_on[4], sfx_hold[4];
static u8 sfx_speed[4], sfx_tm[4];
static u8 speed, rowt, cur_song = 255, layers = 15, playing;
static u8 sfx_data_loaded;
static u8 sfxbuf[300];
static u16 sfxoff[24];
static u8 sfxcount;

static u16 period_for(u8 ch, u8 n) {
    u8 idx = n;
    if (ch == 2) idx = (u8)(n + 12);
    if (idx > 84) idx = 84;
    return ptab[idx];
}
static void voice_trig(u8 ch, Voice *v, u8 n) {
    if (ch == 3) {
        u8 d = (u8)(n & 7);
        plat_snd_trig(3, drum_nr43[d], drum_env[d], 0);
        return;
    }
    if (ch == 2) { plat_snd_trig(2, period_for(2, n), (u8)(v->env & 0x60) ? v->env : 0x20, 0); return; }
    plat_snd_trig(ch, period_for(ch, n), v->env, v->duty);
}
/* decode events from voice until a note/rest consumed; returns 0 if stream ended */
static u8 step_voice(u8 ch, Voice *v, const u8 *base, u8 is_sfx, u8 muted) {
    u8 guard = 0;
    for (;;) {
        u8 c = base[v->pc++];
        if (++guard > 40) return 1;
        if (c < 0xE0) {
            u8 len = base[v->pc++];
            v->timer = len ? len : 1;
            v->note = c;
            if (!muted && c != 0x7F) {
                if (c == 0) { plat_snd_off(ch); v->vp = 0; }
                else { voice_trig(ch, v, c); v->vp = 0; }
            }
            return 1;
        }
        switch (c) {
        case 0xE0: v->env = base[v->pc++]; break;
        case 0xE1: v->duty = base[v->pc++]; break;
        case 0xE2: v->vib = base[v->pc++]; break;
        case 0xE3: v->loop = v->pc; break;
        case 0xE5: if (!is_sfx) speed = base[v->pc++]; else v->pc++; break;
        case 0xE6: v->wave = base[v->pc++]; if (ch == 2 && !muted && !is_sfx) plat_snd_wave(waves[v->wave & 3]); break;
        case 0xE7: { u16 t = rd16(base + v->pc); v->pc += 2; v->ret = v->pc; v->pc = t; } break;
        case 0xE8: v->pc = v->ret; break;
        case 0xFE: v->pc = v->loop; break;
        default: /* 0xFF end */
            v->pc--; v->on = 0; if (!muted) plat_snd_off(ch);
            return 0;
        }
    }
}
void audio_init(void) API { plat_snd_wave(waves[0]); sfx_data_loaded = 0; }
void audio_stop(void) API { u8 i; for (i = 0; i < 4; i++) { plat_snd_off(i); mv[i].on = 0; sfx_on[i] = 0; } playing = 0; cur_song = 255; }
u8 audio_cur(void) API { return cur_song; }
void audio_play(u8 id) API {
    u8 i;
    if (id == cur_song && playing) return;
    audio_stop();
    if (id == 255) return;
    plat_chunk(CH_SONG + id, g_music, MUSIC_MAX);
    speed = g_music[1];
    for (i = 0; i < 4; i++) {
        mv[i].pc = rd16(g_music + 4 + i * 2); mv[i].loop = mv[i].pc; mv[i].ret = 0;
        mv[i].timer = 1; mv[i].env = 0x80; mv[i].duty = 2; mv[i].vib = 0; mv[i].vp = 0; mv[i].note = 0; mv[i].wave = 0;
        mv[i].on = mv[i].pc ? 1 : 0;
    }
    plat_snd_wave(waves[0]);
    rowt = 0; cur_song = id; playing = 1;
    layers = 15;
}
void audio_layers(u8 mask) API { u8 i; layers = mask; for (i = 0; i < 4; i++) if (!(mask & (1 << i)) && !sfx_on[i]) plat_snd_off(i); }
void audio_fadeout(void) API { audio_stop(); }
static void sfx_load(void) {
    u16 sz = plat_chunk_size(CH_SFX), i;
    if (sz > sizeof sfxbuf) sz = sizeof sfxbuf;
    plat_chunk(CH_SFX, sfxbuf, sz);
    sfxcount = sfxbuf[0];
    for (i = 0; i < sfxcount && i < 24; i++) sfxoff[i] = rd16(sfxbuf + 1 + i * 2);
    sfx_data_loaded = 1;
}
void audio_sfx(u8 id) API {
    u8 ch;
    if (!sfx_data_loaded) sfx_load();
    if (id >= sfxcount) return;
    ch = (u8)(sfxbuf[sfxoff[id]] & 3);
    sfx_speed[ch] = sfxbuf[sfxoff[id] + 1];
    sv[ch].pc = (u16)(sfxoff[id] + 2); sv[ch].loop = sv[ch].pc; sv[ch].timer = 1; sv[ch].env = 0xA1; sv[ch].duty = 2; sv[ch].vib = 0;
    sv[ch].on = 1; sfx_tm[ch] = 1; sfx_on[ch] = 1;
}
void audio_blip(u8 pitch) API {
    if (sfx_on[1] && sfx_hold[1] == 0) return;
    plat_snd_trig(1, period_for(1, pitch), 0x71, 1);
    sfx_on[1] = 1; sfx_hold[1] = 3;
}
void audio_tick(void) API {
    u8 i;
    /* sfx */
    for (i = 0; i < 4; i++) {
        if (!sfx_on[i]) continue;
        if (sfx_hold[i]) { if (--sfx_hold[i] == 0) { sfx_on[i] = 0; plat_snd_off(i); } continue; }
        if (--sfx_tm[i] == 0) {
            if (sv[i].timer > 1) { sv[i].timer--; sfx_tm[i] = sfx_speed[i]; }
            else if (!step_voice(i, &sv[i], sfxbuf, 1, 0) || !sv[i].on) { sfx_on[i] = 0; plat_snd_off(i); }
            else sfx_tm[i] = sfx_speed[i];
        }
    }
    if (!playing) return;
    if (++rowt >= speed) {
        rowt = 0;
        for (i = 0; i < 4; i++) {
            if (!mv[i].on) continue;
            if (--mv[i].timer == 0) {
                if (!step_voice(i, &mv[i], g_music, 0, (u8)(sfx_on[i] || !(layers & (1 << i))))) {
                    /* channel ended */
                }
            }
        }
        { u8 any = 0; for (i = 0; i < 4; i++) any |= mv[i].on; if (!any) { playing = 0; } }
    }
    /* vibrato */
    for (i = 0; i < 3; i++) {
        if (mv[i].vib && mv[i].note && mv[i].on && !sfx_on[i] && (layers & (1 << i))) {
            s16 d;
            mv[i].vp = (u8)(mv[i].vp + 14);
            d = (s16)(((s16)isin(mv[i].vp) * mv[i].vib) >> 7);
            plat_snd_period(i, (u16)((s16)period_for(i, mv[i].note) + d));
        }
    }
}
