from scanner import Scanner


FIRST_SETS = {
    'comp': ['main', 'comp'],
    'stmt': ['in', 'out', 'bit'],
}


# begin AST classes
class Node:
    def __init__(self) -> None:
        self.children = []

    def __repr__(self) -> str:  #todo improve this method - json?
        return f'{self.__class__.__name__} -> {self.children}'
    
    def add_child(self, child):
        self.children.append(child)


class Mod(Node):
    pass


class Comp(Node):
    def __init__(self) -> None:
        super().__init__()
        self.id = ''
        self.isMain = False


class Signal(Node):
    def __init__(self) -> None:
        super().__init__()
        self.id = ''
        self.type = 0
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
    def mod(self) -> Node:
        mod = Mod()

        while self.get_current_token().label in FIRST_SETS['comp']:
            mod.add_child(self.comp())

        self.match_label('EOF')

        return mod

    # comp = ['main'], 'comp', ID, '{', {stmt}, '}';
    def comp(self):
        comp = Comp()

        if self.get_current_token().label == 'main':
            comp.isMain = True
            self.advance()

        self.match_label('comp')
        self.advance()
        self.match_label('id')
        comp.id = self.get_current_token().lexeme
        self.advance()
        self.match_label('l_brace')
        self.advance()

        while self.get_current_token().label in FIRST_SETS['stmt']:
            comp.add_child(self.stmt())

        self.match_label('r_brace')
        self.advance()

        return comp

    # stmt = decl | assign;
    def stmt(self):  #todo add assign
        return self.decl()

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
