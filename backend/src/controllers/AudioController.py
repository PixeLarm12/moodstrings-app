from src.validators import FileValidator
from src.services.MidiService import MidiService
from src.services.AIService import AIService
from src.services.AudioService import AudioService
from datetime import date
from fastapi.responses import StreamingResponse
from src.utils import FileUtil
from src.utils.StringUtil import sanitize_chord_name, classify_tempo
import io

def transcribe(file):
    response = FileValidator.validate(file)

    if not response:
        redirect_action = FileUtil.redirectByFileType(file)

        if redirect_action == 'transcribe':
            audio_service = AudioService(file)
            midi_file = audio_service.create_midi_file()
            midi_service = MidiService(midi_data=midi_file, wav_path=audio_service.get_wav_path())
            audio_service.cleanup()
        else:
            midi_service = MidiService(file=file)

        ai_service = AIService()
        emotions = []

        chordsForteClass = midi_service.extract_chords_forteclass()

        emotions.append(ai_service.rf_predict(chordsForteClass))

        key_info = midi_service.find_estimate_key()
        relative_scales = midi_service.find_relative_scales()
        bpm, tempo_name = classify_tempo(midi_service.find_tempo())
        progression = midi_service.extract_notes_and_chords()

        if not progression.get("chords") and not progression.get("notes"):
            return {"error": "Something went wrong. We couldn't extract either chords or notes."}

        return {
            "progression": progression,
            "emotions": emotions,
            "relative_scales": [relative_scales],
            "tempo": {
                "time": bpm,
                "name": tempo_name,
            },
            "key": f"{sanitize_chord_name(key_info['key'], 'tab')} ({sanitize_chord_name(key_info['key'])})",
            "tonic": f"{sanitize_chord_name(key_info['tonic'], 'tab')} ({sanitize_chord_name(key_info['tonic'])})",
        }


    return response

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




