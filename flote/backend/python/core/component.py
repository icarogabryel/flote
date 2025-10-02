from collections import deque

from .busses import Bus


class Component():
    """This class represents a component."""
    def __init__(self, id_: str) -> None:
        self.id_: str = id_
        self.busses: dict[str, Bus] = {}

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
            self.busses[id].insert_value(new_value)

        self.stabilize()
