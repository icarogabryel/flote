import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import flooat as ft

with open('src\\halfAdder.ft', 'r') as f:
    code = f.read()

comp = ft.make_comp(code)
print(comp.bus_dict)

comp.input({'a': False, 'b': False})
comp.input({'a': False, 'b': True})
comp.input({'a': True, 'b': False})
comp.input({'a': True, 'b': True})

comp.save_vcd()
