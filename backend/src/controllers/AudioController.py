from src.validators import FileValidator
from src.services.MidiService import MidiService

def upload(file):
    response = FileValidator.validate(file)

    if not response:
        midi_service = MidiService(file)
        instruments = midi_service.get_instruments_name()

        return { "instruments" : instruments }
    
    return response