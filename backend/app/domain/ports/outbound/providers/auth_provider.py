from abc import ABC, abstractmethod
from typing import Optional

class IAuthTokenProvider(ABC):
    @abstractmethod
    def create_access_token(self, data: dict) -> str:
        ...

    @abstractmethod
    def create_refresh_token(self, data: dict) -> str:
        ...

    @abstractmethod
    def decode_token(self, token: str) -> Optional[dict]:
        ...

    @abstractmethod
    def hash_password(self, password: str) -> str:
        ...

    @abstractmethod
    def verify_password(self, plain: str, hashed: str) -> bool:
        ...
