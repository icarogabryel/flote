import re
from abc import ABC, abstractmethod
from typing import Any, Optional


class Evaluator(ABC):
    """Base class for all evaluators."""
    @abstractmethod
    def evaluate(self) -> 'BusValue':
        """Evaluate the expression."""
        pass


class SimulationError(Exception):
    """This class represents an error in the simulation."""
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class VcdValue(ABC):
    """This base class represents a value that can be represented in a VCD file."""
    @abstractmethod
    def get_vcd_repr(self) -> str:
        pass


class BusValue(VcdValue):
    """This class represents a value in the circuit."""
    def __init__(self, value=None) -> None:
        self.raw_value: Any = self.get_default() if value is None else value

    @abstractmethod
    def get_default(self) -> Any:
        pass

    @abstractmethod
    def __getitem__(self, index) -> 'BusValue':
        pass

    @abstractmethod
    def __invert__(self) -> 'BusValue':
        pass

    @abstractmethod
    def __and__(self, other: 'BusValue') -> 'BusValue':
        pass

    @abstractmethod
    def __or__(self, other: 'BusValue') -> 'BusValue':
        pass

    @abstractmethod
    def __xor__(self, other: 'BusValue') -> 'BusValue':
        pass


class Bus(ABC):
    """This class represents a bus in the circuit."""
    def __init__(self) -> None:
        # Id to help debugging
        self.id: Optional[str] = None  # The id of the bus.
        # The assignment of the bus. It can be an expression or None.
        self.assignment: Optional[Evaluator] = None
        self.value: BusValue = self.get_default()  # The value of the bus.
        # The list of buses that the current bus depends on.
        self.influence_list: list[Bus] = []

    def __str__(self) -> str:
        return (
            f'id: {self.id} assign: {self.assignment} IL: {[bus.id for bus in self.influence_list]}'
            f' Value: {self.value}'
        )

    def __repr__(self) -> str:
        return self.__str__()

    @abstractmethod
    def get_default(self) -> BusValue:
        """This method returns the default value of the bus."""
        pass

    @abstractmethod
    def get_valid_values(self) -> list[str]:
        """This method returns the valid values for the bus."""
        pass

    @abstractmethod
    def insert_value(self, value) -> None:
        """This method inserts a value into the bus if it is valid"""
        pass

    def assign(self):
        """Do the assignment of the bus when not None."""
        if self.assignment:
            self.value = self.assignment.evaluate()


class BitBusValue(BusValue):
    """This class represents a value of a BitBus."""
    def __repr__(self):
        return f'{self.raw_value}'

    def get_vcd_repr(self):
        value = ''.join(['1' if bit else '0' for bit in self.raw_value])

        return value

    def get_default(self) -> list[bool]:
        return [False]

    #* Operators overloading
    def __getitem__(self, index) -> 'BitBusValue':
        return self.raw_value[index]

    def __invert__(self) -> 'BitBusValue':
        return BitBusValue([not bit for bit in self.raw_value])

    def __and__(self, other) -> 'BitBusValue':
        return BitBusValue([a and b for a, b in zip(self.raw_value, other.raw_value)])

    def __or__(self, other) -> 'BitBusValue':
        return BitBusValue([a or b for a, b in zip(self.raw_value, other.raw_value)])

    def __xor__(self, other) -> 'BitBusValue':
        return BitBusValue([a ^ b for a, b in zip(self.raw_value, other.raw_value)])
    #* End of operators overloading


class BitBus(Bus):
    """This class represents a bit bus in the circuit."""
    def get_default(self) -> BitBusValue:
        return BitBusValue()

    def set_dimension(self, dimension: int) -> None:
        self.value = BitBusValue([False] * dimension)

    def get_valid_values(self) -> list[str]:
        return ['[01]+']

    def insert_value(self, value: str) -> None:
        if not re.fullmatch(r'[01]+', value):
            raise SimulationError(
                f'Invalid value "{value}". Valid values are: '
                f'{self.get_valid_values()}'
            )

        if len(value) != len(self.value.raw_value):
            raise SimulationError(
                f'Invalid value "{value}". The value must have '
                f'{len(self.value.raw_value)} bits.'
            )

        self.value = BitBusValue([bool(int(bit)) for bit in value.strip('"')])
