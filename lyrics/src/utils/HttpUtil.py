from fastapi.responses import JSONResponse
from enum import Enum

class HttpUtil:
    @staticmethod
    def response(data, code, message):
        if isinstance(code, Enum):
            code = code.value
        if isinstance(message, Enum):
            message = message.value

        return JSONResponse(
            status_code=code,
            content={
                "code": code,
                "message": message,
                "data": data or []
            }
        )