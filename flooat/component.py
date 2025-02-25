class Bit:
    """This class represents a bit signal in the circuit."""

    def __init__(self):
        self.assignment = None  # The assignment of the bit. It can be an expression or None.
        self.value: bool = False  # The binary value of the bit.
        self.sensitivity_list: list[str] = []  # The list of bits that the current bit value depends on.

    #* Operators overloading
    def __invert__(self) -> bool:
        return not self.value

    def __and__(self, other: 'Bit') -> bool:
        return self.value and other.value

    def __or__(self, other: 'Bit') -> bool:
        return self.value or other.value

    def __xor__(self, other: 'Bit') -> bool:
        return self.value ^ other.value
    #* End of operators overloading

    def __repr__(self):
        return f'Assign: {self.assignment}, Current Value: {self.value}, SL: {self.sensitivity_list}'
    
    def assign(self):
        """Do the assignment of the bit when not None."""

        if self.assignment:
            self.value = self.assignment()


class Component:
    """
    This class represents a circuit component.

    Attributes:
        id (str): The component id/Name.
        bits_dict (dict[str, Bit]): A dictionary with the bits of the component.
        influence_list (dict[str, list[str]]): The list of bits that each bit influences.
        time (int): The current time of the simulation.
        vcd (str): The vcd file of the simulation.
    """

    def __init__(self, id) -> None:
        self.id: str = id
        self.bits_dict: dict[str, Bit] = {}  #todo change to mark inputs and outputs
        self.influence_list: dict[str, list[str]] = {}
        self.time = -1  #todo improve this
        self.vcd = ''  #todo make a class for this

    def __repr__(self):
        return f'Component {self.id}: {self.bits_dict}'

    def make_influence_list(self):
        """
        This method creates an adjacency list of the bits of the component.

        Each bit signal is a key and the value is a list of bits that the key bit influences.
        The adjacency list is used to make the bits stabilization. If a bit is changed,
        all bits that depend on it are added to the queue.
        """

        for bit in self.bits_dict:  # Create a list in the dict for each bit
            self.influence_list[bit] = []

        for bit in self.bits_dict:  # For each bit in the component
            for sensibility_signal in self.bits_dict[bit].sensitivity_list:  # For each bit that the current bit are influenced by
                self.influence_list[sensibility_signal].append(bit)  # Add the current bit to the list of bits that the sensibility bit influences

    def stabilize(self):
        """
        This method stabilizes the bits of the component.

        It is wanted new values (an input stimulus) to the component.
        """

        queue = list(self.bits_dict.keys())  #todo make dont add inputs

        while queue:
            bit_name = queue.pop(0)
            bit = self.bits_dict[bit_name]

            p_value = bit.value
            bit.assign()
            a_value = bit.value

            if p_value != a_value:  # Dynamic programming: Only add the bits that changed
                for bit_influenced in self.influence_list[bit_name]:
                    if bit_influenced not in queue:
                        queue.append(bit_influenced)

    def input(self, new_values: dict[str, bool]) -> None:
        for id, new_value in new_values.items():
            if id in self.bits_dict:
                self.bits_dict[id].value = new_value
            else:
                raise KeyError(f"Bit signal '{id}' not found in the component.")

        self.stabilize()

        self.update_vcd()  #todo change to a class object

    def update_vcd(self):  #todo remove
        self.time += 1  #todo make custom
        vcd = f'#{self.time}\n\n'

        for bit in self.bits_dict.keys():
            vcd += f'b{int(self.bits_dict[bit].value)} {bit}\n'

        vcd += '\n'

        self.vcd += vcd

    def save_vcd(self, file_name: str = None) -> None:  #todo remove
        if file_name is None:
            file_name = self.id
        
        #make vcd header
        vcd = f'$timescale 1 ns $end\n\n$scope module {self.id} $end\n'

        for bit in self.bits_dict:
            vcd += f'$var wire 1 {bit} {bit} $end\n'

        self.update_vcd()

        vcd += '\n$upscope $end\n\n$enddefinitions $end\n\n'

        self.vcd = vcd + self.vcd

        with open(f'{file_name}.vcd', 'w') as f:
            f.write(self.vcd)
