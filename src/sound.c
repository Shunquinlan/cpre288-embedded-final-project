#include "../inc/sound.h"
#include "../inc/open_interface.h"
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

/*
 * Simple wrapper around the CyBot / Roomba sound support.
 *
 * Reserved songs:
 *   song 0 : OK beep
 *   song 1 : error beep
 *   song 2 : EXIT cue (manual / auto exit start)
 *   song 3 : "End of Mission" / end-of-mission slow theme
 *   song 4 : "SOLDIER FOUND" alarm (short 3-tone alert)
 *
 * Higher song numbers can be used for custom sounds if desired.
 */

#define ROOMBA_MAX_SONGS  8
#define ROOMBA_MAX_NOTES 16

/* If note-name macros are not defined anywhere else, define them here.
 * Roomba uses MIDI-style note numbers:
 *   C4 = 60, A4 = 69, E5 = 76, etc.
 */
#ifndef NOTE_C4
#define NOTE_C4 60
#endif

#ifndef NOTE_E4
#define NOTE_E4 64
#endif

#ifndef NOTE_G4
#define NOTE_G4 67
#endif

#ifndef NOTE_A4
#define NOTE_A4 69
#endif

#ifndef NOTE_C5
#define NOTE_C5 72
#endif

#ifndef NOTE_E5
#define NOTE_E5 76
#endif

/* Track which song slots are loaded (0–ROOMBA_MAX_SONGS-1). */
static uint8_t loaded_songs[ROOMBA_MAX_SONGS] = {0};

/* ------------ low-level wrappers ------------ */

void sound_load_song(uint8_t songNumber,
                     const uint8_t *notes,
                     const uint8_t *durations,
                     uint8_t length)
{
    if (songNumber >= ROOMBA_MAX_SONGS) return;
    if (length == 0 || length > ROOMBA_MAX_NOTES) return;
    if (!notes || !durations) return;

    oi_loadSong(songNumber, length,
                (unsigned char *)notes,
                (unsigned char *)durations);

    loaded_songs[songNumber] = 1;
}

void sound_play_song(uint8_t songNumber)
{
    if (songNumber >= ROOMBA_MAX_SONGS) return;
    if (!loaded_songs[songNumber]) {
        // Song not loaded; silently ignore.
        return;
    }
    oi_play_song(songNumber);
}

/* ------------ default init + convenience beeps ------------ */

void sound_init(void)
{
    /* Song 0: OK beep (A4, quick) */
    static const uint8_t ok_notes[] = { NOTE_A4 };
    static const uint8_t ok_durs[]  = { 16 };   /* 16/64 s */

    sound_load_song(0, ok_notes, ok_durs, 1);

    /* Song 1: error beep (E5 -> C4, both quick) */
    static const uint8_t err_notes[] = { NOTE_E5, NOTE_C4 };
    static const uint8_t err_durs[]  = { 16, 16 };

    sound_load_song(1, err_notes, err_durs, 2);

    /* Song 2: EXIT cue – high, staccato A5–E6–A5 */
    static const uint8_t exit_notes[] = { 81, 88, 81 };       // A5, E6, A5-ish
    static const uint8_t exit_durs[]  = { 16, 16, 32 };       // pretty quick

    sound_load_song(2, exit_notes, exit_durs, 3);

    /* Song 3: "end of mission" – slow descending line */
    // G4–F4–Eb4–D4–C4–Bb3–G3 (approximate MIDI note numbers)
    static const uint8_t soldier_notes[] =
        { 67, 65, 63, 62, 60, 58, 55 };
    static const uint8_t soldier_durs[]  =
        { 48, 48, 48, 48, 64, 32, 96 };      // durations in 1/64 s

    sound_load_song(3, soldier_notes, soldier_durs, 7);

    /* Song 4: "SOLDIER FOUND" alarm – ascending C major arpeggio
     * Pattern: C4-E4-G4-C5 (bright, attention-grabbing)
     * Distinguishable from other sounds by ascending pattern
     */  
    static const uint8_t soldier_found_notes[] = {NOTE_C4, NOTE_E4, NOTE_G4, NOTE_C5};
    static const uint8_t soldier_found_durs[] = {16, 16, 16, 32}; // Each note duration

    sound_load_song(4, soldier_found_notes, soldier_found_durs, 4);
}

