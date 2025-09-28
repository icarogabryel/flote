"""
This module defines the bus representation in the intermediate representation with the Base Bus
class and its std subclasses.
"""
from abc import abstractmethod
from typing import Any, Optional

from .expr_nodes import ExprNode
from .representation import JsonRepresentation


class BusValueDto(JsonRepresentation):
    """This class represents a value in the circuit."""
    def __init__(self, value=None) -> None:
        self.raw_value: Any = self.get_default() if value is None else value

    @abstractmethod
    def get_default(self) -> Any:
        pass

    def to_json(self):
        return self.raw_value


class BusDto(JsonRepresentation):
    """This class represents a bus in the circuit."""
    def __init__(self) -> None:
        self.id_: Optional[str] = None  # The id of the bus.
        # The assignment of the bus. It can be an expression or None.
        self._assignment: Optional[ExprNode] = None
        self.value: BusValueDto = self.get_default()  # The value of the bus.
        # The list of buses that the current bus depends on.
        self.influence_list: list[BusDto] = []

    def __str__(self) -> str:
        return (
            f'id: {self.id_} assign: {self.assignment}'
            f' IL: {[bus.id_ for bus in self.influence_list]}'
            f' Value: {self.value}'
        )

    def __repr__(self) -> str:
        return self.__str__()

    @abstractmethod
    def get_default(self) -> BusValueDto:
        """This method returns the default value of the bus."""
        pass

    def to_json(self):
        if self._assignment is None:
            assignment_json = None
        else:
            assignment_json = self._assignment.to_json()

        return {
            'id': self.id_,
            'assignment': assignment_json,
            'value': self.value.to_json(),
            'influence_list': [bus.id_ for bus in self.influence_list]
        }

    def set_assignment(self, expr: ExprNode) -> None:
        """This method adds an assignment to the bus."""
        self.assignment = expr

        sensitivity_list = expr.get_sensitivity_list()

        for bus in sensitivity_list:
            if self not in bus.influence_list:
                bus.influence_list.append(self)


class BitBusValueDto(BusValueDto):
    """This class represents a value of a BitBus."""
    def __repr__(self):
        return f'{self.raw_value}'

    def get_default(self) -> list[bool]:
        return [False]


class BitBusDto(BusDto):
    """This class represents a bit bus in the circuit."""
    def get_default(self) -> BitBusValueDto:
        return BitBusValueDto()

    def set_dimension(self, dimension: int) -> None:
        self.value = BitBusValueDto([False] * dimension)
