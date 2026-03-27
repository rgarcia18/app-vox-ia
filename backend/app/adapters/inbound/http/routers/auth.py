from fastapi import APIRouter, HTTPException, Response, Cookie, Request, Depends
from typing import Optional
from collections import defaultdict
from datetime import datetime, timezone

from app.domain.ports.inbound.auth_ports import ILoginUseCase, IRefreshTokenUseCase
from app.adapters.inbound.http.schemas.auth import LoginRequest
from app.infrastructure.config.settings import settings
from app.infrastructure.container.dependencies import get_login_use_case, get_refresh_token_use_case

router = APIRouter(prefix="/api/auth", tags=["auth"])

_login_attempts: dict[str, list] = defaultdict(list)


def _check_rate_limit(ip: str):
    now = datetime.now(timezone.utc).timestamp()
    window = settings.RATE_LIMIT_WINDOW_SECONDS
    _login_attempts[ip] = [t for t in _login_attempts[ip] if now - t < window]
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


@router.post("/login")
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    use_case: ILoginUseCase = Depends(get_login_use_case),
):
    ip = request.client.host if request.client else "unknown"
    _check_rate_limit(ip)

    result = use_case.execute(body.username, body.password)

    if not result:
        _login_attempts[ip].append(datetime.now(timezone.utc).timestamp())
        raise HTTPException(
            status_code=401,
            detail={"error": "invalid_credentials", "message": "Usuario o contraseña incorrectos"},
        )

    _login_attempts[ip] = []
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        samesite="lax",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        secure=False,
    )
    return {"access_token": result["access_token"], "user": result["user"]}


@router.post("/refresh")
async def refresh(
    refresh_token: Optional[str] = Cookie(default=None),
    use_case: IRefreshTokenUseCase = Depends(get_refresh_token_use_case),
):
    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail={"error": "missing_refresh_token", "message": "Token de refresco no encontrado"},
        )
    new_token = use_case.execute(refresh_token)
    if not new_token:
        raise HTTPException(
            status_code=401,
            detail={"error": "invalid_refresh_token", "message": "Sesión expirada"},
        )
    return {"access_token": new_token}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")
    return {"message": "Sesión cerrada exitosamente"}
