import pretty_midi
from fastapi import UploadFile
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

    def get_instruments_name(self):
        instruments = []

        for item in self._midi_data.instruments:
            instruments.append({
                "name": item.name,
                "program": int(item.program),
                "isDrum": bool(item.is_drum),
            })

        return instruments
    
    def extract_chords_by_guitar_type(self, chord_threshold=3):
        general_midi_guitar_names = {
            24: "Acoustic Guitar (nylon)",
            25: "Acoustic Guitar (steel)",
            26: "Electric Guitar (jazz)",
            27: "Electric Guitar (clean)",
            28: "Electric Guitar (muted)",
            29: "Overdriven Guitar",
            30: "Distortion Guitar",
            31: "Guitar Harmonics"
        }

        result = []

        for instrument in self._midi_data.instruments:
            if not instrument.is_drum and 24 <= instrument.program <= 31:
                program = instrument.program
                notes_by_time = {}

                for note in instrument.notes:
                    if note.start not in notes_by_time:
                        notes_by_time[note.start] = []
                    notes_by_time[note.start].append(note.pitch)

                unique_chords = set()

                for time, pitches in notes_by_time.items():
                    if len(pitches) >= chord_threshold:
                        chord = tuple(sorted(pretty_midi.note_number_to_name(p) for p in pitches))
                        unique_chords.add(chord)

                if unique_chords:
                    result.append({
                        "program": f"{program}",
                        "title": general_midi_guitar_names.get(program, f"Program {program}"),
                        "chords": [list(chord) for chord in sorted(unique_chords)]
                    })

        return result


