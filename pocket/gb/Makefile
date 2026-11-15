# Capt & Co. Pocket Edition - Game Boy / Game Boy Color (GBDK-2020)
# make assets   regenerate tiles/levels/music from pocket/tools/*.py (needs python3)
# make all      build build/captco.gb (DMG, 4 shades) and build/captco.gbc (CGB, 15-bit colour)
GBDK_HOME ?= /opt/gbdk
LCC = $(GBDK_HOME)/bin/lcc
SRC = src/main.c src/assets.c src/levels.c src/music_data.c
# MBC5 + RAM + battery (0x1B), 32 KB ROM, 8 KB SRAM, 6-char title
MBC = -Wm-yt0x1B -Wm-yo2 -Wm-ya1 -Wm-yn"CAPTCO"

all: build/captco.gb build/captco.gbc

build/captco.gb: $(SRC) src/assets.h src/levels.h src/music_data.h
	@mkdir -p build
	$(LCC) -Wa-l -Wl-m -Wl-j $(MBC) -o $@ $(SRC)

build/captco.gbc: $(SRC) src/assets.h src/levels.h src/music_data.h
	@mkdir -p build
	$(LCC) -DTARGET_GBC -Wa-l -Wl-m -Wl-j $(MBC) -Wm-yC -o $@ $(SRC)

assets:
	python3 ../tools/export_gb.py

clean:
	rm -rf build
.PHONY: all assets clean
