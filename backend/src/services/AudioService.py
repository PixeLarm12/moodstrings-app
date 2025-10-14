import io
import os
import tempfile
import subprocess
from pathlib import Path
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
        ext = Path(self.uploaded_file.filename).suffix
        tmp_input = self.TMP_DIR / f"{next(tempfile._get_candidate_names())}{ext}"
        with open(tmp_input, "wb") as f:
            f.write(self.uploaded_file.file.read())

        tmp_wav = self.TMP_DIR / f"{next(tempfile._get_candidate_names())}.wav"

        subprocess.run([
            "ffmpeg",
            "-y",  
            "-i", str(tmp_input),
            "-ac", "1",       
            "-ar", "16000",    
            "-c:a", "pcm_s16le",
            str(tmp_wav)
        ], check=True)

        tmp_input.unlink()
        self.set_wav_path(str(tmp_wav))
        return str(tmp_wav)

    def apply_filters(self):
        samples, sr = sf.read(self.get_wav_path(), dtype='float32')
        samples = nr.reduce_noise(y=samples, sr=sr, prop_decrease=0.7)
        sf.write(self.get_wav_path(), samples, sr)

    def create_midi_file(self):
        self.prepare_wav_file()
        self.apply_filters()
        _, midi_data, _ = predict(self.get_wav_path())
        self.set_midi_data(midi_data)
        return self.get_midi_data()


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
        if self._wav_path and os.path.exists(self._wav_path):
            os.remove(self._wav_path)

