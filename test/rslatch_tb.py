import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import flote as ft

def test_rslatch():
    with open('src/RSLatch.ft', 'r') as f:
        comp = ft.elaborate(f.read())

    print(comp)

    comp.stimulate({'set': False, 'rst': True})
    comp.wait(1)
    comp.stimulate({'set': False, 'rst': False})
    comp.wait(1)
    comp.stimulate({'set': True, 'rst': False})
    comp.wait(1)
    comp.stimulate({'set': False, 'rst': False})
    comp.wait(1)
    comp.stimulate({'set': True, 'rst': False})
    comp.wait(1)
    comp.stimulate({'set': False, 'rst': False})
    comp.wait(1)
    comp.stimulate({'set': False, 'rst': True})
    comp.wait(1)
    comp.stimulate({'set': False, 'rst': False})
    comp.wait(1)
    comp.stimulate({'set': True, 'rst': False})
    comp.wait(1)
    comp.stimulate({'set': False, 'rst': False})
    comp.wait(1)
    comp.stimulate({'set': False, 'rst': True})
    comp.wait(1)
    comp.stimulate({'set': False, 'rst': False})
    comp.wait(1)

    with open('waves/RSLatch.vcd', 'w') as f:
        f.write(comp.dump_vcd())

test_rslatch()
print('ok')
