import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import flote as ft

def test_rslatch():
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

test_rslatch()
print('ok')
