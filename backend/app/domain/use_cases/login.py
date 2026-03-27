from typing import Optional
from app.domain.ports.inbound.auth_ports import ILoginUseCase
from app.domain.ports.outbound.repositories.user_repository import IUserRepository
from app.domain.ports.outbound.providers.auth_provider import IAuthTokenProvider

class LoginUseCase(ILoginUseCase):
    def __init__(self, user_repo: IUserRepository, auth_provider: IAuthTokenProvider):
        self._user_repo = user_repo
        self._auth_provider = auth_provider

    def execute(self, username: str, password: str) -> Optional[dict]:
        user = self._user_repo.authenticate(username, password)
        if not user:
            return None
        token_data = {"sub": user.id, "username": user.username}
        return {
            "access_token": self._auth_provider.create_access_token(token_data),
            "refresh_token": self._auth_provider.create_refresh_token(token_data),
            "user": {
                "id": user.id,
                "username": user.username,
                "displayName": user.display_name,
                "createdAt": user.created_at,
                "lastLoginAt": user.last_login_at,
            },
        }
