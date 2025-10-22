import os
import tempfile
import subprocess
import numpy as np
import librosa
import soundfile as sf
import noisereduce as nr
from pathlib import Path
from typing import Dict, List, Any


class ChromaService:
    TMP_DIR = Path("/app/tmp_chroma")
    TMP_DIR.mkdir(exist_ok=True)

    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
        self._wav_path = None
        self._chord_segments = None

    # -----------------------------
    # Getters/Setters
    # -----------------------------
    def get_wav_path(self):
        return self._wav_path

    def set_wav_path(self, wav_path):
        self._wav_path = wav_path

    def get_chord_segments(self):
        return self._chord_segments

    def set_chord_segments(self, chords):
        self._chord_segments = chords

    # -----------------------------
    # Step 1 - Convert to WAV (same logic as AudioService)
    # -----------------------------
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
            "-ac", "1",          # mono
            "-ar", "44100",      # sample rate
            "-c:a", "pcm_s16le",
            str(tmp_wav)
        ], check=True)

        tmp_input.unlink()
        self.set_wav_path(str(tmp_wav))
        return str(tmp_wav)

    # -----------------------------
    # Step 2 - Apply noise reduction
    # -----------------------------
    def apply_filters(self):
        samples, sr = sf.read(self.get_wav_path(), dtype='float32')
        samples = nr.reduce_noise(y=samples, sr=sr, prop_decrease=0.7)
        sf.write(self.get_wav_path(), samples, sr)

    # -----------------------------
    # Step 3 - Chord template builder
    # -----------------------------
    @classmethod
    def build_chord_templates(cls) -> Dict[str, np.ndarray]:
        templates = {}

        def triad(root: int, intervals: List[int]) -> np.ndarray:
            vec = np.zeros(12, dtype=float)
            for i in intervals:
                vec[(root + i) % 12] = 1.0
            if vec.sum() > 0:
                vec /= np.linalg.norm(vec)
            return vec

        major_intervals = [0, 4, 7]
        minor_intervals = [0, 3, 7]

        for root_idx, name in enumerate(cls.NOTE_NAMES):
            templates[f"{name}:maj"] = triad(root_idx, major_intervals)
            templates[f"{name}:min"] = triad(root_idx, minor_intervals)

        return templates

    # -----------------------------
    # Step 4 - Detect chords
    # -----------------------------
    @classmethod
    def detect_chords_from_audio(cls, wav_path: str, hop_length: int = 2048) -> List[Dict[str, Any]]:
        templates = cls.build_chord_templates()

        y, sr = librosa.load(wav_path, sr=44100, mono=True)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)

        chords = []
        for t in range(chroma.shape[1]):
            chroma_vec = chroma[:, t] / (np.linalg.norm(chroma[:, t]) + 1e-6)
            best_chord = None
            best_score = -1
            for chord_name, template in templates.items():
                score = np.dot(chroma_vec, template)
                if score > best_score:
                    best_score = score
                    best_chord = chord_name
            time_sec = librosa.frames_to_time(t, sr=sr, hop_length=hop_length)
            chords.append({
                "time": float(time_sec),
                "chord": best_chord,
                "confidence": float(best_score)
            })

        # Agrupa acordes iguais consecutivos
        grouped = []
        if chords:
            current = chords[0].copy()
            current["start"] = 0.0
            for i in range(1, len(chords)):
                if chords[i]["chord"] != current["chord"]:
                    current["end"] = chords[i]["time"]
                    grouped.append(current)
                    current = chords[i].copy()
                    current["start"] = chords[i]["time"]
            current["end"] = chords[-1]["time"]
            grouped.append(current)

        return grouped

    # -----------------------------
    # Step 5 - Full pipeline
    # -----------------------------
    def recognize_chords(self):
        try:
            self.prepare_wav_file()
            self.apply_filters()
            chords = self.detect_chords_from_audio(self.get_wav_path())
            self.set_chord_segments(chords)
            return {
                "file": self.uploaded_file.filename,
                "chords": chords
            }
        finally:
            self.cleanup()

    # -----------------------------
    # Step 6 - Cleanup
    # -----------------------------
    def cleanup(self):
        if self._wav_path and os.path.exists(self._wav_path):
            os.remove(self._wav_path)
