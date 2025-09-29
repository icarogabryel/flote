import flote as ft

from tests.utils import BASE_DIR


def test():
    half_adder = ft.elaborate_from_file(
        BASE_DIR / 'tests/duts/HalfAdder.ft'
    )
    print(half_adder)

    half_adder.update({'a': '0', 'b': '0'})
    half_adder.wait(10)

    print(half_adder)

    half_adder.update({'a': '0', 'b': '1'})
    half_adder.wait(10)

    print(half_adder)

    half_adder.update({'a': '1', 'b': '0'})
    half_adder.wait(10)

    print(half_adder)

    half_adder.update({'a': '1', 'b': '1'})
    half_adder.wait(10)

    print(half_adder)

    #half_adder.save_vcd('HalfAdder.vcd')


if __name__ == '__main__':
    test()
