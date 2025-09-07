import flote as ft
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent


def test_rs_latch():
    latch = ft.elaborate_from_file(BASE_DIR / 'tests/examples/RsLatch.ft')

    print(latch)

    latch.update({'set': '0', 'rst': '1'})
    latch.wait(1)
    latch.update({'set': '0', 'rst': '0'})
    latch.wait(1)
    latch.update({'set': '1', 'rst': '0'})
    latch.wait(1)
    latch.update({'set': '0', 'rst': '0'})
    latch.wait(1)
    latch.update({'set': '1', 'rst': '0'})
    latch.wait(1)
    latch.update({'set': '0', 'rst': '0'})
    latch.wait(1)
    latch.update({'set': '0', 'rst': '1'})
    latch.wait(1)
    latch.update({'set': '0', 'rst': '0'})
    latch.wait(1)
    latch.update({'set': '1', 'rst': '0'})
    latch.wait(1)
    latch.update({'set': '0', 'rst': '0'})
    latch.wait(1)
    latch.update({'set': '0', 'rst': '1'})
    latch.wait(1)
    latch.update({'set': '0', 'rst': '0'})
    latch.wait(1)

    # latch.save_vcd(BASE_DIR / 'tests/waves/RsLatch.vcd')


if __name__ == '__main__':
    test_rs_latch()
