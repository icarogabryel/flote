# from warnings import warn

from .frontend.builder import Builder
from .frontend.parser import Parser
from .frontend.scanner import Scanner
from .testbench import TestBench

#TODO implement Rust backend
# try:
#     from .backend.rust.core import Renderer
# except ImportError:
#     warn('Rust backend not available, using Python backend.')

#     from .backend.python.core import Renderer

from .backend.python.core import Renderer


def elaborate(code: str) -> TestBench:
    scanner = Scanner(code)
    tokens_stream = scanner.token_stream

    parser = Parser(tokens_stream)
    ast = parser.ast

    builder = Builder(ast)
    ir = builder.ir

    render = Renderer(ir)
    component = render.component

    test_bench = TestBench(component)

    return test_bench


def elaborate_from_file(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    return elaborate(code)


def get_ir(code: str) -> str:
    scanner = Scanner(code)
    tokens_stream = scanner.token_stream

    parser = Parser(tokens_stream)
    ast = parser.ast

    builder = Builder(ast)
    ir = builder.ir

    return ir
