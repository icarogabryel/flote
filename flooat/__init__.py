from .scanner import Scanner
from .parser import Parser
from .builder import Builder
from .component import Component

def make_comp(code):
    scanner = Scanner(code)
    parser = Parser(scanner)
    print(parser.ast)
    builder = Builder(parser)

    component = builder.get_component()

    return component
