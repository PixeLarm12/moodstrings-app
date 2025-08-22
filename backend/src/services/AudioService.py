import io
import tempfile
from pydub import AudioSegment
import numpy as np
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
from src.services.MidiService import MidiService

class AudioService:
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file 
        self._midi_data = None

    def transcribe_to_midi(self):
        mp3_bytes = self.uploaded_file.file.read()

        mp3_audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
        mp3_audio = mp3_audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp_wav:
            mp3_audio.export(tmp_wav.name, format="wav")

            output_dict, midi_data, note_events = predict(tmp_wav.name)
            self._midi_data = midi_data

        return MidiService(midi_data=self._midi_data)
    
    def transcribe(self):
        mp3_bytes = self.uploaded_file.file.read()

        mp3_audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
        mp3_audio = mp3_audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            mp3_audio.export(tmp_wav.name, format="wav")
            wav_path = tmp_wav.name

        model_output, midi_data, note_events = predict(wav_path)

        return MidiService(midi_data=midi_data)

