import flote as ft
from pathlib import Path


FILE_DIR = Path(__file__).resolve().parent
path = FILE_DIR / 'src/FourBitAdder.ft'


def test():
    half_adder = ft.elaborate_from_file(path)
    print(half_adder)


if __name__ == '__main__':
    test()
