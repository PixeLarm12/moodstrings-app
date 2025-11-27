from fastapi import UploadFile
from src.services import AudioService
from src.enums import HttpEnum
from src.exceptions import AppException

async def analyze_audio(lang = "en-US", media: UploadFile = None):
    service = AudioService(media)
    content = await service.transcribe(lang=lang)

    if not content:
        raise AppException(
            code=HttpEnum.Code.INTERNAL_SERVER_ERROR,
            message=f"No lyrics could be extracted from audio.",
            data=[]
        )

    return content, HttpEnum.Code.OK, ''