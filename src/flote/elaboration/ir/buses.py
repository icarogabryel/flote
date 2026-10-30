"""
This module defines the bus representation in the intermediate representation with the
Base Bus class and its std subclasses.
"""

# TODO refactor __str__ and __repr__ of this module

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from flote.elaboration.ir.representation import JsonRepresentation

if TYPE_CHECKING:
    from .expression_nodes import ExpressionNode


class BusDto(JsonRepresentation):
    """This abstract class represents a bus in the circuit."""

    def __init__(self, identifier: str, type_: str) -> None:
        self.identifier = identifier
        self.type_ = type_
        self.assignment: None | ExpressionNode = None
        self.value: Any = self.get_default()
        # The list of buses that the current bus depends on.
        self.influence_list: list[BusDto] = []

    def __str__(self) -> str:
        return (
            f"id: {self.identifier} assign: {self.assignment}"
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

    def __init__(self, identifier: str, dimension: int, msb_descending: bool) -> None:
        self.dimension = dimension
        super().__init__(identifier, "bit_bus")
        self.msb_descending = msb_descending

    def get_default(self) -> list[bool]:
        return [False] * self.dimension

    def to_json(self) -> dict[str, Any]:
        if self.assignment is None:
            assignment_json = None
        else:
            assignment_json = self.assignment.to_json()

        return {
            "id": self.identifier,
            "type": self.type_,
            "value": self.value,
            "msb_descending": self.msb_descending,
            "assignment": assignment_json,
            "influence_list": [bus.identifier for bus in self.influence_list],
        }
