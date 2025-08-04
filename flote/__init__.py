from flote.model.component import Component

from .elaboration.builder import Builder
from .elaboration.parser import Parser
from .elaboration.scanner import Scanner


def elaborate(code) -> Component:
    scanner = Scanner(code)
    tokens_stream = scanner.token_stream

    parser = Parser(tokens_stream)
    ast = parser.ast

    builder = Builder(ast)
    component = builder.get_component()

    return component


def elaborate_from_file(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    return elaborate(code)
