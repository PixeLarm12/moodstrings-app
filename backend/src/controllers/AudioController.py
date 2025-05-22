from src.validators import FileValidator
from src.services.MidiService import MidiService

def upload(file):
    response = FileValidator.validate(file)

    if not response:
        midi_service = MidiService(file)

        data = midi_service.extract_chords_by_guitar_type()

        return { "instruments" : data }
    
    return response