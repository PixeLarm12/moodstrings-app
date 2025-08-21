import pretty_midi
from music21 import chord, pitch
from src.utils.StringUtil import normalize_chord_name
from io import BytesIO

class MidiService:
    def __init__(self, file=None, midi_data=None):
        if midi_data:
            self._midi_data = midi_data
        elif file:
            self._midi_data = pretty_midi.PrettyMIDI(BytesIO(file.file.read()))
        else:
            raise ValueError("You must provide either a file or midi_data.")

    @property
    def midi_data(self):
        return self._midi_data

    @midi_data.setter
    def midi_data(self, value):
        self._midi_data = pretty_midi.PrettyMIDI(BytesIO(value.file.read()))

    def extract_chords(self, chord_threshold=3):
        raw_chords = []
        named_chords = [];

        for instrument in self._midi_data.instruments:
            if not instrument.is_drum and 24 <= instrument.program <= 31:
                notes_by_time = {}

                for note in instrument.notes:
                    notes_by_time.setdefault(note.start, []).append(note.pitch)

                previous_chord = None
                for time in sorted(notes_by_time.keys()):
                    pitches = notes_by_time[time]
                    if len(pitches) >= chord_threshold:
                        item = '+'.join(sorted(pretty_midi.note_number_to_name(p) for p in pitches))
                        if item != previous_chord:
                            raw_chords.append(item)

        for raw in raw_chords:
            note_names = raw.split("+")
            objChord = chord.Chord(note_names)
            named_chords.append(normalize_chord_name(objChord.pitchedCommonName))

        return ' - '.join(named_chords)

    def notes_to_chord_name(self, pitches: list[int]):
        if not pitches or len(pitches) < 2:
            return ""

        try:
            normalized_pitches = []
            for p in pitches:
                p_name = pretty_midi.note_number_to_name(p)[:-1]  
                normalized_pitches.append(p_name)

            c = chord.Chord(normalized_pitches)
            return c.root()
        except Exception:
            return '+'.join([pretty_midi.note_number_to_name(p) for p in pitches])