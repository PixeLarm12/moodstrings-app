import os
import tempfile
from pydub import AudioSegment
import speech_recognition as sr
from src.enums import HttpEnum
from src.exceptions import AppException

class AudioService:
    SUPPORTED_EXTENSIONS = [".mp3", ".wav", ".ogg", ".flac", ".m4a", "webm"]

    def __init__(self, file):
        self.file = file

    async def transcribe(self, lang="en-US", chunk_size=30):
        try:
            suffix = os.path.splitext(self.file.filename)[-1].lower()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
                self.file.file.seek(0)

                audio = AudioSegment.from_file(self.file.file, format=suffix.replace(".", ""))
                audio = audio.set_channels(2)
                audio = audio.set_frame_rate(32000)
                audio.export(tmp_wav.name, format="wav")

                tmp_wav_path = tmp_wav.name

            recognizer = sr.Recognizer()
            full_text = []

            with sr.AudioFile(tmp_wav_path) as source:
                duration = source.DURATION
                current = 0.0


                while current < duration:
                    try:
                        audio_data = recognizer.record(source, duration=chunk_size)

                        text = recognizer.recognize_google(audio_data, language=lang)
                        full_text.append(text + "\n\n")

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

            raw = " ".join(full_text).strip()
            return self.format_lyrics(raw)


        except Exception as e:
            raise AppException(
                code=HttpEnum.Code.INTERNAL_SERVER_ERROR,
                message=f"[{HttpEnum.Message.INTERNAL_SERVER_ERROR.value}] Audio transcription error: {e}",
                data=[]
            )

    def format_lyrics(self, text: str, words_per_line=8):
        words = text.split()
        
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)

            if len(current_line) >= words_per_line:
                current_line[0] = current_line[0].capitalize()
                lines.append(" ".join(current_line))
                current_line = []

        if current_line:
            lines.append(" ".join(current_line))

        blocks = []
        for i in range(0, len(lines), 4):
            block = "\n".join(lines[i:i+4])
            blocks.append(block)

        return "\n\n".join(blocks)

