from scanner import Scanner


FIRST_SETS = {
    'comp': ['main', 'comp'],
    'stmt': ['in', 'out', 'bit', 'id'],
    'decl': ['in', 'out', 'bit'],
    'assign': ['id'],
}


# begin AST classes
class Mod:
    def __init__(self) -> None:
        self.comps = []

    def add_comp(self, comp):
        self.comps.append(comp)

    def __repr__(self) -> str:
        repr = ''

        for comp in self.comps:  #todo alter to json
            repr += f'{comp} '
            
        return f'Mod({self.comps})'


class Comp:
    def __init__(self) -> None:
        self.id = ''
        self.is_main = False
        self.stmts = []

    def add_stmt(self, stmt):
        self.stmts.append(stmt)

    def __repr__(self) -> str:
        repr = ''

        for stmt in self.stmts:  #todo alter to json
            repr += f'{stmt} '

        return f'Comp({self.id}, {self.is_main}, {self.stmts})'


class Signal:
    def __init__(self) -> None:
        self.id = ''
        self.type = 0

    def __repr__(self) -> str:
        return f'Signal({self.id}, {self.type})'

class Assign:
    def __init__(self) -> None:
        self.dt: str = None
        self.expr: Expr = None

    def __repr__(self) -> str:
        return f'Assign({self.dt}, {self.expr})'

class Expr:
    def __init__(self) -> None:
        self.op = 'none'
        self.l_expr = None
        self.r_expr = None
        self.l_value_sensitivity_list = []
        self.r_value_sensitivity_list = []

    def __repr__(self) -> str:
        return f'Expr({self.l_expr} {self.op} {self.r_expr})'
# end AST classes


class SyntacticalError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'Syntactical Error: {self.message}'


class Parser:
    def __init__(self, scanner: Scanner) -> None:
        self.scanner = scanner
        self.ast = None
        self.current_token = self.scanner.get_token()

        self.parse()

    def advance(self):
        self.current_token = self.scanner.get_token()

    def get_current_token(self):
        return self.current_token

    def match_label(self, expected_label):
        token = self.get_current_token()

        if token.label != expected_label:
            raise SyntacticalError(f'Unexpected Token. Expected \'{expected_label}\'. Got \'{token.label}\'.')

    def parse(self):
        self.ast = self.mod()

    # mod = {comp};
    def mod(self):
        mod = Mod()

        while self.get_current_token().label in FIRST_SETS['comp']:
            mod.add_comp(self.comp())

        self.match_label('EOF')

        return mod

    # comp = ['main'], 'comp', ID, '{', {stmt}, '}';
    def comp(self):
        comp = Comp()

        if self.get_current_token().label == 'main':
            comp.is_main = True
            self.advance()

        self.match_label('comp')
        self.advance()
        self.match_label('id')
        comp.id = self.get_current_token().lexeme
        self.advance()
        self.match_label('l_brace')
        self.advance()

        while self.get_current_token().label in FIRST_SETS['stmt']:
            comp.add_stmt(self.stmt())

        self.match_label('r_brace')
        self.advance()

        return comp

    # stmt = decl | assign;
    def stmt(self):
        if (label := self.get_current_token().label) in FIRST_SETS['decl']:
            return self.decl()
        elif label in FIRST_SETS['assign']:
            return self.assign()

    # decl = {'in' | 'out'}, 'bit', ID, ';';
    def decl(self):  #todo improve this algorithm
        signal = Signal()

        if self.get_current_token().label == 'in':
            signal.type = -1
            self.advance()
        elif self.get_current_token().label == 'out':
            signal.type = 1
            self.advance()

        self.match_label('bit')
        self.advance()
        self.match_label('id')
        signal.id = self.get_current_token().lexeme
        self.advance()
        self.match_label('semicolon')
        self.advance()

        return signal
    
    # assign = ID, '=', expr, ';';
    def assign(self):
        assign = Assign()

        self.match_label('id')
        assign.dt = self.get_current_token().lexeme
        self.advance()
        self.match_label('assign')
        self.advance()
        assign.expr = self.expr()
        self.match_label('semicolon')
        self.advance()

        return assign

    # expr = ID, op, ID, ';';
    def expr(self):
        expr = Expr()

        self.match_label('id')
        expr.l_expr = self.get_current_token().lexeme
        self.advance()

        expr.op = self.op()

        self.match_label('id')
        expr.r_expr = self.get_current_token().lexeme
        self.advance()

        return expr

    # op = 'and' | 'or';
    def op(self):
        if self.get_current_token().label == 'and':
            self.advance()
            return 'and'
        elif self.get_current_token().label == 'or':
            self.advance()
            return 'or'
        elif self.get_current_token().label == 'xor':
            self.advance()
            return 'xor'
        else:
            raise SyntacticalError('Unexpected Token. Expected \'and\' or \'or\'.')
