"""
This module defines the bus representation in the intermediate representation with the Base Bus
class and its std subclasses.
"""
from abc import abstractmethod
from typing import Any, Generic, Optional, TypeVar

from .expr_node import ExprNode
from .representation import JsonRepresentation

AssignType = TypeVar('AssignType')
ValueType = TypeVar('ValueType')


class BaseBusDto(Generic[AssignType, ValueType], JsonRepresentation):
    """This class represents a bus in the circuit."""
    def __init__(self) -> None:
        self.id_: Optional[str] = None  # The id of the bus.
        self.type: Optional[str] = None  # The type of the bus.
        self.assignment: AssignType | None = None
        self.value: ValueType = self.get_default()  # The value of the bus.
        # The list of buses that the current bus depends on.
        self.influence_list: list[BaseBusDto[AssignType, ValueType]] = []

    def __str__(self) -> str:
        return (
            f'id: {self.id_} assign: {self.assignment}'
            f' IL: {[bus for bus in self.influence_list]}'
            f' Value: {self.value}'
        )

    @abstractmethod
    def get_default(self) -> ValueType:
        """This method returns the default value of the bus."""
        pass


#TODO see if i really need this?
class BusValueDto(JsonRepresentation):
    """This class represents a value in the circuit."""
    def __init__(self, value=None) -> None:
        self.raw_value: Any = self.get_default() if value is None else value

    @abstractmethod
    def get_default(self) -> Any:
        pass


class BusDto(BaseBusDto[ExprNode, BusValueDto]):
    """This class represents a bus in the circuit."""
    def __init__(self) -> None:
        super().__init__()

    def make_influence_list(self) -> None:
        """This method adds an assignment to the bus."""
        sensitivity_list = self.assignment.get_sensitivity_list() if self.assignment else []

        for bus in sensitivity_list:
            if self not in bus.influence_list:
                bus.influence_list.append(self)

    # @abstractmethod
    # def get_default(self) -> BusValueDto:
    #     """This method returns the default value of the bus."""
    #     pass

    # @abstractmethod
    # def to_json(self) -> dict[str, Any]:
    #     pass


class HlsBusDto(BaseBusDto[Any, Any]):
    def __init__(self, id_) -> None:
        super().__init__()
        self.id_ = id_

    def get_default(self) -> None:
        return None

    def to_json(self):
        return {
            'id': self.id_,
            'type': 'hls_bus',
        }


class BitBusValueDto(BusValueDto):
    """This class represents a value of a BitBus."""
    def __repr__(self):
        return f'{self.raw_value}'

    def get_default(self) -> list[bool]:
        return [False]

    def to_json(self) -> dict[str, Any]:
        return self.raw_value


class BitBusDto(BusDto):
    """This class represents a bit bus in the circuit."""
    def __init__(self) -> None:
        super().__init__()
        self.type = 'bit_bus'

    def get_default(self) -> BitBusValueDto:
        return BitBusValueDto()

    def set_dimension(self, dimension: int) -> None:
        self.value = BitBusValueDto([False] * dimension)

    def to_json(self):
        if self.assignment is None:
            assignment_json = None
        else:
            assignment_json = self.assignment.to_json()

        #TODO add type of bus
        return {
            'id': self.id_,
            'type': self.type,
            'value': self.value.to_json(),
            'assignment': assignment_json,
            'influence_list': [bus.id_ for bus in self.influence_list]
        }
