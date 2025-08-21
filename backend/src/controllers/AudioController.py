from src.validators import FileValidator
from src.services.MidiService import MidiService
from src.services.IAService import IAService
from src.services.AudioService import AudioService
from fastapi.responses import StreamingResponse
from src.services.AudioService import AudioService
import io

def upload(file):
    response = FileValidator.validate(file)

    if not response:
        midi_service = MidiService(file=file)
        ia_service = IAService()

        chordsPlayed = midi_service.extract_chords()

        if not chordsPlayed:
            return {"error": "Unable to extract harmonic progression"}

        emotion, genre = ia_service.predict(chordsPlayed)

        return {
            "emotion": emotion,
            # "genre": genre, will be implemented in the future
            "progression": chordsPlayed,
        }
    
    return response

async def test_mp3(file):
    audio_service = AudioService(file)
    midi_service = audio_service.transcribe_to_midi()

    midi_io = io.BytesIO()
    midi_service.midi_data.write(midi_io)
    midi_io.seek(0)

    return StreamingResponse(
        midi_io,
        media_type="audio/midi",
        headers={"Content-Disposition": "attachment; filename=saida.mid"}
    )
