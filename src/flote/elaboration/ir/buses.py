"""
This module defines the bus representation in the intermediate representation with the
Base Bus class and its std subclasses.
"""

# TODO refactor __str__ and __repr__ of this module

from typing import TYPE_CHECKING, Any

from flote.elaboration.ir.representation import JsonRepresentation

if TYPE_CHECKING:
    from .expression_nodes import ExpressionNode


class BitBusDto(JsonRepresentation):
    """This class represents a bit bus in the circuit."""

    type_ = "bit_bus"

    def __init__(self, identifier: str, dimension: int, msb_descending: bool) -> None:
        self.identifier = identifier
        self.dimension = dimension
        self.msb_descending = msb_descending
        self.assignment: None | ExpressionNode = None
        self.value: list[bool] = [False] * dimension
        # The list of buses that the current bus depends on. TODO is that right?
        self.influence_list: list[BitBusDto] = []

    def __str__(self) -> str:
        return (
            f"id: {self.identifier} assign: {self.assignment}"
            f" IL: {[bus for bus in self.influence_list]}"
            f" Value: {self.value}"
        )

    def make_influence_list(self) -> None:
        """This method adds an assignment to the bus."""  # TODO is that right?
        sensitivity_list: list[BitBusDto] = []
        if self.assignment:
            sensitivity_list = self.assignment.get_sensitivity_list()

        for bus in sensitivity_list:
            if self not in bus.influence_list:
                bus.influence_list.append(self)

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
