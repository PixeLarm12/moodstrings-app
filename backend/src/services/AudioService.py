import io
import os
import tempfile
from pathlib import Path
from pydub import AudioSegment
from basic_pitch.inference import predict
import soundfile as sf
import noisereduce as nr
import librosa
from music21 import stream, chord, note, tempo, midi, harmony

class AudioService:
    TMP_DIR = Path("/app/tmp_audio")
    TMP_DIR.mkdir(exist_ok=True)

    def __init__(self, uploaded_file=None, is_recorded=False):
        self.uploaded_file = uploaded_file
        self.is_recorded = is_recorded
        self._midi_data = None
        self._wav_path = None

    def get_midi_data(self):
        return self._midi_data

    def set_midi_data(self, midi_data):
        self._midi_data = midi_data

    def get_wav_path(self):
        return self._wav_path

    def set_wav_path(self, wav_path):
        self._wav_path = wav_path

    def prepare_wav_file(self):
        filename = self.uploaded_file.filename
        ext = Path(filename).suffix.lower()

        if self.is_recorded:
            input_format = "webm"
        else:
            input_format = ext.replace(".", "") or "mp3"  # mp3 or original ext

        tmp_input = self.TMP_DIR / f"{next(tempfile._get_candidate_names())}.{input_format}"

        self.uploaded_file.file.seek(0)
        with open(tmp_input, "wb") as f:
            f.write(self.uploaded_file.file.read())

        tmp_wav = self.TMP_DIR / f"{next(tempfile._get_candidate_names())}.wav"

        try:
            audio = AudioSegment.from_file(tmp_input, format=input_format)
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(tmp_wav, format="wav")
        except Exception as e:
            raise RuntimeError(f"Failed to convert {input_format} to WAV: {e}")

        tmp_input.unlink(missing_ok=True)
        self.set_wav_path(str(tmp_wav))
        return str(tmp_wav)


    def apply_filters(self):
        samples, sr = sf.read(self.get_wav_path(), dtype='float32')
        samples = nr.reduce_noise(y=samples, sr=sr, prop_decrease=0.7)
        sf.write(self.get_wav_path(), samples, sr)

    def create_midi_file(self):
        self.prepare_wav_file()  # mp3 -> wav
        self.apply_filters()      # denoise
        self.pitch_shift_wav(n_steps=12)  # shift 1 octave up

        _, midi_data, _ = predict(self.get_wav_path())
        self.set_midi_data(midi_data)

        return self.get_midi_data()
    
    def create_midi_file_from_progression(self, chord_progression: str, bpm: int = 90, duration: float = 1.0):
        if not chord_progression or not isinstance(chord_progression, str):
            raise ValueError("Chord progression must be a non-empty string.")
        
        chords_list = [
            ch.strip().replace('"', '')
            for ch in chord_progression.split("-")
        ]

        

        if not chords_list:
            raise ValueError("Chord progression must contain at least one chord.")

        s = stream.Stream()
        s.append(tempo.MetronomeMark(number=bpm))

        for raw_chord in chords_list:
            try: 
                if raw_chord.find("b") != -1:
                    raw_chord = raw_chord.replace('b', '-') # music21 bemol is 'flat'
                elif raw_chord.find("♭") != -1:
                    raw_chord = raw_chord.replace('♭', '-') # music21 bemol is 'flat'
                
                ch = harmony.ChordSymbol(raw_chord)
                c = chord.Chord(ch.pitches) # just to create Chord object separated

            except Exception:
                
                c = note.Note(raw_chord)

            c.duration.quarterLength = duration
            s.append(c)

        midi_io = io.BytesIO()
        mf = midi.translate.streamToMidiFile(s)
        mf.open('/tmp/temp.mid', 'wb')
        mf.write()
        mf.close()

        with open('/tmp/temp.mid', 'rb') as f:
            midi_io.write(f.read())
        midi_io.seek(0)

        self.set_midi_data(midi_io)
        return midi_io

    def pitch_shift_wav(self, n_steps=12):
        wav_path = self.get_wav_path()
        samples, sr = librosa.load(wav_path, sr=None)
        shifted = librosa.effects.pitch_shift(y=samples, sr=sr, n_steps=n_steps)
        sf.write(wav_path, shifted, sr)

    def adjust_bpm(self):
        if not self._wav_tmp_file:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                self._wav_tmp_file = tmp_wav.name
                self._midi_data.write(tmp_wav.name)

        samples, sr = sf.read(self._wav_tmp_file, dtype='float32')

        onset_env = librosa.onset.onset_strength(y=samples, sr=sr)
        tempo_est = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
        self._estimated_bpm = float(tempo_est[0]) if len(tempo_est) > 0 else 120.0

    def cleanup(self):
        try:
            if self._wav_path and os.path.exists(self._wav_path):
                import gc
                gc.collect()  # force release of lingering references
                os.remove(self._wav_path)
                print(f"Deleted temporary WAV file: {self._wav_path}")
        except PermissionError:
            print("File still in use, retrying cleanup...")


