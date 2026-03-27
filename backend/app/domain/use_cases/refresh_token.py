from typing import Optional
from app.domain.ports.inbound.auth_ports import IRefreshTokenUseCase
from app.domain.ports.outbound.providers.auth_provider import IAuthTokenProvider

class RefreshTokenUseCase(IRefreshTokenUseCase):
    def __init__(self, auth_provider: IAuthTokenProvider):
        self._auth_provider = auth_provider

    def execute(self, refresh_token: str) -> Optional[str]:
        payload = self._auth_provider.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        token_data = {"sub": payload["sub"], "username": payload["username"]}
        return self._auth_provider.create_access_token(token_data)
