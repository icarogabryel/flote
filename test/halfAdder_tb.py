import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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
