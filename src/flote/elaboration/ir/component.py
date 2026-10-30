"""Data transfer object for a component."""

# TODO refactor __str__ and __repr__ of this module

from typing import Any

from flote.elaboration.ir.buses import BusDto
from flote.elaboration.ir.representation import JsonRepresentation


class ComponentDto(JsonRepresentation):
    """This class represents a component in the circuit."""

    def __init__(self, identifier: str) -> None:
        self.identifier: str = identifier
        self.buses: list[BusDto] = []

    def __repr__(self) -> str:
        return "\n".join([bus.__str__() for bus in self.buses])

    def __str__(self) -> str:
        return f"Component {self.identifier}:\n{self.__repr__()}"

    def add_subcomponent(self, subcomponent: "ComponentDto", alias: str) -> None:
        """Add a subcomponent to this component."""
        for bus in subcomponent.buses:
            bus.identifier = f"{alias}.{bus.identifier}"
            self.buses.append(bus)

    def make_netlist(self) -> None:
        """Create influence lists for all buses in the component."""
        for bus in self.buses:
            bus.make_influence_list()

    def to_json(self) -> dict[str, Any]:
        return {
            "component": {
                "id": self.identifier,
                "buses": [bus.to_json() for bus in self.buses],
            }
        }
