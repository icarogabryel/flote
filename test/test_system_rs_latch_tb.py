import flote as ft


def test_rs_latch():
    latch = ft.elaborate_from_file('src/RsLatch.ft')

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

    latch.save_vcd('waves/RsLatch.vcd')


if __name__ == '__main__':
    test_rs_latch()
