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

    async def transcribe(self, chunk_size=30):
        try:
            suffix = os.path.splitext(self.file.filename)[-1].lower()

            if suffix not in self.SUPPORTED_EXTENSIONS:
                raise AppException(
                    code=HttpEnum.Code.UNPROCESSABLE_ENTITY,
                    message=f"[{HttpEnum.Message.UNPROCESSABLE_ENTITY.value}] Extension {suffix} not supported.",
                    data=[]
                )

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
                self.file.file.seek(0)

                audio = AudioSegment.from_file(self.file.file, format=suffix.replace(".", ""))
                audio = audio.set_channels(1)
                audio = audio.set_frame_rate(16000)
                audio.export(tmp_wav.name, format="wav")

                tmp_wav_path = tmp_wav.name

            recognizer = sr.Recognizer()
            full_text = []

            with sr.AudioFile(tmp_wav_path) as source:
                duration = source.DURATION
                current = 0.0


                while current < duration:
                    print(f"current: {current}")
                    try:
                        audio_data = recognizer.record(source, duration=chunk_size)

                        text = recognizer.recognize_google(audio_data, language="pt-BR")
                        full_text.append(text)

                    except sr.UnknownValueError:
                        full_text.append("")
                    except sr.RequestError as e:
                        raise AppException(
                            code=HttpEnum.Code.BAD_REQUEST,
                            message=f"[{HttpEnum.Message.BAD_REQUEST.value}] Recognition service error: {e}",
                            data=[]
                        )
                    except Exception as e:
                        raise AppException(
                            code=HttpEnum.Code.INTERNAL_SERVER_ERROR,
                            message=f"[{HttpEnum.Message.INTERNAL_SERVER_ERROR.value}] Chunk transcription error: {e}",
                            data=[]
                        )

                    current += chunk_size

            os.remove(tmp_wav_path)
            return " ".join(full_text).strip()

        except Exception as e:
            raise AppException(
                code=HttpEnum.Code.INTERNAL_SERVER_ERROR,
                message=f"[{HttpEnum.Message.INTERNAL_SERVER_ERROR.value}] Audio transcription error: {e}",
                data=[]
            )
