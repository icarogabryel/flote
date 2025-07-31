"""
Tests for the integration of Scanner, Parser, and Builder classes in the Flote
project.
"""
from enum import Enum
from pathlib import Path

from flote import Builder, Parser, Scanner


BASE_DIR = Path(__file__).parent.parent


class TestMode(Enum):
    NONE = 0
    SCANNER = 1
    PARSER = 2
    BUILDER = 3


TEST_MODE = TestMode.BUILDER.value


def main():
    with open(BASE_DIR / 'tests/src/HalfAdder.ft') as file:
        code = file.read()

    if TEST_MODE > 0:
        print('- Token Stream:\n')

        scanner = Scanner(code)

        tokens = scanner.token_stream
        for token in tokens:
            print(token)

        if TEST_MODE > 1:
            print('\n- AST:\n')

            tokens = tokens if TEST_MODE > 0 else []
            parser = Parser(tokens)

            print(parser.ast)

            if TEST_MODE > 2:
                print('\nComponent:\n')

                ast = parser.ast
                builder = Builder(ast)
                print(builder.get_component())


if __name__ == "__main__":
    main()
