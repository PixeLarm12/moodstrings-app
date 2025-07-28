import pretty_midi
from music21 import chord, pitch
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
        chords = []

        # general_midi_guitar_names = {
        #     24: "Acoustic Guitar (nylon)",
        #     25: "Acoustic Guitar (steel)",
        #     26: "Electric Guitar (jazz)",
        #     27: "Electric Guitar (clean)",
        #     28: "Electric Guitar (muted)",
        #     29: "Overdriven Guitar",
        #     30: "Distortion Guitar",
        #     31: "Guitar Harmonics"
        # }

        for instrument in self._midi_data.instruments:
            if not instrument.is_drum and 24 <= instrument.program <= 31:
                notes_by_time = {}

                for note in instrument.notes:
                    notes_by_time.setdefault(note.start, []).append(note.pitch)

                previous_chord = None
                for time in sorted(notes_by_time.keys()):
                    pitches = notes_by_time[time]
                    if len(pitches) >= chord_threshold:
                        chord = '+'.join(sorted(pretty_midi.note_number_to_name(p) for p in pitches))
                        if chord != previous_chord:
                            chords.append(chord)
                            previous_chord = chord
        
        return ' - '.join(chords)

    def convert_progression_to_chord_names(self, progression_str):
        named_chords = []

        for raw_chord in progression_str.split(" - "):
            note_names = raw_chord.split("+")
            try:
                simplified = [n[:-1] if n[-1].isdigit() else n for n in note_names]

                midi_pitches = [pitch.Pitch(n) for n in simplified]
                c = chord.Chord(midi_pitches)
                named_chords.append(c.figure)
            except Exception:
                named_chords.append(raw_chord)

        return ' - '.join(named_chords)
    
    def notes_to_chord_name(self, pitches: list[int]):
        if not pitches or len(pitches) < 2:
            return ""

        try:
            normalized_pitches = []
            for p in pitches:
                p_name = pretty_midi.note_number_to_name(p)[:-1]  
                # normalized_p = pitch.Pitch(p_name + '4')
                # normalized_pitches.append(normalized_p)
                normalized_pitches.append(p_name)

            c = chord.Chord(normalized_pitches)
            return c.root()
        except Exception:
            return '+'.join([pretty_midi.note_number_to_name(p) for p in pitches])
        
    def extract_named_progression(self, chord_threshold=3) -> str:
        named_chords = []

        for instrument in self._midi_data.instruments:
            if not instrument.is_drum and 24 <= instrument.program <= 31:
                notes_by_time = {}
                for note in instrument.notes:
                    notes_by_time.setdefault(note.start, []).append(note.pitch)

                prev = None
                for time in sorted(notes_by_time):
                    pitches = notes_by_time[time]
                    if len(pitches) >= chord_threshold:
                        pitch = self.notes_to_chord_name(pitches)
                        if pitch and pitch != prev:
                            named_chords.append(pitch.name)
                            prev = pitch.name

        return " - ".join(named_chords)