from abc import ABC, abstractmethod


#TODO type all this
class UnaryOperator(ABC):
    def __init__(self, expr) -> None:
        self.expr = expr

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'{self.__class__.__name__} ({self.expr})'

    @abstractmethod
    def evaluate(self):
        """Evaluate the unary operation."""
        pass


class BinaryOperator(ABC):
    def __init__(self, l_expr, r_expr) -> None:
        self.l_expr = l_expr
        self.r_expr = r_expr

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'({self.l_expr}) {self.__class__.__name__} ({self.r_expr})'

    @abstractmethod
    def evaluate(self):
        """Evaluate the binary operation."""
        pass


class Not(UnaryOperator):
    def __repr__(self) -> str:
        return f'Not {self.expr}'

    def evaluate(self):
        return - self.expr.evaluate()


class And(BinaryOperator):
    def __repr__(self) -> str:
        return f'And {self.l_expr} {self.r_expr}'

    def evaluate(self):
        return self.l_expr.evaluate() & self.r_expr.evaluate()


class Or(BinaryOperator):
    def __repr__(self) -> str:
        return f'Or {self.l_expr} {self.r_expr}'

    def evaluate(self):
        return self.l_expr.evaluate() | self.r_expr.evaluate()


class Xor(BinaryOperator):
    def __repr__(self) -> str:
        return f'Xor {self.l_expr} {self.r_expr}'

    def evaluate(self):
        return self.l_expr.evaluate() ^ self.r_expr.evaluate()


class Nand(BinaryOperator):
    def __repr__(self) -> str:
        return f'Nand {self.l_expr} {self.r_expr}'

    def evaluate(self):
        return - (self.l_expr.evaluate() & self.r_expr.evaluate())


class Nor(BinaryOperator):
    def __repr__(self) -> str:
        return f'Nor {self.l_expr} {self.r_expr}'

    def evaluate(self):
        return - (self.l_expr.evaluate() | self.r_expr.evaluate())


class Xnor(BinaryOperator):
    def __repr__(self) -> str:
        return f'Xnor {self.l_expr} {self.r_expr}'

    def evaluate(self):
        return - (self.l_expr.evaluate() ^ self.r_expr.evaluate())
