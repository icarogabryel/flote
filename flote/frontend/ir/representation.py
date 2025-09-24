from abc import ABC, abstractmethod
from typing import Any


class Representation(ABC):
    @abstractmethod
    def to_repr(self) -> Any:
        pass
