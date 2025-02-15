from abc import ABC, abstractmethod

class Mod:
    def __init__(self) -> None:
        self.comps = []

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
        self.stmts = []

    def add_stmt(self, stmt):
        self.stmts.append(stmt)

    def __repr__(self) -> str:
        repr = ''

        for stmt in self.stmts:
            repr += f'{stmt} '

        return f'Comp({self.id}, {self.is_main}, {self.stmts})'
    
    def __str__(self) -> str:
        string = f'|-- Comp: {self.id}'

        if self.is_main:
            string += ' (main)'

        string += '\n'

        for stmt in self.stmts:
            stmt_str = str(stmt).replace('\n', '\n|  ')
            string += f'|  |-- {stmt_str}\n'

        return string


class Decl:
    def __init__(self) -> None:
        self.id = ''
        self.conn = 0
        self.type = 'bit'

    def __repr__(self) -> str:
        return f'Decl({self.id}, {self.type})'
    
    def __str__(self) -> str:
        string = f'Decl: {self.id} ({self.type}'

        if self.conn == -1:
            string += ', input)'
        elif self.conn == 1:
            string += ', output)'
        else:
            string += ', internal)'

        return string


class Assign:
    def __init__(self) -> None:
        self.dt: str = None
        self.expr = None

    def __repr__(self) -> str:
        return f'Assign({self.dt}, {self.expr})'
    
    def __str__(self) -> str:
        expr_str = str(self.expr).replace('\n', '\n|    ')
        return f'Assign\n|  |-- {self.dt}\n|-- {expr_str}'


class UnaryOp(ABC):
    def __init__(self, expr) -> None:
        self.expr = expr

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        return self.__repr__()


class BinaryOp(ABC):
    l_expr = None
    r_expr = None

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        str = f'{self.__class__.__name__}\n|  |-- {self.l_expr}\n|-- {self.r_expr}'

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
        return f'Identifier {self.id}'
    
    def __str__(self) -> str:
        return self.__repr__()


class Binary:
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f'Binary {self.value}'
    
    def __str__(self) -> str:
        return self.__repr__()
