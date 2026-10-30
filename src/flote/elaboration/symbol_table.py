from flote.elaboration import ast_nodes
from flote.elaboration.ir.buses import BusDto
from flote.elaboration.ir.component import ComponentDto

# TODO refactor __str__ and __repr__ of this module


class BusSymbol:
    """Class that represents a bus symbol."""

    def __init__(
        self,
        type: str,
        is_assigned: bool,
        connection_type: ast_nodes.Connection,
        size: int,
        msb_descending: bool,
        object_: BusDto,
    ) -> None:
        self.type = type
        self.is_assigned = is_assigned
        self.connection_type = connection_type
        self.size = size
        self.msb_descending = msb_descending
        self.object_ = object_

        self.is_read: bool = False
        self.is_lower_lvl: bool = False

    def __str__(self) -> str:
        return (
            f"| {self.type} | {self.is_assigned} | {self.connection_type} | {self.size}"
            f" | {self.is_read} | {self.is_lower_lvl} | {self.msb_descending} |"
        )


class ComponentSymbol:
    """Class that represents a component symbol."""

    def __init__(self) -> None:  # TODO see if is better with constructor
        self.bus_symbols: dict[str, BusSymbol] = {}
        self.object_: ComponentDto | None = None

    def __str__(self) -> str:
        return "\n".join(
            f"| {bus_id} | {bus_symbol} |"
            for bus_id, bus_symbol in self.bus_symbols.items()
        )


class SymbolTable:
    """Class that represents the symbol table formed in the builder."""

    def __init__(self) -> None:
        self.component_symbols: dict[str, ComponentSymbol] = {}

    def __str__(self) -> str:
        return "\n".join(
            f"Component: {comp_id}\n{comp_table}"
            for comp_id, comp_table in self.component_symbols.items()
        )
