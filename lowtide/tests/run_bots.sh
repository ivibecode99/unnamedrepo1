#!/bin/bash
# Playthrough bots: each plays the real game from the title screen to the credits and checks the ending bit in the save file.
cd "$(dirname "$0")/.."
BIN=${1:-build/linux-x64/lowtide}
rc=0
for e in peace neutral fight true; do
  echo "== ending: $e"; python3 tests/bot.py $e --bin $BIN | tail -2 || rc=1
done
exit $rc
