import pretty_midi
from io import BytesIO

class MidiService:
    def __init__(self, file):
        self._midi_data = pretty_midi.PrettyMIDI(BytesIO(file.file.read()))

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