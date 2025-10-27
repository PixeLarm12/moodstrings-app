import tempfile
from io import BytesIO
from src.utils.StringUtil import simplify_chord_name, sanitize_chord_name
import pretty_midi
from music21 import chord, converter, tempo, analysis, harmony, scale
import soundfile as sf
import librosa
from src.utils.StringUtil import simplify_chord_name, sanitize_chord_name, get_chord_note_names
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
                rel_minor = scale.MinorScale(tonic.transpose(-3))
                relatives["relative_minor"] = str(rel_minor.tonic.name + " minor")
            elif mode == "minor":
                rel_major = scale.MajorScale(tonic.transpose(3))
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

    def build_chord_timeline(self, bucket_size: float = 0.25) -> list[str]:
        """
        Build a chronological list of chord names detected in the MIDI file.
        Returns a list like ['C:maj', 'G:maj', 'Am', 'F:maj', ...]
        """
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

                    # 🧹 Normalize Unicode accidentals
                    normalized = [n.replace("♯", "#").replace("♭", "b") for n in note_names]

                    objChord = chord.Chord(normalized)
                    sc = sanitize_chord_name(simplify_chord_name(objChord.pitchedCommonName), 'tab')

                    if sc and sc != prev_chord:
                        timeline.append(sc)
                        prev_chord = sc

        return timeline

    def detect_repeated_chords(self, timeline: list[str]) -> list[tuple[int, str]]:
        """
        Detect repeated consecutive chords in a given timeline.
        Returns a list of tuples like [(index, chord_name), ...]
        """
        repeats = []
        for i in range(1, len(timeline)):
            if timeline[i] == timeline[i - 1]:
                repeats.append((i - 1, timeline[i]))
        return repeats


    def detect_progressions(self, timeline: list[str]) -> list[list[str]]:
        """
        Detect known common progressions like I–IV–V–I or C–G–Am–F.
        Returns a list of matching chord sequences.
        """
        known_patterns = [
            ["C", "G", "Am", "F"],
            ["G", "D", "Em", "C"],
            ["D", "G", "A"],
            ["I", "IV", "V", "I"],
            ["ii", "V", "I"]
        ]

        matches = []
        for pat in known_patterns:
            for i in range(len(timeline) - len(pat) + 1):
                if timeline[i:i + len(pat)] == pat:
                    matches.append(pat)
        return matches

    def enrich_timeline(self, timeline: list[str]) -> list[dict]:
        enriched = []

        for chord_name in timeline:
            try:
                if chord_name != "[No Name]":
                    objChord = chord.Chord(chord_name)

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

