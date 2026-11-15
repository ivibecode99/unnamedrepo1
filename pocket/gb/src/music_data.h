#ifndef MUSIC_DATA_H
#define MUSIC_DATA_H
#include <stdint.h>
#define NOTE_MIN 36
#define NOTE_COUNT 61
#define TRACK_STEPS 64
#define NUM_TRACKS 4
extern const uint16_t note_freq[NOTE_COUNT];
extern const uint8_t track_lead[NUM_TRACKS][TRACK_STEPS];
extern const uint8_t track_bass[NUM_TRACKS][TRACK_STEPS];
#endif
