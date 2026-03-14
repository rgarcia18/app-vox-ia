from fastapi import APIRouter, HTTPException, Response, Cookie, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from typing import Optional
import re
from collections import defaultdict
from datetime import datetime, timezone

from app.models.user import user_db
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.core.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Rate limiting en memoria: {ip: [timestamps]}
_login_attempts: dict[str, list] = defaultdict(list)


class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username debe tener entre 3 y 50 caracteres")
        if not re.match(r'^[a-zA-Z0-9._@-]+$', v):
            raise ValueError("Username contiene caracteres inválidos")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6 or len(v) > 100:
            raise ValueError("Password debe tener entre 6 y 100 caracteres")
        return v


def _check_rate_limit(ip: str):
    """Verifica si la IP ha excedido el límite de intentos"""
    now = datetime.now(timezone.utc).timestamp()
    window = settings.RATE_LIMIT_WINDOW_SECONDS

    # Limpiar intentos viejos
    _login_attempts[ip] = [
        t for t in _login_attempts[ip] if now - t < window
    ]

    if len(_login_attempts[ip]) >= settings.RATE_LIMIT_MAX_ATTEMPTS:
        oldest = min(_login_attempts[ip])
        retry_after = int(window - (now - oldest))
        raise HTTPException(
            status_code=429,
            detail={
                "error": "too_many_requests",
                "message": "Demasiados intentos de login",
                "retry_after": retry_after,
            },
        )


def _record_attempt(ip: str):
    now = datetime.now(timezone.utc).timestamp()
    _login_attempts[ip].append(now)


def _clear_attempts(ip: str):
    _login_attempts[ip] = []


@router.post("/login")
async def login(request: Request, body: LoginRequest, response: Response):
    ip = request.client.host if request.client else "unknown"

    # Rate limiting
    _check_rate_limit(ip)

    # Autenticar usuario
    user = user_db.authenticate(body.username, body.password)

    if not user:
        _record_attempt(ip)
        raise HTTPException(
            status_code=401,
            detail={
                "error": "invalid_credentials",
                "message": "Usuario o contraseña incorrectos",
            },
        )

    # Login exitoso - limpiar intentos
    _clear_attempts(ip)

    # Generar tokens
    token_data = {"sub": user["id"], "username": user["username"]}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Setear cookie httpOnly
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",   # lax para desarrollo local
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        secure=False,     # True en producción con HTTPS
    )

    return {
        "access_token": access_token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "displayName": user["displayName"],
            "createdAt": user["createdAt"],
            "lastLoginAt": user["lastLoginAt"],
        },
    }


@router.post("/refresh")
async def refresh(refresh_token: Optional[str] = Cookie(default=None)):
    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail={"error": "missing_refresh_token", "message": "Token de refresco no encontrado"},
        )

    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail={"error": "invalid_refresh_token", "message": "Sesión expirada"},
        )

    # Generar nuevo access token
    token_data = {"sub": payload["sub"], "username": payload["username"]}
    access_token = create_access_token(token_data)

    return {"access_token": access_token}


@router.post("/logout")
async def logout(response: Response):
    # Limpiar cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="lax",
    )
    return {"message": "Sesión cerrada exitosamente"}
