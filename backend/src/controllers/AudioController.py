from src.validators import FileValidator
from src.services.MidiService import MidiService
from src.services.AIService import AIService
from src.services.AudioService import AudioService
from datetime import date
from fastapi.responses import StreamingResponse
from src.utils import FileUtil
from src.utils.StringUtil import sanitize_chord_name, classify_tempo
import io

def transcribe(file, is_recorded):
    errors = FileValidator.validate(file)

    if len(errors) <= 0:
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

        if not progression.get("chords") and not progression.get("notes"):
            return {"error": "Something went wrong. We couldn't extract either chords or notes."}

        return {
            "progression": progression,
            "tempo": {
                "time": bpm,
                "name": tempo_name,
            },
        }

    return {
        "errors": errors
    }

def progression_info(chordProgression, noteProgression, tempo, file):
    errors = []

    if not tempo:
        errors.append({"message": "BPM not informed."})
    elif not chordProgression and not noteProgression:
        errors.append({"message": "Progression not informed."})
    elif tempo <= 0:
        errors.append({"message": "BPM has incorrect value."})

    if len(errors) <= 0:
        audio_service = AudioService(file)
        midi_file = audio_service.create_midi_file_from_progression(chord_progression=chordProgression, bpm=tempo)
        midi_service = MidiService(midi_data=midi_file, bpm=tempo)
        progression = midi_service.extract_notes_and_chords()

        ai_service = AIService()

        chordsForteClass = midi_service.extract_chords_forteclass()

        emotion = ai_service.rf_predict(chordsForteClass)

        key_info = midi_service.find_estimate_key()
        relative_scales = midi_service.find_relative_scales()
        bpm, tempo_name = classify_tempo(midi_service.find_tempo())

        key_info = midi_service.correct_key_with_first_event(key_info, progression)

        return {
            "progression": progression,
            "emotion": emotion,
            "relative_scales": [relative_scales],
            "tempo": {
                "time": bpm,
                "name": tempo_name,
            },
            "key_name": key_info['key'],
            "tonic": key_info['tonic']
        }
    
    return {
        "errors": errors
    }

async def get_midi_to_download(file):
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
        return {"error": str(e)}
    
async def get_musical_sheet_to_download(file):
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
        return {"error": str(e)}




