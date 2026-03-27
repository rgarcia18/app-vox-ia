from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.user import User

class IUserRepository(ABC):
    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[User]:
        ...

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        ...
