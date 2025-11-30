# Syntax Reference

This page provides a complete reference for Flote's syntax based on its EBNF grammar.

## Grammar Overview

Flote's grammar is formally defined in Extended Backus-Naur Form (EBNF). This reference provides practical examples for each construct.

## Program Structure

A Flote program consists of component declarations:

```flote
comp ComponentA {
    // ...
}

main comp ComponentB {
    // ...
}

comp ComponentC {
    // ...
}
```

**Rules:**

- At least one component must be declared
- Exactly one component must be marked as `main`
- Components can appear in any order

## Component Declaration

### Syntax

```text
component ::= ["main"] "comp" identifier "{" component_body "}"
```

### Examples

```flote
// Simple component
comp SimpleGate {
    in bit a;
    out bit b = not a;
}

// Main component
main comp TopLevel {
    in bit clock;
    out bit data;
}
```

## Signal Declarations

### Syntax

```text
bus_declaration ::= [direction] "bit" identifier [vector] ["=" assignment]

direction ::= "in" | "out"

vector ::= "[" ["-"] integer "]"
```

### Input Signals

```flote
in bit single_input;        // Single bit input
in bit input_bus[8];        // 8-bit input (ascending)
in bit input_bus[-8];       // 8-bit input (descending)
```

### Output Signals

```flote
out bit single_output = logic;       // Must be assigned
out bit output_bus[4] = <a, b, c, d>;
```

### Internal Signals

```flote
bit internal;                   // No direction specified
bit intermediate = a and b;
bit internal_bus[8];
```

## Vector Indexing

### Ascending Vectors

```flote
in bit data[8];  // Indices: 0, 1, 2, 3, 4, 5, 6, 7

out bit bit0 = data[0];
out bit bit7 = data[7];
out bit slice = data[2:5];  // Bits 2, 3, 4, 5
```

### Descending Vectors

```flote
in bit data[-8];  // Indices: 7, 6, 5, 4, 3, 2, 1, 0

out bit bit7 = data[7];
out bit bit0 = data[0];
out bit slice = data[5:2];  // Bits 5, 4, 3, 2
```

### Slicing Syntax

```text
index ::= identifier "[" integer [":" integer] "]"
```

Examples:

```flote
data[3]      // Single bit at index 3
data[0:3]    // Slice from 0 to 3 (inclusive)
data[4:7]    // Slice from 4 to 7
```

## Logic Operations

### Unary Operators

```text
not_expr ::= "not" primary
```

```flote
out bit inverted = not input;
out bit complex = not (a and b);
```

### Binary Operators

```text
and_expr ::= primary ("and" | "nand") primary
xor_expr ::= and_expr ("xor" | "xnor") and_expr
or_expr ::= xor_expr ("or" | "nor") xor_expr
```

**AND Family:**

```flote
out bit and_result = a and b;
out bit nand_result = a nand b;
```

**XOR Family:**

```flote
out bit xor_result = a xor b;
out bit xnor_result = a xnor b;
```

**OR Family:**

```flote
out bit or_result = a or b;
out bit nor_result = a nor b;
```

### Operator Precedence

From highest to lowest:

1. **Parentheses** `()`
2. **NOT** `not`
3. **AND/NAND** `and`, `nand`
4. **XOR/XNOR** `xor`, `xnor`
5. **OR/NOR** `or`, `nor`

**Example with precedence:**

```flote
// Without parentheses
out bit result1 = a or b and c;     // = a or (b and c)

// With parentheses
out bit result2 = (a or b) and c;   // Different!

// Complex expression
out bit result3 = not a and b or c xor d;
// Evaluates as: ((not a) and b) or (c xor d)
```

## Concatenation

### Syntax

```text
concatenation ::= "<" assignment ("," assignment)* ">"
```

### Examples

```flote
in bit a;
in bit b;
in bit c;

// Concatenate into 3-bit bus
out bit abc[3] = <a, b, c>;

// Concatenate vectors
in bit low[4];
in bit high[4];
out bit byte[8] = <high, low>;

// Mixed concatenation
in bit bits[4];
in bit extra;
out bit extended[5] = <bits, extra>;
```

**Bit Ordering:**

The first element in concatenation becomes the highest index:

```flote
<a, b, c>  // a = index 2, b = index 1, c = index 0
```

## Literals

### Syntax

```text
literal ::= '"' ("0" | "1")+ '"'
```

### Examples

```flote
bit zero = "0";
bit one = "1";
bit four_bits = "1010";
bit byte = "11110000";

// Can assign to buses
out bit data[8] = "10101010";
```

**Rules:**

- Must be enclosed in double quotes
- Only `0` and `1` characters allowed
- Length must match target bus size

## Sub-component Instantiation

### Syntax

```text
sub_declaration ::= "sub" identifier ["as" identifier]
```

### Examples

```flote
// Without alias
sub HalfAdder;

// With alias
sub HalfAdder as ha1;
sub HalfAdder as ha2;

// HLS components (start with @)
sub @PythonCounter as counter;
```

## Signal Assignment

### To Sub-component Inputs

```text
sub_assignment ::= identifier "." identifier "=" assignment
```

