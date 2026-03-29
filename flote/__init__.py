from pathlib import Path
from warnings import warn

from .elaboration.builder import Builder
from .elaboration.parser import Parser
from .elaboration.scanner import Scanner
from .testbench import TestBench


class ElaborationError(Exception):
    """This class represents an error in the elaboration process."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


def render(
    ast,
    rust_backend,
):
    if rust_backend:
        try:
            from .simulation.fpga import Renderer as RustRenderer

            builder = Builder(ast)
            ir = builder.netlist
            render = RustRenderer(ir)
            return render.component
        except ImportError:
            warn("Rust backend not available, falling back to Python backend.")

    builder = Builder(ast)
    netlist = builder.netlist

    # Render with Python backend
    from .simulation.renderer import Renderer as PythonRenderer

    render = PythonRenderer(netlist)
    return render.component


def elaborate(code: str, rust_backend=True) -> TestBench:
    # 1. Lexical analysis and token stream generation
    scanner = Scanner(code)
    tokens_stream = scanner.token_stream

    # 2. Syntax analysis and AST generation
    parser = Parser(tokens_stream)
    ast = parser.ast

    # 3. Semantical analysis and IR generation
    component = render(ast, rust_backend=rust_backend)

    # 4. Creating the testbench and encapsulating the component
    assert component is not None, "Elaboration failed: component is None"
    test_bench = TestBench(component)
    return test_bench


def elaborate_file(file_path, rust_backend=True) -> TestBench:
    p = Path(file_path)
    with p.open("r", encoding="utf-8") as file:
        code = file.read()

    return elaborate(code, rust_backend=rust_backend)


def get_token_stream(code: str):
    scanner = Scanner(code)
    return scanner.token_stream


def get_ast(code: str):
    token_stream = get_token_stream(code)
    parser = Parser(token_stream)
    return parser.ast


def get_netlist(code: str):
    ast = get_ast(code)
    builder = Builder(ast)
    return builder.netlist
