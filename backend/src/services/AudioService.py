import io
import os
import tempfile
import subprocess
from pathlib import Path
from pydub import AudioSegment
from basic_pitch.inference import predict
import soundfile as sf
import noisereduce as nr
import librosa

class AudioService:
    TMP_DIR = Path("/app/tmp_audio")
    TMP_DIR.mkdir(exist_ok=True)

    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
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
        ext = Path(self.uploaded_file.filename).suffix or ".mp3"
        tmp_input = self.TMP_DIR / f"{next(tempfile._get_candidate_names())}{ext}"

        self.uploaded_file.file.seek(0)

        with open(tmp_input, "wb") as f:
            content = self.uploaded_file.file.read()
            if not content:
                raise RuntimeError("Uploaded file is empty or unreadable.")
            f.write(content)

        tmp_wav = self.TMP_DIR / f"{next(tempfile._get_candidate_names())}.wav"

        try:
            audio = AudioSegment.from_file(tmp_input, format="mp3")
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(tmp_wav, format="wav")
        except Exception as e:
            raise RuntimeError(f"Failed to convert MP3 to WAV: {e}")

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