```flote
comp Parent {
    in bit parent_input;
    sub Child as c;

    // Assign to child's input
    c.input = parent_input;
    c.enable = "1";
}
```

### From Sub-component Outputs

```flote
comp Parent {
    sub Child as c;

    // Read child's output
    out bit parent_output = c.output;
    bit internal = c.status;
}
```

## References

### Simple Reference

```flote
out bit output = input;  // Reference another signal
```

### Hierarchical Reference

```flote
sub Child as c;
out bit data = c.signal;  // Reference child's signal
```

### Indexed Reference

```flote
in bit bus[8];
out bit bit3 = bus[3];
out bit slice = bus[0:3];
```

## Complete Examples

### Simple Component

```flote
comp Inverter {
    in bit input;
    out bit output = not input;
}
```

### Component with Internal Signals

```flote
comp AndOrGate {
    in bit a;
    in bit b;
    in bit c;

    bit and_result = a and b;
    out bit or_result = and_result or c;
}
```

### Hierarchical Component

```flote
comp HalfAdder {
    in bit a;
    in bit b;
    out bit sum = a xor b;
    out bit carry = a and b;
}

comp FullAdder {
    in bit a;
    in bit b;
    in bit carry_in;

    sub HalfAdder as ha1;
    sub HalfAdder as ha2;

    ha1.a = a;
    ha1.b = b;

    ha2.a = ha1.sum;
    ha2.b = carry_in;

    out bit sum = ha2.sum;
    out bit carry_out = ha1.carry or ha2.carry;
}
```

### Component with Vectors

```flote
comp ByteAnd {
    in bit a[8];
    in bit b[8];
    out bit result[8];

    result[0] = a[0] and b[0];
    result[1] = a[1] and b[1];
    result[2] = a[2] and b[2];
    result[3] = a[3] and b[3];
    result[4] = a[4] and b[4];
    result[5] = a[5] and b[5];
    result[6] = a[6] and b[6];
    result[7] = a[7] and b[7];
}
```

### Feedback Circuit

```flote
comp SRLatch {
    in bit set;
    in bit reset;
    out bit q;
    out bit q_bar;

    q = reset nor q_bar;
    q_bar = set nor q;
}
```

## Comments

```flote
// Single-line comment

comp Example {
    in bit a;  // Inline comment
    // Comment before code
    out bit b = not a;
}
```

**Rules:**

- Start with `//`
- Extend to end of line
- No multi-line comment syntax

## Identifiers

### Rules

```text
identifier ::= (letter | "_") (letter | digit | "_")*
```

- Must start with letter or underscore
- Can contain letters, digits, underscores
- Case-sensitive
- Cannot be keywords

### Valid Examples

```flote
mySignal
input_1
_internal
Data_Bus_8bit
```

### Invalid Examples

```text
1signal      // Starts with digit
my-signal    // Contains hyphen
in           // Reserved keyword
```

## Keywords

Reserved words that cannot be used as identifiers:

```text
and      nand     as       bit      comp
in       main     nor      not      or
out      sub      xnor     xor
```

## Special Prefixes

### HLS Components

Identifiers starting with `@` are reserved for HLS (High-Level Synthesis) components:

```flote
sub @Counter as cnt;
sub @Memory as mem;
```

These components are defined in Python rather than Flote.

## Whitespace

Whitespace (spaces, tabs, newlines) is generally ignored except:

- Inside string literals
- Between tokens

Both are valid:

```flote
// Compact
comp A{in bit a;out bit b=not a;}

// Spaced
comp A {
    in bit a;
    out bit b = not a;
}
```

## Formal Grammar (EBNF)

The complete formal grammar from `docs/flote.ebnf`:

```ebnf
program = component, {component};

component = ["main"], "comp", identifier, "{", component_body, "}";

component_body = {bus_declaration | sub_declaration | sub_assignment};

bus_declaration = [direction], "bit", identifier, [vector], ["=", assignment];

direction = "in" | "out";

vector = "[", ["-"], integer, "]";

sub_declaration = "sub", identifier, ["as", identifier];

sub_assignment = identifier, ".", identifier, "=", assignment;

assignment = logic_or | concatenation;

concatenation = "<", assignment, {",", assignment}, ">";

logic_or = logic_xor, {("or" | "nor"), logic_xor};

logic_xor = logic_and, {("xor" | "xnor"), logic_and};

logic_and = logic_not, {("and" | "nand"), logic_not};

logic_not = "not", logic_not | primary;

primary = literal | index | reference | "(", assignment, ")";

literal = '"', ("0" | "1"), {("0" | "1")}, '"';

index = identifier, "[", integer, [":", integer], "]";

reference = identifier, [".", identifier];

identifier = (letter | "_"), {letter | digit | "_"};

integer = digit, {digit};

letter = "a" | "b" | ... | "z" | "A" | "B" | ... | "Z";

digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9";
```

## Next Steps

- **[Basic Concepts](basic-concepts.md)** - Understand the fundamentals
- **[Components](components.md)** - Learn component design patterns
- **[Logic Operations](logic-operations.md)** - Master boolean expressions
- **[Examples](../examples/half-adder.md)** - See syntax in action

---

*This reference covers all valid Flote syntax. Use it as a quick lookup while coding!*
