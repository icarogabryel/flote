import re
from abc import ABC, abstractmethod
from typing import Any, Optional, Union

from .operations import Operations, Evaluator

BusValue = Union['BitBusValue']
Assignment = Union[Operations, BusValue]


class Bus(ABC):
    """This class represents a bus in the circuit."""
    def __init__(self) -> None:
        # The assignment of the bus. It can be an expression or None.
        self.assignment: Optional[Assignment] = None
        self.value: Any = self.get_default()  # The value of the bus.
        # The list of buses that the current bus depends on.
        self.sensitivity_list: list[str] = []

    @abstractmethod
    def get_default(self) -> Any:
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


class BitBusValue(Evaluator):
    """This class represents a value of a BitBus."""
    def __init__(self, value: list[bool] = [False]) -> None:
        self.value = value

    def __repr__(self):
        return f'{self.value}'

    def __str__(self):
        return f'{self.value}'

    # * Operators overloading
    def __invert__(self) -> 'BitBusValue':
        return BitBusValue([not bit for bit in self.value])

    def __and__(self, other: 'BitBusValue') -> 'BitBusValue':
        if len(self.value) != len(other.value):
            raise ValueError("BitBusValue operands must have the same length")
        return BitBusValue([a and b for a, b in zip(self.value, other.value)])

    def __or__(self, other: 'BitBusValue') -> 'BitBusValue':
        if len(self.value) != len(other.value):
            raise ValueError("BitBusValue operands must have the same length")
        return BitBusValue([a or b for a, b in zip(self.value, other.value)])

    def __xor__(self, other: 'BitBusValue') -> 'BitBusValue':
        return BitBusValue([a ^ b for a, b in zip(self.value, other.value)])
    # * End of operators overloading

    def evaluate(self):
        """Evaluate the bus value based on its assignment."""
        return self.value


class BitBus(Bus):
    """This class represents a bit bus in the circuit."""
    def get_default(self) -> BitBusValue:
        return BitBusValue()

    def set_dimension(self, dimension: int) -> None:
        self.value = BitBusValue([False] * dimension)

    def get_valid_values(self) -> list[str]:
        return ['[01]+']

    def insert_value(self, value: str) -> None:
        if re.match(r'^\"[01]+\"$', value):
            raise ValueError(
                f'Invalid value "{value}". Valid values are: '
                f'{self.get_valid_values()}'
            )

        self.value = BitBusValue([bool(int(bit)) for bit in value.strip('"')])

    def __repr__(self):
        return (
            f'Assigned: {self.assignment}, Current Value: '
            f'{self.value}, SL: {self.sensitivity_list}'
        )
