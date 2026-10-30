"""This module defines the expression nodes used in the assignment of a bus."""

# TODO refactor __str__ and __repr__ of this module
# TODO refactor names to complete names

from abc import abstractmethod
from typing import Any, TypeAlias

from flote.elaboration.ir.buses import BusDto
from flote.elaboration.ir.representation import JsonRepresentation


class ExpressionNode(JsonRepresentation):
    @abstractmethod
    def get_sensitivity_list(self) -> list[BusDto]:
        return []


class Ref(ExpressionNode):
    """This class represents a reference to a bus in the circuit."""

    def __init__(
        self, bus: BusDto, slice_begin: int | None, slice_end: int | None
    ) -> None:
        self.bus = bus
        self.slice_begin = slice_begin
        self.slice_end = slice_end

    def __repr__(self) -> str:
        return f"Ref({self.bus.identifier})"

    def __str__(self) -> str:
        return f"Ref ({self.bus.identifier})"

    def get_sensitivity_list(self) -> list[BusDto]:
        return [self.bus]

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "ref",
            "args": {
                "id": self.bus.identifier,
                "slice_begin": self.slice_begin,
                "slice_end": self.slice_end,
            },
        }


class Conc(ExpressionNode):
    """This class represents a concatenation of expressions."""

    def __init__(self, exprs: list[ExpressionNode]) -> None:
        self.exprs = exprs

    def __repr__(self) -> str:
        return f"Conc({self.exprs})"

    def __str__(self) -> str:
        desc = "Conc:"

        for expr in self.exprs:
            expr_desc = str(expr).replace("\n", "\n|  ")
            desc += f"\n|  |- {expr_desc}"

        return desc

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "conc",
            "args": {"exprs": [expr.to_json() for expr in self.exprs]},
        }

    def get_sensitivity_list(self) -> list[BusDto]:
        sensitivity_list: list[BusDto] = []

        for expr in self.exprs:
            sensitivity_list += expr.get_sensitivity_list()

        return sensitivity_list


class Const(ExpressionNode):
    """This class represents a constant value in the circuit."""

    def __init__(self, value: Any) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"Const({self.value})"

    def __str__(self) -> str:
        return f"Const ({self.value})"

    def to_json(self) -> dict[str, Any]:
        return {"type": "const", "args": {"value": self.value}}

    def get_sensitivity_list(self) -> list[BusDto]:
        return []


class UnaryOperation(ExpressionNode):
    """Base class for all unary operations."""

    def __init__(self, expr: ExpressionNode) -> None:
        self.expr = expr

    def get_sensitivity_list(self) -> list[BusDto]:
        return self.expr.get_sensitivity_list()


class BinaryOperation(ExpressionNode):
    """Base class for all binary operations."""

    def __init__(self, l_expr: ExpressionNode, r_expr: ExpressionNode) -> None:
        self.l_expr = l_expr
        self.r_expr = r_expr

    def get_sensitivity_list(self) -> list[BusDto]:
        return self.l_expr.get_sensitivity_list() + self.r_expr.get_sensitivity_list()


class Not(UnaryOperation):
    def __repr__(self) -> str:
        return f"Not {self.expr}"

    def __str__(self) -> str:
        return f"Not ({self.expr})"

    def to_json(self) -> dict[str, Any]:
        return {"type": "not", "args": {"expr": self.expr.to_json()}}


class And(BinaryOperation):
    def __repr__(self) -> str:
        return f"And {self.l_expr} {self.r_expr}"

    def __str__(self) -> str:
        return f"And ({self.l_expr}, {self.r_expr})"

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "and",
            "args": {"l_expr": self.l_expr.to_json(), "r_expr": self.r_expr.to_json()},
        }


class Or(BinaryOperation):
    def __repr__(self) -> str:
        return f"Or {self.l_expr} {self.r_expr}"

    def __str__(self) -> str:
        return f"Or ({self.l_expr}, {self.r_expr})"

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "or",
            "args": {"l_expr": self.l_expr.to_json(), "r_expr": self.r_expr.to_json()},
        }


class Xor(BinaryOperation):
    def __repr__(self) -> str:
        return f"Xor {self.l_expr} {self.r_expr}"

    def __str__(self) -> str:
        return f"Xor ({self.l_expr}, {self.r_expr})"

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "xor",
            "args": {"l_expr": self.l_expr.to_json(), "r_expr": self.r_expr.to_json()},
        }


class Nand(BinaryOperation):
    def __repr__(self) -> str:
        return f"Nand {self.l_expr} {self.r_expr}"

    def __str__(self) -> str:
        return f"Nand ({self.l_expr}, {self.r_expr})"

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "nand",
            "args": {"l_expr": self.l_expr.to_json(), "r_expr": self.r_expr.to_json()},
        }


class Nor(BinaryOperation):
    def __repr__(self) -> str:
        return f"Nor {self.l_expr} {self.r_expr}"

    def __str__(self) -> str:
        return f"Nor ({self.l_expr}, {self.r_expr})"

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "nor",
            "args": {"l_expr": self.l_expr.to_json(), "r_expr": self.r_expr.to_json()},
        }


class Xnor(BinaryOperation):
    def __repr__(self) -> str:
        return f"Xnor {self.l_expr} {self.r_expr}"

    def __str__(self) -> str:
        return f"Xnor ({self.l_expr}, {self.r_expr})"

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "xnor",
            "args": {"l_expr": self.l_expr.to_json(), "r_expr": self.r_expr.to_json()},
        }


Operation: TypeAlias = And | Or | Xor | Nand | Nor | Xnor | Not
