from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.domain.exceptions.audio_exceptions import (
    InvalidAudioFormatException,
    AudioTooLargeException,
    AudioProcessingException,
)
from app.domain.exceptions.auth_exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    TooManyAttemptsException,
)

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidAudioFormatException)
    async def invalid_format_handler(request: Request, exc: InvalidAudioFormatException):
        return JSONResponse(status_code=400, content={"error": "invalid_format", "message": str(exc)})

    @app.exception_handler(AudioTooLargeException)
    async def too_large_handler(request: Request, exc: AudioTooLargeException):
        return JSONResponse(status_code=413, content={"error": "file_too_large", "message": str(exc)})

    @app.exception_handler(AudioProcessingException)
    async def processing_error_handler(request: Request, exc: AudioProcessingException):
        return JSONResponse(status_code=500, content={"error": "processing_error", "message": str(exc)})

    @app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException):
        return JSONResponse(status_code=401, content={"error": "invalid_credentials", "message": str(exc)})

    @app.exception_handler(InvalidTokenException)
    async def invalid_token_handler(request: Request, exc: InvalidTokenException):
        return JSONResponse(status_code=401, content={"error": "invalid_token", "message": str(exc)})

    @app.exception_handler(TooManyAttemptsException)
    async def too_many_attempts_handler(request: Request, exc: TooManyAttemptsException):
        return JSONResponse(
            status_code=429,
            content={"error": "too_many_requests", "message": str(exc), "retry_after": exc.retry_after},
        )
