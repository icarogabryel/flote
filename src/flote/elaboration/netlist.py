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
) -> list[str]:
    """Return the buses referenced by an expression."""
    if expression is None or isinstance(expression, ConstDto):
        return []

    if isinstance(expression, RefDto):
        return [expression.bus]

    if isinstance(expression, ConcDto):
        sensitivity_list: list[str] = []
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
    bus_identifier: str,
    sensitivity_list: list[str],
    buses_by_id: dict[str, BitBusDto],
) -> None:
    """Add the assigned bus to each bus in its sensitivity list."""
    for sensitive_bus_id in sensitivity_list:
        sensitive_bus = buses_by_id[sensitive_bus_id]
        if bus_identifier not in sensitive_bus.influence_list:
            sensitive_bus.influence_list.append(bus_identifier)


def make_netlist(component: ComponentDto) -> ComponentDto:
    """Populate influence lists from the component's bus assignments."""
    buses_by_id = {bus.identifier: bus for bus in component.buses}
    for bus in component.buses:
        sensitivity_list = calculate_sensitivity_list(bus.assignment)
        calculate_influence_list(bus.identifier, sensitivity_list, buses_by_id)

    return component
