import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from flooat.scanner import Scanner
from flooat.parser import Parser
from flooat.visitor import Visitor


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

    print('\nComponent:\n')
    visitor = Visitor(parser.ast)
    component = visitor.get_component()
    print(component)

    print('\nBits:\n')
    component.input({'a': False, 'b': True})
    component.input({'a': True, 'b': False})
    component.input({'a': True, 'b': True})
    component.input({'a': False, 'b': False})
    component.save_vcd('test')

if __name__ == '__main__':
    main()
