# Project "Capt & Co." – Master Plan

Working title: **Capt & Co.** (hero: **Pip Marlowe**; living hat: **Capt**; villain: **Baron Von Grumblebelt**, a sulky clockwork aristocrat who steals the world's Stars to power his giant music box). All names, art, music and SFX are original.

## 1. Reality check (read first)
- This is a multi-year-scale scope. I will deliver it as **vertical slices that always run**, in strict priority order. Anything not reached is listed honestly in TODO.md, never faked.
- Environment today: **no Godot, no arm-none-eabi, no SDCC/GBDK, no Emscripten, no aarch64 cross-gcc**. Plan: download pinned official tool releases (Godot 4.4.x + export templates, GBDK-2020, devkitARM + Butano) in CI and, if the sandbox proxy allows, locally. Anything I cannot run locally is marked **"CI-verified only"** or **"unverified"** in TODO.md.
- Headless Godot gives me real automated tests (GUT-free: own tiny test runner) and screenshots via software rendering. It does **not** give me real "feel" or 60 FPS / R36S 30 FPS measurements; those need your hardware and I will say so rather than claim them.
- Cannot do locally: real cartridge flashing, R36S hardware tests, code signing/notarization for macOS. These are documented, not tested.

## 2. Architecture (Godot 4.4, GDScript, single codebase)
Folder layout (game lives in subfolders; existing site at repo root is left untouched):
```
game/                       Godot project (project.godot)
  autoload/                 Game (state), SaveSystem, AudioBus, Settings, Input map, SceneRouter, Dialogue
  core/                     StateMachine, Health, Interactable, Collectible base classes
  player/                   Pip (CharacterBody3D), move states, CameraRig, Capt (hat projectile)
  capture/                  CaptureComponent + 15+ Capturable scripts (each: movement + ability)
  enemies/                  enemy base + behaviors
  bosses/                   5 bosses + final, phase FSM
  kingdoms/                 forest/ desert/ city/ ocean/ snow/ sky_volcano/ hub_airship/ final/
  props/                    stars, coins, shops, checkpoints, springs, doors
  ui/                       HUD, pause, dialogue box, save-select, settings, shop, map
  story/                    dialogue .json (all text), cutscene scripts, npc registry
  audio/                    synth.gd (runtime synth), music scores (data), sfx recipes
  assets_gen/               procedural mesh/texture builders (tool scripts), toon shader
  tests/                    headless test runner + suites
  export_presets.cfg
tools/                      build.sh, gen_assets.py, music_render.py, ci helpers
web/                        landing page (static) + exported build goes to web/play/
pocket/                     Pocket Edition demake
  gba/ (Butano C++)  gb/ gbc/ (GBDK-2020 C)  shared/ (level data, converters)
docs/                       PLAN.md, FLASHING.md, R36S.md, PLAY_GUIDE.md
.github/workflows/          one workflow per target
README.md  TODO.md  CREDITS.md
```
Key decisions
- **Procedural art only**: characters/props built from primitives + CSG-baked ArrayMesh with chunky proportions; a custom **toon/soft-shade shader** (stepped diffuse + rim). Textures generated in code. Zero downloaded art by default → CREDITS stays clean (CC0 only if I add any, with licence recorded).
- **Audio**: runtime synthesizer (square/tri/noise/FM + simple reverb) driven by note-data scores (one theme per kingdom + boss + title + hub), rendered to `AudioStreamWAV` at load (or pre-rendered OGG via tools/music_render.py for web/R36S to cut CPU). SFX are small synth recipes.
- **Data-driven content**: kingdoms, stars, coins, NPC dialogue, shop items in JSON/Resources so counts (60+ stars, 25+ NPCs) are verifiable by tests.
- **Player**: CharacterBody3D with a state machine (run, jump, triple, long jump, ground pound, wall jump, swim, throw, spin, roll, dive), coyote time + jump buffer, camera rig with collision + invert option.
- **Capture**: Capt hits target → `capturable.on_captured(player)` swaps input control to target's controller; release on button/timeout; interface lets each creature override `move()`, `ability()`, `release()`.
- **Performance tiers**: `Settings.quality` = High / Medium / Low(R36S). Low: 640x480, no shadows/SSAO/glow, MSAA off, simple mats, LOD/distance culling, fewer particles, 30 FPS cap, pre-rendered audio, Compatibility renderer (GLES3) for Mali.
- **Renderer**: Compatibility renderer for all targets (Web needs it; R36S needs it) – one rendering path to test.
- **Save**: JSON in `user://save_{0,1,2}.json`, versioned + migration, atomic write (tmp + rename), checksum.

## 3. Asset pipeline
1. `tools/gen_assets.py` / Godot `@tool` scripts bake meshes, textures, icons → `game/assets_gen/out/` (committed, deterministic).
2. `tools/music_render.py` renders score data → OGG (CI) so we can ship pre-rendered audio on low-spec targets.
3. Pocket: `pocket/shared/convert.py` turns palette-indexed PNG/tile data + level maps into Butano graphics and GBDK C arrays (tiles generated by script, no external art).

## 4. Milestones (each: run → test → fix → commit)
| # | Milestone | Exit criteria |
|---|---|---|
| M0 | Scaffold: Godot project, CI skeleton, test runner, README/TODO/CREDITS, toon shader | headless boot passes in CI |
| M1 | Core movement + camera + gamepad/KB map, test box level | all 11 moves reachable; collision/movement tests green |
| M2 | **Forest kingdom** (full): stars, coins, shop, NPCs, HUD, pause, settings | complete playable kingdom |
| M3 | Capture system + 15 capturables (first 6 in forest/desert) | capture/release tests green |
| M4 | Boss framework + boss 1; save system w/ 3 slots + tests | save/load round-trip tests |
| M5 | Story: intro, cutscene runner, dialogue (25+ NPCs), hub airship, skip option | dialogue data validator test |
| M6 | Kingdoms 2–6 (desert, city, ocean, snow, sky/volcano), bosses 2–5, final level + final boss | 60+ stars verified by data test |
| M7 | Audio full pass (music/kingdom, SFX) | all cues present, no clipping test |
| M8 | Polish + perf presets (High/Med/Low) | profiling notes, R36S preset at 640x480 |
| M9 | Ports: Win/Linux/macOS(x86_64+arm64) builds, Web + landing, Linux ARM64 R36S + gamepad map | CI artifacts per target |
| M10 | Pocket Edition: GBA (Butano), GB + GBC (GBDK), 3–4 levels, 2 bosses, SRAM save | .gba/.gb/.gbc built in CI, run in emulator headless smoke test |
| M11 | Docs: flashing guide, play guide, final folder `dist/` | README steps verified |

Priority if time runs short: M0–M5 + M9 (web) + M10 first, then M6 breadth. I will tell you exactly what shipped.

## 5. Testing strategy
- Custom headless runner: `godot --headless --path game -s tests/run_all.gd` (exit code ≠ 0 on fail).
- Suites: save/load (round-trip, corrupt file, version migration), movement/collision (physics frames: jump heights, wall jump, floor snap, no tunnelling), capture/release, collectible counting, dialogue/data validators (no missing speaker, ≥25 NPCs, ≥60 stars, every kingdom has coin type), input-map completeness.
- Smoke: boot each kingdom scene headless for N frames, no errors.
- Pocket: build + run ROM in a headless emulator (mGBA / SameBoy CLI) for a frames-without-crash check where installable.

## 6. Builds and CI (one workflow per target)
| Target | Method |
|---|---|
| Windows x86_64, Linux x86_64, macOS (x86_64 + arm64, universal) | Godot export templates in GH Actions (`build-desktop.yml`); macOS ad-hoc signed, unsigned/notarization documented |
| Web | HTML5 export (`build-web.yml`), COOP/COEP-free single-thread build so static hosting (GitHub Pages) works; landing page `web/index.html` |
| Linux ARM64 (R36S/R36H) | Godot arm64 Linux export on ARM runner (`build-r36s.yml`), launch script `Capt.sh` for ArkOS/dArkOS/ROCKNIX (PortMaster-style, uses gptokeyb/SDL mapping), low-spec preset default, 640x480, 30 FPS |
| GBA | devkitARM + Butano container (`build-pocket.yml`) → `.gba` |
| GB / GBC | GBDK-2020 release → `.gb` / `.gbc` |
`tools/build.sh <target>` runs the same steps locally.

## 6b. R36S/R36H gamepad mapping (draft)
D-pad/left stick move · A jump · B throw Capt · X spin/roll · Y camera reset · L1/R1 camera · L2 crouch/ground-pound · R2 dive · Start pause · Select map. Finalized in docs/R36S.md with SDL `gamecontrollerdb` entry.

## 7. Pocket Edition scope
- 2D side view, same story compressed: Forest, Desert, City, Volcano (GBC/GBA) ; GB: 3 levels. 2 bosses (Mossback, Baron). Hat-throw (boomerang) mechanic.
- GBA: Butano, 15-bit palettes, SRAM save. GBC: 15-bit palettes, MBC5+RAM+Battery. GB: 4 shades, MBC5+RAM+Battery, **3 levels, 1 boss** if it doesn't fit (documented).
- Flashing doc: GBA flash carts (EZ-Flash, EverDrive GBA) + bootleg writers; GB/GBC: EverDrive GB/Joey Jr/flash carts; cart types **MBC5+RAM+battery** for GB/GBC and **FLASH1M/SRAM 32KB** for GBA. No claim of testing on real hardware.
- R36S runs the `.gba` through its built-in gpSP/mGBA core by dropping it in `ROMS/gba`.

## 8. Risks
1. Scope: 6 kingdoms + 6 bosses + 15 capturables + 25 NPCs is huge; mitigated by data-driven kits and shared enemy/boss frameworks.
2. Procedural art quality: will look "chunky stylized", not studio-grade.
3. Toolchain downloads may be blocked by the sandbox proxy → CI-only verification.
4. R36S Mali (Compatibility GLES3) perf is unmeasured without hardware.
5. 3D feel needs human playtesting; I'll expose tunables in one `tuning.tres`.

## 9. Licensing policy
Only generated/procedural assets + synthesized audio. Any CC0 asset must be added to CREDITS.md with source URL + licence. Godot (MIT), Butano (zlib), GBDK-2020 (MIT-like) are credited.
