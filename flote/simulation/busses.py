import re
from abc import ABC, abstractmethod
from typing import Any, Optional

class Evaluator(ABC):
    """Base class for all evaluators."""
    @abstractmethod
    def evaluate(self) -> Any:
        """Evaluate the expression."""
        pass


class VcdValue(ABC):
    """This base class represents a value that can be represented in a VCD file."""
    @abstractmethod
    def get_vcd_repr(self) -> str:
        pass


class BusValue(VcdValue):
    """This class represents a value in the circuit."""
    def __init__(self, value=None) -> None:
        self.value: Any = self.get_default() if value is None else value

    @abstractmethod
    def get_default(self) -> Any:
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


class Bus(Evaluator):
    """This class represents a bus in the circuit."""
    def __init__(self) -> None:
        # The assignment of the bus. It can be an expression or None.
        self.assignment: Optional[Evaluator | BusValue] = None
        self.value: BusValue = self.get_default()  # The value of the bus.
        # The list of buses that the current bus depends on.
        self.sensitivity_list: list[str] = []

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

    def evaluate(self):
        return self.value

    def assign(self):
        """Do the assignment of the bus when not None."""
        if self.assignment:
            self.value = self.assignment.evaluate()


class BitBusValue(BusValue):
    """This class represents a value of a BitBus."""
    def __repr__(self):
        return f'{self.value}'

    def get_vcd_repr(self):
        value = ''.join(['1' if bit else '0' for bit in self.value])

        return value

    def get_default(self) -> list[bool]:
        return [False]

    #* Operators overloading
    def __invert__(self) -> 'BitBusValue':
        assert self.value is not None

        return BitBusValue([not bit for bit in self.value])

    def __and__(self, other: 'BitBusValue') -> 'BitBusValue':
        assert self.value is not None
        if len(self.value) != len(other.value):
            raise ValueError("BitBusValue operands must have the same length")
        return BitBusValue([a and b for a, b in zip(self.value, other.value)])

    def __or__(self, other: 'BitBusValue') -> 'BitBusValue':
        if len(self.value) != len(other.value):
            #TODO Remove, this  should be handled in elaboration phase.
            raise ValueError("BitBusValue operands must have the same length")
        return BitBusValue([a or b for a, b in zip(self.value, other.value)])

    def __xor__(self, other: 'BitBusValue') -> 'BitBusValue':
        return BitBusValue([a ^ b for a, b in zip(self.value, other.value)])
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
        if re.match(r'^\"[01]+\"$', value):
            raise ValueError(
                f'Invalid value "{value}". Valid values are: '
                f'{self.get_valid_values()}'
            )

        self.value = BitBusValue([bool(int(bit)) for bit in value.strip('"')])

    def __repr__(self):
        return (
            f'Assignment: {self.assignment}, Current Value: '
            f'{self.value}, SL: {self.sensitivity_list}'
        )
