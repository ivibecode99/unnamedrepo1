# Decisions
- Game lives in `lowtide/` so the repo's existing static site at the root is untouched.
- Web backend is SDL-free (Emscripten SDL2 port download hash-mismatched via the proxy); same soft PPU/synth as desktop.
- GBA: bare-metal arm-none-eabi with own crt0/linker script instead of devkitARM/libtonc/Butano (not installable here).
- Audio: custom 4-channel driver on the same note data on every platform instead of hUGEDriver/maxmod (one data format, one driver, exact hardware model).
- Overworld: rooms <=256x256 px, no streaming; 8x8 OBJ mode; NPC overworld sprites are single 16x16 frames with bob/flip idle (portraits/battle sprites carry full animation).
- DMG test ROM copy clears the CGB flag because mGBA picks the model from the header.
