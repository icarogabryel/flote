from json import dumps

from flote.frontend.builder import Builder
from flote.frontend.parser import Parser
from flote.frontend.scanner import Scanner

from tests.utils import BASE_DIR


TESTS_DIR = BASE_DIR / 'tests'


def make_ir(dut: str) -> str:
    """Helper function to create an IR from source code."""

    scanner = Scanner(dut)
    token_stream = scanner.token_stream

    assert token_stream is not None

    parser = Parser(token_stream)
    ast = parser.ast

    builder = Builder(ast)
    ir = builder.ir
    ir.make_influence_lists()

    ir_json = dumps(ir.to_json(), indent=4)

    return ir_json


def test_ir():
    """Test the IR generation from source code."""
    with open(TESTS_DIR / 'duts' / 'Inverter.ft', 'r') as f:
        dut = f.read()

    ir_json = make_ir(dut)

    print(ir_json)


if __name__ == '__main__':
    test_ir()
