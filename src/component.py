from parser import Assign, Expr


class Bit:  #todo create constructor
    assignment: Assign = Expr()  #todo change to None
    value: bool = False
    is_stabilized = False
    is_changed = False
    sensitivity_list: list[str] = []

    def __repr__(self):
        return f'Bit({self.assignment}, {self.value}, {self.is_stabilized}, {self.is_changed}, {self.sensitivity_list})'


class Component:
    def __init__(self, id) -> None:
        self.id: str = id
        self.bits_dict: dict[str, Bit] = {}  #todo change to mark inputs and outputs
        self.time = -1  #todo improve this
        self.vcd = ''

    def __repr__(self):
        return f'Component({self.id}, {self.bits_dict})'

    def assign(self, bit: Bit) -> None:
        match bit.assignment.op:
            case 'none':
                pass
            case 'and':
                bit.value = self.bits_dict[bit.assignment.l_expr].value & self.bits_dict[bit.assignment.r_expr].value
            case 'or':
                bit.value = self.bits_dict[bit.assignment.l_expr].value | self.bits_dict[bit.assignment.r_expr].value
            case 'xor':
                bit.value = self.bits_dict[bit.assignment.l_expr].value ^ self.bits_dict[bit.assignment.r_expr].value

        bit.is_changed = True
        bit.is_stabilized = True

    def stabilize(self):
        are_all_bits_stabilized = False

        while not are_all_bits_stabilized:
            for bit in self.bits_dict.values(): # Check if all bits are stabilized
                if not bit.is_stabilized:

                    self.assign(bit)

            for bit in self.bits_dict.values(): # Check if the sensibility list has changed values
                for sensibility_bit in bit.sensitivity_list:
                    if self.bits_dict[sensibility_bit].is_changed:
                        bit.is_stabilized = False
                        
                        break
            else:
                are_all_bits_stabilized = True

            for bit in self.bits_dict.values():
                bit.is_changed = False

    def input(self, new_values: dict[str, bool]) -> None:
        for value in new_values.keys():
            self.bits_dict[value].value = new_values[value]
            self.bits_dict[value].is_stabilized = True
            self.bits_dict[value].is_changed = True

        self.stabilize()
        print(self.bits_dict)
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
