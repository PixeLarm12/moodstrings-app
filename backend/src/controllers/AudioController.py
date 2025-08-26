from src.validators import FileValidator
from src.services.MidiService import MidiService
from src.services.IAService import IAService
from src.services.AudioService import AudioService
from fastapi.responses import StreamingResponse
from src.services.AudioService import AudioService
from src.utils import FileUtil
import io

def test_audio(file):
    response = FileValidator.validate(file)

    if not response:
        redirect_action = FileUtil.redirectByFileType(file)

        if redirect_action == 'transcribe':
            audio_service = AudioService(file)

            midi_file = audio_service.create_midi_file()
            
            midi_service = MidiService(midi_data=midi_file)
        else:
            midi_service = MidiService(file=file)

        # ia_service = IAService()

        chordsPlayedV1 = midi_service.extract_chords()
        # chordsPlayedV2 = midi_service.extract_chords_new()
        key_info = midi_service.find_estimate_key()
        tempo = midi_service.find_tempo()

        if not chordsPlayedV1:
            return {"error": "Unable to extract harmonic progression"}
        
        return {
            # "emotion": emotion,
            # "genre": genre, will be implemented in the future
            "chordProgression": chordsPlayedV1,
            # "chordProgressionV2": chordsPlayedV2,
            "tempo": tempo,
            "key": key_info['key'],
            "mode": key_info['mode'],
            "tonic": key_info['tonic']
        }

        # midi_io = io.BytesIO()
        # midi_service.midi_data.write(midi_io)
        # midi_io.seek(0)

        # return StreamingResponse(
        #     midi_io,
        #     media_type="audio/midi",
        #     headers={"Content-Disposition": "attachment; filename=saida.mid"}
        # )

    return response


