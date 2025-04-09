import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import flote as ft

with open('src\\halfAdder.ft', 'r') as f:
    code = f.read()

comp = ft.elaborate(code)
print(comp.bus_dict)

comp.stimulate({'a': False, 'b': False})
comp.wait(10)
comp.stimulate({'a': False, 'b': True})
comp.wait(10)
comp.stimulate({'a': True, 'b': False})
comp.wait(10)
comp.stimulate({'a': True, 'b': True})
comp.wait(10)

result = comp.dump_vcd()

print(result)
