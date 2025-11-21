from src.validators import FileValidator
from src.services.MidiService import MidiService
from src.services.AIService import AIService
from src.services.AudioService import AudioService
from datetime import date
from fastapi.responses import StreamingResponse
from src.utils import FileUtil
from src.utils.StringUtil import classify_tempo, clean_chord_name
import io

def transcribe(file, is_recorded):
    errors = FileValidator.validate(file)

    if len(errors) <= 0:
        try:
            redirect_action = FileUtil.redirectByFileType(file)
            bpm = 0
            tempo_name = ""

            if redirect_action == 'transcribe':
                audio_service = AudioService(file, is_recorded=(is_recorded == 1))
                midi_file = audio_service.create_midi_file()
                midi_service = MidiService(midi_data=midi_file, wav_path=audio_service.get_wav_path())
                
                bpm, tempo_name = classify_tempo(midi_service.find_tempo())

                audio_service.cleanup()
            else:
                midi_service = MidiService(file=file)

            progression = midi_service.extract_notes_and_chords()

            if not progression.get("chords"):
                errors.append({"message": "Something went wrong. We couldn't extract chord progression."})
                return {"errors": errors}

            return {
                "progression": progression,
                "tempo": {
                    "time": bpm,
                    "name": tempo_name,
                },
            }
        except Exception as e:
                errors.append({"message": f"{e}"})

    return {
        "errors": errors
    }

def progression_info(chord_progression, tempo, file):
    errors = []

    if not tempo:
        errors.append({"message": "BPM not informed."})
    elif not chord_progression:
        errors.append({"message": "Progression not informed."})
    elif tempo <= 0:
        errors.append({"message": "BPM can't be less or equal than 0."})
    elif tempo > 320:
        errors.append({"message": "BPM can't be higher than 320."})

    if len(errors) <= 0:
        try:
            cleaned = clean_chord_name(chord_progression)
            
            audio_service = AudioService(file)
            midi_file = audio_service.create_midi_file_from_progression(chord_progression=cleaned, bpm=tempo)
            midi_service = MidiService(midi_data=midi_file, bpm=tempo)
            progression = midi_service.extract_notes_and_chords()

            ai_service = AIService()            

            key_info = midi_service.find_estimate_key()
            key_info = midi_service.correct_key_with_first_event(key_info, progression)
            bpm, tempo_name = classify_tempo(midi_service.find_tempo())
            scale = midi_service.find_scale(key_info, cleaned)
            
            if scale['exists']:
                relative_scales = midi_service.find_relative_scales()
            else:
                relative_scales = None
                scale = None
                
            chordsForteClass = midi_service.extract_chord_progression_forteclass()

            emotion = ai_service.rf_predict(chordsForteClass[:-1], key_info["mode"], key_info["tonic"])

            return {
                "progression": progression,
                "emotion": emotion,
                "scales": {
                    "actual": scale,
                    "relatives": relative_scales
                },
                "tempo": {
                    "time": bpm,
                    "name": tempo_name,
                },
                "key_name": key_info['key'],
                "tonic": key_info['tonic']
            }    
        except Exception as e:
            errors.append({"message": f"{e}"})
        
    return {
        "errors": errors
    }

async def get_midi_to_download(file):
    errors = []
    try:
        midi_service = MidiService()

        midi_data = midi_service.process(file)

        midi_io = io.BytesIO()
        midi_data.write(midi_io)
        midi_io.seek(0)
        today = date.today()
        filename=f"{today}_played_progression.mid"

        return StreamingResponse(
            midi_io,
            media_type="audio/midi",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        errors.append({"message": f"{e}"})

    return {
        "errors": errors
    }
    
async def get_musical_sheet_to_download(file):
    errors = []
    try:
        midi_service = MidiService(file=file)

        xml_content = midi_service.export_musicxml()

        sheet_io = io.BytesIO(xml_content.encode("utf-8"))
        sheet_io.seek(0)

        today = date.today()
        filename = f"{today}_musical_sheet.musicxml"

        return StreamingResponse(
            sheet_io,
            media_type="application/vnd.recordare.musicxml+xml",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        errors.append({"message": f"{e}"})

    return {
        "errors": errors
    }




