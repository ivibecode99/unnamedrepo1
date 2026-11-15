# LOWTIDE — Architecture

One portable C99 core, one data pipeline, three thin backends.

```
 content/ + tools/*.py ──► chunks (blob) ──► per-platform packaging
                                   │
 core/*.c  (C99, 8/16-bit safe) ───┼──► platform/sdl  (desktop, R36S)   + platform/soft (software PPU + synth)
   VM · world · text · battle ·    ├──► platform/web  (Emscripten, canvas/WebAudio) + platform/soft
   audio sequencer · save · UI     ├──► platform/gba  (bare-metal arm-none-eabi, own crt0/ld)
                                   └──► platform/gb   (GBDK-2020/SDCC, MBC5, banked)
```

## Logical machine
160x144, a tile machine modelled on GBC: 256 shared 8x8 2bpp tiles (BG+OBJ), a 32x32 scrolling BG map, a
32x32 "window" layer that is opaque from pixel row `wy` down, 40 8x8 sprites, 8 BG + 8 OBJ palettes of 4 RGB555 colours.
Colour index 0 = lightest/transparent .. 3 = darkest, so DMG (4 shades) is the same art.
Rooms are <=16x16 metatiles (256x256 px) so the BG map never needs streaming.
The backend contract is `core/lt.h` (`plat_*`). SDL/web render it in software; GBA maps it to BG0/BG1/WIN/OBJ
(160x144 centred in 240x160 with a black border); GB writes VRAM directly.

## Data: chunks
Everything is a numbered chunk (`tools/chunks.py`, ids in `core/layout.h`): tiles, palettes, maps, scripts, battles,
songs, strings. Core copies chunks into small RAM buffers (`g_scene`, `g_music`, `g_tmp`) via `plat_chunk_read`.
GB: chunks are packed into 16KB banks (`tools/pack_gb.py`), directory in bank 0, core code autobanked (`API` = `__banked`).
Rule on GB: never pass pointers to ROM data across banked calls (copy to RAM first).

## Script VM
Story, dialogue, map events, shops and battle scripts are bytecode (`core/vm.c`, compiler `tools/scriptc.py`): 8-bit vars,
u16 offsets, inline strings with control codes. Identical bytes run on every platform.

## Battle
Attack patterns are emitter data (origin, speed, angle, spread, count, period, kind) interpreted by `core/battle.c`.
Bullet cap and density are per-platform constants (PLATFORMS.md).

## Audio
4 channels (2 pulse, wave, noise) — the exact GB/GBA PSG model. Songs are note-event streams with pattern calls
(`tools/music.py`). `core/audio.c` drives `plat_snd_*`; GB/GBA write hardware registers, SDL/web run an emulating synth.

## Saving
3 slots + meta/options block. SRAM on GB/GBA, file on desktop/R36S, localStorage on web.
