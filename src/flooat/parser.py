from .scanner import Scanner


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

        for stmt in self.stmts:  #todo alter to json
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
        return f'Assign: {self.dt}\n|  |-- {expr_str}'


class UnaryOp:
    def __init__(self, op: str, value: str) -> None:
        self.op = op
        self.value = value

    def __repr__(self) -> str:
        return f'({self.op} {self.value})'
    
    def __str__(self) -> str:
        value_str = str(self.value).replace('\n', '\n|  ')
        return f'{self.op}\n|-- {value_str}'


class BinaryOp:
    def __init__(self, l_expr: str, op: str, r_expr: str) -> None:
        self.l_expr = l_expr
        self.op = op
        self.r_expr = r_expr

    def __repr__(self) -> str:
        return f'{self.op}\n|-- {self.l_expr}\n|-- {self.r_expr}'
    
    def __str__(self) -> str:
        l_expr_str = str(self.l_expr).replace('\n', '\n|  ')
        r_expr_str = str(self.r_expr).replace('\n', '\n|  ')
        return f'{self.op}\n|-- {l_expr_str}\n|-- {r_expr_str}'


class Signal:
    def __init__(self, id: str) -> None:
        self.id = id

    def __repr__(self) -> str:
        return f'Signal {self.id}'
    
    def __str__(self) -> str:
        return f'Signal {self.id}'
# end AST classes


class SyntacticalError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'Syntactical Error: {self.message}'


class Parser:
    def __init__(self, token_stream) -> None:
        self.token_stream = token_stream
        self.ast = None
        self.current_token = self.token_stream.pop(0)

        self.parse()

    def advance(self):
        self.current_token = self.token_stream.pop(0)

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
        declaration = Decl()

        if self.get_current_token().label == 'in':
            declaration.conn = -1
            self.advance()
        elif self.get_current_token().label == 'out':
            declaration.conn = 1
            self.advance()

        self.match_label('bit')  #todo chango to add other types
        declaration.type = 'bit'
        self.advance()
        self.match_label('id')
        declaration.id = self.get_current_token().lexeme
        self.advance()
        self.match_label('semicolon')
        self.advance()

        return declaration
    
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

    # expr = term, expr_dash;
    def expr(self):
        l_expr = self.term()

        if self.get_current_token().label in ['or', 'nor']:
            binaryOp = self.expr_dash()
            binaryOp.l_expr = l_expr
            return binaryOp
        else:
            return l_expr
        
    # expr_dash = ('or' | 'nor'), term, expr_dash | ε;
    def expr_dash(self):
        if (token_label := self.get_current_token().label) == 'or':
            op = token_label
            self.advance()
        
        elif token_label == 'nor':
            op = token_label
            self.advance()
        
        else:
            raise SyntacticalError('Unexpected Token. Expected \'or\' or \'nor\'.')
        
        l_son = self.term()

        if self.get_current_token().label in ['or', 'nor']:
            child_node = self.expr_dash()
            child_node.l_expr = l_son
            node = BinaryOp(None, op, child_node)
            return node
        else:
            # Sem mais operadores, criar o nó atual
            return BinaryOp(None, op, l_son)
        
    # term = factor, term*;
    def term(self):
        l_expr = self.factor()

        if self.get_current_token().label in ['xor', 'xnor']:
            binaryOp = self.term_dash()
            binaryOp.l_expr = l_expr
            return binaryOp
        else:
            return l_expr
    
    # term_dash = ('xor' | 'xnor'), factor, term_dash | ε;
    def term_dash(self):
        if (token_label := self.get_current_token().label) == 'xor':
            op = token_label
            self.advance()
        
        elif token_label == 'xnor':
            op = token_label
            self.advance()
        
        else:
            raise SyntacticalError('Unexpected Token. Expected \'xor\' or \'xnor\'.')
        
        l_son = self.factor()

        if self.get_current_token().label in ['xor', 'xnor']:
            child_node = self.term_dash()
            child_node.l_expr = l_son
            node = BinaryOp(None, op, child_node)
            return node
        else:
            # Sem mais operadores, criar o nó atual
            return BinaryOp(None, op, l_son)

    # factor = primary, factor*;
    def factor(self):
        l_expr = self.primary()

        if self.get_current_token().label in ['and', 'nand']:
            binaryOp = self.factor_dash()
            binaryOp.l_expr = l_expr
            return binaryOp
        else:
            return l_expr

    # factor* = ('and' | 'nand'), primary, factor* | ε;
    def factor_dash(self) -> BinaryOp:
        if (token_label := self.get_current_token().label) == 'and':
            op = token_label
            self.advance()
        
        elif token_label == 'nand':
            op = token_label
            self.advance()
        
        else:
            raise SyntacticalError('Unexpected Token. Expected \'and\' or \'nand\'.')
        
        primary = self.primary()  #! change name and organization

        if self.get_current_token().label in ['and', 'nand']:
            child_node = self.factor_dash()
            child_l_son = primary
            child_node.l_expr = child_l_son
            node = BinaryOp(None, op, child_node)
            
            return node
        else:
            return BinaryOp(None, op, primary)

    # primary = 'not', primary | '(', expr, ')' | ID | BIN ;
    def primary(self):
        if (token_label := self.get_current_token().label) == 'id':
            signal = Signal(self.get_current_token().lexeme)
            self.advance()

            return signal

        # elif token_label == 'bin':
        #     type = 'bin'
        #     value = self.get_current_token().lexeme
        #     self.advance()

        #     return Primary(type, value)

        elif token_label == 'not':  #todo change to own rule
            op = self.get_current_token().lexeme
            self.advance()

            return UnaryOp(op, self.primary())

        elif token_label == 'l_paren':
            self.advance()
            expr = self.expr()
            self.match_label('r_paren')
            self.advance()

            return expr
