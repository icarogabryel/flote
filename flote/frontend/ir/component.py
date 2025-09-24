from .busses import BusDto
from .representation import Representation


class ComponentDto(Representation):
    def __init__(self, id_: str) -> None:
        self.id_: str = id_  # The id of the component.
        self.busses: list[BusDto] = []
        self.subcomponents: list[ComponentDto] = []

    def __repr__(self):
        return f'{'\n'.join([bus.__str__() for bus in self.busses])}'

    def __str__(self) -> str:
        return f'Component {self.id_}:\n{self.__repr__()}'

    def to_repr(self) -> dict:
        return {
            'component': self.id_,
            'busses': [bus.to_repr() for bus in self.busses],
            'subcomponents': [comp.to_repr() for comp in self.subcomponents]}
