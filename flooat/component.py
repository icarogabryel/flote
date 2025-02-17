class Bit:
    assignment = None
    value: bool = False
    sensitivity_list: list[str] = []

    def __invert__(self) -> bool:
        return not self.value

    def __and__(self, other: 'Bit') -> bool:
        return self.value and other.value

    def __or__(self, other: 'Bit') -> bool:
        return self.value or other.value

    def __xor__(self, other: 'Bit') -> bool:
        return self.value ^ other.value

    def __repr__(self):
        return f'Bit({self.assignment}, v{self.value}, sl{self.sensitivity_list})'


class Component:
    def __init__(self, id) -> None:
        self.id: str = id
        self.bits_dict: dict[str, Bit] = {}  #todo change to mark inputs and outputs
        self.time = -1  #todo improve this
        self.vcd = ''  #todo make a class for this

    def __repr__(self):
        return f'Component({self.id}, {self.bits_dict})'

    def make_adj_list(self, bits_dict: dict[str, Bit]) -> dict[str, list[str]]:
        influence_list: dict[str, list[str]] = {}

        for bit in bits_dict:
            influence_list[bit] = []

        for bit in bits_dict:
            for sensibility in bits_dict[bit].sensitivity_list:
                influence_list[sensibility].append(bit)

        return influence_list

    def get_value(self, assign) -> bool:  #! delete this
        if (type := assign.__class__.__name__) == 'Signal':
            return self.bits_dict[assign.id].value
        elif type == 'UnaryOp':
            if assign.op == 'not':
                return not self.get_value(assign.expr)
        elif type == 'BinaryOp':
            if assign.op == 'and':
                return self.get_value(assign.l_expr) and self.get_value(assign.r_expr)
            elif assign.op == 'or':
                return self.get_value(assign.l_expr) or self.get_value(assign.r_expr)
            elif assign.op == 'xor':
                return self.get_value(assign.l_expr) ^ self.get_value(assign.r_expr)
            elif assign.op == 'nand':
                return not (self.get_value(assign.l_expr) and self.get_value(assign.r_expr))
        else:
            raise NotImplementedError(f'{assign.__class__.__name__} Operation {type} not implemented') #! resolve this
        
    def assign(self, bit: Bit) -> None:  #! delete this
        if bit.assignment is None:
            print(f'{bit} is none')
        else:
            bit.value = bit.assignment()

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

    def input(self, new_values: dict[str, bool]) -> None:  #todo improve: make only inputs
        for value in new_values.keys():
            self.bits_dict[value].value = new_values[value]
            # self.bits_dict[value].is_stabilized = True
            # self.bits_dict[value].is_changed = True

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