void sound_play_ok(void)
{
    sound_play_song(0);
}

void sound_play_error(void)
{
    sound_play_song(1);
}

/* --- Short, clearly different EXIT sound --- */
void sound_play_exit(void)
{
    sound_play_song(2);
}

/* --- Slow "end of mission" theme --- */
void sound_play_end_mission(void)
{
    sound_play_song(3);
}

/* --- Alias for backwards compatibility --- */
void sound_play_soldier_down(void)
{
    sound_play_end_mission();
}

/* --- short "SOLDIER FOUND" alarm (3-tone cue) --- */
void sound_play_soldier_found(void)
{
    sound_play_song(4);
}

/* ------------ minimal implementations of the "fancy" helpers ------------ */
/* These are mostly unused by ProtoCue, but we keep small, safe versions so
 * that any calls from other code will still link and simply do nothing or
 * return 0 on error.
 */

int sound_parse_and_load(uint8_t songNum, const char* songData)
{
    /* Very small parser: expect "NOTE:%d;DUR:%d". If format is bad, return 0. */
    int note = 0;
    int dur  = 0;

    if (!songData) return 0;
    if (sscanf(songData, "NOTE:%d;DUR:%d", &note, &dur) != 2) {
        return 0;
    }
    if (note < 31 || note > 127) return 0;
    if (dur <= 0 || dur > 255) return 0;
    if (songNum >= ROOMBA_MAX_SONGS) return 0;

    {
        uint8_t n[1];
        uint8_t d[1];
        n[0] = (uint8_t)note;
        d[0] = (uint8_t)dur;
        sound_load_song(songNum, n, d, 1);
    }

    return 1;
}

void sound_get_status(char* status)
{
    int i;
    if (!status) return;

    /* Report first four slots (0–3) as a simple string of 0/1. */
    for (i = 0; i < 4 && i < ROOMBA_MAX_SONGS; i++) {
        status[i] = (loaded_songs[i] ? '1' : '0');
    }
    status[4] = '\0';
}

void sound_clear_song(uint8_t songNum)
{
    if (songNum >= ROOMBA_MAX_SONGS) return;

    loaded_songs[songNum] = 0;

    /* Loading a 0-length song is the usual way to clear a slot.
     * If the OI ignores it, it's still harmless.
     */
    oi_loadSong(songNum, 0, NULL, NULL);
}

/* Clear only higher-numbered "custom" songs.
 * We keep 0–4 reserved for OK/error/exit/end-mission/soldier-found.
 */
void sound_clear_all_custom_songs(void)
{
    uint8_t i;
    for (i = 5; i < ROOMBA_MAX_SONGS; i++) {   // start at 5, keep 0–4
        sound_clear_song(i);
    }
}

int sound_load_custom_song(uint8_t songNumber,
                           const char* noteData,
                           const char* durData,
                           uint8_t length)
{
    /* Minimal implementation: only support a single-note "custom" song.
     * Good enough to keep the project linking.
     */
    int note = 0;
    int dur  = 0;

    if (!noteData || !durData) return 0;
    if (length == 0) return 0;
    if (songNumber >= ROOMBA_MAX_SONGS) return 0;

    note = atoi(noteData);
    dur  = atoi(durData);

    if (note < 31 || note > 127) return 0;
    if (dur <= 0 || dur > 255) return 0;

    {
        uint8_t n[1];
        uint8_t d[1];
        n[0] = (uint8_t)note;
        d[0] = (uint8_t)dur;
        sound_load_song(songNumber, n, d, 1);
    }

    return 1;
}
