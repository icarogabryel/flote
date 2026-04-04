# Flote

<br>

<div align="center">
  <img src="https://i.postimg.cc/nz5SPMR6/logo.png" width="40%" alt="Flote logo"/>
</div>

<br>

<div align="center">
  <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/icarogabryel/flote?style=flat&logo=github&color=yellow" />
  <img alt="GitHub Workflow" src="https://img.shields.io/github/actions/workflow/status/icarogabryel/flote/CI.yml" />
  <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/flote?color=blue" />
  <img alt="License" src="https://img.shields.io/github/license/icarogabryel/flote" />
  <img alt="Documentation" src="https://img.shields.io/badge/Docs-Read%20the%20Docs-orange" />
</div>

## 🛸 Introduction

Flote is a hardware description language and Python framework for hardware simulation. It is designed to be **friendly, simple, light and productive**. More easy to use and learn than Verilog and VHDL. Using Flote, you can create integrated circuits component by using it's HDL and/or Python framework.

<div align="center">
  <img src="https://i.postimg.cc/xC7p4qpr/print.png" width="90%" alt="Flote in VS Code"/>
</div>

Here is an example of a half adder in Flote:

```flote
comp HalfAdder {
  in bit a, b;

  out bit sum = a xor b;
  out bit carry = a and b;

}
```

## ⚙️ How it works

Flote's frontend (the elaborator) parses designs written in the Flote HDL and produces a netlist representing the circuit. The frontend includes a scanner, a parser and a builder, with the builder responsible for assembling the netlist. The backend (available in Python or Rust) converts that netlist into a simulation model - an object exposed by the Python API that replicates the integrated circuit's behavior. The simulation model is composed of signals and buses and relies on event-driven simulation combined with dynamic programming techniques to compute the circuit's temporal behavior. The Python package also supports exporting simulation data to waveform files (for example, VCD).

## 📚 Documentation

The documentation can be found at [flote.readthedocs.io](https://flote.readthedocs.io).

## 🚀 Release

Flote is in beta development. You can see the latest releases in [the GitHub repository](https://github.com/icarogabryel/flote/releases).

## 🎁 Buy Me a ~~Coffee~~ Beer

<div align="center">
  <img src="https://i.postimg.cc/VNND86yt/cold-stone.gif" width="300px" alt="Stone Cold"/>
</div>

If Flote helps you, consider supporting its development:

[Sponsor on GitHub](https://github.com/sponsors/icarogabryel)

## 📝 To Do List

To finish the beta version, the following tasks need to be completed:

- [X] Make the component class for simulation
- [X] Make EBNF for the language
- [X] Make Scanner
- [X] Make Parser
- [X] Make Builder
- [X] Add expressions
- [X] Make testbench class
- [X] Create signal class for waveform dump
- [X] Improve the algorithm of simulation (n² -> n+e)
- [X] Publish initial beta package in PyPI
- [X] Improve declaration to accept assignment
- [X] Make declaration order not necessary
- [X] Make multi-declaration support
- [X] Add Arrays signals support
  - [X] Declaration
  - [X] Assignment
  - [X] Operation
  - [X] Error handling for declaration and assignment
  - [X] .vcd dump support for multi-dimensional bit signals
  - [X] Indexing
  - [X] Slicing
  - [X] Error handling for indexing and slicing
  - [X] Concatenation
  - [X] Reverse arrays support
- [X] Add sub-components support
  - [X] Instantiation
  - [X] Connection
  - [X] Error handling for instantiation and connection
  - [X] .vcd dump scope support for sub-components
- [ ] complete Python API
- [ ] Make automated tests
- [X] Create GitHub Actions for CI/CD
- [ ] Create complete documentation
- [ ] Make oficial Site with GitHub pages

For future releases, the following features are planned:

Version 2:

- [ ] Implement abstract Python components
- [ ] Make FPGA support (Altera and Xilinx)
- [ ] Implement Rust backend for faster FPGA simulation
- [ ] Create import feature
- [ ] Create VS Code extension for language server support
- [ ] Add multi-dimensional array support

Version 3:

- [ ] Create std libs
- [ ] Package manager
- [ ] Add generate statement support
- [ ] Add multi-assignment support
- [ ] Add in-out signals support
- [ ] Add x-bit (0, 1, x, z) support
- [ ] FPGA superset language

---

<div align="center">
  <i>Flote is an open-source project developed as part of academic research at Federal University of Piauí and my humble bedroom, Brazil 🇧🇷</i>
  <br />
  <br />
  <img src="docs/imgs/brazil-mentioned.png" width="25%" alt="Brazil Mentioned"/>
</div>
