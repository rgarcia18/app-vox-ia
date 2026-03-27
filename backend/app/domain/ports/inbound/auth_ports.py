from abc import ABC, abstractmethod
from typing import Optional

class ILoginUseCase(ABC):
    @abstractmethod
    def execute(self, username: str, password: str) -> Optional[dict]:
        ...

class IRefreshTokenUseCase(ABC):
    @abstractmethod
    def execute(self, refresh_token: str) -> Optional[str]:
        ...
