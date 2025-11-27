import os
import tempfile
from pydub import AudioSegment
import speech_recognition as sr
from src.enums import HttpEnum
from src.exceptions import AppException

class AudioService:
    SUPPORTED_EXTENSIONS = [".mp3", ".wav", ".ogg", ".flac", ".m4a"]

    def __init__(self, file):
        self.file = file

    async def transcribe(self):
        try:
            suffix = os.path.splitext(self.file.filename)[-1].lower()

            if suffix not in self.SUPPORTED_EXTENSIONS:
                raise AppException(
                    code=HttpEnum.Code.UNPROCESSABLE_ENTITY,
                    message=f"[{HttpEnum.Message.UNPROCESSABLE_ENTITY.value}] Extesion {suffix} not supported.",
                    data=[]
                )

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
                audio = AudioSegment.from_file(self.file.file, format=suffix.replace(".", ""))
                audio.export(tmp_wav.name, format="wav")
                tmp_wav_path = tmp_wav.name

            recognizer = sr.Recognizer()
            with sr.AudioFile(tmp_wav_path) as source:
                audio_data = recognizer.record(source)

            text = recognizer.recognize_google(audio_data, language="pt-BR")

            os.remove(tmp_wav_path)

            return text

        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            raise AppException(
                code=HttpEnum.Code.BAD_REQUEST,
                message=f"[{HttpEnum.Message.BAD_REQUEST.value}] Error connecting to recognition service: {e}",
                data=[]
            )
        except Exception as e:
            raise AppException(
                code=HttpEnum.Code.INTERNAL_SERVER_ERROR,
                message=f"[{HttpEnum.Message.INTERNAL_SERVER_ERROR.value}] Video transcription error: {e}",
                data=[]
            )