"""Separated module with base expression node class to avoid circular imports."""
from abc import abstractmethod

from .representation import JsonRepresentation


class ExprNode(JsonRepresentation):
    @abstractmethod
    def get_sensitivity_list(self) -> list:
        return []
