"""Functions for the API."""

from pathlib import Path

from flote.elaboration.ast_nodes import Module
from flote.elaboration.builder import Builder
from flote.elaboration.parser import Parser
from flote.elaboration.scanner import Scanner, Token
from flote.simulation.renderer import Renderer
from flote.testbench import TestBench


def elaborate(code: str) -> TestBench:
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


def elaborate_file(file_path: str) -> TestBench:
    """
    Elaborate the code from the given file path and return a TestBench instance for
    simulation.
    """
    p = Path(file_path)
    with p.open("r", encoding="utf-8") as file:
        code = file.read()

    return elaborate(code)


def get_token_stream(code: str) -> list[Token]:
    scanner = Scanner(code)
    return scanner.token_stream


def get_ast(code: str) -> Module:
    token_stream = get_token_stream(code)
    parser = Parser(token_stream)
    return parser.ast


def get_netlist(code: str) -> str:
    ast = get_ast(code)
    builder = Builder(ast)
    return builder.netlist


def render_netlist(netlist: str) -> TestBench:
    """Render the given netlist and return the component for simulation."""
    render = Renderer(netlist)
    testbench = TestBench(render.component)
    return testbench
