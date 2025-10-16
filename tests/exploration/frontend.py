import sys
from pathlib import Path

from flote.frontend.builder import Builder
from flote.frontend.parser import Parser
from flote.frontend.scanner import Scanner


BASE_DIR = Path(__file__).parent.parent.parent
TESTS_DIR = BASE_DIR / 'tests'


def make_ir(source_code: str) -> str:
    """Helper function to create an IR from source code."""

    scanner = Scanner(source_code)
    token_stream = scanner.token_stream
    print(token_stream)

    parser = Parser(token_stream)
    ast = parser.ast
    print(ast)

    builder = Builder(ast)
    ir = builder.ir
    print(ir)

    return ir


if __name__ == '__main__':
    """Test the IR generation from source code."""
    duts_dir = TESTS_DIR / 'duts'
    files = sorted([p for p in duts_dir.iterdir() if p.is_file()])

    print("Available DUTs:")
    for i, p in enumerate(files, 1):
        print(f"{i}: {p.name}")

    while True:
        while True:
            try:
                choice = input("Choice the DUT number to see (or 'q' to exit): ").strip()
                if choice.lower() == 'q':
                    sys.exit(0)

                idx = int(choice)
                if 1 <= idx <= len(files):
                    selected = files[idx - 1]
                    break
            except (ValueError, KeyboardInterrupt):
                pass

            print("Entrada inválida. Tente novamente.")

        with open(selected, 'r', encoding='utf-8') as f:
            dut = f.read()

        print('\n')
        ir_json = make_ir(dut)
        print(ir_json)
        print('\n')
