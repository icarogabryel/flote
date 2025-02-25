from typing import Optional
from .ast import *


class Bit:
    def __init__(self):
        self.assignment: Optional[ExprElem] = None
        self.value: bool = False
        self.sensitivity_list: list[str] = []

    def __invert__(self) -> bool:
        return not self.value

    def __and__(self, other: 'Bit') -> bool:
        return self.value and other.value

    def __or__(self, other: 'Bit') -> bool:
        return self.value or other.value

    def __xor__(self, other: 'Bit') -> bool:
        return self.value ^ other.value

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
        id (str): The component id.
        bits_dict (dict[str, Bit]): A dictionary with the bits of the component.
        time (int): The current time of the simulation.
        vcd (str): The vcd file of the simulation.
    """

    def __init__(self, id) -> None:
        self.id: str = id
        self.bits_dict: dict[str, Bit] = {}  #todo change to mark inputs and outputs
        self.time = -1  #todo improve this
        self.vcd = ''  #todo make a class for this

    def __repr__(self):
        return f'Component({self.id}, {self.bits_dict})'

    def make_adj_list(self, bits_dict: dict[str, Bit]) -> dict[str, list[str]]:
        """
        This method creates an adjacency list of the bits of the component.
        The adjacency list is used to make the bits stabilization. If a bit is changed, all bits that depend on it are added to the queue.

        Args:
        bits_dict (dict[str, Bit]): A dictionary with the bits of the component.
        """

        influence_list: dict[str, list[str]] = {}

        for bit in bits_dict:
            influence_list[bit] = []

        for bit in bits_dict:  # For each bit in the component
            for sensibility in bits_dict[bit].sensitivity_list:  # For each bit that the current bit depends on
                influence_list[sensibility].append(bit)  # Add the current bit to the list of bits that the sensibility bit influences

        return influence_list

    def stabilize(self):
        adj_list = self.make_adj_list(self.bits_dict)
        queue = list(self.bits_dict.keys()) 

        while queue:
            bit_name = queue.pop(0)
            bit = self.bits_dict[bit_name]

            p_value = bit.value
            bit.assign()
            a_value = bit.value

            if p_value != a_value:
                for bit_influenced in adj_list[bit_name]:
                    if bit_influenced not in queue:
                        queue.append(bit_influenced)

    def input(self, new_values: dict[str, bool]) -> None:
        for value in new_values.keys():
            self.bits_dict[value].value = new_values[value]
        self.stabilize()

        for bit in self.bits_dict:
            print(f'{bit}: {self.bits_dict[bit].value}')

        print('\n\n')
        self.update_vcd()

    def update_vcd(self):
        self.time += 1  #todo make custom
        vcd = f'#{self.time}\n\n'

        for bit in self.bits_dict.keys():
            vcd += f'b{int(self.bits_dict[bit].value)} {bit}\n'

        vcd += '\n'

        self.vcd += vcd

    def save_vcd(self, file_name: str = None) -> None:
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

    # add inputs and get outputs
    def get_bits(self):
        return self.bits_dict
