#!/bin/bash
# Build every artifact that can be built on this machine into dist/. Missing toolchains are reported, never faked.
set -u
cd "$(dirname "$0")/.."
D=dist; mkdir -p $D; VER=$(date +%Y.%m.%d)
step() { echo "== $*"; }
python3 tools/build_data.py > /dev/null || exit 1
step "Game Boy / Game Boy Color"; if [ -x /opt/gbdk/bin/lcc ] || command -v lcc >/dev/null; then ./tools/build_gb.sh >/dev/null 2>&1 && cp build/gb/lowtide.gbc $D/lowtide.gbc && python3 tests/check_roms.py $D/lowtide.gbc; else echo "GBDK-2020 not found: skipped"; fi
step "Game Boy Advance"; if command -v arm-none-eabi-gcc >/dev/null; then ./tools/build_gba.sh >/dev/null 2>&1 && cp build/gba/lowtide.gba $D/lowtide.gba && python3 tests/check_roms.py $D/lowtide.gba; else echo "arm-none-eabi-gcc not found: skipped"; fi
step "Linux x86_64"; mkdir -p build/cmake-native && (cd build/cmake-native && cmake ../.. -DCMAKE_BUILD_TYPE=Release >/dev/null && make -j4 >/dev/null 2>&1) && {
  rm -rf build/pkg-linux && mkdir -p build/pkg-linux/lowtide && cp build/cmake-native/lowtide build/pkg-linux/lowtide/ && cp README.md build/pkg-linux/lowtide/ && printf '#!/bin/sh\ncd "$(dirname "$0")"\nexec ./lowtide "$@"\n' > build/pkg-linux/lowtide/run.sh && chmod +x build/pkg-linux/lowtide/run.sh
  tar czf $D/lowtide-linux-x86_64.tar.gz -C build/pkg-linux lowtide; echo "ok"; } || echo "failed"
step "Linux aarch64 + R36S/R36H"; if command -v aarch64-linux-gnu-gcc >/dev/null && [ -d "${SDL2_AARCH64:-/tmp/sdl-a64}" ]; then
  export SDL2_AARCH64=${SDL2_AARCH64:-/tmp/sdl-a64}
  for t in generic r36s; do mkdir -p build/cmake-a64-$t; flag=OFF; [ $t = r36s ] && flag=ON
    (cd build/cmake-a64-$t && cmake ../.. -DCMAKE_TOOLCHAIN_FILE=../../cmake/aarch64-linux.cmake -DCMAKE_BUILD_TYPE=Release -DLT_R36S=$flag -DSDL2_DIR=$SDL2_AARCH64/lib/cmake/SDL2 >/dev/null && make -j4 >/dev/null 2>&1); done
  rm -rf build/pkg-a64 && mkdir -p build/pkg-a64/lowtide && cp build/cmake-a64-generic/lowtide README.md build/pkg-a64/lowtide/ && tar czf $D/lowtide-linux-aarch64.tar.gz -C build/pkg-a64 lowtide
  rm -rf build/pkg-r36s && mkdir -p build/pkg-r36s/lowtide && cp packaging/r36s/Lowtide.sh build/pkg-r36s/ && cp build/cmake-a64-r36s/lowtide packaging/r36s/port.json README.md build/pkg-r36s/lowtide/
  (cd build/pkg-r36s && zip -qr ../../$D/lowtide-r36s-portmaster.zip .); echo ok
else echo "aarch64 cross toolchain / SDL2 not found: skipped"; fi
step "Windows x64"; if command -v x86_64-w64-mingw32-gcc >/dev/null && [ -d "${SDL2_MINGW:-/tmp/sdlw/SDL2-2.30.9/x86_64-w64-mingw32}" ]; then
  export SDL2_MINGW=${SDL2_MINGW:-/tmp/sdlw/SDL2-2.30.9/x86_64-w64-mingw32}; mkdir -p build/cmake-win
  (cd build/cmake-win && cmake ../.. -DCMAKE_TOOLCHAIN_FILE=../../cmake/mingw-w64-x86_64.cmake -DCMAKE_BUILD_TYPE=Release -DSDL2_DIR=$SDL2_MINGW/lib/cmake/SDL2 >/dev/null && make -j4 >/dev/null 2>&1)
  rm -rf build/pkg-win && mkdir -p build/pkg-win/lowtide && cp build/cmake-win/lowtide.exe $SDL2_MINGW/bin/SDL2.dll README.md build/pkg-win/lowtide/ && (cd build/pkg-win && zip -qr ../../$D/lowtide-windows-x64.zip lowtide); echo ok
else echo "mingw-w64 / SDL2 mingw dev package not found: skipped"; fi
step "Web"; if command -v emcc >/dev/null; then EM_CONFIG=${EM_CONFIG:-/tmp/em.cfg} ./tools/build_web.sh >/dev/null 2>&1 && (cd build/web && zip -qr ../../$D/lowtide-web.zip index.html index.js index.wasm) && echo ok || echo failed; else echo "emcc not found: skipped"; fi
step "Previews (sprite sheets, map sheet, music WAVs)"; python3 tools/sheet.py build/dist_art >/dev/null && python3 tools/render_music.py build/dist_music >/dev/null && (cd build && zip -qr ../$D/lowtide-art-music-previews.zip dist_art dist_music maps_sheet.png 2>/dev/null) && echo ok
step "macOS universal"; echo "built by CI (.github/workflows/release.yml) on a macOS runner; cannot be built on this Linux host"
ls -la $D
