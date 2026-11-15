#if defined(__SDCC)
#pragma bank 255
#endif
#include "lt.h"
/* integer sine (quarter table, 256 steps/turn, +-127) and small RNG */
static CONSTMEM s8 qs[65] = {
  0,3,6,9,12,16,19,22,25,28,31,34,37,
  40,43,46,49,51,54,57,60,63,65,68,71,73,
  76,78,81,83,85,88,90,92,94,96,98,100,102,
  104,106,107,109,111,112,113,115,116,117,118,120,121,
  122,122,123,124,125,125,126,126,126,127,127,127,127
};
s8 isin(u8 a) API {
    u8 q = a & 63;
    s8 v;
    switch (a >> 6) {
    case 0: return qs[q];
    case 1: return qs[64 - q];
    case 2: v = qs[q]; return (s8)(-v);
    default: v = qs[64 - q]; return (s8)(-v);
    }
}
s8 icos(u8 a) API { return isin((u8)(a + 64)); }
/* angle of vector (dx,dy), 0=right, 64=down (screen coords); ~1 unit accuracy */
u8 iatan(s16 dy, s16 dx) API {
    s16 ax = dx < 0 ? -dx : dx, ay = dy < 0 ? -dy : dy, r;
    u8 a;
    if (ax == 0 && ay == 0) return 0;
    if (ax >= ay) { r = (s16)((ay * 32) / ax); a = (u8)(r + (r * (32 - r) * 11) / 1024); }
    else { r = (s16)((ax * 32) / ay); a = (u8)(64 - (r + (r * (32 - r) * 11) / 1024)); }
    if (dx >= 0 && dy >= 0) return a;
    if (dx < 0 && dy >= 0) return (u8)(128 - a);
    if (dx < 0 && dy < 0) return (u8)(128 + a);
    return (u8)(256 - a);
}
static u16 rs = 0xACE1;
void rnd_seed(u16 s) API { rs = s ? s : 0xACE1; }
u8 rnd(void) API {
    u16 b = ((rs >> 0) ^ (rs >> 2) ^ (rs >> 3) ^ (rs >> 5)) & 1;
    rs = (u16)((rs >> 1) | (b << 15));
    b = ((rs >> 0) ^ (rs >> 2) ^ (rs >> 3) ^ (rs >> 5)) & 1;
    rs = (u16)((rs >> 1) | (b << 15));
    return (u8)(rs ^ (rs >> 8));
}
