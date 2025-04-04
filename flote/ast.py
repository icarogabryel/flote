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
        desc = '|- Mod:'

        for comp in self.comps:
            comp_desc = str(comp).replace('\n', '\n|  ')
            desc += f'\n|  |- {comp_desc}'

        return desc


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
        desc = f'Comp: {self.id}'

        if self.is_main:
            desc += ' (main)'

        for stmt in self.stmts:
            desc += '\n'
            desc_stmt = str(stmt).replace('\n', '\n|  ')
            desc += f'|  |- {desc_stmt}'

        return desc


class Decl:
    def __init__(self) -> None:
        self.id = ''
        self.conn = INTERNAL
        self.type = 'bit'
        self.assign: Optional[ExprElem] = None

    def __repr__(self) -> str:
        return f'Decl({self.id}, {self.type})'

    def __str__(self) -> str:
        desc = f'Decl: "{self.id}" ({self.type}'

        if self.conn == -1:
            desc += ', input)'
        elif self.conn == 1:
            desc += ', output)'
        else:
            desc += ', internal)'

        if self.assign:
            desc_assign = str(self.assign).replace('\n', '\n|  ')
            desc += f'\n|  |- assign: {desc_assign}'

        return desc


ExprElem = Union['Identifier', 'Binary', 'UnaryOp', 'BinaryOp']


class Assign:
    def __init__(self) -> None:
        self.dt: Optional[Identifier] = None
        self.expr: Optional[ExprElem] = None

    def __repr__(self) -> str:
        return f'Assign({self.dt}, {self.expr})'

    def __str__(self) -> str:
        desc_expr = str(self.expr).replace('\n', '\n|  ')
        return f'Assign:\n|  |- dt: {self.dt}\n|  |- expr: {desc_expr}'


class UnaryOp(ABC):
    expr:  Optional[ExprElem] = None

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        desc_expr = f'{self.expr}'.replace('\n', '\n|  ')
        return f'{self.__class__.__name__}\n|  |  |- {desc_expr}'


class BinaryOp(ABC):
    l_expr: Optional[ExprElem] = None
    r_expr: Optional[ExprElem] = None

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        l_expr = f'{self.l_expr}'.replace('\n', '\n|  ')
        r_expr = f'{self.r_expr}'.replace('\n', '\n|  ')

        desc = f'{self.__class__.__name__}\n|  |- l_expr: {l_expr}\n|  |- r_expr: {r_expr}'

        return desc


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
        return f'BitField: {int(self.value)}'

    def __str__(self) -> str:
        return self.__repr__()
