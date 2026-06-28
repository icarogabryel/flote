"""
This module defines the bus representation in the intermediate representation with the
Base Bus class and its std subclasses.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from .representation import JsonRepresentation

if TYPE_CHECKING:
    from .expr_nodes import ExprNode


class BusDto(JsonRepresentation):
    """This class represents a bus in the circuit."""

    def __init__(self) -> None:
        self.id_: Optional[str] = None  # The id of the bus.
        self.type: Optional[str] = None  # The type of the bus.
        self.assignment: ExprNode | None = None
        self.value: Any = self.get_default()  # The value of the bus.
        # The list of buses that the current bus depends on.
        self.influence_list: list[BusDto] = []

    def __str__(self) -> str:
        return (
            f"id: {self.id_} assign: {self.assignment}"
            f" IL: {[bus for bus in self.influence_list]}"
            f" Value: {self.value}"
        )

    def make_influence_list(self) -> None:
        """This method adds an assignment to the bus."""
        sensitivity_list: list[BusDto] = []
        if self.assignment:
            sensitivity_list = self.assignment.get_sensitivity_list()

        for bus in sensitivity_list:
            if self not in bus.influence_list:
                bus.influence_list.append(self)

    @abstractmethod
    def get_default(self) -> Any:
        """This method returns the default value of the bus."""
        pass

    @abstractmethod
    def to_json(self) -> dict[str, Any]:
        pass


class BitBusDto(BusDto):
    """This class represents a bit bus in the circuit."""

    def __init__(self) -> None:
        super().__init__()
        self.type = "bit_bus"
        self.msb_descending = False

    def get_default(self) -> list[bool]:
        return [False]

    def set_dimension(self, dimension: int) -> None:
        self.value = [False] * dimension

    def to_json(self):
        if self.assignment is None:
            assignment_json = None
        else:
            assignment_json = self.assignment.to_json()

        return {
            "id": self.id_,
            "type": self.type,
            "value": self.value,
            "msb_descending": self.msb_descending,
            "assignment": assignment_json,
            "influence_list": [bus.id_ for bus in self.influence_list],
        }
