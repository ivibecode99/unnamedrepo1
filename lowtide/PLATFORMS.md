# Platform notes, reductions, and what was (not) tested

All platforms run the same C99 core and the same data blob: same zones, bosses, endings, story and music data. Nothing in the story was cut for any platform.

## Reductions / differences
| Area | Desktop / Web / R36S (SDL soft PPU) | GBA | GB / GBC / DMG |
|---|---|---|---|
| Logical screen | 160x144, integer scaled + letterbox (R36S: fixed 3x on 640x480) | 160x144 centred in 240x160 with black border (no decorative border art yet) | 160x144 native |
| Max bullets on screen | 40 | 40 (same build constants as desktop) | **16** |
| Pattern density | 8/8 of authored bullet counts | 8/8 | **5/8** of authored counts (min 1) |
| Bullet hit radius | 3 px | 3 px | **4 px** (compensates the lower density) |
| Colour | RGB555 palettes per zone | RGB555 palettes per zone | GBC: same palettes. **DMG: 4 shades** (palette index 0..3 maps to white..black; art is authored in that order) |
| Fades | per-pixel blend | hardware BLDCNT | GBC: palette blend, DMG: BGP shade shift |
| Sprites | 8x8 OBJ mode, 4 per character | same | same (OAM 40, <=10/line) |
| Window layer / text box | software | BG1 + WIN0 | hardware window |
| Music | 4-channel software synth emulating the GB PSG | GBA PSG registers (same note data) | GB PSG registers (same note data) |
| Save | file / localStorage, 8 KB image | SRAM ("SRAM_V113" tag) | MBC5 battery SRAM (cart type 0x1B, 32 KB) |
| Key remap | yes (desktop/web); R36S: no (gamepad layout fixed) | no | no |
| ROM size | n/a | 185 KB | 512 KB (data in banks 8..17, code in banks 1..3) |
| Memory (GB) | n/a | n/a | WRAM ~7 KB used of 8 KB; scene buffer 2304 B, music 800 B |

Other deliberate reductions (all platforms): overworld NPCs have a single 16x16 frame with a bob/flip idle; rooms are at most 256x256 px; at most 6 distinct actors and 14 entities per room.
Not done: decorative GBA border art; Super Game Boy palettes/border; GBA/GB link or rumble features.

## Verified in this environment
* Native Linux SDL2 build: run headless; unit tests (`make test`, 20 checks) pass.
* **Playthrough bot** (`tests/run_bots.sh`): plays the real SDL build from the title screen to the credits for **Peace, Neutral, Fight and True** endings using only controller input
  (BFS walking, dialogue, block puzzles, ordered-lantern puzzles, rhythm + sorting mini-games, bullet dodging, listen/release or attack plans). It retries after in-game deaths (the Fight route needed ~50 retries). Ending bits were read back from the save file.
* Web build: loads in headless Chromium (Playwright), title/menu/new game/intro verified with keyboard input.
* GBC and DMG-mode (header-patched copy; mGBA picks the model from the header) and GBA ROMs in mGBA headless: title, menu, new game intro, naming screen, overworld, battle, and in-game saving (SV slot written into battery SRAM, both platforms). GB profiling hook shows 100 vblanks per 100 logic frames in the overworld (full speed).
* ROM headers (`tests/check_roms.py`): GB MBC5+RAM+battery (0x1B), 512 KB, 32 KB RAM, header/global checksum OK; GBA logo/complement/SRAM tag OK.
* Audio: register-level check in mGBA (NR52/NR12/NR22 and GBA SOUNDCNT_X/SND regs show the expected channels and envelopes playing). The headless WAV capture in my mGBA harness returned silence even for a known-good beep ROM, so **GB/GBA audio output was not captured as waveform**; the SDL synth path and the Python preview renderer (31 WAVs) were checked numerically (non-silent, no clipping).
* aarch64 R36S/Linux binary: built with the cross compiler, runs under QEMU user-mode with SDL dummy drivers and renders the title (`--headless`).
* Windows x64: cross-built (PE32+ GUI) with MinGW; **not run** (no Windows/Wine here).

## NOT tested (needs real hardware or a missing host)
* Any real Game Boy / GBC / GBA / flash cart (timing, SRAM wear, audio quality, LCD behaviour), Super Game Boy.
* A **full playthrough on the Game Boy and GBA ROMs**: the bot drives the SDL build (same core and data, but compiled with gcc rather than SDCC/arm-gcc). On GB/GBA only the smoke scenes above were run in an emulator; SDCC-specific bugs deeper in the story are possible.
* R36S / R36H on-device (SDL KMSDRM, PortMaster launcher, controller mapping, performance), ArkOS/dArkOS/ROCKNIX.
* macOS universal app (built only by CI on a macOS runner; never run here). Windows exe (see above). Touch controls on a real phone (layout implemented, only desktop Chromium exercised).
* The GitHub Actions workflow has not been executed by GitHub.
