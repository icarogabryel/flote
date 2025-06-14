import flote as ft


half_adder = ft.elaborate_from_file('src/halfAdder.ft')

half_adder.stimulate({'a': '0', 'b': '0'})
half_adder.wait(10)

half_adder.stimulate({'a': '0', 'b': '1'})
half_adder.wait(10)

half_adder.stimulate({'a': '1', 'b': '0'})
half_adder.wait(10)

half_adder.stimulate({'a': '1', 'b': '1'})
half_adder.wait(10)

half_adder.save_vcd('halfAdder.vcd')
