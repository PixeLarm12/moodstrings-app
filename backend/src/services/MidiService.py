import pretty_midi
import tempfile
from music21 import chord, converter, tempo
from src.utils.StringUtil import simplify_chord_name, sanitize_chord_name, get_chord_note_names
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

    def extract_chords(self, chord_threshold=2):
        raw_chords = []
        named_chords = [];

        for instrument in self._midi_data.instruments:
            if not instrument.is_drum:
                notes_by_time = {}

                bucket_size = 0.25
                for note in instrument.notes:
                    bucket = round(note.start / bucket_size) * bucket_size
                    notes_by_time.setdefault(bucket, []).append(note.pitch)

                previous_chord = None
                for time in sorted(notes_by_time.keys()):
                    pitches = notes_by_time[time]
                    if len(pitches) >= chord_threshold:
                        item = '+'.join(sorted(pretty_midi.note_number_to_name(p) for p in pitches))
                        if item != previous_chord:
                            raw_chords.append(item)

        prev = None
        for raw in raw_chords:
            note_names = raw.split("+")
            objChord = chord.Chord(note_names)
            # user isChord to check if is chord of isNote/isRest
            sc = simplify_chord_name(objChord.pitchedCommonName)
            if sc and sc != prev:
                named_chords.append(sc)
                prev = sc

        named_chords_dict = {}
        prev = None

        for raw in raw_chords:
            note_names = raw.split("+")
            objChord = chord.Chord(note_names)
            
            sc = sanitize_chord_name(simplify_chord_name(objChord.pitchedCommonName), 'tab')
            
            if sc and sc != prev:
                # sc = ChordName
                named_chords_dict[sc] = [
                    get_chord_note_names(list(dict.fromkeys(objChord.pitchNames))), # notes
                    # objChord.pitchedCommonName, # name
                    sanitize_chord_name(objChord.pitchedCommonName) # name
                ]
                prev = sc

        return named_chords_dict

    def create_midi_converter(self):
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp_midi:
            self._midi_data.write(tmp_midi.name)
            midi_path = tmp_midi.name

        return converter.parse(midi_path)

    def find_tempo(self):
        midi_file = self.create_midi_converter()

        tempos = midi_file.recurse().getElementsByClass(tempo.MetronomeMark)

        response = [];

        if tempos:
            for t in tempos:
                response.append(f"{ t.number } BPM");
        else:
            print("There's no expressive tempo mark into midi file.")

        return " - ".join(response)
    
    def find_estimate_key(self):
        midi_file = self.create_midi_converter()

        key = midi_file.analyze('key')

        return {
            'key': str(key),
            'mode': key.mode,
            'tonic': str(key.tonic),
        }

