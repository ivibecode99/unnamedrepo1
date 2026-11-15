#!/bin/bash
# Build lowtide.gbc (works on DMG too). Needs GBDK-2020 at $GBDK (default /opt/gbdk).
set -e
cd "$(dirname "$0")/.."
export GBDK=${GBDK:-/opt/gbdk}; export GBDKDIR=$GBDK/; export PATH=$GBDK/bin:$PATH
python3 tools/build_data.py
OUT=build/gb; mkdir -p $OUT/gen
FIRSTDATA=${FIRSTDATA:-8}
python3 tools/pack_gb.py build/gen/blob.bin $OUT/gen $FIRSTDATA
LASTBANK=$(ls $OUT/gen/bank_*.c | wc -l); TOTAL=$((FIRSTDATA + LASTBANK))
ROMBANKS=2; while [ $ROMBANKS -lt $TOTAL ]; do ROMBANKS=$((ROMBANKS*2)); done
CORE=$(ls core/*.c)
lcc -Icore -DPLATFORM_GB $EXTRA -Wm-yt0x1A -Wm-yn"LOWTIDE" -Wm-yo$ROMBANKS -Wm-ya4 -Wm-yc -Wl-j -Wl-m -autobank -Wb-ext=.rel -Wb-min=1 -Wb-max=$((FIRSTDATA-1)) \
  -o $OUT/lowtide.gbc platform/gb/main_gb.c $CORE $OUT/gen/chunkdir.c $OUT/gen/bank_*.c
ls -la $OUT/lowtide.gbc
