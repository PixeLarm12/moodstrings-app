import io
import tempfile
from pydub import AudioSegment
from basic_pitch.inference import predict
from pedalboard import Pedalboard, Compressor, HighpassFilter, LowpassFilter, Gain
import soundfile as sf
import noisereduce as nr

class AudioService:
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
        mp3_bytes = self.uploaded_file.file.read()

        mp3_audio = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
        mp3_audio = mp3_audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            mp3_audio.export(tmp_wav.name, format="wav")

            self.set_wav_path(tmp_wav.name)
    
    def apply_filters(self):
        samples, sr = sf.read(self.get_wav_path())

        samples = nr.reduce_noise(y=samples, sr=sr, prop_decrease=0.7)

        # board = Pedalboard([
        #     # HighpassFilter(cutoff_frequency_hz=40.0),   
        #     # LowpassFilter(cutoff_frequency_hz=16000.0), 
        #     Gain(gain_db=3.0),                         
        #     Compressor(threshold_db=-25, ratio=2.0),   
        # ])

        # samples = board(samples, sr)

        sf.write(self.get_wav_path(), samples, sr)
    
    def create_midi_file(self):
        self.prepare_wav_file()

        self.apply_filters()

        model_output, midi_data, note_events = predict(self.get_wav_path())

        self.set_midi_data(midi_data)

        return self.get_midi_data()