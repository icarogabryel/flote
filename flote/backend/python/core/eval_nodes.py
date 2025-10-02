from .busses import BusValue, Bus, Evaluator


class Ref(Evaluator):
    """This class represents a reference to a bus in the circuit."""
    def __init__(self, bus: Bus, index: None | int):
        self.bus = bus
        self.index = index

    def __repr__(self) -> str:
        return f'{self.bus.id}'

    def evaluate(self) -> BusValue:
        if self.index:
            return self.bus.value[self.index]

        return self.bus.value


class Const(Evaluator):
    def __init__(self, value: BusValue) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f'Const({self.value})'

    def evaluate(self) -> BusValue:
        return self.value


class UnaryOperation(Evaluator):
    def __init__(self, expr: Evaluator) -> None:
        self.expr = expr

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.expr})'


class BinaryOperation(Evaluator):
    def __init__(self, l_expr: Evaluator, r_expr: Evaluator) -> None:
        self.l_expr = l_expr
        self.r_expr = r_expr

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'({self.l_expr}) {self.__class__.__name__} ({self.r_expr})'


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
