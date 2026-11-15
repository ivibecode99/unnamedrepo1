# Desktop SDL2 build (native). See tools/ for other targets.
CORE := $(wildcard core/*.c)
CFLAGS ?= -O2 -std=gnu99 -Wall -Wextra -Wno-unused-parameter -Wno-unused-function -Icore
BUILD := build/linux-x64
.PHONY: data native
data:
	python3 tools/build_data.py
native: data
	mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(shell sdl2-config --cflags) -o $(BUILD)/lowtide $(CORE) platform/sdl/sdl_main.c platform/soft/soft.c build/gen/blob.c $(shell sdl2-config --libs) -lm
