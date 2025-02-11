import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import src as ft

def test_rslatch():
    with open('RSLatch.ft', 'r') as f:
        comp = ft.make_comp(f.read())

    comp.input({'s': False, 'r': True})
    comp.input({'s': False, 'r': False})
    comp.input({'s': True, 'r': False})
    comp.input({'s': False, 'r': False})
    comp.input({'s': True, 'r': False})
    comp.input({'s': False, 'r': False})
    comp.input({'s': False, 'r': True})
    comp.input({'s': False, 'r': False})

    comp.save_vcd()

test_rslatch()
print('ok')
