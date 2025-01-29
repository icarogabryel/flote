from .parser import Assign


class Bit:  #todo create constructor
    assignment: Assign = None
    value: bool = False
    sensitivity_list: list[str] = []

    def __repr__(self):
        return f'Bit({self.assignment}, v{self.value}, s{self.is_stabilized}, c{self.is_changed}, sl{self.sensitivity_list})'


class RawComponent:
    def __init__(self, id) -> None:
        self.id: str = id
        self.bits_dict: dict[str, Bit] = {}  #todo change to mark inputs and outputs
        self.time = -1  #todo improve this
        self.vcd = ''

    def __repr__(self):
        return f'Component({self.id}, {self.bits_dict})'

    # def stabilize(self):
    #     are_all_bits_stabilized = False

    #     while not are_all_bits_stabilized:
    #         for bit in self.bits_dict.values(): # Check if all bits are stabilized
    #             if not bit.is_stabilized:

    #                 self.assign(bit)

    #         for bit in self.bits_dict.values(): # Check if the sensibility list has changed values
    #             for sensibility_bit in bit.sensitivity_list:
    #                 if self.bits_dict[sensibility_bit].is_changed:
    #                     bit.is_stabilized = False
                        
    #                     break
            
    #         are_all_bits_stabilized = all(bit.is_stabilized for bit in self.bits_dict.values())

    #         for bit in self.bits_dict.values():
    #             bit.is_changed = False

    def make_adj_list(self, bits_dict: dict[str, Bit]) -> dict[str, list[str]]:
        influence_list: dict[str, list[str]] = {}

        for bit in bits_dict:
            influence_list[bit] = []

        for bit in bits_dict:
            for sensibility in bits_dict[bit].sensitivity_list:
                influence_list[sensibility].append(bit)

        return influence_list

    def stabilize(self):
        adj_list = self.make_adj_list(self.bits_dict)
        queue = list(self.bits_dict.keys())

        while queue:
            bit_name = queue.pop(0)
            bit = self.bits_dict[bit_name]
            p_value = bit.value
            self.assign(bit)
            a_value = bit.value

            if p_value != a_value:
                for bit_influenced in adj_list[bit_name]:
                    if bit_influenced not in queue:
                        queue.append(bit_influenced)

    def input(self, new_values: dict[str, bool]) -> None:
        for value in new_values.keys():
            self.bits_dict[value].value = new_values[value]
            self.bits_dict[value].is_stabilized = True
            self.bits_dict[value].is_changed = True

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

    def save_vcd(self):
        #make vcd header
        vcd = f'$timescale 1 ns $end\n\n$scope module {self.id} $end\n'

        for bit in self.bits_dict:
            vcd += f'$var wire 1 {bit} {bit} $end\n'

        self.update_vcd()

        vcd += '\n$upscope $end\n\n$enddefinitions $end\n\n'

        self.vcd = vcd + self.vcd

        with open(f'{self.id}.vcd', 'w') as f:
            f.write(self.vcd)

    # add inputs and get outputs
    def get_bits(self):
        return self.bits_dict


class Component(RawComponent):
    def __init__(self, id) -> None:
        super().__init__(id)

        self.token_stream
        self.AST

    def get_token_stream(self):
        return self.token_stream