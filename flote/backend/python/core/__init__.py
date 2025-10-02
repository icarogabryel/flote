from json import loads

from . import eval_nodes
from .busses import BitBus, BitBusValue, Bus
from .component import Component


class Renderer:
    def __init__(self, ir: str):
        self.ir = ir
        self.buffer_bus_dict: dict[str, Bus] = {}
        self.component = self.render()

    def render_expr(self, j_expr) -> eval_nodes.Evaluator | None:
        """Render an expression from an intermediate representation (IR) json string.

        Args:
            j_expr (dict): The intermediate representation of the expression.

        Returns:
            ExprNode: The rendered expression node.
        """
        expr_type = j_expr['type']

        if expr_type == 'const':
            value = BitBusValue(j_expr['args']['value'])

            return eval_nodes.Const(value)
        elif expr_type == 'ref':
            bus_id = j_expr['args']['id']
            bus = self.buffer_bus_dict[bus_id]
            ref_slice = j_expr['args']['slice']

            return eval_nodes.Ref(bus, ref_slice)
        elif expr_type == 'not':
            expr = self.render_expr(j_expr['args']['expr'])
            assert expr is not None, "Failed to render NOT expression"

            return eval_nodes.Not(expr)
        #TODO also put in a func/dict
        elif expr_type in ('and', 'or', 'xor', 'nand', 'nor', 'xnor'):
            l_expr = self.render_expr(j_expr['args']['l_expr'])
            r_expr = self.render_expr(j_expr['args']['r_expr'])

            if expr_type == 'and':
                assert l_expr is not None, "Failed to render AND left expression"
                assert r_expr is not None, "Failed to render AND right expression"

                return eval_nodes.And(l_expr, r_expr)
            elif expr_type == 'or':
                assert l_expr is not None, "Failed to render OR left expression"
                assert r_expr is not None, "Failed to render OR right expression"

                return eval_nodes.Or(l_expr, r_expr)
            elif expr_type == 'xor':
                assert l_expr is not None, "Failed to render XOR left expression"
                assert r_expr is not None, "Failed to render XOR right expression"

                return eval_nodes.Xor(l_expr, r_expr)
            elif expr_type == 'nand':
                assert l_expr is not None, "Failed to render NAND left expression"
                assert r_expr is not None, "Failed to render NAND right expression"

                return eval_nodes.Nand(l_expr, r_expr)
            elif expr_type == 'nor':
                assert l_expr is not None, "Failed to render NOR left expression"
                assert r_expr is not None, "Failed to render NOR right expression"

                return eval_nodes.Nor(l_expr, r_expr)
            elif expr_type == 'xnor':
                assert l_expr is not None, "Failed to render XNOR left expression"
                assert r_expr is not None, "Failed to render XNOR right expression"

                return eval_nodes.Xnor(l_expr, r_expr)

        else:
            assert False, f'Unknown expression type: {expr_type}'

    def render(self) -> Component:
        """Render a circuit from an intermediate representation (IR) json string.

        Args:
            ir (str): The intermediate representation of the quantum circuit.

        Returns:
            Circuit: The rendered quantum circuit.
        """

        # Parse the IR string to get a structured representation
        j_ir = loads(self.ir)

        j_component = j_ir['component']
        j_component_id = j_component['id']
        component = Component(j_component_id)
        j_busses = j_component['busses']

        for j_bus in j_busses:
            bit_bus = BitBus()
            bit_bus.id = j_bus['id']
            type = j_bus['type']

            #TODO add other types
            if type == 'bit_bus':
                bit_bus.value = BitBusValue(j_bus['value'])
            else:
                assert False, 'Invalid IR.'

            self.buffer_bus_dict[j_bus['id']] = bit_bus

        for j_bus in j_busses:
            bit_bus = self.buffer_bus_dict[j_bus['id']]

            if j_bus['assignment'] is not None:
                assignment = self.render_expr(j_bus['assignment'])

                assert assignment is not None, f"Failed to render assignment for bus {j_bus['id']}"

                bit_bus.assignment = assignment

            for influenced_bus_id in j_bus['influence_list']:
                influenced_bus = self.buffer_bus_dict[influenced_bus_id]

                if influenced_bus not in bit_bus.influence_list:
                    bit_bus.influence_list.append(influenced_bus)

        component.busses = self.buffer_bus_dict

        return component
