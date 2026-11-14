"""Build netlist relationships for the dataclass IR."""

from flote.ir.buses import BitBusDto
from flote.ir.component import ComponentDto
from flote.ir.expression import (
    BinaryOperationDto,
    ConcDto,
    ConstDto,
    ExpressionDto,
    RefDto,
    UnaryOperationDto,
)


def calculate_sensitivity_list(
    expression: ExpressionDto | None,
) -> list[BitBusDto]:
    """Return the buses referenced by an expression."""
    if expression is None or isinstance(expression, ConstDto):
        return []

    if isinstance(expression, RefDto):
        return [expression.bus]

    if isinstance(expression, ConcDto):
        sensitivity_list: list[BitBusDto] = []
        for expr in expression.exprs:
            sensitivity_list.extend(calculate_sensitivity_list(expr))
        return sensitivity_list

    if isinstance(expression, UnaryOperationDto):
        return calculate_sensitivity_list(expression.expr)

    if isinstance(expression, BinaryOperationDto):
        return calculate_sensitivity_list(
            expression.l_expr
        ) + calculate_sensitivity_list(expression.r_expr)

    raise TypeError(f"Unsupported expression DTO: {type(expression).__name__}")


def calculate_influence_list(
    bus: BitBusDto,
    sensitivity_list: list[BitBusDto],
) -> None:
    """Add the assigned bus to each bus in its sensitivity list."""
    for sensitive_bus in sensitivity_list:
        if not any(
            influenced_bus is bus for influenced_bus in sensitive_bus.influence_list
        ):
            sensitive_bus.influence_list.append(bus)


def make_netlist(component: ComponentDto) -> ComponentDto:
    """Populate influence lists from the component's bus assignments."""
    for bus in component.buses:
        sensitivity_list = calculate_sensitivity_list(bus.assignment)
        calculate_influence_list(bus, sensitivity_list)

    return component
