from scanner import Scanner
from parser import Parser

def main():
    with open('..\\tests\\halfAdder.ft', 'r') as f:
        code = f.read()

    print(code)

    scanner = Scanner(code)
    parser = Parser(scanner)

    print(parser.ast)

if __name__ == '__main__':
    main()
