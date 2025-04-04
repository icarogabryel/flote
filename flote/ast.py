from abc import ABC, abstractmethod
from typing import Union, Optional


INTERNAL = 0
INPUT = -1
OUTPUT = 1


class Mod:
    def __init__(self) -> None:
        self.comps: list[Comp] = []

    def add_comp(self, comp):
        self.comps.append(comp)

    def __repr__(self) -> str:
        repr = ''

        for comp in self.comps:
            repr += f'{comp} '

        return f'Mod({self.comps})'
    
    def __str__(self) -> str:
        string = ''

        for comp in self.comps:
            string += f'{comp}\n\n'

        return string


class Comp:
    def __init__(self) -> None:
        self.id = ''
        self.is_main = False
        self.stmts: list[Union[Decl, Assign]] = []

    def add_stmt(self, stmt):
        self.stmts.append(stmt)

    def __repr__(self) -> str:
        repr = ''

        for stmt in self.stmts:
            repr += f'{stmt} '

        return f'Comp({self.id}, {self.is_main}, {self.stmts})'

    def __str__(self) -> str:
        string = f'|- Comp: {self.id}'

        if self.is_main:
            string += ' (main)'

        string += '\n'

        for stmt in self.stmts:
            stmt_str = str(stmt).replace('\n', '\n|  ')
            string += f'|  |- {stmt_str}\n'

        return string


class Decl:
    def __init__(self) -> None:
        self.id = ''
        self.conn = INTERNAL
        self.type = 'bit'
        self.assign: Optional[ExprElem] = None

    def __repr__(self) -> str:
        return f'Decl({self.id}, {self.type})'

    def __str__(self) -> str:
        string = f'Decl: "{self.id}" ({self.type}'

        if self.conn == -1:
            string += ', input)'
        elif self.conn == 1:
            string += ', output)'
        else:
            string += ', internal)'

        if self.assign:
            assign_str = str(self.assign).replace('\n', '\n|  ')
            string += f'\n|  |- assign: {assign_str}'

        return string


ExprElem = Union['Identifier', 'Binary', 'UnaryOp', 'BinaryOp']


class Assign:
    def __init__(self) -> None:
        self.dt: Optional[Identifier] = None
        self.expr: Optional[ExprElem] = None

    def __repr__(self) -> str:
        return f'Assign({self.dt}, {self.expr})'

    def __str__(self) -> str:
        expr_str = str(self.expr).replace('\n', '\n|  ')
        return f'Assign\n|  |- dt: {self.dt}\n|  |- expr: {expr_str}'


class UnaryOp(ABC):
    expr:  Optional[ExprElem] = None

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        expr = f'{self.expr}'.replace('\n', '\n|  ')
        return f'{self.__class__.__name__}\n|  |  |- {expr}'


class BinaryOp(ABC):
    l_expr: Optional[ExprElem] = None
    r_expr: Optional[ExprElem] = None

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        l_expr = f'{self.l_expr}'.replace('\n', '\n|  ')
        r_expr = f'{self.r_expr}'.replace('\n', '\n|  ')

        str = f'{self.__class__.__name__}\n|  |  |- l_expr: {l_expr}\n|  |  |- r_expr: {r_expr}'

        return str


class Not(UnaryOp):
    def __repr__(self) -> str:
        return f'Not {self.expr}'


class And(BinaryOp):
    def __repr__(self) -> str:
        return f'And {self.l_expr} {self.r_expr}'


class Or(BinaryOp):
    def __repr__(self) -> str:
        return f'Or {self.l_expr} {self.r_expr}'


class Xor(BinaryOp):
    def __repr__(self) -> str:
        return f'Xor {self.l_expr} {self.r_expr}'


class Nand(BinaryOp):
    def __repr__(self) -> str:
        return f'Nand {self.l_expr} {self.r_expr}'


class Nor(BinaryOp):
    def __repr__(self) -> str:
        return f'Nor {self.l_expr} {self.r_expr}'


class Xnor(BinaryOp):
    def __repr__(self) -> str:
        return f'Xnor {self.l_expr} {self.r_expr}'


class Identifier:
    def __init__(self, id: str) -> None:
        self.id = id

    def __repr__(self) -> str:
        return f'Id: "{self.id}"'

    def __str__(self) -> str:
        return self.__repr__()


class Binary:
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f'Binary {int(self.value)}'

    def __str__(self) -> str:
        return self.__repr__()
