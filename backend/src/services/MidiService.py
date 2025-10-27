import tempfile
from io import BytesIO
import pretty_midi
from music21 import chord as m21Chord, converter as m21Converter, key as m21Key, harmony as m21Harmony
import soundfile as sf
import librosa
from src.utils.StringUtil import sanitize_chord_name, simplify_chord_name
import os
from src.enums import MusicEnum

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

        self._tone_info = self.find_estimate_key()

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

    def get_chord_function(self, root_note):
        try:
            tone = f"{self._tone_info['tonic']} {self._tone_info['mode']}"
            tonic, mode = tone.split()
        except Exception:
            return "Out of scale"

        scale_notes = (
            MusicEnum.Scales.MAJOR.value.get(tonic)
            if mode.lower() == "major"
            else MusicEnum.Scales.MINOR.value.get(tonic)
        )

        if not scale_notes:
            return "Out of scale"

        if root_note not in scale_notes:
            return "Out of scale"

        index = scale_notes.index(root_note)
        roman, name = MusicEnum.HarmonicFunctions.FUNCTIONS.value[index]

        return f"{roman} ({name})"

    def extract_chords_forteclass(self, chord_threshold=2):
        raw_chords = []
        forte_classes = []

        for instrument in self._midi_data.instruments:
            if instrument.is_drum:
                continue

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
                objChord = m21Chord.Chord(note_names)
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
            return m21Converter.parse(tmp_midi.name)

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
        detected_key: m21Key.Key = midi_file.analyze("key")

        self._tone_info = {
            "tonic": detected_key.tonic.name,
            "mode": detected_key.mode.lower()
        }

        tonic = self._tone_info["tonic"]
        mode = self._tone_info["mode"]

        scale_notes = (
            MusicEnum.Scales.MAJOR.value.get(tonic)
            if mode == "major"
            else MusicEnum.Scales.MINOR.value.get(tonic)
        )

        if not scale_notes:
            return {"error": "Scale not mapped in enum"}

        if mode == "major":
            triad_qualities = ["major", "minor", "minor", "major", "major", "minor", "diminished"]
        else:
            triad_qualities = ["minor", "diminished", "major", "minor", "minor", "major", "major"]

        harmonic_chords = []

        for i, root in enumerate(scale_notes):
            quality = triad_qualities[i]
            chord_name = f"{root} {quality}"
            chord_function = self.get_chord_function(root)

            harmonic_chords.append({
                "function": chord_function,
                "chord": chord_name
            })

        return {
            "key": f"{tonic} {mode}",
            "chords": harmonic_chords
        }


    def build_chord_timeline(self, bucket_size: float = 0.25) -> list[str]:
        timeline = []
        prev_chord = None

        for instrument in self.midi_data.instruments:
            if instrument.is_drum:
                continue

            notes_by_time = {}
            for note in instrument.notes:
                bucket = round(note.start / bucket_size) * bucket_size
                notes_by_time.setdefault(bucket, []).append(note.pitch)

            for time in sorted(notes_by_time.keys()):
                pitches = notes_by_time[time]
                if len(pitches) >= 2:
                    note_names = [librosa.midi_to_note(p) for p in pitches]
                    normalized = [n.replace("♯", "#").replace("♭", "b") for n in note_names]

                    objChord = m21Chord.Chord(normalized)

                    chord_ui = simplify_chord_name(objChord.pitchedCommonName) 

                    if chord_ui and chord_ui != prev_chord:
                        timeline.append(chord_ui)
                        prev_chord = chord_ui

        return timeline


    def enrich_timeline(self, timeline: list[str]) -> list[dict]:
        enriched = []

        for chord_name in timeline:
            try:
                if chord_name != "[No Name]":
                    objChord = m21Chord.Chord(chord_name)

                    note_names = [n.nameWithOctave[:-1] if len(n.nameWithOctave) > 1 else n.name for n in objChord.pitches]
                    unique_notes = list(dict.fromkeys(note_names))

                    root_note = objChord.root().name
                    function = self.get_chord_function(root_note)

                    sc = sanitize_chord_name(simplify_chord_name(objChord.pitchedCommonName), 'tab')

                    if sc != "[No Name]": 
                        enriched.append({
                            "chord": sc or chord_name,
                            "notes": unique_notes,
                            "function": function,
                        })
            except Exception as e:
                enriched.append({
                    "chord": chord_name,
                    "notes": [],
                    "function": "Unknown",
                    "error": str(e)
                })

        return enriched
        
    def extract_chord_progression(self, bucket_size: float = 0.25) -> list[dict]:
        chord_progression = []
        prev_chord = None

        for instrument in self.midi_data.instruments:
            if instrument.is_drum:
                continue

            notes_by_time = {}
            for note in instrument.notes:
                bucket = round(note.start / bucket_size) * bucket_size
                notes_by_time.setdefault(bucket, []).append(note.pitch)

            for time in sorted(notes_by_time.keys()):
                pitches = notes_by_time[time]
                if len(pitches) >= 2:
                    note_names = [librosa.midi_to_note(p) for p in pitches]
                    normalized = [n.replace("♯", "#").replace("♭", "b") for n in note_names]

                    try:
                        objChord = m21Chord.Chord(normalized)
                    except Exception:
                        continue 

                    chord_name = sanitize_chord_name(simplify_chord_name(objChord.pitchedCommonName), 'tab')
                    
                    if not chord_name or chord_name == "[No Name]" or chord_name == prev_chord:
                        continue
                    prev_chord = chord_name

                    chord_notes = [n.name for n in objChord.pitches]

                    try:
                        root_note = objChord.root().name
                        function = self.get_chord_function(root_note)
                    except Exception:
                        function = "Unknown"

                    chord_progression.append({
                        "chord": chord_name,
                        "name": sanitize_chord_name(chord_name),
                        "notes": chord_notes,
                        "function": function
                    })

        return chord_progression

