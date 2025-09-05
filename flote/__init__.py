from .elaboration.builder import Builder
from .elaboration.parser import Parser
from .elaboration.scanner import Scanner
from .simulation.test_bench import TestBench


def elaborate(code) -> TestBench:
    scanner = Scanner(code)
    tokens_stream = scanner.token_stream

    parser = Parser(tokens_stream)
    ast = parser.ast

    builder = Builder(ast)
    model = builder.get_component()

    test_bench = TestBench(model)

    return test_bench


def elaborate_from_file(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    return elaborate(code)
