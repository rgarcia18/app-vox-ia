from abc import ABC, abstractmethod

class IHealthProvider(ABC):
    @abstractmethod
    def is_healthy(self) -> bool:
        ...
