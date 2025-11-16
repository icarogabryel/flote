"""Data transfer object for a component."""
from __future__ import annotations

from typing import Any, Generic, TypeVar

from .buses import BaseBusDto, BusDto, HlsBusDto
from .representation import JsonRepresentation

BusType = TypeVar('BusType')


class BaseComponentDto(Generic[BusType], JsonRepresentation):
    """This class represents a component in the circuit."""
    def __init__(self, id_: str) -> None:
        self.id_: str = id_
        self.busses: list[BusType] = []


class ComponentDto(BaseComponentDto[BusDto | HlsBusDto]):
    def __init__(self, id_: str) -> None:
        super().__init__(id_)

    def __repr__(self):
        return '\n'.join([bus.__str__() for bus in self.busses])

    def __str__(self) -> str:
        return f'Component {self.id_}:\n{self.__repr__()}'

    def add_subcomponent(self, subcomponent: ComponentDto | HlsComponentDto, alias: str) -> None:
        """Add a subcomponent to this component."""
        for bus in subcomponent.busses:
            bus.id_ = f'{alias}.{bus.id_}'
            self.busses.append(bus)

    def make_influence_lists(self) -> None:
        """Create influence lists for all buses in the component."""
        for bus in self.busses:
            if isinstance(bus, BusDto):
                bus.make_influence_list()

    def to_json(self):
        return {
            'component': {
                'id': self.id_,
                'busses': [bus.to_json() for bus in self.busses],
            }
        }


class HlsComponentDto(BaseComponentDto[HlsBusDto]):
    def __init__(self, id_: str):
        super().__init__(id_)

    def to_json(self) -> None | dict[str, Any]:
        return {
            'hls_component': {
                'id': self.id_,
                'busses': [bus.to_json() for bus in self.busses],
            }
        }
