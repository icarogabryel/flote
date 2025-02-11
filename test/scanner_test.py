# Tests for the scanner module

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flooat import Scanner


def main():
    with open('example/incrementor.ft', 'r') as file:
        code = file.read()

    scanner = Scanner(code)

    print("Token Stream:\n")
    for token in scanner.token_stream:  # Print the token stream
        print(token)

if __name__ == "__main__":
    main()
