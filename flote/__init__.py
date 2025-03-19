from .scanner import Scanner
from .parser import Parser
from .builder import Builder

def make_comp(code):
    scanner = Scanner(code)
    parser = Parser(scanner)
    builder = Builder(parser.ast)

    component = builder.get_component()

    return component
