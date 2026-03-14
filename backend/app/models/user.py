from datetime import datetime, timezone
from typing import Optional
import uuid
from app.core.security import hash_password, verify_password
from app.core.config import settings


# Base de datos en memoria (para prototipo académico)
# En producción: reemplazar con PostgreSQL/SQLite
class UserDB:
    def __init__(self):
        self._users: dict[str, dict] = {}
        self._seed_admin()

    def _seed_admin(self):
        """Crea el usuario admin por defecto al iniciar"""
        admin_id = str(uuid.uuid4())
        self._users[settings.ADMIN_USERNAME.lower()] = {
            "id": admin_id,
            "username": settings.ADMIN_USERNAME,
            "password_hash": hash_password(settings.ADMIN_PASSWORD),
            "displayName": settings.ADMIN_DISPLAY_NAME,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "lastLoginAt": None,
        }

    def get_by_username(self, username: str) -> Optional[dict]:
        return self._users.get(username.lower())

    def update_last_login(self, username: str):
        user = self._users.get(username.lower())
        if user:
            user["lastLoginAt"] = datetime.now(timezone.utc).isoformat()

    def authenticate(self, username: str, password: str) -> Optional[dict]:
        user = self.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user["password_hash"]):
            return None
        self.update_last_login(username)
        return user


# Instancia global
user_db = UserDB()
