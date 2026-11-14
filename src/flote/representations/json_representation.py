"""JSON representation for the dataclass intermediate representation."""

from typing import Any

from flote.ir import component, expression


def _expression_to_json(expression_dto: expression.ExpressionDto) -> dict[str, Any]:
    if isinstance(expression_dto, expression.RefDto):
        return {
            "type": "ref",
            "args": {
                "id": expression_dto.bus.identifier,
                "slice_begin": expression_dto.slice_begin,
                "slice_end": expression_dto.slice_end,
            },
        }

    if isinstance(expression_dto, expression.ConstDto):
        return {"type": "const", "args": {"value": expression_dto.value}}

    if isinstance(expression_dto, expression.ConcDto):
        return {
            "type": "conc",
            "args": {
                "exprs": [_expression_to_json(expr) for expr in expression_dto.exprs]
            },
        }

    if isinstance(expression_dto, expression.NotDto):
        return {
            "type": "not",
            "args": {"expr": _expression_to_json(expression_dto.expr)},
        }

    binary_types: dict[type[expression.BinaryOperationDto], str] = {
        expression.AndDto: "and",
        expression.OrDto: "or",
        expression.XorDto: "xor",
        expression.NandDto: "nand",
        expression.NorDto: "nor",
        expression.XnorDto: "xnor",
    }
    for expression_type, type_name in binary_types.items():
        if isinstance(expression_dto, expression_type):
            return {
                "type": type_name,
                "args": {
                    "l_expr": _expression_to_json(expression_dto.l_expr),
                    "r_expr": _expression_to_json(expression_dto.r_expr),
                },
            }

    raise TypeError(f"Unsupported expression DTO: {type(expression_dto).__name__}")


def component_to_json(component_dto: component.ComponentDto) -> dict[str, Any]:
    return {
        "component": {
            "id": component_dto.identifier,
            "buses": [
                {
                    "id": bus.identifier,
                    "type": "bit_bus",
                    "value": bus.value,
                    "msb_descending": bus.msb_descending,
                    "assignment": (
                        None
                        if bus.assignment is None
                        else _expression_to_json(bus.assignment)
                    ),
                    "influence_list": [
                        influenced_bus.identifier
                        for influenced_bus in bus.influence_list
                    ],
                }
                for bus in component_dto.buses
            ],
        }
    }
