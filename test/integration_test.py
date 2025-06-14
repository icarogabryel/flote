"""
Tests for the integration of Scanner, Parser, and Builder classes in the Flote
project.
"""
from pathlib import Path
from flote.scanner import Scanner
from flote.parser import Parser
from flote.builder import Builder


FILE_DIR = Path(__file__).resolve().parent
# 1 for Scanner, 2 for Parser, 3 for Builder
TEST_MODE = 0


def main():
    with open(FILE_DIR / 'src/halfAdder.ft') as file:
        code = file.read()

    if TEST_MODE > 0:
        scanner = Scanner(code)

        print('Token Stream:\n')

        tokens = scanner.get_token_stream()
        for token in tokens:
            print(token)

    if TEST_MODE > 1:
        scanner = Scanner(code)
        parser = Parser(scanner)

        print('\nAST:\n')
        print(parser.ast)

    if TEST_MODE > 2:
        builder = Builder(parser.ast)

        print('\nComponent:\n')
        print(builder.get_component())


if __name__ == "__main__":
    main()
