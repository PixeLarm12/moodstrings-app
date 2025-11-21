import tempfile
from io import BytesIO
import pretty_midi
from pretty_midi import PrettyMIDI
from music21 import chord as m21Chord, converter as m21Converter, key as m21Key, harmony as m21Harmony, pitch as m21Pitch, scale as m21Scale
import soundfile as sf
import librosa
from src.utils.StringUtil import sanitize_chord_name, simplify_chord_name, clean_pitched_common_name
import os
from src.enums import MusicEnum
from collections import Counter
from typing import Dict, Any
from collections import defaultdict

class MidiService:
    def __init__(self, file=None, midi_data=None, wav_path=None, bpm=None):
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
        if bpm:
            self._estimated_bpm = bpm
        else:
            self.adjust_bpm()
        self._tone_info = self.find_estimate_key()
        self._global_root_note = None
        self._scale = {
            "key": "",
            "chords": []
        }

    @property
    def midi_data(self):
        return self._midi_data

    @midi_data.setter
    def midi_data(self, value):
        self._midi_data = pretty_midi.PrettyMIDI(BytesIO(value.file.read()))

    def adjust_bpm(self):
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
        roman, name = MusicEnum.HarmonicFunctions.FUNCTIONS_EN.value[index]

        return f"{roman} ({name})"

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

        if not first_event:
            corrected_key = f"{detected_tonic}{'' if detected_mode == 'major' else 'm'}"

            return {
                "tonic": f"{sanitize_chord_name(str(detected_tonic), 'tab')} ({sanitize_chord_name(str(detected_tonic))})",
                "key": f"{sanitize_chord_name(str(corrected_key), 'tab')} ({sanitize_chord_name(str(corrected_key))})",
                "mode": detected_mode
            }

        first_root = self._global_root_note

        relative = (
            MusicEnum.Scales.RELATIVE_KEYS.value.get(detected_tonic) 
            or MusicEnum.Scales.RELATIVE_KEYS_INV.value.get(detected_tonic)
        )

        if first_root == detected_tonic:
            corrected_key = f"{detected_tonic}{'' if detected_mode == 'major' else 'm'}"

            return {
                "tonic": f"{sanitize_chord_name(str(detected_tonic), 'tab')} ({sanitize_chord_name(str(detected_tonic))})",
                "key": f"{sanitize_chord_name(str(corrected_key), 'tab')} ({sanitize_chord_name(str(corrected_key))})",
                "mode": detected_mode
            }

        if relative == first_root:
            corrected_tonic = first_root
            corrected_mode = "major" if detected_mode == "minor" else "minor"
            corrected_key = f"{corrected_tonic}{'' if corrected_mode == 'major' else 'm'}"

            return {
                "tonic": f"{sanitize_chord_name(str(corrected_tonic), 'tab')} ({sanitize_chord_name(str(corrected_tonic))})",
                "key": f"{sanitize_chord_name(str(corrected_key), 'tab')} ({sanitize_chord_name(str(corrected_key))})",
                "mode": corrected_mode
            }

        inferred_mode = "minor" if "m" in first_event and "maj" not in first_event else "major"

        corrected_tonic = first_root
        corrected_mode = inferred_mode
        corrected_key = f"{corrected_tonic}{'' if corrected_mode == 'major' else 'm'}"
        return {
                "tonic": f"{sanitize_chord_name(str(corrected_tonic), 'tab')} ({sanitize_chord_name(str(corrected_tonic))})",
                "key": f"{sanitize_chord_name(str(corrected_key), 'tab')} ({sanitize_chord_name(str(corrected_key))})",
                "mode": corrected_mode
            }


    def find_estimate_key(self, objKey = None):
        if not objKey:
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
    
    def find_scale(self, key_info, progression):
        self._scale = {
            "key": "",
            "mode": "",
            "tonic": "",
            "chords": [],
            "exists": False
        }

        tonic = key_info["tonic"].split(" ")[0]
        mode = key_info.get("mode").lower()

        raw_chords = [
            ch.strip().replace('"', '')
            for ch in progression.replace("–", "-").replace("—", "-").split("-")
        ]

        # extract only root notes - deriveAll uses notes, not chords. So, some cases that have Am, should be A, for example
        chords_list = [self.extract_root(ch) for ch in raw_chords if ch]

        major_scale = m21Scale.MajorScale()
        minor_scale = m21Scale.MinorScale()

        derived_minors = minor_scale.deriveAll(chords_list)
        derived_majors = major_scale.deriveAll(chords_list)

        actual_scale = None
        for maj in derived_majors:
            if tonic == maj.getTonic().name:
                actual_scale = maj
                mode = "major"
                tonic = maj.getTonic().name.replace("-", "b")
                self._tone_info = self.find_estimate_key(objKey=m21Key.Key(tonic, mode))

        for min in derived_minors:
            if tonic == min.getTonic().name:
                actual_scale = min
                mode = "minor"
                tonic = min.getTonic().name.replace("-", "b")
                self._tone_info = self.find_estimate_key(objKey=m21Key.Key(tonic, mode))


        if actual_scale != None:
            harmonic_chords = []
            for i, pitch in enumerate(actual_scale.pitches):
                chord_name = pitch.name.replace("-", "b")
                name = sanitize_chord_name(chord_name.replace("-", "b"))
                function = actual_scale.getScaleDegreeFromPitch(pitch.name)
                function_roman = MusicEnum.HarmonicFunctions.FUNCTIONS_EN.value[function-1]

                harmonic_chords.append({
                    "function": function_roman,
                    "chord": chord_name,
                    "name": name
                })

            key_name = sanitize_chord_name(actual_scale.name.replace("-", "b"), 'tab')
            key_full_name = sanitize_chord_name(actual_scale.name.replace("-", "b"))

            key = f"{key_name} ({key_full_name})"

            self._scale = {
                "key": key,
                "mode": mode,
                "tonic": tonic,
                "chords": harmonic_chords,
                "exists": True
            }

        return self._scale

    def extract_root(self, ch_str: str) -> str:
        try:
            ch = m21Harmony.ChordSymbol(ch_str)
            root = ch.root().name
            return root.replace("-", "b")
        except Exception:
            return ch_str.replace("-", "b")


    def find_relative_scales(self):
        mode = self._scale["mode"]
        tonic = self._scale["tonic"]
        
        if mode == "major":
            selfScaleObj = m21Scale.MajorScale(m21Pitch.Pitch(self._scale["tonic"]))
            relative = selfScaleObj.getRelativeMinor()
            mode = "minor"
            tonic = relative.getTonic().name.replace("-", "b")
        else:
            selfScaleObj = m21Scale.MinorScale(m21Pitch.Pitch(self._scale["tonic"]))
            relative = selfScaleObj.getRelativeMajor()
            mode = "major"
            tonic = relative.getTonic().name.replace("-", "b")

        harmonic_chords = []
        for i, pitch in enumerate(relative.pitches):
            chord_name = pitch.name.replace("-", "b")
            name = sanitize_chord_name(chord_name.replace("-", "b"))
            function = relative.getScaleDegreeFromPitch(pitch.name)
            function_roman = MusicEnum.HarmonicFunctions.FUNCTIONS_EN.value[function-1]

            harmonic_chords.append({
                "function": function_roman,
                "chord": chord_name,
                "name": name
            })
            
        key_name = sanitize_chord_name(relative.name.replace("-", "b"), 'tab')
        key_full_name = sanitize_chord_name(relative.name.replace("-", "b"))

        key = f"{key_name} ({key_full_name})"

        return {
            "key": key,
            "chords": harmonic_chords,
            "mode": mode,
            "tonic": tonic
        }

    def extract_chord_progression(self, bucket_size: float = 0.18) -> list[dict]:
        chord_progression = []
        prev_chord = None

        MIN_VELOCITY = 35       # soft notes could be noise
        MIN_DURATION = 0.07

        for instrument in self.midi_data.instruments:
            if instrument.is_drum:
                continue
            
            notes_by_time = {}

            for note in instrument.notes:
                duration = note.end - note.start
                if note.velocity < MIN_VELOCITY or duration < MIN_DURATION:
                    continue

                bucket = round(note.start / bucket_size) * bucket_size
                notes_by_time.setdefault(bucket, []).append(note.pitch)

            for time in sorted(notes_by_time.keys()):
                pitches = notes_by_time[time]

                # min 2 notes to create chord
                if len(pitches) >= 2:
                    note_names = [librosa.midi_to_note(p) for p in pitches]

                    normalized = [n.replace("♯", "#").replace("♭", "b") for n in note_names]

                    try:
                        objChord = m21Chord.Chord(normalized)
                    except Exception:
                        continue

                    # chord_name = sanitize_chord_name(simplify_chord_name(objChord.pitchedCommonName), 'tab')
                    chord_name = clean_pitched_common_name(objChord.pitchedCommonName)
                    
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

        return {
            "root_note": self._global_root_note,
            "chords": chords
        }
    
    def extract_chord_progression_forteclass(self, bucket_size: float = 0.18) -> str:
        chord_sequence = []
       
        MIN_VELOCITY = 35       # soft notes could be noise
        MIN_DURATION = 0.07

        for instrument in self.midi_data.instruments:
            if instrument.is_drum:
                continue
            # Group notes by start time bucket
            notes_by_time = {}
            for note in instrument.notes:
                duration = note.end - note.start
                if note.velocity < MIN_VELOCITY or duration < MIN_DURATION:
                    continue

                bucket = round(note.start / bucket_size) * bucket_size
                notes_by_time.setdefault(bucket, []).append(note.pitch)

            for t in sorted(notes_by_time.keys()):
                pitches = notes_by_time[t]

                note_names = [librosa.midi_to_note(p) for p in pitches]
                normalized = [n.replace("♯", "#").replace("♭", "b") for n in note_names]

                try:
                    objChord = m21Chord.Chord(normalized)
                except Exception:
                    continue

                chord_name = objChord.forteClassTn

                # Add root pitch class as prefix to distinguish repeated ForteClass in different keys
                # root_pc = objChord.root().pitchClass
                quality = objChord.quality
                chord_sequence.append(f"{chord_name}")

        # Join all chords with comma
        return ",".join(chord_sequence)