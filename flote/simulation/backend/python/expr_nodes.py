from .busses import BusValue, Evaluator
from .component import Component
from abc import ABC, abstractmethod


class ExprNode():
    def get_sensitivity_list(self):
        return []


class BusRef(Evaluator, ExprNode):
    """This class represents a reference to a bus in the circuit."""
    def __init__(self, bus):
        self.bus = bus

    def __repr__(self) -> str:
        return f'{self.bus}'

    def evaluate(self) -> BusValue:
        return self.bus.value

    def get_sensitivity_list(self):
        return [self.bus]



class Const(Evaluator):
    def __init__(self, value: BusValue) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f'Const({self.value})'

    def evaluate(self) -> BusValue:
        return self.value


#TODO type all this
class UnaryOperation(Evaluator):
    def __init__(self, expr: Evaluator) -> None:
        self.expr = expr

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.expr})'

    def get_sensitivity_list(self):
        return self.expr.get_sensitivity_list()


class BinaryOperation(Evaluator):
    def __init__(self, l_expr: Evaluator, r_expr: Evaluator) -> None:
        self.l_expr = l_expr
        self.r_expr = r_expr

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'({self.l_expr}) {self.__class__.__name__} ({self.r_expr})'

    def get_sensitivity_list(self):
        return self.l_expr.get_sensitivity_list() + self.r_expr.get_sensitivity_list()


class Not(UnaryOperation):
    def __repr__(self) -> str:
        return f'Not {self.expr}'

    def evaluate(self):
        return ~ self.expr.evaluate()


class And(BinaryOperation):
    def __repr__(self) -> str:
        return f'And {self.l_expr} {self.r_expr}'

    def evaluate(self):
        return self.l_expr.evaluate() & self.r_expr.evaluate()


class Or(BinaryOperation):
    def __repr__(self) -> str:
        return f'Or {self.l_expr} {self.r_expr}'

    def evaluate(self):
        return self.l_expr.evaluate() | self.r_expr.evaluate()


class Xor(BinaryOperation):
    def __repr__(self) -> str:
        return f'Xor {self.l_expr} {self.r_expr}'

    def evaluate(self):
        return self.l_expr.evaluate() ^ self.r_expr.evaluate()


class Nand(BinaryOperation):
    def __repr__(self) -> str:
        return f'Nand {self.l_expr} {self.r_expr}'

    def evaluate(self):
        return ~ (self.l_expr.evaluate() & self.r_expr.evaluate())


class Nor(BinaryOperation):
    def __repr__(self) -> str:
        return f'Nor {self.l_expr} {self.r_expr}'

    def evaluate(self):
        return ~ (self.l_expr.evaluate() | self.r_expr.evaluate())


class Xnor(BinaryOperation):
    def __repr__(self) -> str:
        return f'Xnor {self.l_expr} {self.r_expr}'

    def evaluate(self):
        return ~ (self.l_expr.evaluate() ^ self.r_expr.evaluate())


Operations = And | Or | Xor | Nand | Nor | Xnor | Not
