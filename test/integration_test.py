# Tests for the scanner module

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flooat.scanner import Scanner
from flooat.parser import Parser


def main():
    with open('src/incrementor.ft', 'r') as file:
        code = file.read()

    scanner = Scanner(code)

    print("Token Stream:\n")
    for token in scanner.token_stream:  # Print the token stream
        print(token)

    parser = Parser(scanner.token_stream)

    print("\nAST:\n")
    print(parser.ast)  # Print the AST


if __name__ == "__main__":
    main()
