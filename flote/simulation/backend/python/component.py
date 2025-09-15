from .busses import Bus


class Component:
    def __init__(self) -> None:
        self.busses: dict[str, Bus] = {}

    def __repr__(self):
        return f'{self.busses}'

    def add_bus(self, bus_id: str, bus: Bus) -> None:
        """
        This method adds a bus to the component.

        Args:
            bus (Bus): The bus to be added.
        """
        assert bus_id not in self.busses, f'Bus with id "{bus_id}" already exists.'

        self.busses[bus_id] = bus

    def add_busses(self, component_id, buses: dict[str, Bus]) -> None:
        """
        This method adds multiple buses to the component.

        Args:
            buses (dict[str, Bus]): The buses to be added.
        """
        for bus_id, bus in buses.items():
            key = f'{component_id}.{bus_id}'
            self.busses[key] = bus

    def add_component(self, component_id: str, component: 'Component') -> None:
        """
        This method adds the busses of a component to the current component.

        Args:
            component (Component): The component to be added.
        """
        for bus_id, bus in component.busses.items():
            new_id = f'{component_id}.{bus_id}'

            assert new_id not in self.busses, f'Bus with id "{new_id}" already exists.'

            self.busses[new_id] = bus
