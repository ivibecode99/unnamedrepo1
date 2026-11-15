# Flashing the Pocket Edition to a real cartridge

> **Honesty note:** the three ROMs were tested **in emulators only** (PyBoy for `.gb`/`.gbc`, mGBA for `.gba`, scripted end-to-end tests in `pocket/tests/`). I have no flash carts or cartridge writers here, so everything below is based on the ROM headers (which I verified) and the vendors' documented behaviour, not on a real-hardware test run.

## ROM facts (verified from the built files)

| File | Size | Header facts |
|---|---|---|
| `captco.gb` | 32 KiB | title `CAPTCO`, CGB flag `0x00` (DMG only), cartridge type **`0x1B` = MBC5 + RAM + BATTERY**, ROM size code `0x00` (32 KiB / 2 banks), RAM size code `0x02` (**8 KiB SRAM**) |
| `captco.gbc` | 32 KiB | same, but CGB flag `0xC0` (**Game Boy Color only**) |
| `captco_pocket.gba` | ≈125 KiB | title `CAPTCO POCKET`, game code `CAPT`, header checksum fixed (`gbafix`), save type string **`SRAM_V113`** (32 KiB battery SRAM) |

The game stores: furthest level reached, stars, coins and a checksum (9 bytes at the start of SRAM). It does not need more than 1 SRAM bank.

## Supported cartridge types

### Game Boy / Game Boy Color (`.gb` / `.gbc`)
Anything that can emulate **MBC5 with battery-backed SRAM (≥ 8 KiB)**:
* **Flash carts (copy the file to the SD card):** Krikzz *EverDrive GB* (X3/X5/X7/Series), *EZ-Flash Jr*, *Joey Jr.* and compatible clones. All of these map MBC5 and create a `.sav` next to the ROM.
* **Blank repro cartridges + writer:** carts with an MBC5 mapper, a flash ROM ≥ 32 KiB and 8–32 KiB SRAM with a battery, e.g. the *Game Boy Flash Cart* family sold for the **GBxCart RW** (insideGadgets). Write with **FlashGBX** (it detects the cart and lists the chip) – choose "Write ROM", select `captco.gb(c)`, tick "Write save data"/"Restore save" only if you want to inject a save, and verify afterwards.
* **Plain "ROM only" or MBC1/MBC3 carts do not work** for saving (wrong mapper / no SRAM); the game would still run but lose progress.
* Use `.gb` on an original Game Boy / Pocket / Super Game Boy; use `.gbc` on a Game Boy Color / GBA (CGB mode) – `.gbc` will **not** boot on a monochrome Game Boy.
* If your flash chip needs a padded image: `truncate -s 64K captco.gb` (pads with zeros; the header still says 32 KiB, which is fine).

### Game Boy Advance (`.gba`)
* **Flash carts:** *EZ-Flash Omega / Omega Definitive*, *EZ-Flash IV*, *EverDrive-GBA (X5/X7)*. Copy the ROM to the SD card, launch it, and if the cart asks for the **save type choose "SRAM" (32 KiB)** – the ROM also carries the `SRAM_V113` marker so auto-detect normally picks it.
* **Blank repro cartridges + writer:** repro carts with a flash ROM chip and **SRAM + battery** (32 KiB SRAM is plenty). Write with **FlashGBX** (GBxCart RW) or the vendor's writer. Carts whose only save memory is *Flash* or *EEPROM* will not keep the save unless you rebuild with a different save type (Butano supports `bn::sram` only for SRAM carts; ask for a Flash build if needed).
* Some writers want a power-of-two image: `truncate -s 256K captco_pocket.gba`.
* **R36S / R36H and other emulation handhelds:** copy to `roms/gba/` – no flashing needed.

## Step by step: flash cart
1. Format the SD card FAT32 and copy `captco.gb`, `captco.gbc` and/or `captco_pocket.gba` to it.
2. Insert the card, power the console and pick the ROM in the cart's menu.
3. (GBA only) If asked, choose **SRAM / 32 KiB** as the save type.
4. Play. Progress is written when you finish a level; power off from the title screen or after "STAR GET" to be safe.

## Step by step: blank cart + GBxCart RW (FlashGBX)
1. Install FlashGBX, plug in the GBxCart RW, insert the blank cart and click *Detect Cartridge*.
2. *Flash Cartridge* → select the ROM → if prompted for the cart type pick the one matching your repro cart (MBC5 + 8–32 KiB SRAM for GB/GBC; SRAM flash cart for GBA).
3. Enable *Verify* and write; wait for the green "Done".
4. Optionally *Write Save Data* with an existing `.sav`.
5. Put the cart in a console, check that "CONTINUE" appears after finishing level 1 and rebooting.

## Resetting the save
Hold nothing: choose **NEW GAME** from the title screen (it overwrites the save when you finish the next level), or wipe the SRAM with your writer's "Erase save" function.
