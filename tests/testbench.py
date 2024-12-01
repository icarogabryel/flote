import flooat as ft

with open('..\\tests\\halfAdder.ft', 'r') as f:
    code = f.read()

comp = ft.make_comp(code)

comp.input({'a': False, 'b': False})
comp.input({'a': False, 'b': True})
comp.input({'a': True, 'b': False})
comp.input({'a': True, 'b': True})

comp.save_vcd()
