from .ir.busses import BusDto
from .ir.component import ComponentDto


class BusSymbol:
    """Class that represents a bus symbol in the symbol table."""
    def __init__(self, type, is_assigned, connection_type, size: int):
        self.type = type
        self.is_assigned = is_assigned
        self.connection_type = connection_type
        self.size = size
        self.is_read = False
        self.object: None | BusDto = None

    def __repr__(self):
        return (
            f'| {self.type} | {self.is_assigned} | {self.connection_type} | '
            f'{self.is_read} |'
        )


class CompTable:
    """Class that represents a component's symbol table."""
    def __init__(self):
        self.busses: dict[str, BusSymbol] = {}
        self.object: None | ComponentDto = None

    def __str__(self):
        return '\n'.join(
            f'| {bus_id} | {bus_symbol} |'
            for bus_id, bus_symbol in self.busses.items()
        )


class SymbolTable:
    """Class that represents the symbol table formed in the builder."""
    def __init__(self):
        self.components: dict[str, CompTable] = {}

    def __str__(self):
        return '\n'.join(
            f'Component: {comp_id}\n{comp_table}'
            for comp_id, comp_table in self.components.items()
        )
