from src.validators import FileValidator
from src.services.MidiService import MidiService
from src.services.AIService import AIService
from src.services.AudioService import AudioService
from fastapi.responses import StreamingResponse
from src.utils import FileUtil
from src.utils.StringUtil import sanitize_chord_name, get_mode_name, classify_tempo
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

        ai_service = AIService()

        chordsPlayed = midi_service.extract_chords()
        chordsForteClass = midi_service.extract_chords_forteclass()
        
        emotion = ai_service.knn_predict(chordsForteClass)
        # chordsPlayedV2 = midi_service.extract_chords_new()
        key_info = midi_service.find_estimate_key()
        bpm, tempo_name = classify_tempo(midi_service.find_tempo())

        if not chordsPlayed:
            return {"error": "Unable to extract harmonic progression"}

        chord_list = [
            {
                "chord": k,
                "notes": v[0],
                "name": v[1],
            }
            for k, v in chordsPlayed.items()
        ]

        return {
            # "genre": genre, will be implemented in the future
            "chord_progression": chord_list,
            "emotion": emotion,
            "tempo": bpm,
            "tempo_name": tempo_name,
            "key": f"{sanitize_chord_name(key_info['key'], 'tab')} ({sanitize_chord_name(key_info['key'])})",
            "mode": get_mode_name(key_info['mode']),
            "tonic": f"{sanitize_chord_name(key_info['tonic'], 'tab')} ({sanitize_chord_name(key_info['tonic'])})",
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


