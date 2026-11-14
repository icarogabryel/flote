from flote.ir import expression as ir_expression
from flote.ir.component import ComponentDto
from flote.simulation import expression
from flote.simulation.buses import BitBus, BitBusValue
from flote.simulation.component import Component


def bools_to_value(bits: list[bool]) -> BitBusValue:  # TODO check if has better way?
    """Convert the IR bit list (index 0 = MSB) into a BitBusValue."""
    number = 0
    for bit in bits:
        number = (number << 1) | bool(bit)

    return BitBusValue(len(bits), number)


class Renderer:
    def __init__(self, ir: ComponentDto) -> None:
        self.ir = ir
        self.buffer_bus_dict: dict[str, BitBus] = {}
        self.component = self.render()

    def render_expr(self, expr: ir_expression.ExpressionDto) -> expression.Evaluator:
        """Render an expression from the dataclass intermediate representation."""
        if isinstance(expr, ir_expression.ConstDto):
            value = bools_to_value(expr.value)

            return expression.Const(value)
        elif isinstance(expr, ir_expression.RefDto):
            bus = self.buffer_bus_dict[expr.bus.identifier]
            return expression.Ref(bus, expr.slice_begin, expr.slice_end)
        elif isinstance(expr, ir_expression.NotDto):
            return expression.Not(self.render_expr(expr.expr))
        elif isinstance(expr, ir_expression.ConcDto):
            rendered_exprs: list[expression.Evaluator] = []
            for sub_expr in expr.exprs:
                rendered_exprs.append(self.render_expr(sub_expr))
            return expression.Conc(rendered_exprs)
        elif isinstance(expr, ir_expression.BinaryOperationDto):
            binary_expr_types: dict[
                type[ir_expression.BinaryOperationDto],
                type[expression.BinaryOperation],
            ] = {
                ir_expression.AndDto: expression.And,
                ir_expression.OrDto: expression.Or,
                ir_expression.XorDto: expression.Xor,
                ir_expression.NandDto: expression.Nand,
                ir_expression.NorDto: expression.Nor,
                ir_expression.XnorDto: expression.Xnor,
            }
            for expression_type, evaluator_type in binary_expr_types.items():
                if isinstance(expr, expression_type):
                    return evaluator_type(
                        self.render_expr(expr.l_expr),
                        self.render_expr(expr.r_expr),
                    )

        raise TypeError(f"Unknown expression DTO: {type(expr).__name__}")

    def render(self) -> Component:
        """Render a circuit from a dataclass intermediate representation."""
        component = Component(self.ir.identifier)

        for ir_bus in self.ir.buses:
            bus = BitBus()
            bus.id = ir_bus.identifier
            bus.value = bools_to_value(ir_bus.value)
            bus.msb_descending = ir_bus.msb_descending
            self.buffer_bus_dict[ir_bus.identifier] = bus

        for ir_bus in self.ir.buses:
            bit_bus = self.buffer_bus_dict[ir_bus.identifier]

            if ir_bus.assignment is not None:
                bit_bus.assignment = self.render_expr(ir_bus.assignment)

            for influenced_ir_bus in ir_bus.influence_list:
                influenced_bus = self.buffer_bus_dict[influenced_ir_bus.identifier]
                if influenced_bus not in bit_bus.influence_list:
                    bit_bus.influence_list.append(influenced_bus)

        component.buses = self.buffer_bus_dict

        return component
