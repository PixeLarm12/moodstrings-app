import tempfile
from io import BytesIO
import pretty_midi
from music21 import chord, converter, tempo, analysis, harmony, scale
import soundfile as sf
import librosa
from src.utils.StringUtil import simplify_chord_name, sanitize_chord_name, get_chord_note_names
import os

class MidiService:
    def __init__(self, file=None, midi_data=None, wav_path=None):
        if midi_data:
            self._midi_data = midi_data
        elif file:
            self._midi_data = pretty_midi.PrettyMIDI(BytesIO(file.file.read()))
        else:
            raise ValueError("You must provide either a file or midi_data.")

        self._wav_tmp_file = wav_path
        self.adjust_bpm()  

    @property
    def midi_data(self):
        return self._midi_data

    @midi_data.setter
    def midi_data(self, value):
        self._midi_data = pretty_midi.PrettyMIDI(BytesIO(value.file.read()))

    def adjust_bpm(self):
        """Estimativa de BPM a partir do MIDI"""
        if self._wav_tmp_file is None or not os.path.exists(self._wav_tmp_file):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                self._wav_tmp_file = tmp_wav.name
                self._midi_data.write(tmp_wav.name)

        samples, sr = sf.read(self._wav_tmp_file, dtype='float32')
        onset_env = librosa.onset.onset_strength(y=samples, sr=sr)
        tempo_est = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
        self._estimated_bpm = float(tempo_est[0]) if len(tempo_est) > 0 else 120.0


    def get_estimated_bpm(self):
        return getattr(self, "_estimated_bpm", 120.0)

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

    def extract_chords_forteclass(self, chord_threshold=2):
        raw_chords = []
        forte_classes = []

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
                            previous_chord = item

        prev_forte = None
        for raw in raw_chords:
            note_names = raw.split("+")
            try:
                objChord = chord.Chord(note_names)
                forte_class = objChord.forteClassTn
                
                if forte_class is not None and forte_class != prev_forte:
                    forte_classes.append(str(forte_class))
                    prev_forte = forte_class
            except Exception:
                continue

        return ' - '.join(forte_classes)

    def create_midi_converter(self):
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tmp_midi:
            self._midi_data.write(tmp_midi.name)
            return converter.parse(tmp_midi.name)

    def find_estimate_key(self):
        midi_file = self.create_midi_converter()
        key = midi_file.analyze("key")
        return {
            "key": str(key),
            "mode": key.mode,
            "tonic": str(key.tonic),
        }
    
    def find_tempo(self):
        return self.get_estimated_bpm()

    def find_relative_scales(self):
        midi_file = self.create_midi_converter()
        key = midi_file.analyze("key")

        tonic = key.tonic
        mode = key.mode.lower()

        relatives = {}

        try:
            if mode == "major":
                rel_minor = scale.MinorScale(tonic.transpose(-3))  # 3 semitons abaixo
                relatives["relative_minor"] = str(rel_minor.tonic.name + " minor")
            elif mode == "minor":
                rel_major = scale.MajorScale(tonic.transpose(3))  # 3 semitons acima
                relatives["relative_major"] = str(rel_major.tonic.name + " major")
        except Exception:
            pass

        try:
            major_scale = scale.MajorScale(tonic) if mode == "major" else scale.MajorScale(tonic.transpose(3))
            degrees = ["Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"]
            relatives["modes"] = []

            for i, deg in enumerate(degrees):
                new_tonic = major_scale.pitchFromDegree(i + 1)
                relatives["modes"].append(f"{new_tonic.name} {deg}")
        except Exception:
            pass

        return relatives


