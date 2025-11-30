# Full Adder

A **Full Adder** adds three 1-bit inputs: two data bits and a carry-in. It produces a sum and carry-out.

## Truth Table

| A | B | Carry In | Sum | Carry Out |
|---|---|----------|-----|-----------|
| 0 | 0 | 0        | 0   | 0         |
| 0 | 0 | 1        | 1   | 0         |
| 0 | 1 | 0        | 1   | 0         |
| 0 | 1 | 1        | 0   | 1         |
| 1 | 0 | 0        | 1   | 0         |
| 1 | 0 | 1        | 0   | 1         |
| 1 | 1 | 0        | 0   | 1         |
| 1 | 1 | 1        | 1   | 1         |

## Logic

**Sum:** Output 1 when odd number of inputs are 1

```
sum = a ⊕ b ⊕ carry_in
```

**Carry Out:** Output 1 when at least two inputs are 1

```
carry_out = (a ∧ b) ∨ (a ∧ carry_in) ∨ (b ∧ carry_in)
```

## Implementation Strategies

### Strategy 1: Direct Logic

Implement truth table directly with logic gates.

### Strategy 2: Two Half Adders

A full adder can be built from two half adders and an OR gate.

## Implementation: Direct Logic

```flote
// FullAdderDirect.ft
main comp FullAdder {
    in bit a;
    in bit b;
    in bit carry_in;

    // Sum: XOR all three inputs
    bit a_xor_b = a xor b;
    out bit sum = a_xor_b xor carry_in;

    // Carry: majority function
    bit ab = a and b;
    bit a_cin = a and carry_in;
    bit b_cin = b and carry_in;
    out bit carry_out = ab or a_cin or b_cin;
}
```

## Implementation: Two Half Adders

```flote
// HalfAdder.ft
comp HalfAdder {
    in bit a;
    in bit b;
    out bit sum = a xor b;
    out bit carry = a and b;
}

// FullAdderHierarchical.ft
main comp FullAdder {
    in bit a;
    in bit b;
    in bit carry_in;

    // First half adder: add a and b
    sub HalfAdder as ha1;
    ha1.a = a;
    ha1.b = b;

    // Second half adder: add result with carry_in
    sub HalfAdder as ha2;
    ha2.a = ha1.sum;
    ha2.b = carry_in;

    // Output sum from second half adder
    out bit sum = ha2.sum;

    // Carry out if either half adder produced carry
    out bit carry_out = ha1.carry or ha2.carry;
}
```

## Testbench

```python
# test_full_adder.py
import flote as ft

# Elaborate the circuit
full_adder = ft.elaborate_file('FullAdder.ft')

# Test all 8 input combinations
test_cases = [
    ('0', '0', '0', '0', '0'),  # (a, b, cin, expected_sum, expected_cout)
    ('0', '0', '1', '1', '0'),
    ('0', '1', '0', '1', '0'),
    ('0', '1', '1', '0', '1'),
    ('1', '0', '0', '1', '0'),
    ('1', '0', '1', '0', '1'),
    ('1', '1', '0', '0', '1'),
    ('1', '1', '1', '1', '1'),
]

print("Testing Full Adder")
print("=" * 60)
print("A | B | Cin | Sum | Cout | Expected | Status")
print("-" * 60)

all_passed = True

for a, b, cin, expected_sum, expected_cout in test_cases:
    # Apply inputs
    full_adder.update({'a': a, 'b': b, 'carry_in': cin})
    full_adder.wait(10)

    # Read outputs
    sum_out = full_adder.read('sum')
    cout_out = full_adder.read('carry_out')

    # Check results
    passed = (sum_out == expected_sum and cout_out == expected_cout)
    status = "✓ PASS" if passed else "✗ FAIL"
    all_passed = all_passed and passed

    print(f"{a} | {b} |  {cin}  |  {sum_out}  |  {cout_out}   | {expected_sum},{expected_cout}      | {status}")

print("-" * 60)
print(f"Result: {'All tests passed! ✓' if all_passed else 'Some tests failed ✗'}")

# Save waveform
full_adder.save_vcd('full_adder.vcd')
print("\nWaveform saved to full_adder.vcd")
```

## Running the Example

```bash
# Run the testbench
python test_full_adder.py
```

**Expected Output:**

```
Testing Full Adder
============================================================
A | B | Cin | Sum | Cout | Expected | Status
------------------------------------------------------------
0 | 0 |  0  |  0  |  0   | 0,0      | ✓ PASS
0 | 0 |  1  |  1  |  0   | 1,0      | ✓ PASS
0 | 1 |  0  |  1  |  0   | 1,0      | ✓ PASS
0 | 1 |  1  |  0  |  1   | 0,1      | ✓ PASS
1 | 0 |  0  |  1  |  0   | 1,0      | ✓ PASS
1 | 0 |  1  |  0  |  1   | 0,1      | ✓ PASS
1 | 1 |  0  |  0  |  1   | 0,1      | ✓ PASS
1 | 1 |  1  |  1  |  1   | 1,1      | ✓ PASS
------------------------------------------------------------
Result: All tests passed! ✓

Waveform saved to full_adder.vcd
```

