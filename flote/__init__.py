from .elaboration.builder import Builder
from .elaboration.parser import Parser
from .elaboration.scanner import Scanner


def elaborate(code):
    scanner = Scanner(code)
    parser = Parser(scanner)
    builder = Builder(parser.ast)

    component = builder.get_component()

    return component


def elaborate_from_file(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    return elaborate(code)
