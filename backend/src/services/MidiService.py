import tempfile
from io import BytesIO
import pretty_midi
from pretty_midi import PrettyMIDI
from music21 import chord as m21Chord, converter as m21Converter, key as m21Key, harmony as m21Harmony, pitch as m21Pitch
import soundfile as sf
import librosa
from src.utils.StringUtil import sanitize_chord_name, simplify_chord_name
import os
from src.enums import MusicEnum
from collections import Counter
from typing import Dict, Any

class MidiService:
    def __init__(self, file=None, midi_data=None, wav_path=None):
        if midi_data:
            if isinstance(midi_data, PrettyMIDI):
                self._midi_data = midi_data
            elif isinstance(midi_data, BytesIO):
                midi_data.seek(0)
                self._midi_data = PrettyMIDI(midi_data)
            elif isinstance(midi_data, (bytes, bytearray)):
                self._midi_data = PrettyMIDI(BytesIO(midi_data))
            else:
                raise TypeError("midi_data must be PrettyMIDI, BytesIO, or bytes")
        elif file:
            self._midi_data = PrettyMIDI(BytesIO(file.file.read()))
        else:
            raise ValueError("You must provide either a file or midi_data.")

        self._wav_tmp_file = wav_path
        self.adjust_bpm()
        self._tone_info = self.find_estimate_key()
        self._global_root_note = None

    @property
    def midi_data(self):
        return self._midi_data

    @midi_data.setter
    def midi_data(self, value):
        self._midi_data = pretty_midi.PrettyMIDI(BytesIO(value.file.read()))

    import numpy as np

    def adjust_bpm(self):
        """Estimativa de BPM a partir do MIDI ou WAV"""
        if not self._wav_tmp_file or not os.path.exists(self._wav_tmp_file):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                self._wav_tmp_file = tmp_wav.name
                try:
                    audio = self._midi_data.fluidsynth()
                    sf.write(tmp_wav.name, audio, 44100, subtype='PCM_16')
                except Exception as e:
                    print(f"[WARN] Could not synthesize MIDI: {e}")
                    self._estimated_bpm = 120.0
                    return

        try:
            samples, sr = sf.read(self._wav_tmp_file, dtype='float32')
            onset_env = librosa.onset.onset_strength(y=samples, sr=sr)
            tempo_est = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
            self._estimated_bpm = float(tempo_est[0]) if len(tempo_est) > 0 else 120.0
        except Exception as e:
            print(f"[WARN] Could not estimate BPM: {e}")
            self._estimated_bpm = 120.0


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

    def correct_key_with_first_event(
        self,
        detected_key: Dict[str, Any],
        progression: Dict[str, Any]
    ) -> Dict[str, Any]:

        detected_tonic = detected_key["tonic"]
        detected_mode = detected_key["mode"]

        first_event = None
        if progression.get("chords") and len(progression["chords"]) > 0:
            first_event = progression["chords"][0]["chord"]
        elif progression.get("notes") and len(progression["notes"]) > 0:
            first_event = progression["notes"][0]

        if not first_event:
            corrected_key = f"{corrected_tonic}{'' if corrected_mode == 'major' else 'm'}"

            return {
                "tonic": f"{sanitize_chord_name(str(corrected_tonic), 'tab')} ({sanitize_chord_name(str(corrected_tonic))})",
                "key": f"{sanitize_chord_name(str(corrected_key), 'tab')} ({sanitize_chord_name(str(corrected_key))})"
            }

        first_root = self._global_root_note

        relative = (
            MusicEnum.Scales.RELATIVE_KEYS.value.get(detected_tonic) 
            or MusicEnum.Scales.RELATIVE_KEYS_INV.value.get(detected_tonic)
        )

        if first_root == detected_tonic:
            corrected_key = f"{corrected_tonic}{'' if corrected_mode == 'major' else 'm'}"

            return {
                "tonic": f"{sanitize_chord_name(str(corrected_tonic), 'tab')} ({sanitize_chord_name(str(corrected_tonic))})",
                "key": f"{sanitize_chord_name(str(corrected_key), 'tab')} ({sanitize_chord_name(str(corrected_key))})"
            }

        if relative == first_root:
            corrected_tonic = first_root
            corrected_mode = "major" if detected_mode == "minor" else "minor"
            corrected_key = f"{corrected_tonic}{'' if corrected_mode == 'major' else 'm'}"

            return {
                "tonic": f"{sanitize_chord_name(str(corrected_tonic), 'tab')} ({sanitize_chord_name(str(corrected_tonic))})",
                "key": f"{sanitize_chord_name(str(corrected_key), 'tab')} ({sanitize_chord_name(str(corrected_key))})"
            }

        inferred_mode = "minor" if "m" in first_event and "maj" not in first_event else "major"

        corrected_tonic = first_root
        corrected_mode = inferred_mode
        corrected_key = f"{corrected_tonic}{'' if corrected_mode == 'major' else 'm'}"
        return {
                "tonic": f"{sanitize_chord_name(str(corrected_tonic), 'tab')} ({sanitize_chord_name(str(corrected_tonic))})",
                "key": f"{sanitize_chord_name(str(corrected_key), 'tab')} ({sanitize_chord_name(str(corrected_key))})"
            }


    def find_estimate_key(self):
        midi_file = self.create_midi_converter()
        objKey = midi_file.analyze("key")

        if objKey.mode is "major":
            key = objKey[:-1]
        elif objKey.mode is "minor":
            key = objKey[:-1] = "m"
        else:
            key = objKey

        return {
            "key": str(objKey),
            "tonic": str(objKey.tonic),
            "mode": str(objKey.mode),
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
    
    def export_musicxml(self):
        midi_score = self.create_midi_converter()

        with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False, mode="w", encoding="utf-8") as tmp_xml:
            midi_score.write('musicxml', fp=tmp_xml.name)

        # Read the content back to memory
        with open(tmp_xml.name, "r", encoding="utf-8") as f:
            xml_content = f.read()

        return xml_content

    def extract_note_sequence(self, bucket_size: float = 0.05, min_gap: float = 0.01, valid_range=("E2", "E6"), min_duration: float = 0.05) -> list[str]:
        low_pitch = m21Pitch.Pitch(valid_range[0]).midi
        high_pitch = m21Pitch.Pitch(valid_range[1]).midi

        sequence = []
        last_time = -1
        last_note = None

        for instrument in self._midi_data.instruments:
            if instrument.is_drum:
                continue

            notes_sorted = sorted(instrument.notes, key=lambda n: n.start)

            for note in notes_sorted:
                note_name = librosa.midi_to_note(note.pitch).replace("♯", "#").replace("♭", "b")

                # Filter by pitch range
                try:
                    midi_num = m21Pitch.Pitch(note_name).midi
                    if not (low_pitch <= midi_num <= high_pitch):
                        continue
                except Exception:
                    continue

                # Filter very short notes
                duration = note.end - note.start
                if duration < min_duration:
                    continue

                # Preserve double/triple notes, only skip duplicates with almost zero gap
                if last_note == note_name and (note.start - last_time) < 0.005:
                    continue

                sequence.append(note_name[:-1]) # remove last char (number, for example C5)
                last_note = note_name
                last_time = note.start

        return sequence

    def extract_notes_and_chords(self) -> dict:
        chords = self.extract_chord_progression()
        notes = self.extract_note_sequence()

        # Resolve global root note
        if chords:
            try:
                # first chord's root is good heuristic
                first_root = chords[0].get("notes", [])
                if first_root:
                    # get actual root via music21 chord
                    chord_obj = m21Chord.Chord(first_root)
                    self._global_root_note = chord_obj.root().name
            except Exception:
                self._global_root_note = None
        else:
            # fallback to note mode estimation
            self._global_root_note = self._infer_root_from_notes(notes)

        return {
            "root_note": self._global_root_note,
            "notes": notes,
            "chords": chords
        }

    
    def _infer_root_from_notes(self, notes: list[str]) -> str:
        if not notes:
            return None

        pitch_classes = []
        for n in notes:
            try:
                p = m21Pitch.Pitch(n)
                pitch_classes.append(p.pitchClass)
            except Exception:
                continue

        if not pitch_classes:
            return None

        most_common = Counter(pitch_classes).most_common(1)[0][0]
        
        return m21Pitch.Pitch(midi=most_common).name