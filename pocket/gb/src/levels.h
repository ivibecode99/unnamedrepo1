#ifndef LEVELS_H
#define LEVELS_H
#include <stdint.h>
#define NUM_LEVELS 4
typedef struct { uint8_t type, x, y; } EnemySpawn;
typedef struct { const char *name; const uint8_t *rle; uint16_t rle_len; uint8_t w; uint8_t theme; uint8_t boss; uint8_t music; uint8_t n_enemies; const EnemySpawn *enemies; uint8_t arena_x0, arena_x1; uint8_t goal_x, goal_y; uint8_t coins; } LevelInfo;
extern const LevelInfo level_info[NUM_LEVELS];
#endif
