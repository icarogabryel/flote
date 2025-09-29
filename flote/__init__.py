from warnings import warn

from .frontend.builder import Builder
from .frontend.parser import Parser
from .frontend.scanner import Scanner
from .test_bench import TestBench

try:
    from .backend.rust.core.renderer import Renderer
except ImportError:
    warn('Rust backend not available, using Python backend.')

    from .backend.python.core.renderer import Renderer


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
