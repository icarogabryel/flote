"""Data transfer object for a component."""
from .busses import BusDto
from .representation import JsonRepresentation


class ComponentDto(JsonRepresentation):
    def __init__(self, id_: str) -> None:
        self.id_: str = id_
        self.busses: list[BusDto] = []

    def __repr__(self):
        return '\n'.join([bus.__str__() for bus in self.busses])

    def __str__(self) -> str:
        return f'Component {self.id_}:\n{self.__repr__()}'

    def add_subcomponent(self, subcomponent: 'ComponentDto', alias: str) -> None:
        """Add a subcomponent to this component."""
        for bus in subcomponent.busses:
            bus.id_ = f'{alias}.{bus.id_}'
            self.busses.append(bus)

    def make_influence_lists(self) -> None:
        """Create influence lists for all buses in the component."""
        for bus in self.busses:
            bus.make_influence_list()

    def to_json(self):
        return {
            'component': {
                'id': self.id_,
                'busses': [bus.to_json() for bus in self.busses],
            }
        }
