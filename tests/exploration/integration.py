import flote as ft
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent.parent
TESTS_DIR = BASE_DIR / 'tests'


def test_ast():
    with open(TESTS_DIR / 'duts/HalfAdder.ft', 'r', encoding='utf-8') as file:
        code = file.read()
    ast = ft.get_ast(code)
    print(ast)


if __name__ == '__main__':
    test_ast()
