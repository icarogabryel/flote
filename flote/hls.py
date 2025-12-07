"""
Interfaces to create HLD components and busses easily by the users and translate the data to
Builder and Renderer friendly.
"""
from typing import Any, Callable

from .backend.python.core.buses import BaseBus, HlsBus
from .frontend.ast_nodes import Connection
from .frontend.symbol_table import BusSymbol


class Bus:
    def __init__(
        self,
        id_: str,
        size: int,
        assignment=None,
        initial_value: Any = 0,
        influence_list: list[BaseBus] = [],
        vcd_repr_func: Callable = lambda x: str(x)
    ) -> None:
        self.id_ = id_
        self.size = size
        self.initial_value = initial_value
        self.assignment = assignment
        self.connection_type = Connection.INPUT if self.assignment is None else Connection.OUTPUT

        if (self.connection_type == Connection.OUTPUT) and (len(influence_list) > 0):
            raise ValueError('Input bus cannot have influence list.')

        self.influence_list = influence_list
        self.vcd_repr_func = vcd_repr_func

    def get_symbol(self) -> BusSymbol:
        symbol = BusSymbol(
            type=None,
            #! Trate if is input and have assignment -> error
            is_assigned=self.assignment is not None,
            connection_type=self.connection_type,
            size=self.size
        )
        symbol.is_lower_lvl = True

        return symbol

    def get_bus(self) -> HlsBus:
        return HlsBus(
            id_=self.id_,
            value=self.initial_value,
            assignment=self.assignment,
            influence_list=self.influence_list,
            vcd_repr_func=self.vcd_repr_func
        )


class Component:
    def __init__(self, id_: str, buses: list[Bus]) -> None:
        self.id_ = id_
        self.buses = buses

    def render(self) -> tuple[dict[str, BusSymbol], list[HlsBus]]:
        bus_symbols: dict[str, BusSymbol] = {}
        hls_buses: list[HlsBus] = []

        for bus in self.buses:
            bus_symbol = bus.get_symbol()
            bus_symbols[bus.id_] = bus_symbol

            hls_bus = bus.get_bus()
            hls_bus.id_ = bus.id_
            hls_buses.append(hls_bus)

        return bus_symbols, hls_buses
