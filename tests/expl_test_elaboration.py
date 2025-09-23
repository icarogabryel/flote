"""
Tests for the integration of Scanner, Parser, and Builder classes in the Flote
project.
"""
from enum import Enum
from pathlib import Path

from flote import Builder, Parser, Scanner
from flote.backend.backend.python.circuit import Circuit


BASE_DIR = Path(__file__).parent.parent


class TestMode(Enum):
    SCANNER = 0
    PARSER = 1
    BUILDER = 2


TEST_MODE = TestMode.BUILDER.value


def main():
    with open(BASE_DIR / 'tests/examples/Inverter.ft') as file:
        code = file.read()

    if TEST_MODE >= TestMode.SCANNER.value:
        print('- Token Stream:\n')

        scanner = Scanner(code)

        tokens = scanner.token_stream
        for token in tokens:
            print(token)

        if TEST_MODE >= TestMode.PARSER.value:
            print('\n- AST:\n')

            tokens = tokens if TEST_MODE > 0 else []
            parser = Parser(tokens)

            print(parser.ast)

            if TEST_MODE >= TestMode.BUILDER.value:
                print('\nModel:\n')

                ast = parser.ast
                builder = Builder(ast)
                co = builder.get_component()

                ci = Circuit()
                ci.busses = co.busses
                print(ci)
                ci.stabilize()
                print(ci)


if __name__ == "__main__":
    main()
