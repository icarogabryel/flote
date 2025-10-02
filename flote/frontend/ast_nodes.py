from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Union


class Connection(Enum):
    """Enum to represent the connection type of a declaration."""
    INTERNAL = 0
    INPUT = -1
    OUTPUT = 1


#TODO this is not used in builder yet
class Msb(Enum):
    """Enum to represent the most significant bit (MSB) direction."""
    ASCENDING = 0
    DESCENDING = 1


# * AST Nodes
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
        self.stmts: list[Union[Decl, Assign, Inst]] = []
        self.line_number = 0

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
        #TODO make id be an identifier object, not string
        self.id = ''
        self.conn = Connection.INTERNAL
        self.type = 'bit'
        self.dimension: Optional[Dimension] = None
        #TODO change atribute name to 'assignment_expr'
        self.assign: Optional[ExprElem] = None
        self.line_number = 0

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

        if self.dimension:
            desc += f'\n|  |- dimension: {self.dimension}'

        if self.assign:
            desc_assign = str(self.assign).replace('\n', '\n|  ')
            desc += f'\n|  |- assign: {desc_assign}'

        return desc


class Identifier:
    def __init__(self, id: str) -> None:
        self.id = id
        self.line_number: Optional[int] = None

    def __repr__(self) -> str:
        return f'Id: "{self.id}"'

    def __str__(self) -> str:
        return self.__repr__()


class Dimension:
    def __init__(self, size=1, msb=Msb.ASCENDING) -> None:
        # Private to ensure size is set through the setter method
        self.size: int = size
        self.msb: Optional[Msb] = msb

    def __repr__(self) -> str:
        msb_name = self.msb.name if self.msb is not None else None
        return f'Dimension(size={self.size}, MSB={msb_name})'

    def __str__(self) -> str:
        msb_name = self.msb.name if self.msb is not None else None
        return f'Dimension: {self.size}, MSB={msb_name}'


ExprElem = Union['Ref', 'BitField', 'UnaryOp', 'BinaryOp']


#TODO change name to 'Assignment'
class Assign:
    def __init__(self, destiny: 'Identifier', expr: ExprElem) -> None:
        self.destiny = destiny
        self.expr = expr

    def __repr__(self) -> str:
        return f'Assign({self.destiny}, {self.expr})'

    def __str__(self) -> str:
        desc_expr = str(self.expr).replace('\n', '\n|  ')
        return (
            f'Assign:\n|  |- destiny: {self.destiny}\n|  |- expr: {desc_expr}'
        )


class UnaryOp(ABC):
    expr: Optional[ExprElem] = None

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        desc_expr = f'{self.expr}'.replace('\n', '\n|  ')
        return f'{self.__class__.__name__}\n|  |  |- {desc_expr}'


class BinaryOp(ABC):
    l_expr: Optional[ExprElem] = None
    r_expr: Optional[ExprElem] = None

    def __init__(self, line_number: int) -> None:
        self.line_number = line_number

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        l_expr = f'{self.l_expr}'.replace('\n', '\n|  ')
        r_expr = f'{self.r_expr}'.replace('\n', '\n|  ')

        desc = (
            f'{self.__class__.__name__}\n|  |- l_expr: {l_expr}\n|  |- r_expr:'
            f' {r_expr}'
        )

        return desc


class NotOp(UnaryOp):
    def __repr__(self) -> str:
        return f'Not {self.expr}'


class AndOp(BinaryOp):
    def __repr__(self) -> str:
        return f'And {self.l_expr} {self.r_expr}'


class OrOp(BinaryOp):
    def __repr__(self) -> str:
        return f'Or {self.l_expr} {self.r_expr}'


class XorOp(BinaryOp):
    def __repr__(self) -> str:
        return f'Xor {self.l_expr} {self.r_expr}'


class NandOp(BinaryOp):
    def __repr__(self) -> str:
        return f'Nand {self.l_expr} {self.r_expr}'


class NorOp(BinaryOp):
    def __repr__(self) -> str:
        return f'Nor {self.l_expr} {self.r_expr}'


class XnorOp(BinaryOp):
    def __repr__(self) -> str:
        return f'Xnor {self.l_expr} {self.r_expr}'


class Ref():
    def __init__(self, id_):
        self.id_: Identifier = id_
        self.slice: None | int = None


class BitField:
    def __init__(self, value: str) -> None:
        self.value = value.strip('"')
        self.size = len(value)

    def __repr__(self) -> str:
        return f'BitField: {self.value}'

    def __str__(self) -> str:
        return self.__repr__()


class Inst:
    def __init__(self) -> None:
        self.comp_id: Optional[str] = None
        self.sub_alias: Optional[str] = None
        self.line_number: Optional[int] = None

    def __repr__(self) -> str:
        return f'Inst({self.comp_id}, {self.sub_alias})'

    def __str__(self) -> str:
        return f'Inst: {self.sub_alias} of {self.comp_id}'
