from collections import deque

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


class Circuit():
    """This class represents a circuit component."""
    def __init__(self, busses: dict[str, Bus] = {}) -> None:
        self.busses = busses
        self.interface = None
        self.inputs = []

    def __repr__(self):
        repr = ''
        for bus_id, bus in self.busses.items():
            repr += f'{bus_id}: {bus} {bus.influence_list}\n'

        return repr

    def get_values(self) -> dict[str, str]:
        """
        This method returns the values of the component as a dictionary.
        The keys are the bit names and the values are the bit values.
        """
        return {
            bit_name: str(bit.value) for bit_name, bit in self.busses.items()
        }

    def stabilize(self):
        """
        This method stabilizes the bits of the component.

        It is wanted new values (an input stimulus) to the component.
        """
        queue = deque(self.busses.values())

        while queue:
            bus = queue.popleft()

            p_value = bus.value
            bus.assign()
            a_value = bus.value

            #TODO Verifica se esse condicional escapa todas as vezes ou não.
            # Dynamic programming: Only add the bits that changed
            if p_value != a_value:
                for bus_influenced in bus.influence_list:
                    if bus_influenced not in queue:
                        queue.append(bus_influenced)

    def update_signals(self, new_values: dict[str, str]) -> None:
        for id, new_value in new_values.items():
            if id in self.inputs:
                # Insert the new value into the bus
                self.busses[id].insert_value(new_value)
            else:  # todo improve logic
                raise KeyError(
                    f'Bit signal "{id}" not found in the component.'
                )

        self.stabilize()
