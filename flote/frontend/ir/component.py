"""Data transfer object for a component."""
from .busses import BusDto
from .representation import JsonRepresentation


class ComponentDto(JsonRepresentation):
    def __init__(self, id_: str) -> None:
        self.id_: str = id_
        self.busses: list[BusDto] = []

    def __repr__(self):
        return f'{'\n'.join([bus.__str__() for bus in self.busses])}'

    def __str__(self) -> str:
        return f'Component {self.id_}:\n{self.__repr__()}'

    def to_json(self):
        return {
            'component': {
                'id': self.id_,
                'busses': [bus.to_json() for bus in self.busses],
            }
        }
