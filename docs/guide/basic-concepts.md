# Basic Concepts

This page introduces the fundamental concepts you need to understand to work effectively with Flote.

## Components

**Components** are the building blocks of digital circuits in Flote. Every circuit is a component.

```flote
comp MyComponent {
    // Component contents
}
```

Think of a component as a black box with:

- **Inputs**: Signals coming in
- **Outputs**: Signals going out
- **Internal Logic**: How inputs are transformed into outputs

### Main Component

Every Flote file must have exactly one `main` component - the top-level component:

```flote
main comp TopLevel {
    in bit clock;
    out bit result;
}
```

The `main` keyword designates which component is the entry point for simulation.

## Signals (Buses)

**Signals** (called "buses" in Flote) carry digital values through your circuit.

### Declaration

Signals are declared with a direction and type:

```flote
in bit a;      // Input signal
out bit b;     // Output signal
bit c;         // Internal signal
```

**Signal Directions:**

- `in` - Input (values come from outside)
- `out` - Output (values go to outside)
- (no direction) - Internal (used only inside component)

### Bit Type

Currently, Flote supports the `bit` type for binary (0/1) signals:

```flote
bit signal;    // Single bit
bit bus[8];    // 8-bit bus
bit data[-8];  // 8-bit bus (descending indices)
```

## Logic Operations

Flote provides all standard logic gates as operators:

### Basic Gates

```flote
out bit not_a = not a;        // NOT
out bit a_and_b = a and b;    // AND
out bit a_or_b = a or b;      // OR
out bit a_xor_b = a xor b;    // XOR
```

### Complementary Gates

```flote
out bit nand_out = a nand b;  // NAND
out bit nor_out = a nor b;    // NOR
out bit xnor_out = a xnor b;  // XNOR
```

### Operator Precedence

From highest to lowest:

1. `not` (unary)
2. `and`, `nand`
3. `xor`, `xnor`
4. `or`, `nor`

Use parentheses to override precedence:

```flote
out bit result = (a or b) and c;  // Different from: a or (b and c)
```

## Assignment

Signals receive values through assignment using `=`:

### Direct Assignment

```flote
out bit result = input;  // Direct connection
```

### Expression Assignment

```flote
out bit result = a xor (b and c);  // Complex expression
```

### Multiple Assignments (NOT Allowed)

```flote
bit signal = input1;
signal = input2;  // ERROR: signal already assigned
```

!!! warning "Single Assignment Rule"
    Each signal can only be assigned once. This prevents ambiguity and models hardware reality - a wire can't have two drivers.

## Literals

You can use binary literals directly:

```flote
bit const_zero = "0";
bit const_one = "1";
bit multi_bit = "1010";   // 4-bit constant
```

Literals are strings of `0` and `1` characters, enclosed in quotes.

## References

Reference signals by their identifier:

```flote
comp Example {
    in bit input;
    bit internal = input;      // Reference input
    out bit output = internal; // Reference internal
}
```

### Hierarchical References

Access sub-component signals using dot notation:

```flote
comp Parent {
    sub Child as c;
    out bit result = c.output;  // Reference child's output
}
```

## Vectors (Buses)

Multi-bit signals are declared with size:

### Vector Declaration

```flote
bit bus[8];     // 8-bit ascending: bus[0] to bus[7]
bit data[-8];   // 8-bit descending: data[7] to data[0]
```

### Indexing

Access individual bits:

```flote
comp Example {
    in bit data[8];
    out bit bit0 = data[0];
    out bit bit7 = data[7];
}
```

### Slicing

Extract bit ranges:

```flote
in bit data[8];
out bit lower = data[0:3];  // Bits 0, 1, 2, 3
out bit upper = data[4:7];  // Bits 4, 5, 6, 7
```

### Concatenation

Combine signals into vectors:

```flote
in bit a;
in bit b;
in bit c;
out bit abc[3] = <a, b, c>;  // Concatenate into 3-bit bus
```

Order matters - first element becomes the most significant:

```flote
<a, b, c>  // a is bit 2, b is bit 1, c is bit 0
```

## Hierarchical Design

Build complex circuits from simpler components:

### Sub-component Instantiation

```flote
comp HalfAdder {
    in bit a;
    in bit b;
    out bit sum = a xor b;
    out bit carry = a and b;
}

comp FullAdder {
    sub HalfAdder as ha1;  // Instantiate HalfAdder
    sub HalfAdder as ha2;  // Instantiate another

    // Connect to sub-components...
}
```

### Aliasing

The `as` keyword creates an alias for the instance:

```flote
sub HalfAdder as ha1;  // 'ha1' is the alias
```

Without alias, use the component name:

```flote
sub HalfAdder;  // Access as 'HalfAdder.signal'
```

### Connecting Sub-components

Connect parent signals to child inputs:

```flote
comp Parent {
    in bit parent_in;
    sub Child as c;

    c.input = parent_in;  // Connect parent input to child input
}
```

Read child outputs:

```flote
comp Parent {
    sub Child as c;
    out bit parent_out = c.output;  // Read child output
}
```

## Feedback

Flote supports feedback (signals that depend on themselves):

```flote
comp RSLatch {
    in bit set;
    in bit rst;
    out bit q;
    out bit not_q;

    q = rst nor not_q;      // q depends on not_q
    not_q = set nor q;      // not_q depends on q
}
```

The simulator uses **delta cycles** to resolve feedback until signals stabilize.

!!! warning "Oscillation"
    Some feedback configurations never stabilize (e.g., `a = not a`). The simulator will detect infinite loops and raise an error.

## Comments

Flote supports single-line comments:

```flote
// This is a comment
comp Example {  // Comment after code
    in bit a;   // Another comment
}
```

Multi-line comments are not currently supported - use multiple single-line comments:

```flote
// This is
// a multi-line
// comment
```

## Identifiers

Valid identifier rules:

- Start with letter or underscore: `a`, `_signal`
- Continue with letters, digits, underscores: `signal1`, `data_bus`
- Case-sensitive: `Signal` ≠ `signal`
- Cannot be keywords: `bit`, `comp`, `in`, `out`, etc.

### HLS Component Prefix

Identifiers starting with `@` are reserved for HLS components:

```flote
sub @MyHLSComponent;  // External Python component
```

## Keywords

Reserved words you cannot use as identifiers:

```
comp    main    sub     as
in      out     bit
and     or      xor     not
nand    nor     xnor
```

## Best Practices

### Naming Conventions

```flote
// Use descriptive names
comp FullAdder {          // PascalCase for components
    in bit carry_in;      // snake_case for signals
    out bit sum_bit;
}
```

### Signal Organization

```flote
comp Organized {
    // Group by direction
    in bit input1;
    in bit input2;

    // Internal signals
    bit intermediate;

    // Outputs last
    out bit output1;
    out bit output2;
}
```

### Comment Complex Logic

```flote
comp Complex {
    in bit a;
    in bit b;
    in bit c;

    // Compute majority function: output 1 if >= 2 inputs are 1
    out bit majority = (a and b) or (b and c) or (a and c);
}
```

## Next Steps

Now that you understand the basics:

- **[Syntax Reference](syntax-reference.md)** - Complete language grammar
- **[Components](components.md)** - Deep dive into component design
- **[Logic Operations](logic-operations.md)** - Master boolean algebra in Flote
- **[Examples](../examples/half-adder.md)** - See real circuits

---

*These concepts form the foundation of all Flote circuits. Master them and you're ready for anything!*
