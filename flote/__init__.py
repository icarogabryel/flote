from pathlib import Path

from .elaboration.builder import Builder
from .elaboration.parser import Parser
from .elaboration.scanner import Scanner
from .simulation.renderer import Renderer
from .testbench import TestBench


class ElaborationError(Exception):
    """This class represents an error in the elaboration process."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


def elaborate(code: str, rust_backend=True) -> TestBench:
    """Elaborate the given code and return a TestBench instance for simulation."""
    # 1. Lexical analysis and token stream generation
    scanner = Scanner(code)
    tokens_stream = scanner.token_stream

    # 2. Syntax analysis and AST generation
    parser = Parser(tokens_stream)
    ast = parser.ast

    # 3. Semantical analysis and IR generation
    builder = Builder(ast)
    netlist = builder.netlist

    # 4. Creating the component for simulation
    render = Renderer(netlist)
    component = render.component

    assert component is not None, "Elaboration failed: component is None"
    testbench = TestBench(component)
    return testbench


def elaborate_file(file_path, rust_backend=True) -> TestBench:
    """
    Elaborate the code from the given file path and return a TestBench instance for
    simulation.
    """
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


def render_netlist(netlist):
    """Render the given netlist and return the component for simulation."""
    render = Renderer(netlist)
    testbench = TestBench(render.component)
    return testbench
