"""Module containing the base class for JSON representation."""
from abc import ABC, abstractmethod
from typing import Any


class JsonRepresentation(ABC):
    "Base class for all classes that can be represented as JSON."
    @abstractmethod
    def to_json(self) -> None | dict[str, Any]:
        pass
