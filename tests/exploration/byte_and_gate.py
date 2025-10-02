from flote import elaborate_from_file

byte_and_gate = elaborate_from_file(
    'tests/examples/ByteAndGate.ft'
)

print(byte_and_gate)

byte_and_gate.update({'a': '00000000', 'b': '00000000'})
byte_and_gate.wait(10)

byte_and_gate.update({'a': '11111111', 'b': '00000000'})
byte_and_gate.wait(10)

byte_and_gate.update({'a': '11111111', 'b': '11111111'})
byte_and_gate.wait(10)
byte_and_gate.update({'a': '10101010', 'b': '11001100'})
byte_and_gate.wait(10)

byte_and_gate.save_vcd('ByteAndGate.vcd')
