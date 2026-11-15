#!/usr/bin/env bash
# Capt & Co. build script.  Usage: tools/build.sh <target> [more targets]
#   targets: setup test linux windows macos web r36s pocket-gb pocket-gbc pocket-gba dist all
# Env:  GODOT=/path/to/godot (default: godot in PATH)   GBDK_HOME=/path/to/gbdk   BUTANO=/path/to/butano/butano
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GODOT="${GODOT:-godot}"
OUT="$ROOT/build"
DIST="$ROOT/dist"
mkdir -p "$OUT" "$DIST"

import_project() { "$GODOT" --headless --path "$ROOT/game" --import >/dev/null 2>&1 || true; }
export_preset() { # preset, relative output
  import_project
  mkdir -p "$(dirname "$OUT/$2")"
  "$GODOT" --headless --path "$ROOT/game" --export-release "$1" "$OUT/$2"
}

for target in "$@"; do
  echo "=== $target"
  case "$target" in
    setup)   import_project ;;
    test)    import_project; "$GODOT" --headless --path "$ROOT/game" res://tests/runner.tscn ;;
    linux)   export_preset "Linux x86_64" linux-x86_64/CaptCo.x86_64 ;;
    windows) export_preset "Windows x86_64" windows/CaptCo.exe ;;
    macos)   export_preset "macOS Universal" macos/CaptCo.zip ;;
    web)
      export_preset "Web" web/index.html
      rm -rf "$OUT/site"; mkdir -p "$OUT/site/play"
      cp -r "$ROOT/web/"* "$OUT/site/"; cp -r "$OUT/web/"* "$OUT/site/play/"
      echo "Serve with:  python3 -m http.server -d $OUT/site 8080" ;;
    r36s)
      export_preset "Linux ARM64 (R36S)" linux-arm64/CaptCo.arm64
      P="$DIST/captco"; rm -rf "$P"; mkdir -p "$P/captco"
      cp "$OUT/linux-arm64/CaptCo.arm64" "$ROOT/r36s/capt.gptk" "$ROOT/r36s/gamecontrollerdb.txt" "$P/captco/"
      cp "$ROOT/r36s/CaptCo.sh" "$P/"
      (cd "$DIST" && rm -f CaptCo-r36s-arm64.zip && zip -qr CaptCo-r36s-arm64.zip captco) ;;
    pocket-gb|pocket-gbc) make -C "$ROOT/pocket/gb" all; mkdir -p "$DIST/pocket"; cp "$ROOT/pocket/gb/build/"*.gb* "$DIST/pocket/" ;;
    pocket-gba) make -C "$ROOT/pocket/gba" LIBBUTANO="${BUTANO:?set BUTANO=/path/to/butano/butano}"; mkdir -p "$DIST/pocket"; cp "$ROOT/pocket/gba/"*.gba "$DIST/pocket/" ;;
    dist)
      mkdir -p "$DIST"
      [ -d "$OUT/linux-x86_64" ] && (cd "$OUT/linux-x86_64" && zip -qr "$DIST/CaptCo-linux-x86_64.zip" .)
      [ -d "$OUT/windows" ] && (cd "$OUT/windows" && zip -qr "$DIST/CaptCo-windows-x86_64.zip" .)
      [ -f "$OUT/macos/CaptCo.zip" ] && cp "$OUT/macos/CaptCo.zip" "$DIST/CaptCo-macos-universal.zip"
      [ -d "$OUT/site" ] && (cd "$OUT/site" && zip -qr "$DIST/CaptCo-web.zip" .)
      ls -la "$DIST" ;;
    all) "$0" test linux windows macos web r36s pocket-gb pocket-gbc dist ;;
    *) echo "unknown target $target"; exit 2 ;;
  esac
done
