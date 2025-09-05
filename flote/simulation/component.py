from .busses import Bus


class Component():
    """
    This class represents a circuit component.

    Attributes:
        id (str): The component id/Name.
        bits_dict (dict[str, Bit]): A dictionary with the bits of the
            component.
        influence_list (dict[str, list[str]]): The list of bits that each bit
            influences.
        time (int): The current time of the simulation.
        vcd (str): The vcd file of the simulation.
    """
    def __init__(self, id) -> None:
        self.id: str = id
        self.bus_dict: dict[str, Bus] = {}
        self.inputs: list[str] = []
        self.influence_list: dict[str, list[str]] = {}

    def __repr__(self):
        return f'Component {self.id}: {self.bus_dict}'

    def get_values(self) -> dict[str, str]:
        """
        This method returns the values of the component as a dictionary.
        The keys are the bit names and the values are the bit values.
        """
        return {
            bit_name: str(bit.value) for bit_name, bit in self.bus_dict.items()
        }

    def make_influence_list(self):
        """
        This method creates an adjacency list of the bits of the component.

        Each bit signal is a key and the value is a list of bits that the key
        bit influences. The adjacency list is used to make the bits
        stabilization. If a bit is changed, all bits that depend on it are
        added to the queue.
        """
        for bit in self.bus_dict:  # Create a list in the dict for each bit
            self.influence_list[bit] = []

        for bit in self.bus_dict:  # For each bit in the component
            # For each bit that the current bit are influenced by
            for sensibility_signal in self.bus_dict[bit].sensitivity_list:
                # Add the current bit to the list of bits that the sensibility
                # bit influences
                self.influence_list[sensibility_signal].append(bit)

    def stabilize(self):
        """
        This method stabilizes the bits of the component.

        It is wanted new values (an input stimulus) to the component.
        """
        queue = list(self.bus_dict.keys())  # todo make dont add inputs

        while queue:
            bit_name = queue.pop(0)
            bit = self.bus_dict[bit_name]

            p_value = bit.value
            bit.assign()
            a_value = bit.value

            # Dynamic programming: Only add the bits that changed
            if p_value != a_value:
                for bit_influenced in self.influence_list[bit_name]:
                    if bit_influenced not in queue:
                        queue.append(bit_influenced)

    def update_signals(self, new_values: dict[str, str]) -> None:
        for id, new_value in new_values.items():
            if id in self.inputs:
                # Insert the new value into the bus
                self.bus_dict[id].insert_value(new_value)
            else:  # todo improve logic
                raise KeyError(
                    f'Bit signal "{id}" not found in the component.'
                )

        self.stabilize()
