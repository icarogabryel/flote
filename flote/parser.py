from .scanner import Scanner
from . import ast


# Dict of First Sets used to enter syntactical rules
FIRST_SETS = {
    'comp': ['main', 'comp'],
    'stmt': ['in', 'out', 'bit', 'id'],
    'decl': ['in', 'out', 'bit'],
    'assign': ['id'],
    'expr_dash': ['or', 'nor'],
    'term_dash': ['xor', 'xnor'],
    'fact_dash': ['and', 'nand'],
}


class SyntacticalError(Exception):
    def __init__(self, line_number, message):
        self.line_number = line_number
        self.message = message

    def __str__(self):
        return f'Syntactical Error at line {self.line_number}: {self.message}'


class Parser:
    """
    Syntactical Parser for Flote Language.

    Args:
        scanner (Scanner): Scanner object that will provide the token stream.
    """
    def __init__(self, scanner: Scanner) -> None:
        self.scanner = scanner
        # Get the generator token stream from the scanner
        self.token_stream = self.scanner.get_token_stream()
        self.ast = None
        # Get the first token from the stream
        self.current_token = next(self.token_stream)

        self.parse()

    def advance(self):
        """Move to the next token in the token stream on demand."""
        self.current_token = next(self.token_stream)

    def get_current_token(self):
        return self.current_token

    def match_label(self, expected_label):
        token = self.get_current_token()

        if token.label != expected_label:
            raise SyntacticalError(
                self.scanner.line_number,
                (
                    f'Unexpected Token. Expected "{expected_label}". Got'
                    '"{token.label}".'
                )
            )

    def parse(self):
        """
        Start the parsing process  by entering the first rule of the grammar.
        """
        self.ast = self.mod()

    # Syntactical Rules

    # * mod = {comp}
    def mod(self):
        mod = ast.Mod()

        mod.add_comp(self.comp())

        while self.get_current_token().label in FIRST_SETS['comp']:
            mod.add_comp(self.comp())

        self.match_label('EOF')

        return mod

    # * comp = ['main'], 'comp', ID, '{', {stmt}, '}'
    def comp(self):
        comp = ast.Comp()
        comp.line_number = self.scanner.line_number

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

    # * stmt = decl | assign
    def stmt(self):
        if (label := self.get_current_token().label) in FIRST_SETS['decl']:
            return self.decl()
        elif label in FIRST_SETS['assign']:
            return self.assign()

        assert False, f'Unexpected Token: {label}'

    # * decl = {'in' | 'out'}, 'bit', ID, {'=', expr}, ';'
    def decl(self):
        decl = ast.Decl()
        decl.line_number = self.scanner.line_number

        if self.get_current_token().label == 'in':
            decl.conn = -1
            self.advance()
        elif self.get_current_token().label == 'out':
            decl.conn = 1
            self.advance()

        self.match_label('bit')  # todo adjust to accept other types
        decl.type = 'bit'
        self.advance()
        self.match_label('id')
        decl.id = self.get_current_token().lexeme
        self.advance()

        if self.get_current_token().label == 'assign':
            self.advance()
            decl.assign = self.expr()

        self.match_label('semicolon')
        self.advance()

        return decl

    # * assign = ID, '=', expr, ';'
    def assign(self):
        assign = ast.Assign()

        self.match_label('id')

        identifier = ast.Identifier(self.get_current_token().lexeme)
        identifier.line_number = self.scanner.line_number
        assign.dt = identifier

        self.advance()
        self.match_label('assign')
        self.advance()
        assign.expr = self.expr()
        self.match_label('semicolon')
        self.advance()

        return assign

    # * expr = term, exprDash
    def expr(self):
        term = self.term()

        # If expr' is not an empty production (there are more operators),
        if self.get_current_token().label in FIRST_SETS['expr_dash']:
            # the coming node is the father of term
            current_node = self.expr_dash()
            # and term will be his left son.
            current_node.l_expr = term

            # A complete node is returned to the top routine.
            return current_node
        else:
            return term

    # * exprDash = ('or' | 'nor'), term, exprDash | ε
    def expr_dash(self):
        token = self.get_current_token().label

        if token == 'or':
            current_node = ast.Or()
            self.advance()

        elif token == 'nor':
            current_node = ast.Nor()
            self.advance()

        else:
            raise SyntacticalError(
                self.scanner.line_number,
                'Expected "or" or "nor".'
            )

        term = self.term()

        # If there are more operators,
        if self.get_current_token().label in FIRST_SETS['expr_dash']:
            # the coming son node is the father of term
            son_node = self.expr_dash()
            # and term will be his left son. the son node is complete now.
            son_node.l_expr = term

            # Then, the son node will be the right son of the current node.
            current_node.r_expr = son_node

            # The current note returns with empty left expr to be filled by the
            # top routine.
            return current_node

        # If there are no more operators, term is the right son of the current
        # node.
        else:
            current_node.r_expr = term

            # The current note returns with empty left expr to be filled by the
            # top routine
            return current_node

    # * term = factor, termDash
    def term(self):
        factor = self.fact()

        if self.get_current_token().label in FIRST_SETS['term_dash']:
            current_node = self.term_dash()
            current_node.l_expr = factor

            return current_node

        else:
            return factor

    # * termDash = ('xor' | 'xnor'), factor, termDash | ε
    def term_dash(self):
        token = self.get_current_token().label

        if token == 'xor':
            current_node = ast.Xor()
            self.advance()

        elif token == 'xnor':
            current_node = ast.Xnor()
            self.advance()

        else:
            raise SyntacticalError(
                self.scanner.line_number,
                'Expected "xor" or "xnor".'
            )

        factor = self.fact()

        if self.get_current_token().label in FIRST_SETS['term_dash']:
            son_node = self.term_dash()
            son_node.l_expr = factor

            current_node.r_expr = son_node

            return current_node

        else:
            current_node.r_expr = factor

            return current_node

    # * fact = primary, factDash
    def fact(self):
        primary = self.primary()

        if self.get_current_token().label in FIRST_SETS['fact_dash']:
            current_node = self.fact_dash()
            current_node.l_expr = primary

            return current_node

        else:
            return primary

    # * factDash = ('and' | 'nand'), primary, factDash | ε
    def fact_dash(self):
        token = self.get_current_token().label

        if token == 'and':
            current_node = ast.And()
            self.advance()

        elif token == 'nand':
            current_node = ast.Nand()
            self.advance()

        else:
            raise SyntacticalError(
                self.scanner.line_number,
                'Expected "and" or "nand".'
            )  # todo maybe change to assert

        primary = self.primary()

        if self.get_current_token().label in FIRST_SETS['fact_dash']:
            son_node = self.fact_dash()
            son_node.l_expr = primary

            current_node.r_expr = son_node

            return current_node

        else:
            current_node.r_expr = primary

            return current_node

    # * primary = 'not', primary | '(', expr, ')' | ID | BIN
    def primary(self) -> ast.ExprElem:
        if (token_label := self.get_current_token().label) == 'id':
            identifier = ast.Identifier(self.get_current_token().lexeme)
            identifier.line_number = self.scanner.line_number

            self.advance()

            return identifier

        elif token_label == 'bit_field':
            value = bool(self.get_current_token().lexeme)
            self.advance()

            return ast.BitField(value)

        elif token_label == 'not':
            self.advance()

            node = ast.Not()
            node.expr = self.primary()

            return node

        elif token_label == 'l_paren':
            self.advance()
            expr = self.expr()
            self.match_label('r_paren')
            self.advance()

            return expr

        else:
            raise SyntacticalError(
                self.scanner.line_number,
                'Expected primary.'
            )
