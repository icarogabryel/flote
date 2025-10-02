"""This module defines the expression nodes used in the assignment of a bus."""
from .busses import BusDto, BusValueDto
from .expr_node import ExprNode


class Ref(ExprNode):
    """This class represents a reference to a bus in the circuit."""
    def __init__(self, bus: BusDto, slice: None | int):
        self.bus = bus
        self.slice = slice

    def __repr__(self) -> str:
        return f'Ref({self.bus.id_})'

    def __str__(self) -> str:
        return f'Ref ({self.bus.id_})'

    def get_sensitivity_list(self):
        return [self.bus]

    def to_json(self):
        return {'type': 'ref', 'args': {'id': self.bus.id_, 'slice': self.slice}}


class Const(ExprNode):
    """This class represents a constant value in the circuit."""
    def __init__(self, value: BusValueDto) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f'Const({self.value})'

    def __str__(self) -> str:
        return f'Const ({self.value})'

    def to_json(self):
        return {'type': 'const', 'args': {'value': self.value.to_json()}}

    def get_sensitivity_list(self):
        return []


class UnaryOperation(ExprNode):
    """Base class for all unary operations."""
    def __init__(self, expr: ExprNode) -> None:
        self.expr = expr

    def get_sensitivity_list(self):
        return self.expr.get_sensitivity_list()


class BinaryOperation(ExprNode):
    """Base class for all binary operations."""
    def __init__(self, l_expr: ExprNode, r_expr: ExprNode) -> None:
        self.l_expr = l_expr
        self.r_expr = r_expr

    def get_sensitivity_list(self):
        return self.l_expr.get_sensitivity_list() + self.r_expr.get_sensitivity_list()


class Not(UnaryOperation):
    def __repr__(self) -> str:
        return f'Not {self.expr}'

    def __str__(self) -> str:
        return f'Not ({self.expr})'

    def to_json(self):
        return {'type': 'not', 'args': {'expr': self.expr.to_json()}}


class And(BinaryOperation):
    def __repr__(self) -> str:
        return f'And {self.l_expr} {self.r_expr}'

    def __str__(self) -> str:
        return f'And ({self.l_expr}, {self.r_expr})'

    def to_json(self):
        return {
            'type': 'and',
            'args': {'l_expr': self.l_expr.to_json(), 'r_expr': self.r_expr.to_json()}
        }


class Or(BinaryOperation):
    def __repr__(self) -> str:
        return f'Or {self.l_expr} {self.r_expr}'

    def __str__(self) -> str:
        return f'Or ({self.l_expr}, {self.r_expr})'

    def to_json(self):
        return {
            'type': 'or',
            'args': {'l_expr': self.l_expr.to_json(), 'r_expr': self.r_expr.to_json()}
        }


class Xor(BinaryOperation):
    def __repr__(self) -> str:
        return f'Xor {self.l_expr} {self.r_expr}'

    def __str__(self) -> str:
        return f'Xor ({self.l_expr}, {self.r_expr})'

    def to_json(self):
        return {
            'type': 'xor',
            'args': {'l_expr': self.l_expr.to_json(), 'r_expr': self.r_expr.to_json()}
        }


class Nand(BinaryOperation):
    def __repr__(self) -> str:
        return f'Nand {self.l_expr} {self.r_expr}'

    def __str__(self) -> str:
        return f'Nand ({self.l_expr}, {self.r_expr})'

    def to_json(self):
        return {
            'type': 'nand',
            'args': {'l_expr': self.l_expr.to_json(), 'r_expr': self.r_expr.to_json()}
        }


class Nor(BinaryOperation):
    def __repr__(self) -> str:
        return f'Nor {self.l_expr} {self.r_expr}'

    def __str__(self) -> str:
        return f'Nor ({self.l_expr}, {self.r_expr})'

    def to_json(self):
        return {
            'type': 'nor',
            'args': {'l_expr': self.l_expr.to_json(), 'r_expr': self.r_expr.to_json()}
        }


class Xnor(BinaryOperation):
    def __repr__(self) -> str:
        return f'Xnor {self.l_expr} {self.r_expr}'

    def __str__(self) -> str:
        return f'Xnor ({self.l_expr}, {self.r_expr})'

    def to_json(self):
        return {
            'type': 'xnor',
            'args': {'l_expr': self.l_expr.to_json(), 'r_expr': self.r_expr.to_json()}
        }


Operations = And | Or | Xor | Nand | Nor | Xnor | Not
