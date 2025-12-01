import re
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Optional, Self, TypeVar


T = TypeVar('T')


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


class BaseBus(ABC):
    """This is the base class for all buses."""
    def __init__(self) -> None:
        self.id: Optional[str] = None
        self.assignment: Any = None
        self.value: Any = None
        # The list of buses that the current bus depends on.
        self.influence_list: list['BaseBus'] = []

    @abstractmethod
    def assign(self) -> None:
        pass

    @abstractmethod
    def get_vcd_repr(self) -> str:
        pass

    def insert_value(self, value) -> None:
        self.value = value


class HlsBus(BaseBus):
    """This class represents a bus coming from an HLS component."""
    def __init__(
            self,
            id_: str,
            value: Any,
            vcd_repr_func: Callable,
            assignment: None | Callable = None,
            influence_list: list[BaseBus] = [],
    ) -> None:
        super().__init__()
        self.id_ = id_
        self.value = value
        self.assignment = assignment
        self.influence_list: list[BaseBus] = influence_list
        self.vcd_repr_func = vcd_repr_func

    def assign(self) -> None:
        if self.assignment:
            self.value = self.assignment()

    def get_vcd_repr(self) -> str:
        return self.vcd_repr_func(self.value)


class BusValue(Generic[T]):
    """This class represents a value in the circuit."""
    def __init__(self, value: T | None = None) -> None:
        self.raw_value: T = self.get_default() if value is None else value

    @abstractmethod
    def get_default(self) -> T:
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    @abstractmethod
    def __getitem__(self, index) -> Self:
        pass

    @abstractmethod
    def __add__(self, other: Self) -> Self:
        pass

    @abstractmethod
    def __invert__(self) -> Self:
        pass

    @abstractmethod
    def __and__(self, other: Self) -> Self:
        pass

    @abstractmethod
    def __or__(self, other: Self) -> Self:
        pass

    @abstractmethod
    def __xor__(self, other: Self) -> Self:
        pass


class Bus(BaseBus):
    """This class represents a concrete bus in the circuit."""
    def __init__(self) -> None:
        super().__init__()

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

    def assign(self) -> None:
        """Do the assignment of the bus when not None."""
        if self.assignment:
            self.value = self.assignment.evaluate()


class BitBusValue(BusValue[list[bool]]):
    """This class represents a value of a BitBus."""
    def __repr__(self) -> str:
        return f'{self.raw_value}'

    def get_vcd_repr(self) -> str:
        value = ''.join(['1' if bit else '0' for bit in self.raw_value])

        return value

    def get_default(self) -> list[bool]:
        return [False]

    #* Operators overloading
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BitBusValue):
            return NotImplemented
        return self.raw_value == other.raw_value

    def __getitem__(self, slice: slice) -> 'BitBusValue':
        return BitBusValue(self.raw_value[slice])

    def __add__(self, other: 'BusValue[list[bool]]') -> 'BitBusValue':
        return BitBusValue(self.raw_value + other.raw_value)

    def __invert__(self) -> 'BitBusValue':
        return BitBusValue([not bit for bit in self.raw_value])

    def __and__(self, other: 'BusValue[list[bool]]') -> 'BitBusValue':
        return BitBusValue([a and b for a, b in zip(self.raw_value, other.raw_value)])

    def __or__(self, other: 'BusValue[list[bool]]') -> 'BitBusValue':
        return BitBusValue([a or b for a, b in zip(self.raw_value, other.raw_value)])

    def __xor__(self, other: 'BusValue[list[bool]]') -> 'BitBusValue':
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

    def get_vcd_repr(self) -> str:
        return ''.join(['1' if bit else '0' for bit in self.value.raw_value])

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
