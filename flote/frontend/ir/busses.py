"""
This module defines the bus representation in the intermediate representation with the Base Bus
class and its std subclasses.
"""
from abc import abstractmethod
from typing import Any, Optional

from .expr_node import ExprNode
from .representation import JsonRepresentation


class BusValueDto(JsonRepresentation):
    """This class represents a value in the circuit."""
    def __init__(self, value=None) -> None:
        self.raw_value: Any = self.get_default() if value is None else self.format_value(value)

    @abstractmethod
    def get_default(self) -> Any:
        pass

    @abstractmethod
    def format_value(self, value: Any) -> Any:
        """Converts the input string to the internal representation."""
        pass


class BusDto(JsonRepresentation):
    """This class represents a bus in the circuit."""
    def __init__(self) -> None:
        self.id_: Optional[str] = None  # The id of the bus.
        # The assignment of the bus. It can be an expression or None.
        self.assignment: Optional[ExprNode] = None
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
        if self.assignment is None:
            assignment_json = None
        else:
            assignment_json = self.assignment.to_json()

        #TODO add type of bus
        return {
            'id': self.id_,
            'assignment': assignment_json,
            'value': self.value.to_json(),
            'influence_list': [bus.id_ for bus in self.influence_list]
        }

    def make_influence_list(self) -> None:
        """This method adds an assignment to the bus."""
        sensitivity_list = self.assignment.get_sensitivity_list() if self.assignment else []

        for bus in sensitivity_list:
            if self not in bus.influence_list:
                bus.influence_list.append(self)


class BitBusValueDto(BusValueDto):
    """This class represents a value of a BitBus."""
    def __repr__(self):
        return f'{self.raw_value}'

    def get_default(self) -> list[bool]:
        return [False]

    def format_value(self, value: str) -> list[bool]:
        """Converts the input string to a list of booleans."""
        formatted_value = []

        for char in value.strip('"'):
            if char == '0':
                formatted_value.append(False)
            elif char == '1':
                formatted_value.append(True)
            else:
                assert False, f'Invalid bit value: {char}'

        return formatted_value

    def to_json(self) -> dict[str, Any]:
        return {'bit_bus_value': self.raw_value}


class BitBusDto(BusDto):
    """This class represents a bit bus in the circuit."""
    def get_default(self) -> BitBusValueDto:
        return BitBusValueDto()

    def set_dimension(self, dimension: int) -> None:
        self.value = BitBusValueDto([False] * dimension)
