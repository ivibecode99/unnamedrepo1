#ifndef ASSETS_H
#define ASSETS_H
#include <stdint.h>

#define NUM_BG_TILES 70
#define NUM_SPR_TILES 37
#define FONT_BASE 25
#define FONT_CHARS "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?-:'/x"
#define T_SKY 0
#define T_GRASS 1
#define T_DIRT 2
#define T_BRICK 3
#define T_LAVA 4
#define T_COIN 5
#define T_STAR 6
#define T_TRUNK 7
#define T_LEAF 8
#define T_CACTUS 9
#define T_SAND 10
#define T_SANDFILL 11
#define T_BLD 12
#define T_WINDOW 13
#define T_CLOUD 14
#define T_SPIKE 15
#define T_WALL 16
#define T_METAL 17
#define T_NOTE 18
#define T_GEAR 19
#define T_HILL 20
#define T_HEART 21
#define T_BARRIER 22
#define T_FILL 23
#define T_CITYFILL 24
#define S_PIP0 0
#define S_PIP1 2
#define S_PIP2 4
#define S_PIP3 6
#define S_PIPHAT 8
#define S_HAT0 9
#define S_HAT1 10
#define S_WALK0 11
#define S_WALK1 12
#define S_FLY0 13
#define S_FLY1 14
#define S_BOSS1 15
#define S_BOSS2 24
#define S_PROJ0 33
#define S_PROJ1 34
#define S_PUFF 35
#define S_STAR 36
extern const uint8_t bg_tiles[];
extern const uint8_t spr_tiles[];
extern const uint8_t tile_class[NUM_BG_TILES];   /* bit0 solid, bit1 hazard, bit2 coin, bit3 star */
extern const uint8_t tile_palette[NUM_BG_TILES];
extern const uint16_t bg_palettes[4][5 * 4];
extern const uint16_t spr_palettes[6 * 4];
#endif
