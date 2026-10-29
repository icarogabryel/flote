from flote.elaboration import ast_nodes
from flote.elaboration.scanner import Token

# Dict of First Sets used to enter syntactical rules
FIRST_SETS = {
    "comp": ["main", "comp"],
    "stmt": ["in", "out", "bit", "id", "sub"],
    "decl": ["in", "out", "bit"],
    "expr_dash": ["or", "nor"],
    "term_dash": ["xor", "xnor"],
    "fact_dash": ["and", "nand"],
}


class SyntacticalError(Exception):
    def __init__(self, line_number: int, message: str):
        self.line_number = line_number
        self.message = message

    def __str__(self) -> str:
        return f"Syntactical Error at line {self.line_number}: {self.message}"


class Parser:
    """Syntactical Parser for Flote Language."""

    def __init__(self, token_stream: list[Token]) -> None:
        self.token_stream = token_stream
        self.current_token = self.token_stream.pop(0)
        self.ast = self.parse()

    def advance(self) -> None:
        """Move to the next token in the token stream."""
        self.current_token = self.token_stream.pop(0)

    def get_current_token(self) -> Token:
        return self.current_token

    def match_label(self, expected_label: str) -> None:
        """Validate that the current token matches the expected label."""
        token = self.get_current_token()

        if token.label != expected_label:
            raise SyntacticalError(
                token.line_number,
                f'Unexpected Token. Expected "{expected_label}". Got "{token.label}".',
            )

    def parse(self) -> ast_nodes.Module:
        """Start the parsing process by entering the first rule of the grammar."""
        return self.mod()

    # Syntactical Rules

    # mod = comp, {comp};
    def mod(self) -> ast_nodes.Module:
        components: list[ast_nodes.Component] = [self.comp()]

        while self.get_current_token().label in FIRST_SETS["comp"]:
            components.append(self.comp())

        self.match_label("EOF")
        return ast_nodes.Module(components)

    # comp = ['main'], 'comp', ID, '{', {stmt}, '}'
    def comp(self) -> ast_nodes.Component:
        is_main = False
        if self.get_current_token().label == "main":
            is_main = True
            self.advance()

        self.match_label("comp")
        line_number = self.get_current_token().line_number
        self.advance()
        self.match_label("id")
        identifier = ast_nodes.Identifier(self.get_current_token().lexeme)
        self.advance()
        self.match_label("l_brace")
        self.advance()

        statements: list[
            ast_nodes.Declaration | ast_nodes.Assignment | ast_nodes.Instance
        ] = []
        while self.get_current_token().label in FIRST_SETS["stmt"]:
            result = self.stmt()
            if isinstance(result, list):  # decl() always return a list of Declaration
                for stmt in result:
                    statements.append(stmt)
            else:
                statements.append(result)

        self.match_label("r_brace")
        self.advance()

        return ast_nodes.Component(identifier, line_number, is_main, statements)

    # stmt = decl | asmt | inst
    def stmt(
        self,
    ) -> list[ast_nodes.Declaration] | ast_nodes.Assignment | ast_nodes.Instance:
        if (label := self.get_current_token().label) in FIRST_SETS["decl"]:
            return self.decl()
        elif label == "id":
            return self.asmt()
        elif label == "sub":
            return self.inst()
        else:
            assert False, f"Unexpected Token: {label}"

    # decl = ['in' | 'out'], 'bit', [dim], ID, {',' ID}, ['=', expr], ';';
    def decl(self) -> list[ast_nodes.Declaration]:
        if self.get_current_token().label == "in":
            conn = ast_nodes.Connection.INPUT
            self.advance()
        elif self.get_current_token().label == "out":
            conn = ast_nodes.Connection.OUTPUT
            self.advance()
        else:
            conn = ast_nodes.Connection.INTERNAL

        self.match_label("bit")
        line_number = self.get_current_token().line_number
        self.advance()

        dimension = None
        if self.get_current_token().label == "l_bracket":
            dimension = self.dim()

        self.match_label("id")
        identifiers = [ast_nodes.Identifier(self.get_current_token().lexeme)]
        self.advance()

        while self.get_current_token().label == "comma":
            self.advance()
            self.match_label("id")
            identifiers.append(ast_nodes.Identifier(self.get_current_token().lexeme))
            self.advance()

        assignment_expression = None
        if self.get_current_token().label == "equals":
            self.advance()
            assignment_expression = self.expr()

        self.match_label("semicolon")
        self.advance()

        declarations: list[ast_nodes.Declaration] = []
        for id_ in identifiers:
            declaration = ast_nodes.Declaration(
                id_, line_number, conn, "bit", dimension, assignment_expression
            )
            declarations.append(declaration)

        return declarations

    # dim = "[", ["+" | "-"], DEC, "]";
    def dim(self) -> ast_nodes.Dimension:
        self.match_label("l_bracket")
        self.advance()

        # minus -> descending | plus or none -> ascending
        if (current_token := self.get_current_token().label) in ["plus", "minus"]:
            msb = (
                ast_nodes.Msb.DESCENDING
                if current_token == "minus"
                else ast_nodes.Msb.ASCENDING
            )
            self.advance()
        else:
            msb = ast_nodes.Msb.ASCENDING

        self.match_label("dec")
        token = self.get_current_token()
        assert token.lexeme.isdigit(), (
            f"Token lexeme '{token.lexeme}' is not a valid integer"
        )
        size = int(token.lexeme)
        # Logically, the lexeme of a decimal token should never be a negative integer.
        assert size >= 0, "Dimension size must be non-negative"

        if size == 0:
            raise SyntacticalError(
                token.line_number, "Dimension size must be positive."
            )

        self.advance()
        self.match_label("r_bracket")
        self.advance()

        return ast_nodes.Dimension(msb, size)

    # asmt = (ID | memb), "=", expr, ";";
    def asmt(self) -> ast_nodes.Assignment:
        destiny: None | ast_nodes.Identifier | ast_nodes.Member = None

        self.match_label("id")
        token = self.get_current_token()
        identifier = ast_nodes.Identifier(token.lexeme)
        identifier.line_number = token.line_number
        self.advance()

        if self.get_current_token().label == "dot":
            self.advance()

            member_access = ast_nodes.Member()
            member_access.object = identifier

            self.match_label("id")
            token = self.get_current_token()
            member = ast_nodes.Identifier(token.lexeme)
            member.line_number = token.line_number
            self.advance()

            member_access.member = member

            destiny = member_access  # TODO change name
        else:
            destiny = identifier

        self.match_label("equals")
        self.advance()

        expr = self.expr()

        self.match_label("semicolon")
        self.advance()

        return ast_nodes.Assignment(destiny, expr)

    # expr = term, exprDash
    def expr(self) -> ast_nodes.ExprElem:
        term = self.term()

        # If expr' is not an empty production (there are more operators),
        if self.get_current_token().label in FIRST_SETS["expr_dash"]:
            # the coming node is the father of term
            current_node = self.expr_dash()
            # and term will be his left son.
            current_node.l_expr = term

            # A complete node is returned to the top routine.
            return current_node
        else:
            return term

    # exprDash = ('or' | 'nor'), term, exprDash | ε
    def expr_dash(self) -> ast_nodes.BinaryOp:
        token = self.get_current_token()

        current_node: ast_nodes.OrOp | ast_nodes.NorOp
        if token.label == "or":
            current_node = ast_nodes.OrOp(self.get_current_token().line_number)
            self.advance()
        elif token.label == "nor":
            current_node = ast_nodes.NorOp(self.get_current_token().line_number)
            self.advance()
        else:
            assert False, f"Unexpected Token: {token.label}"

        term = self.term()

        # If there are more operators,
        if self.get_current_token().label in FIRST_SETS["expr_dash"]:
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

    # term = fact, termDash
    def term(self) -> ast_nodes.ExprElem:
        factor = self.fact()

        if self.get_current_token().label in FIRST_SETS["term_dash"]:
            current_node = self.term_dash()
            current_node.l_expr = factor

            return current_node
        else:
            return factor

    # termDash = ("xor" | "xnor"), fact, termDash | ε;
    def term_dash(self) -> ast_nodes.BinaryOp:
        token = self.get_current_token()

        current_node: ast_nodes.XorOp | ast_nodes.XnorOp
        if token.label == "xor":
            current_node = ast_nodes.XorOp(self.get_current_token().line_number)
            self.advance()
        elif token.label == "xnor":
            current_node = ast_nodes.XnorOp(self.get_current_token().line_number)
            self.advance()
        else:
            assert False, f"Unexpected Token: {token.label}"

        factor = self.fact()

        if self.get_current_token().label in FIRST_SETS["term_dash"]:
            son_node = self.term_dash()
            son_node.l_expr = factor

            current_node.r_expr = son_node
            return current_node
        else:
            current_node.r_expr = factor
            return current_node

    # fact = prim, factDash;
    def fact(self) -> ast_nodes.ExprElem:
        primary = self.prim()

        if self.get_current_token().label in FIRST_SETS["fact_dash"]:
            current_node = self.fact_dash()
            current_node.l_expr = primary

            return current_node
        else:
            return primary

    # factDash = ("and" | "nand"), prim, factDash | ε;
    def fact_dash(self) -> ast_nodes.BinaryOp:
        token = self.get_current_token()

        current_node: ast_nodes.AndOp | ast_nodes.NandOp
        if token.label == "and":
            current_node = ast_nodes.AndOp(self.get_current_token().line_number)
            self.advance()
        elif token.label == "nand":
            current_node = ast_nodes.NandOp(self.get_current_token().line_number)
            self.advance()
        else:
            assert False, f"Unexpected Token: {token.label}"

        primary = self.prim()

        if self.get_current_token().label in FIRST_SETS["fact_dash"]:
            son_node = self.fact_dash()
            son_node.l_expr = primary

            current_node.r_expr = son_node
            return current_node
        else:
            current_node.r_expr = primary
            return current_node

    # prim = "not", prim | "(", expr, ")" | ref | BIT_FD | conc;
    def prim(self) -> ast_nodes.ExprElem:
        token = self.get_current_token()

        # prim = "not", prim;
        if (token_label := token.label) == "not":
            self.advance()

            node = ast_nodes.NotOp()
            node.expr = self.prim()

            return node
        # prim = "(", expr, ")";
        elif token_label == "l_paren":
            self.advance()
            expr = self.expr()
            self.match_label("r_paren")
            self.advance()

            return expr
        # prim = ref;
        elif token_label == "id":
            reference: None | ast_nodes.Identifier | ast_nodes.Member = None

            identifier = ast_nodes.Identifier(token.lexeme)
            identifier.line_number = token.line_number
            self.advance()

            if self.get_current_token().label == "dot":
                self.advance()

                member_access = ast_nodes.Member()
                member_access.object = identifier

                self.match_label("id")
                token = self.get_current_token()
                member = ast_nodes.Identifier(token.lexeme)
                member.line_number = token.line_number
                self.advance()

                member_access.member = member

                reference = member_access
            else:
                reference = identifier

            ref = ast_nodes.Reference(reference)

            if self.get_current_token().label == "l_bracket":
                self.advance()

                self.match_label("dec")
                ref.range_begin = int(self.get_current_token().lexeme)
                self.advance()

                if self.get_current_token().label == "colon":
                    self.advance()
                    self.match_label("dec")
                    ref.range_end = int(self.get_current_token().lexeme)
                    self.advance()

                self.match_label("r_bracket")
                self.advance()

            return ref
        # prim = BIT_FD;
        elif token_label == "bit_field":
            value = self.get_current_token().lexeme.strip('"')
            self.advance()

            return ast_nodes.BitField(value)
        # prim = conc;
        elif token_label == "l_angle":
            self.advance()

            expressions: list[ast_nodes.ExprElem] = []
            expressions.append(self.expr())

            while self.get_current_token().label == "comma":
                self.advance()
                expressions.append(self.expr())

            self.match_label("r_angle")
            self.advance()

            return ast_nodes.Concatenation(expressions)
        else:
            raise SyntacticalError(token.line_number, "Expected primary.")

    # inst = 'sub', ID, ['as' ID],';';
    def inst(self) -> ast_nodes.Instance:
        self.match_label("sub")
        line_number = self.get_current_token().line_number
        self.advance()

        self.match_label("id")
        identifier = self.get_current_token().lexeme
        self.advance()

        alias = None
        if self.get_current_token().label == "as":
            self.advance()
            self.match_label("id")
            alias = self.get_current_token().lexeme
            self.advance()

        self.match_label("semicolon")
        self.advance()

        return ast_nodes.Instance(identifier, line_number, alias)
