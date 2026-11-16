# Progress
## Phase 1 - foundations: DONE (verified)
Portable core, SDL/web/GBC/DMG/GBA backends, pixel + chunk + music pipelines, title screen on every target.
## Phase 2 - engine + vertical slice: DONE (verified)
Script VM, world (rooms, collision, pushable blocks, plates, zones, encounters), text box with per-speaker blips and faces, battle with parametric emitters, shield, mercy/listen system, shops, naming, save points (3 slots), mini-games (rhythm, sorting), credits/endings, NG+ meta.
## Phase 3 - content: DONE (breadth), see DECISIONS for length caveat
Prologue + zones 1-5 + finale: 31 rooms, 18 battles (10 enemy types, 6 bosses incl. final, 2 rival fights), 25 speakers, 31 songs + 19 SFX, side stories (Cobb's stew, Rill's song, Inkling's pages) and 5 hidden Memory Shells, 4 endings + New Game+ callbacks.
## Phase 4 - polish: PARTIAL
Done: accessibility options (text speed, reduce flashing, slow-dodge assist, volume, key remap), per-platform bullet caps/density, fixes found by the bot (NPC re-trigger, fades, edge-of-map triggers, game-over guard, mid-script warps).
Not done: broad balance pass beyond what the bot exercised, decorative GBA border, performance tuning beyond the profiled GB overworld, longer dialogue/content.
## Phase 5 - release: DONE for what the host can build
`tools/package.sh` -> `dist/` (GBC, GBA, web, Windows, Linux x86_64/aarch64, R36S PortMaster); macOS via CI; `.github/workflows/lowtide-release.yml`; README with per-platform instructions. See PLATFORMS.md for what is untested.
## Tests
`make test` (VM, save/load, emitters) - pass. `tests/run_bots.sh` - Peace/Neutral/Fight/True all reached from the title screen. `tests/check_roms.py`, mGBA smoke runs, Chromium web run, QEMU aarch64 run.
