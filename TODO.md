# TODO / status

Legend: [x] done and covered by automated tests · [~] done, verified only partly · [ ] not done

## Delivered
- [x] M0 Scaffold: Godot 4.4.1 project, test runner (962 checks), CI, build script, CREDITS
- [x] M1 Core movement: run, jump, triple jump, long jump, backflip, ground pound, wall jump, swim, hat throw, hat spin, roll, dive; camera with collision, invert options
- [x] M2 Forest kingdom + all other kingdoms generated from data (hub, forest, desert, city, ocean, snow, volcano, final)
- [x] M3 Capture system with 18 capturables
- [x] M4 Boss framework: 5 bosses + final boss; 3-slot save system with checksum, atomic writes, migration
- [x] M5 Story: intro, arrival, boss and ending cutscenes; 44 NPCs; dialogue box with skip; fetch quests; shops; hub map
- [x] M6 66 Stars, kingdom coins and shops, kingdom unlock gates
- [x] M7 Music (12 tracks) and 37 SFX, all synthesized
- [x] M8 Quality presets (High/Medium/Low), handheld mode, 30 FPS cap
- [x] M9 Exports: Linux x86_64, Windows, macOS universal, Web (+landing page, +Pages workflow), Linux ARM64 + R36S launcher; CI per target
- [x] M10 Pocket Edition: GB, GBC (GBDK) and GBA (Butano): 4 levels, 2 bosses, hat throw, battery save, emulator tests
- [x] M11 Docs: README, PLAY_GUIDE, R36S, FLASHING

## Known gaps / honest caveats
- [ ] **Performance is unmeasured** on real hardware (desktop GPU and R36S). Only software GL was available. Expect to tune `Settings.view_distance`, light count and particle density.
- [ ] Windows, macOS and ARM64 builds are exported but **never executed**. macOS is not notarized.
- [ ] R36S button mapping is best-effort (see docs/R36S.md); verify on the device.
- [ ] **No mouse/gamepad playtest by a human**: movement feel, camera and difficulty are tuned by numbers and automated tests, not by hand. Tunables live in `game/player/tuning.gd`.
- [ ] 3D art is chunky procedural primitives (toon shaded), not hand-modelled. Characters have simple idle/run/jump poses but no skeletal animation.
- [ ] Level layouts are procedurally generated per kingdom from a seed (landmarks/towers/hidden spots are placed deterministically); they are playable and tested for reachability of key objects, but not hand-polished.
- [ ] Hub airship has no separate "power the engine" cutscene beyond dialogue/unlock messages.
- [ ] GBA Pocket Edition has no music/SFX (Butano audio needs maxmod soundbanks; the GB/GBC versions have music and SFX).
- [ ] Pocket Edition GB/GBC: single-bank 32 KiB ROM; it fits fully (4 levels, 2 bosses) so no cut-down version was needed.
- [ ] Real flash-cart/writer testing of the ROMs.
- [ ] Controller remapping UI (keyboard remap only).
