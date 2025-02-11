from .scanner import Scanner
from .parser import Parser
from .visitor import Visitor
from .component import Component

def make_comp(code):
    scanner = Scanner(code)
    parser = Parser(scanner)
    print(parser.ast)
    visitor = Visitor(parser)

    component = visitor.get_component()
    component.token_stream = scanner.token_stream

    return component
