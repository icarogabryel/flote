import re
from abc import ABC, abstractmethod


def _mask(width: int) -> int:
    """Máscara com `width` bits ligados."""
    return (1 << width) - 1


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
    """Valor de um BitBus: largura + inteiro com os bits.

    Posição 0 é o bit mais à esquerda (MSB), igual à antiga lista de bools.
    """

    __slots__ = ("width", "bits")

    def __init__(self, width: int = 1, bits: int = 0) -> None:
        self.width = width
        self.bits = bits & _mask(width)

    @classmethod
    def _raw(cls, width: int, bits: int) -> "BitBusValue":
        """Caminho rápido: `bits` já está dentro da largura."""
        value = object.__new__(cls)
        value.width = width
        value.bits = bits
        return value

    def __repr__(self) -> str:
        return f"{self.width}'b{self.bits:0{self.width}b}"

    def get_vcd_repr(self) -> str:
        return f"{self.bits:0{self.width}b}"

    @property
    def raw_value(self) -> list[bool]:  # TODO still necessary?
        """Só para compatibilidade/debug. Lento, evite no caminho quente."""
        return [bool(c == "1") for c in self.get_vcd_repr()]

    def _validate_width(self, other: "BitBusValue") -> None:
        if self.width != other.width:
            raise SimulationError(
                f"Width mismatch: {self.width} bits vs {other.width} bits."
            )

    # Operators overloading

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BitBusValue):
            return NotImplemented
        return self.width == other.width and self.bits == other.bits

    def __hash__(self) -> int:
        return hash((self.width, self.bits))

    def __getitem__(self, key: slice) -> "BitBusValue":
        start, stop = key.start, key.stop
        if start < 0 or stop > self.width or stop <= start:
            raise SimulationError(
                f"Invalid range [{start}:{stop}] for {self.width} bits."
            )
        new_width = stop - start
        return self._raw(
            new_width, (self.bits >> (self.width - stop)) & _mask(new_width)
        )

    def __add__(self, other: "BitBusValue") -> "BitBusValue":
        """Concatenação: self fica nos bits altos."""
        return self._raw(
            self.width + other.width, (self.bits << other.width) | other.bits
        )

    def __invert__(self) -> "BitBusValue":
        return self._raw(self.width, ~self.bits & _mask(self.width))

    def __and__(self, other: "BitBusValue") -> "BitBusValue":
        self._validate_width(other)
        return self._raw(self.width, self.bits & other.bits)

    def __or__(self, other: "BitBusValue") -> "BitBusValue":
        self._validate_width(other)
        return self._raw(self.width, self.bits | other.bits)

    def __xor__(self, other: "BitBusValue") -> "BitBusValue":
        self._validate_width(other)
        return self._raw(self.width, self.bits ^ other.bits)


class BitBus:
    """This class represents a bit bus in the circuit."""

    def __init__(self) -> None:
        self.id: None | str = None
        self.assignment: None | Evaluator = None
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

    def set_dimension(self, dimension: int) -> None:  # TODO check if this make sense
        self.value = BitBusValue(dimension)

    def get_valid_values(self) -> list[str]:
        """This method returns the valid values for the bus."""
        return ["[01]+"]

    def insert_value(self, value: str) -> None:  # TODO check if this is the best way
        """This method inserts a value into the bus if it is valid"""
        if not re.fullmatch(r"[01]+", value):
            raise SimulationError(
                f'Invalid value "{value}". Valid values are: {self.get_valid_values()}'
            )

        if len(value) != self.value.width:
            raise SimulationError(
                f'Invalid value "{value}". The value must have {self.value.width} bits.'
            )

        self.value = BitBusValue(len(value), int(value, 2))

    def assign(self) -> None:
        """Do the assignment of the bus when not None."""
        if self.assignment:
            self.value = self.assignment.evaluate()
