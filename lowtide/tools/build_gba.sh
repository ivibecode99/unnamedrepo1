#!/bin/bash
# Build lowtide.gba with arm-none-eabi-gcc (no libtonc/devkitARM needed: bare-metal backend).
set -e
cd "$(dirname "$0")/.."
python3 tools/build_data.py
OUT=build/gba; mkdir -p $OUT
CC=arm-none-eabi-gcc
FL="-mcpu=arm7tdmi -mthumb -Os -ffunction-sections -fdata-sections -fno-strict-aliasing -std=gnu99 -Icore -DPLATFORM_GBA $EXTRA -Wall -Wno-unused-function"
$CC -mcpu=arm7tdmi -marm -c platform/gba/crt0.s -o $OUT/crt0.o
$CC $FL -c platform/gba/main_gba.c -o $OUT/main.o
objs="$OUT/crt0.o $OUT/main.o"
for f in core/*.c; do o=$OUT/$(basename $f .c).o; $CC $FL -c $f -o $o; objs="$objs $o"; done
# embed blob in ROM
python3 - <<PY
import sys
sys.path.insert(0,'tools')
b=open('build/gen/blob.bin','rb').read()
with open('$OUT/blob.s','w') as f:
    f.write('.section .blob,"a"\n.global lt_blob\n.balign 4\nlt_blob:\n')
    for i in range(0,len(b),32): f.write('.byte '+','.join(map(str,b[i:i+32]))+'\n')
PY
$CC -mcpu=arm7tdmi -marm -c $OUT/blob.s -o $OUT/blob.o
$CC -nostartfiles -specs=nano.specs -specs=nosys.specs -mcpu=arm7tdmi -mthumb -Wl,--gc-sections -Wl,-Map=$OUT/lowtide.map -T platform/gba/gba.ld $objs $OUT/blob.o -o $OUT/lowtide.elf -lc -lgcc
arm-none-eabi-objcopy -O binary $OUT/lowtide.elf $OUT/lowtide.gba
python3 tools/gbafix.py $OUT/lowtide.gba
arm-none-eabi-size $OUT/lowtide.elf
