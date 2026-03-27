import uuid
from datetime import datetime, timezone
from typing import Optional

from app.domain.entities.user import User
from app.domain.ports.outbound.repositories.user_repository import IUserRepository
from app.adapters.outbound.auth.jwt_provider import JWTProvider
from app.infrastructure.config.settings import settings


class InMemoryUserRepository(IUserRepository):
    def __init__(self):
        self._auth = JWTProvider()
        self._users: dict[str, dict] = {}
        self._seed_admin()

    def _seed_admin(self):
        self._users[settings.ADMIN_USERNAME.lower()] = {
            "id": str(uuid.uuid4()),
            "username": settings.ADMIN_USERNAME,
            "password_hash": self._auth.hash_password(settings.ADMIN_PASSWORD),
            "display_name": settings.ADMIN_DISPLAY_NAME,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login_at": None,
        }

    def authenticate(self, username: str, password: str) -> Optional[User]:
        record = self._users.get(username.lower())
        if not record:
            return None
        if not self._auth.verify_password(password, record["password_hash"]):
            return None
        record["last_login_at"] = datetime.now(timezone.utc).isoformat()
        return self._to_entity(record)

    def find_by_username(self, username: str) -> Optional[User]:
        record = self._users.get(username.lower())
        return self._to_entity(record) if record else None

    def _to_entity(self, record: dict) -> User:
        return User(
            id=record["id"],
            username=record["username"],
            display_name=record["display_name"],
            created_at=record["created_at"],
            last_login_at=record.get("last_login_at"),
        )
