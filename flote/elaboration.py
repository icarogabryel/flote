from pathlib import Path

from flote.frontend.ir.buses import HlsBusDto

from .backend.python.core.buses import HlsBus
from .backend.python.core.renderer import Renderer
from .frontend.builder import Builder
from .frontend.ir.component import HlsComponentDto
from .frontend.parser import Parser
from .frontend.scanner import Scanner
from .frontend.symbol_table import ComponentTable
from .hls import Component as HlsComponent
from .testbench import TestBench


class ElaborationError(Exception):
    """This class represents an error in the elaboration process."""
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


def elaborate(code: str, rust_backend=False, hls_components: list[HlsComponent] = []) -> TestBench:
    # 1. Lexical analysis and token stream generation
    scanner = Scanner(code)
    tokens_stream = scanner.token_stream

    # 2. Syntax analysis and AST generation
    parser = Parser(tokens_stream)
    ast = parser.ast

    # Try to use Rust backend if Python backend is not forced
    # if rust_backend:
    #     try:
    #         from .backend.rust.core import Renderer
    #     except ImportError:
    #         warn('Rust backend not available or not found, using Python backend.')
    #         from .backend.python.core import Renderer

    #     if len(hls_components) > 0:
    #         raise ElaborationError(
    #             'HLS components integration is only supported with the Python backend.'
    #         )

    #     # 3. Semantical analysis and IR generation
    #     builder = Builder(ast)
    #     ir = builder.ir

    #     # 4. Rendering the component from the IR
    #     render = Renderer(ir)
    #     component = render.component

    #     # 5. Creating the testbench and encapsulating the component
    #     test_bench = TestBench(component)
    #     return test_bench

    # Using Python backend, check for HLS components
    hls_symbol_table: dict[str, ComponentTable] = {}
    hls_components_dtos: dict[str, HlsComponentDto] = {}
    hls_components_buses: dict[str, HlsBus] = {}

    for hls_component in hls_components:
        hls_symbols, sim_buses = hls_component.render()
        hls_buses_dtos: list[HlsBusDto] = []

        # Create symbol table for HLS components
        hls_component_table = ComponentTable()
        hls_component_table.bus_symbols = hls_symbols

        # Create DTO for HLS component
        hls_component_dto = HlsComponentDto(hls_component.id_)
        for bus in sim_buses:
            hls_bus_dto = HlsBusDto(bus.id_)
            hls_buses_dtos.append(hls_bus_dto)
            bus.id_ = f'{hls_component.id_}.{bus.id_}'
            hls_components_buses[bus.id_] = bus

        hls_component_dto.busses = hls_buses_dtos
        hls_components_dtos[hls_component.id_] = hls_component_dto

        hls_component_table.object = hls_component_dto
        hls_symbol_table[hls_component.id_] = hls_component_table

    # 3. Semantical analysis and IR generation
    builder = Builder(ast, hls_symbol_table, hls_components=hls_components_dtos)
    ir = builder.ir

    # 4. Rendering the component from the IR
    render = Renderer(ir, hls_components_buses)
    component = render.component

    # 5. Creating the testbench and encapsulating the component
    test_bench = TestBench(component)
    return test_bench


def elaborate_file(file_path, hls_components: list[HlsComponent] = []) -> TestBench:
    p = Path(file_path)
    with p.open('r', encoding='utf-8') as file:
        code = file.read()

    return elaborate(code, hls_components=hls_components)
