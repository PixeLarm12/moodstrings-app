from src.validators import FileValidator
from src.services.MidiService import MidiService
from src.services.IAService import IAService

def upload(file):
    response = FileValidator.validate(file)

    if not response:
        midi_service = MidiService(file)

        chordsPlayed = midi_service.extract_chords()

        if not chordsPlayed:
            return {"error": "Não foi possível extrair progressão harmônica"}

        ia_service = IAService()  # caminho padrão
        emotion, genre = ia_service.predict(chordsPlayed)

        return {
            "emotion": emotion,
            "genre": genre,
            "progression": chordsPlayed
        }
    
    return response