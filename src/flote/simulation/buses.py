import re
from abc import ABC, abstractmethod
from typing import Any, Optional


class Evaluator(ABC):
    """Base class for all evaluators."""

    @abstractmethod
    def evaluate(self) -> "BitBusValue":
        """Evaluate the expression."""
        pass


class SimulationError(Exception):
    """This class represents an error in the simulation."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class BitBusValue:
    """This class represents a value of a BitBus."""

    def __init__(self, value: list[bool] | None = None) -> None:
        self.raw_value: list[bool] = self.get_default() if value is None else value

    def __repr__(self) -> str:
        return f"{self.raw_value}"

    def get_vcd_repr(self) -> str:
        value = "".join(["1" if bit else "0" for bit in self.raw_value])

        return value

    def get_default(self) -> list[bool]:
        """This method returns the default value of the bus."""
        return [False]

    # Operators overloading

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BitBusValue):
            return NotImplemented
        return self.raw_value == other.raw_value

    def __getitem__(self, slice: slice) -> "BitBusValue":
        return BitBusValue(self.raw_value[slice])

    def __add__(self, other: "BitBusValue") -> "BitBusValue":
        """Used for concatenation of bus values."""
        return BitBusValue(self.raw_value + other.raw_value)

    def __invert__(self) -> "BitBusValue":
        return BitBusValue([not bit for bit in self.raw_value])

    def __and__(self, other: "BitBusValue") -> "BitBusValue":
        return BitBusValue([a and b for a, b in zip(self.raw_value, other.raw_value)])

    def __or__(self, other: "BitBusValue") -> "BitBusValue":
        return BitBusValue([a or b for a, b in zip(self.raw_value, other.raw_value)])

    def __xor__(self, other: "BitBusValue") -> "BitBusValue":
        return BitBusValue([a ^ b for a, b in zip(self.raw_value, other.raw_value)])


class BitBus:
    """This class represents a bit bus in the circuit."""

    def __init__(self) -> None:
        self.id: Optional[str] = None
        self.assignment: Any = None
        self.value: BitBusValue = self.get_default()
        # The list of buses that the current bus depends on.
        self.influence_list: list["BitBus"] = []
        self.msb_descending = False

    def __str__(self) -> str:
        return (
            f"id: {self.id} assign: {self.assignment} IL: "
            f"{[bus.id for bus in self.influence_list]} Value: {self.value}"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def get_default(self) -> BitBusValue:
        """This method returns the default value of the bus."""
        return BitBusValue()

    def set_dimension(self, dimension: int) -> None:
        self.value = BitBusValue([False] * dimension)

    def get_valid_values(self) -> list[str]:
        """This method returns the valid values for the bus."""
        return ["[01]+"]

    def insert_value(self, value: str) -> None:
        """This method inserts a value into the bus if it is valid"""
        if not re.fullmatch(r"[01]+", value):
            raise SimulationError(
                f'Invalid value "{value}". Valid values are: {self.get_valid_values()}'
            )

        if len(value) != len(self.value.raw_value):
            raise SimulationError(
                f'Invalid value "{value}". The value must have '
                f"{len(self.value.raw_value)} bits."
            )

        self.value = BitBusValue([bool(int(bit)) for bit in value.strip('"')])

    def assign(self) -> None:
        """Do the assignment of the bus when not None."""
        if self.assignment:
            self.value = self.assignment.evaluate()
