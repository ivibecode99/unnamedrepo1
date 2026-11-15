#if defined(__SDCC)
#pragma bank 255
#endif
#include "lt.h"
void game_init(void) API {}
void game_start_new(void) API { g_mode = M_PLAY; }
void game_continue(void) API { g_mode = M_PLAY; }
void game_play_frame(void) API {}
