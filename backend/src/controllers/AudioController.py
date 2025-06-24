from src.validators import FileValidator
from src.services.MidiService import MidiService
from src.services.IAService import IAService

def upload(file):
    response = FileValidator.validate(file)

    if not response:
        midi_service = MidiService(file)
        ia_service = IAService()

        chordsPlayed = midi_service.extract_chords()

        if not chordsPlayed:
            return {"error": "Unable to extract harmonic progression"}

        emotion, genre = ia_service.predict(chordsPlayed)

        return {
            "emotion": emotion,
            # "genre": genre, will be implemented in the future
            "progression": chordsPlayed,
            "progression_named": midi_service.extract_named_progression() 
        }
    
    return response