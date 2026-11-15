/* VRAM tile layout shared by tools (parsed) and core. Tile index space is shared by BG and OBJ. */
#define T_CLEAR 0      /* all colour 0 */
#define T_BLACK 1      /* all colour 3 */
#define T_FONT 2       /* ASCII 32..126 -> 95 tiles (2..96) */
#define T_UI 97        /* 31 UI tiles (97..127) */
#define T_PLAYER 128   /* 24 tiles: 3 dirs x 2 frames x 4 */
#define T_ACTOR 152    /* 6 actors x 4 tiles (152..175) */
#define T_FACE 176     /* 16 tiles (176..191) */
#define T_MAP 192      /* 64 tiles (192..255) */
#define T_BSPR 112     /* battle sprites: 16 tiles (112..127) */
#define T_ENEMY 128    /* battle enemy art up to 128 tiles */
#define MAP_TILES 64
/* UI tile offsets from T_UI */
#define UI_TL 0
#define UI_T 1
#define UI_TR 2
#define UI_L 3
#define UI_R 4
#define UI_BL 5
#define UI_B 6
#define UI_BR 7
#define UI_ARROW 8
#define UI_CURSOR 9
#define UI_HEART 10
#define UI_HP0 11     /* hp bar: 11 empty .. 11+8 full (9 tiles, fill 0..8) */
/* palette slots: BG 0-7, OBJ 8-15 */
#define P_UI 0
#define P_ZONE 1       /* BG palettes 1..6 per zone */
#define P_FACE 7
#define P_PLAYER 8
#define P_ACTOR 9      /* OBJ 9..13 */
#define P_BULLET 14
#define P_SOUL 15
/* sizes */
#define SCENE_MAX 2560
#define MUSIC_MAX 1536
#define SCRATCH_MAX 640
#define MAXBUL_GB 16
#define MAXBUL_BIG 48

/* fixed chunk ids (content-generated chunks start at CH_CONTENT) */
#define CH_TILES_UI 0
#define CH_PAL_UI 1
#define CH_STRINGS 2
#define CH_SPEAKERS 3
#define CH_ITEMS 4
#define CH_SHOPS 5
#define CH_ENC 6
#define CH_BSPR 7
#define CH_PLAYER 8
#define CH_TITLE 9
#define CH_SONG 16     /* + song id, up to 48 songs */
#define CH_SFX 64      /* + sfx id (single chunk holds all sfx -> CH_SFX) */
#define CH_CONTENT 80
/* reserved script variables */
#define V_R 0
#define V_KILLS 1
#define V_SPARES 2
#define V_LISTEN 3
#define V_ZONE 4
#define V_NG 5
#define V_LASTBT 6
#define V_SHELLS 7
#define V_BT_TURN 8
#define V_BT_HITS 9
#define V_BT_SHIELD 10
#define V_BT_MOVED 11
#define V_BT_ACTS 12
#define V_BT_FLAG0 13   /* 13..20 per-battle flags (cleared at battle start) */
#define V_PREV_ENDING 21
#define V_BOSSKILLS 22
#define V_BOSSSPARES 23
#define V_USER 32
