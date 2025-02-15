# Tests for the scanner module

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flooat.scanner import Scanner
from flooat.parser import Parser
from flooat.builder import Builder

# 1 for Scanner, 2 for Parser, 3 for Builder
TEST_MODE = 2


def main():

    with open('src/incrementor.ft', 'r') as file:
        code = file.read()

    if TEST_MODE > 0:
        scanner = Scanner(code)

        print("Token Stream:\n")
        for token in scanner.token_stream:
            scanner = Scanner(code)

    if TEST_MODE > 1:
        parser = Parser(scanner.token_stream)

        print("\nAST:\n")
        print(parser.ast)

    if TEST_MODE > 2:
        builder = Builder(parser.ast)

        print("\Component:\n")
        print(builder.get_component())


if __name__ == "__main__":
    main()
