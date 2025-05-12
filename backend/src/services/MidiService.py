import pretty_midi
from fastapi import UploadFile
from io import BytesIO

class MidiService:
    def __init__(self, file):
        self._midi_data = pretty_midi.PrettyMIDI(BytesIO(file.file.read()))
    
    @property
    def midi_data(self):
        return self._midi_data

    @midi_data.setter
    def midi_data(self, value):
        self._midi_data = pretty_midi.PrettyMIDI(BytesIO(value.file.read()))

    def get_instruments_name(self):
        instruments = []

        for item in self._midi_data.instruments:
            instruments.append({
                "name": item.name,
                "program": int(item.program),
                "isDrum": bool(item.is_drum),
            })

        return instruments