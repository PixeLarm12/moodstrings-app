from enum import Enum

class Code(Enum):
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    FOUND = 302
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


class Message(Enum):
    OK = "ok"
    CREATED = "created"
    ACCEPTED = "accepted"
    NO_CONTENT = "no content"
    FOUND = "found"
    BAD_REQUEST = "bad request"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not found"
    METHOD_NOT_ALLOWED = "method not allowed"
    UNPROCESSABLE_ENTITY = "unprocessable entity"
    TOO_MANY_REQUESTS = "too many requests"
    INTERNAL_SERVER_ERROR = "internal server error"
    BAD_GATEWAY = "bad gateway"
    SERVICE_UNAVAILABLE = "service unavailable"
    GATEWAY_TIMEOUT = "gateway timeout"