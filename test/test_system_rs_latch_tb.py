import flote as ft
from pathlib import Path


FILE_DIR = Path(__file__).resolve().parent


def test_rs_latch():
    latch = ft.elaborate_from_file(FILE_DIR / 'src/RsLatch.ft')

    print(latch)

    latch.stimulate({'set': '0', 'rst': '1'})
    latch.wait(1)
    latch.stimulate({'set': '0', 'rst': '0'})
    latch.wait(1)
    latch.stimulate({'set': '1', 'rst': '0'})
    latch.wait(1)
    latch.stimulate({'set': '0', 'rst': '0'})
    latch.wait(1)
    latch.stimulate({'set': '1', 'rst': '0'})
    latch.wait(1)
    latch.stimulate({'set': '0', 'rst': '0'})
    latch.wait(1)
    latch.stimulate({'set': '0', 'rst': '1'})
    latch.wait(1)
    latch.stimulate({'set': '0', 'rst': '0'})
    latch.wait(1)
    latch.stimulate({'set': '1', 'rst': '0'})
    latch.wait(1)
    latch.stimulate({'set': '0', 'rst': '0'})
    latch.wait(1)
    latch.stimulate({'set': '0', 'rst': '1'})
    latch.wait(1)
    latch.stimulate({'set': '0', 'rst': '0'})
    latch.wait(1)

    latch.save_vcd(FILE_DIR / 'waves/RsLatch.vcd')


if __name__ == '__main__':
    test_rs_latch()
