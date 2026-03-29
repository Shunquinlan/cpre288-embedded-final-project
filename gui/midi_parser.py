"""MIDI parsing utilities for CyBot GUI

Provides parse_midi_file() for binary .mid/.midi and parse_midi_text_file()
for the simple text format used previously.

Requires `mido` for binary MIDI parsing.
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Tuple

try:
    from mido import MidiFile
except Exception:
    MidiFile = None  # mido not available — parse_midi_file will return []

NoteDurList = List[Tuple[int, int]]  # (midi_note, roomba_duration_units)


def parse_midi_file(path: str | Path, max_notes: int = 16) -> NoteDurList:
    """
    Parse a binary .mid/.midi file into a list of (note, duration_units)
    suitable for Roomba:
      - notes: 31..127 (MIDI)
      - duration_units: 1..255, where 1 unit = 1/64 second
      - max max_notes notes
    """
    path = Path(path)
    if MidiFile is None:
        # mido not installed — cannot parse binary MIDI
        return []

    mid = MidiFile(path)

    # Pick the track with the most note_on events as the "melody" track
    def note_on_count(track):
        return sum(1 for m in track if getattr(m, 'type', None) == 'note_on' and getattr(m, 'velocity', 0) > 0)

    track = max(mid.tracks, key=note_on_count, default=None)
    if track is None:
        return []

    ticks_per_beat = mid.ticks_per_beat
    tempo = 500_000  # default 120 BPM (microseconds per beat)

    current_ticks = 0
    active_notes = {}  # note -> start_time_in_ticks
    collected = []  # (note, start, end)

    for msg in track:
        current_ticks += getattr(msg, 'time', 0)

        if getattr(msg, 'type', None) == 'set_tempo':
            # some mido messages expose tempo on .tempo
            tempo = getattr(msg, 'tempo', tempo)

        elif getattr(msg, 'type', None) == 'note_on' and getattr(msg, 'velocity', 0) > 0:
            if getattr(msg, 'note', None) is not None and msg.note not in active_notes:
                active_notes[msg.note] = current_ticks

        elif getattr(msg, 'type', None) == 'note_off' or (getattr(msg, 'type', None) == 'note_on' and getattr(msg, 'velocity', 0) == 0):
            note = getattr(msg, 'note', None)
            if note is None:
                continue
            start = active_notes.pop(note, None)
            if start is not None and current_ticks > start:
                collected.append((note, start, current_ticks))

    # Sort by start time
    collected.sort(key=lambda x: x[1])

    result: NoteDurList = []

    for note, start, end in collected:
        if len(result) >= max_notes:
            break

        # Clamp note to Roomba range 31..127
        if note < 31 or note > 127:
            continue

        duration_ticks = end - start
        if duration_ticks <= 0:
            continue

        # Convert ticks -> seconds:
        seconds = duration_ticks * tempo / 1_000_000.0 / ticks_per_beat

        # Convert seconds -> Roomba duration units (1/64 s)
        units = round(seconds * 64.0)
        if units < 1:
            units = 1
        if units > 255:
            units = 255

        result.append((note, units))

    return result


def parse_midi_text_file(path: str | Path) -> NoteDurList:
    """
    Simple text parser for lines like:
      60,16
      62,8
      64,16

    Returns list of (note, duration_units).
    """
    path = Path(path)
    notes: NoteDurList = []
    if not path.exists():
        return notes

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        try:
            if ',' in line:
                n_str, d_str = line.split(',', 1)
            else:
                n_str, d_str = line.split(None, 1)
            note = int(n_str.strip())
            dur = int(d_str.strip())
        except Exception:
            continue

        if 31 <= note <= 127 and 1 <= dur <= 255:
            notes.append((note, dur))

    return notes
