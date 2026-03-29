#ifndef SOUND_H
#define SOUND_H

#include <stdint.h>

/**
 * Initialize Roomba sounds.
 * - Loads a simple "OK" beep as song 0.
 * - Loads a simple "error" sound as song 1.
 *
 * Call this AFTER you have:
 *  - Initialized UART to Roomba
 *  - Sent Start (128) and Safe/Full (131/132) commands.
 */
void sound_init(void);

/**
 * Load a song into Roomba.
 *
 * @param songNumber  Song ID (0–4).
 * @param notes       Pointer to array of note numbers (31–127).
 * @param durations   Pointer to array of durations (in 1/64 sec units).
 * @param length      Number of notes (1–16).
 */
void sound_load_song(uint8_t songNumber,
                     const uint8_t *notes,
                     const uint8_t *durations,
                     uint8_t length);

/**
 * Play a previously loaded song.
 *
 * @param songNumber Song ID (0–4).
 */
void sound_play_song(uint8_t songNumber);

/** Convenience: play the default “OK” beep (song 0). */
void sound_play_ok(void);

/** Convenience: play the default "error" beep (song 1). */
void sound_play_error(void);

/** Convenience: play a short "exit" cue sound. */
void sound_play_exit(void);

/** Convenience: play the "end of mission" slow theme. */
void sound_play_end_mission(void);

/** Convenience: play a short 3-tone "soldier found" alarm. */
void sound_play_soldier_found(void);

/** Alias for sound_play_end_mission (for backwards compatibility). */
void sound_play_soldier_down(void);

/**
 * Load a custom song from GUI-parsed MIDI data.
 * 
 * @param songNumber  Song slot (0-3, slot 4 reserved for system)
 * @param noteData    String containing note values separated by commas
 * @param durData     String containing duration values separated by commas  
 * @param length      Number of notes (1-16)
 * @return            1 if successful, 0 if error
 */
int sound_load_custom_song(uint8_t songNumber, const char* noteData, const char* durData, uint8_t length);

/**
 * Parse and load a song from a formatted string.
 * Format: "NOTES:60,62,64,65;DURS:16,16,16,32"
 * 
 * @param songNumber  Song slot (0-3)
 * @param songData    Formatted string with notes and durations
 * @return            1 if successful, 0 if error
 */
int sound_parse_and_load(uint8_t songNumber, const char* songData);

/**
 * Clear a song slot.
 * 
 * @param songNumber Song slot to clear (0-3)
 */
void sound_clear_song(uint8_t songNumber);

/**
 * Clear all custom song slots (5-7), keeping system songs (0-4) intact.
 */
void sound_clear_all_custom_songs(void);

/**
 * Get status of all song slots.
 * Returns a 4-character string where each character is '1' if loaded, '0' if empty.
 */
void sound_get_status(char* status);

/* Optional: some MIDI note defines to make code readable */
#define NOTE_C4   60
#define NOTE_D4   62
#define NOTE_E4   64
#define NOTE_F4   65
#define NOTE_G4   67
#define NOTE_A4   69
#define NOTE_B4   71
#define NOTE_C5   72
#define NOTE_E5   76

#ifdef __cplusplus

#endif

#endif /* SOUND_H */
