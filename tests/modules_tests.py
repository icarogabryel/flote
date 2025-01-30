import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from flooat.scanner import Scanner
from flooat.parser import Parser


def main():
    with open('halfAdder.ft', 'r') as file:
        code = file.read()

    print("Token Stream:\n")
    scanner = Scanner(code)
    for token in scanner.token_stream:  # Print the token stream
        print(token)

    print("\nAST:\n")
    parser = Parser(scanner.token_stream)
    print(parser.ast)

if __name__ == '__main__':
    main()
