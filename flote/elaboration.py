from pathlib import Path
from warnings import warn

from .frontend.builder import Builder
from .frontend.ir.buses import HlsBusDto
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


def render(ast, rust_backend, hls_components: list[HlsComponent] = []):
    if rust_backend:
        if len(hls_components) > 0:
            warn('HLS components require Python backend, switching from Rust.')
        else:
            try:
                from .backend.rust.core import Renderer as RustRenderer

                builder = Builder(ast)
                ir = builder.ir
                render = RustRenderer(ir)
                return render.component
            except ImportError:
                warn('Rust backend not available, falling back to Python backend.')

    # Process HLS components
    hls_symbol_table: dict[str, ComponentTable] = {}
    hls_components_dtos: dict[str, HlsComponentDto] = {}
    hls_components_buses = {}

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

    # Build IR with HLS components
    builder = Builder(ast, hls_symbol_table, hls_components=hls_components_dtos)
    ir = builder.ir

    # Render with Python backend
    from .backend.python.core import Renderer as PythonRenderer
    render = PythonRenderer(ir, hls_components_buses)
    return render.component


def elaborate(code: str, rust_backend=True, hls_components: list[HlsComponent] = []) -> TestBench:
    # 1. Lexical analysis and token stream generation
    scanner = Scanner(code)
    tokens_stream = scanner.token_stream

    # 2. Syntax analysis and AST generation
    parser = Parser(tokens_stream)
    ast = parser.ast

    # 3. Semantical analysis and IR generation
    component = render(ast, rust_backend=rust_backend, hls_components=hls_components)

    # 4. Creating the testbench and encapsulating the component
    assert component is not None, "Elaboration failed: component is None"
    test_bench = TestBench(component)
    return test_bench


def elaborate_file(
    file_path, rust_backend=True, hls_components: list[HlsComponent] = []
) -> TestBench:
    p = Path(file_path)
    with p.open('r', encoding='utf-8') as file:
        code = file.read()

    return elaborate(code, rust_backend=rust_backend, hls_components=hls_components)
