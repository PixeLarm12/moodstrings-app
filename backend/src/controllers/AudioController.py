from src.validators import FileValidator
from src.services.MidiService import MidiService
from src.services.AIService import AIService
from src.services.AudioService import AudioService
from datetime import date
from fastapi.responses import StreamingResponse
from src.utils import FileUtil
from src.utils.StringUtil import sanitize_chord_name, get_mode_name, classify_tempo
import io

def transcribe(file):
    response = FileValidator.validate(file)

    if not response:
        redirect_action = FileUtil.redirectByFileType(file)

        if redirect_action == 'transcribe':
            audio_service = AudioService(file)
            audio_service.prepare_wav_file()  # mp3 -> wav
            audio_service.apply_filters()      # denoise
            audio_service.pitch_shift_wav(n_steps=12)  # shift 1 octave up
            midi_file = audio_service.create_midi_file()
            midi_service = MidiService(midi_data=midi_file, wav_path=audio_service.get_wav_path())
            audio_service.cleanup()
        else:
            midi_service = MidiService(file=file)

        ai_service = AIService()

        chordsPlayed = midi_service.extract_chords()
        chordsForteClass = midi_service.extract_chords_forteclass()

        timeline = midi_service.build_chord_timeline()
        repeated_chords = midi_service.detect_repeated_chords(timeline)
        progressions = midi_service.detect_progressions(timeline)

        svm_results = ai_service.svm_predict(chordsForteClass)
        rf_results = ai_service.rf_predict(chordsForteClass)
        knn_results = ai_service.knn_predict(chordsForteClass)
        nb_results = ai_service.nb_predict(chordsForteClass)

        emotions = [
            svm_results,
            rf_results,
            knn_results,
            nb_results,
        ]

        key_info = midi_service.find_estimate_key()
        relative_scales = midi_service.find_relative_scales()
        bpm, tempo_name = classify_tempo(midi_service.find_tempo())

        if not chordsPlayed:
            return {"error": "Unable to extract harmonic progression"}

        timeline = midi_service.build_chord_timeline()
        chord_list = midi_service.enrich_timeline(timeline)

        return {
            "chord_progression": chord_list,
            "emotions": emotions,
            "tempo": bpm,
            "tempo_name": tempo_name,
            "key": f"{sanitize_chord_name(key_info['key'], 'tab')} ({sanitize_chord_name(key_info['key'])})",
            "mode": get_mode_name(key_info['mode']),
            "tonic": f"{sanitize_chord_name(key_info['tonic'], 'tab')} ({sanitize_chord_name(key_info['tonic'])})",
            "relative_scales": [relative_scales],
            "repeated_chords": repeated_chords,
            "progressions": progressions
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