## Viewing the Waveform

Open `full_adder.vcd` in GTKWave:

```bash
gtkwave full_adder.vcd
```

You'll see:
- **Inputs:** a, b, carry_in changing through all 8 combinations
- **Outputs:** sum and carry_out responding correctly
- **Internal signals:** (if using hierarchical version) ha1.sum, ha1.carry, ha2.sum, ha2.carry

## Building a 4-bit Adder

Chain full adders to create multi-bit adder:

```flote
// Adder4bit.ft
comp FullAdder {
    in bit a;
    in bit b;
    in bit carry_in;
    out bit sum = (a xor b) xor carry_in;
    bit ab = a and b;
    bit a_cin = a and carry_in;
    bit b_cin = b and carry_in;
    out bit carry_out = ab or a_cin or b_cin;
}

main comp Adder4bit {
    in bit a[4];
    in bit b[4];
    in bit carry_in;
    out bit sum[4];
    out bit carry_out;

    // Instantiate 4 full adders
    sub FullAdder as fa0;
    sub FullAdder as fa1;
    sub FullAdder as fa2;
    sub FullAdder as fa3;

    // Connect bit 0 (LSB)
    fa0.a = a[0];
    fa0.b = b[0];
    fa0.carry_in = carry_in;
    sum[0] = fa0.sum;

    // Connect bit 1
    fa1.a = a[1];
    fa1.b = b[1];
    fa1.carry_in = fa0.carry_out;  // Carry chain
    sum[1] = fa1.sum;

    // Connect bit 2
    fa2.a = a[2];
    fa2.b = b[2];
    fa2.carry_in = fa1.carry_out;
    sum[2] = fa2.sum;

    // Connect bit 3 (MSB)
    fa3.a = a[3];
    fa3.b = b[3];
    fa3.carry_in = fa2.carry_out;
    sum[3] = fa3.sum;
    carry_out = fa3.carry_out;
}
```

**Test the 4-bit adder:**

```python
# test_adder4bit.py
import flote as ft

adder = ft.elaborate_file('Adder4bit.ft')

# Test: 5 + 3 = 8
adder.update({'a': '0101', 'b': '0011', 'carry_in': '0'})
adder.wait(10)
result = adder.read('sum')
print(f"5 + 3 = {int(result, 2)}")  # Should print 8

# Test: 15 + 1 = 16 (overflow)
adder.update({'a': '1111', 'b': '0001', 'carry_in': '0'})
adder.wait(10)
result = adder.read('sum')
carry = adder.read('carry_out')
print(f"15 + 1 = {int(result, 2)}, carry={carry}")  # sum=0, carry=1

adder.save_vcd('adder4bit.vcd')
```

## Key Concepts

### Carry Chain

Full adders connect carry-out to carry-in of next stage:

```
FA0.carry_out → FA1.carry_in → FA2.carry_in → FA3.carry_in
```

This creates a **ripple carry adder**.

### Hierarchical Reuse

The same FullAdder component is instantiated 4 times:

```flote
sub FullAdder as fa0;
sub FullAdder as fa1;
sub FullAdder as fa2;
sub FullAdder as fa3;
```

Each instance is independent but shares the same logic.

### Signal Indexing

Access individual bits of buses:

```flote
fa0.a = a[0];  // Connect bit 0 of 4-bit bus 'a'
fa1.a = a[1];  // Connect bit 1
```

## Challenges

### Challenge 1: Subtractor

Modify the 4-bit adder to perform subtraction using two's complement:

- Invert the second operand
- Set carry_in to 1

```flote
// Hint: Use XOR to conditionally invert
bit b_inverted = b xor sub_mode;
```

### Challenge 2: Adder/Subtractor

Add a control signal that switches between add and subtract:

```flote
in bit operation;  // 0=add, 1=subtract
```

### Challenge 3: 8-bit Adder

Extend to 8 bits. Can you use a loop in Python to generate the connections?

## Next Steps

- **[RS Latch](rs-latch.md)** - Learn about sequential circuits
- **[Multiplexer](multiplexer.md)** - Data selection circuits
- **[Advanced: HLS Components](../advanced/hls-components.md)** - Implement ALU in Python

---

*The full adder is fundamental to arithmetic circuits. Master it and you can build adders, subtractors, and ALUs!*
