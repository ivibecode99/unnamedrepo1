#!/bin/bash
# Build the web version (index.html + wasm) with Emscripten. Uses a writable copy of the emscripten cache if the
# distro install is frozen (Debian/Ubuntu): set EM_CONFIG to a config with FROZEN_CACHE=False.
set -e
cd "$(dirname "$0")/.."
python3 tools/build_data.py
OUT=build/web; mkdir -p $OUT
emcc -O2 -std=gnu99 -Icore -DPLATFORM_WEB core/*.c platform/web/web_main.c platform/soft/soft.c build/gen/blob.c \
  -sALLOW_MEMORY_GROWTH=1 -sINITIAL_MEMORY=33554432 -sEXPORTED_FUNCTIONS=_main,_web_audio_fill,_malloc,_free \
  -sEXPORTED_RUNTIME_METHODS=HEAPU8,UTF8ToString,stringToUTF8,lengthBytesUTF8 -sMINIFY_HTML=0 --shell-file platform/web/shell.html \
  -o $OUT/index.html
ls -la $OUT
