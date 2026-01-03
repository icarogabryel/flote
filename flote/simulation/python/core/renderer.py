from json import loads

from . import eval_nodes
from .buses import BaseBus, BitBus, BitBusValue, HlsBus
from .component import Component


class Renderer:
    def __init__(self, ir: str, hls_buses: dict[str, HlsBus] = {}) -> None:
        self.ir = ir
        self.buffer_bus_dict: dict[str, BaseBus] = {}
        self.hls_buses = hls_buses
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

            ref_slice_begin = j_expr['args']['slice_begin']
            ref_slice_end = j_expr['args']['slice_end']

            return eval_nodes.Ref(bus, ref_slice_begin, ref_slice_end)
        elif expr_type == 'not':
            expr = self.render_expr(j_expr['args']['expr'])
            assert expr is not None, "Failed to render NOT expression"

            return eval_nodes.Not(expr)
        elif expr_type == 'conc':
            exprs = j_expr['args']['exprs']
            rendered_exprs = []
            for expr in exprs:
                rendered_expr = self.render_expr(expr)
                assert rendered_expr is not None, "Failed to render CONCAT expression"
                rendered_exprs.append(rendered_expr)

            return eval_nodes.Conc(rendered_exprs)
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
            bus: BaseBus
            type = j_bus['type']

            match type:
                case 'bit_bus':
                    bus = BitBus()
                    bus.id = j_bus['id']
                    bus.value = BitBusValue(j_bus['value'])
                case 'hls_bus':
                    bus = self.hls_buses[j_bus['id']]
                case _:
                    assert False, 'Invalid IR.'

            self.buffer_bus_dict[j_bus['id']] = bus

        for j_bus in j_busses:
            bit_bus = self.buffer_bus_dict[j_bus['id']]

            if bit_bus.__class__ != BitBus: #TODO better way
                for influenced_bus_id in j_bus['influence_list']:
                    influenced_bus = self.buffer_bus_dict[influenced_bus_id]

                    if influenced_bus not in bit_bus.influence_list:
                        bit_bus.influence_list.append(influenced_bus)

            if j_bus['assignment'] is not None:
                assignment = self.render_expr(j_bus['assignment'])

                assert assignment is not None, f"Failed to render assignment for bus {j_bus['id']}"

                bit_bus.assignment = assignment

            for influenced_bus_id in j_bus['influence_list']:
                influenced_bus = self.buffer_bus_dict[influenced_bus_id]

                if influenced_bus not in bit_bus.influence_list:
                    bit_bus.influence_list.append(influenced_bus)

        component.buses = self.buffer_bus_dict

        return component
