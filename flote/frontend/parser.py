from . import ast_nodes
from .scanner import Token


# Dict of First Sets used to enter syntactical rules
FIRST_SETS = {
    'comp': ['main', 'comp'],
    'stmt': ['in', 'out', 'bit', 'id', 'sub'],
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
    """
    def __init__(self, token_stream: list[Token]) -> None:
        # Get the generator token stream from the scanner
        self.token_stream = token_stream
        self.ast = None
        # Get the first token from the stream
        self.current_token = self.token_stream.pop(0)

        self.parse()

    def advance(self):
        """Move to the next token in the token stream."""
        self.current_token = self.token_stream.pop(0)

    def get_current_token(self):
        return self.current_token

    def match_label(self, expected_label):
        token = self.get_current_token()

        if token.label != expected_label:
            raise SyntacticalError(
                token.line_number,
                (
                    f'Unexpected Token. Expected "{expected_label}". Got'
                    f'"{token.label}".'
                )
            )

    def parse(self):
        """
        Start the parsing process  by entering the first rule of the grammar.
        """
        self.ast = self.mod()

    # Syntactical Rules

    #* mod = {comp}
    def mod(self):
        mod = ast_nodes.Mod()

        mod.add_comp(self.comp())

        while self.get_current_token().label in FIRST_SETS['comp']:
            mod.add_comp(self.comp())

        self.match_label('EOF')

        return mod

    #* comp = ['main'], 'comp', ID, '{', {stmt}, '}'
    def comp(self):
        comp = ast_nodes.Comp()

        if self.get_current_token().label == 'main':
            comp.is_main = True
            self.advance()

        self.match_label('comp')
        comp.line_number = self.get_current_token().line_number
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

    #* stmt = decl | assign | inst
    def stmt(self):
        if (label := self.get_current_token().label) in FIRST_SETS['decl']:
            return self.decl()
        elif label in FIRST_SETS['assign']:
            return self.assign()
        # elif label == 'sub':
        #     return self.inst()
        else:
            assert False, f'Unexpected Token: {label}'

    #* decl = ['in' | 'out'], 'bit', ID, [dimension], ['=', expr], ';';
    def decl(self):
        decl = ast_nodes.Decl()

        if self.get_current_token().label == 'in':
            decl.conn = ast_nodes.Connection.INPUT
            self.advance()
        elif self.get_current_token().label == 'out':
            decl.conn = ast_nodes.Connection.OUTPUT
            self.advance()

        self.match_label('bit')  # todo adjust to accept other types
        decl.line_number = self.get_current_token().line_number
        decl.type = 'bit'
        self.advance()
        self.match_label('id')
        decl.id = self.get_current_token().lexeme
        self.advance()

        if self.get_current_token().label == 'l_bracket':
            decl.dimension = self.dimension()

        if self.get_current_token().label == 'assign':
            self.advance()
            decl.assign = self.expr()

        self.match_label('semicolon')
        self.advance()

        return decl

    #* dimension = '[', ['-'], DEC, ']';
    def dimension(self) -> ast_nodes.Dimension:
        self.match_label('l_bracket')
        self.advance()

        # Check if the dimension is descending
        is_descending = self.get_current_token().label == 'minus'

        if is_descending:
            self.advance()

        msb = (
            ast_nodes.Msb.DESCENDING
            if is_descending else
            ast_nodes.Msb.ASCENDING
        )

        self.match_label('dec')
        token = self.get_current_token()

        assert token.lexeme.isdigit(), (
            f"Token lexeme '{token.lexeme}' is not a valid integer"
        )

        size = int(token.lexeme)

        # Logically, the lexeme of a decimal token should never be a negative
        # integer.
        assert size >= 0, 'Dimension size must be non-negative'

        if size == 0:
            raise SyntacticalError(
                token.line_number,
                'Dimension size must be positive.'
            )

        dimension = ast_nodes.Dimension(size, msb)

        self.advance()
        self.match_label('r_bracket')
        self.advance()

        return dimension

    #* assign = ID, '=', expr, ';'
    def assign(self):
        self.match_label('id')

        token = self.get_current_token()
        identifier = ast_nodes.Identifier(token.lexeme)
        identifier.line_number = token.line_number
        destiny = identifier
        self.advance()

        self.match_label('assign')
        self.advance()

        expr = self.expr()
        self.match_label('semicolon')
        self.advance()

        assign = ast_nodes.Assign(destiny, expr)

        return assign

    #* expr = term, exprDash
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

    #* exprDash = ('or' | 'nor'), term, exprDash | ε
    def expr_dash(self):
        token = self.get_current_token()

        if token.label == 'or':
            current_node = ast_nodes.OrOp(self.get_current_token().line_number)
            self.advance()
        elif token.label == 'nor':
            current_node = ast_nodes.NorOp(self.get_current_token().line_number)
            self.advance()
        else:
            raise SyntacticalError(
                token.line_number,
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

    #* term = factor, termDash
    def term(self):
        factor = self.fact()

        if self.get_current_token().label in FIRST_SETS['term_dash']:
            current_node = self.term_dash()
            current_node.l_expr = factor

            return current_node

        else:
            return factor

    #* termDash = ('xor' | 'xnor'), factor, termDash | ε
    def term_dash(self):
        token = self.get_current_token()

        if token.label == 'xor':
            current_node = ast_nodes.XorOp(self.get_current_token().line_number)
            self.advance()

        elif token.label == 'xnor':
            current_node = ast_nodes.XnorOp(self.get_current_token().line_number)
            self.advance()

        else:
            raise SyntacticalError(
                token.line_number,
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

    #* fact = primary, factDash
    def fact(self):
        primary = self.primary()

        if self.get_current_token().label in FIRST_SETS['fact_dash']:
            current_node = self.fact_dash()
            current_node.l_expr = primary

            return current_node

        else:
            return primary

    #* factDash = ('and' | 'nand'), primary, factDash | ε
    def fact_dash(self):
        token = self.get_current_token()

        if token.label == 'and':
            current_node = ast_nodes.AndOp(self.get_current_token().line_number)
            self.advance()

        elif token.label == 'nand':
            current_node = ast_nodes.NandOp(self.get_current_token().line_number)
            self.advance()

        else:
            raise SyntacticalError(
                token.line_number,
                'Expected "and" or "nand".'
            )  #todo maybe change to assert

        primary = self.primary()

        if self.get_current_token().label in FIRST_SETS['fact_dash']:
            son_node = self.fact_dash()
            son_node.l_expr = primary

            current_node.r_expr = son_node

            return current_node

        else:
            current_node.r_expr = primary

            return current_node

    #* primary = 'not', primary | '(', expr, ')' | ID | BIN
    def primary(self) -> ast_nodes.ExprElem:
        token = self.get_current_token()

        if (token_label := token.label) == 'id':
            identifier = ast_nodes.Identifier(token.lexeme)
            identifier.line_number = token.line_number
            ref = ast_nodes.Ref(identifier)
            self.advance()

            if self.get_current_token().label == 'l_bracket':
                self.advance()

                self.match_label('dec')
                ref.slice = int(self.get_current_token().lexeme)
                self.advance()

                self.match_label('r_bracket')
                self.advance()

            return ref

        elif token_label == 'bit_field':
            value = self.get_current_token().lexeme.strip('"')

            self.advance()

            return ast_nodes.BitField(value)

        elif token_label == 'not':
            self.advance()

            node = ast_nodes.NotOp()
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
                token.line_number,
                'Expected primary.'
            )

    #* inst = 'sub', ID, ['as' ID],';';
    # def inst(self):
    #     self.match_label('sub')
    #     inst = ast_nodes.Inst()
    #     inst.line_number = self.get_current_token().line_number
    #     self.advance()

    #     self.match_label('id')
    #     inst.comp_id = self.get_current_token().lexeme
    #     self.advance()

    #     if self.get_current_token().label == 'as':
    #         self.advance()
    #         self.match_label('id')
    #         inst.sub_alias = self.get_current_token().lexeme
    #         self.advance()
    #     else:
    #         inst.sub_alias = inst.comp_id

    #     self.match_label('semicolon')
    #     self.advance()

    #     return inst
