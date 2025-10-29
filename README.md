# Flote

<br>
<div align="center">
  <img src="https://i.postimg.cc/nz5SPMR6/logo.png" width="40%" alt="Flote logo"/>
</div>
<br>
<div align="center">
  <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/icarogabryel/flote?style=flat&logo=github">
  <img alt="GitHub Workflow" src="https://img.shields.io/github/actions/workflow/status/icarogabryel/flote/CI.yml">
  <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/flote?color=green">
  <img src="https://img.shields.io/github/license/icarogabryel/flote" alt="license"/>
</div>

<!-- stars, build workflow, pypi, readthedocs*, reddit*, license -->
<!-- * not created yet -->

## 🛸 Introduction

Flote is a hardware description language and Python framework for hardware simulation. It is designed to be **friendly, simple, light and productive**. More easy to use and learn than Verilog and VHDL. Using Flote, you can create integrated circuits component by using it's HDL and/or Python framework that work by the HLS (High Level Synthesis) concept.

<div align="center">
  <img src="https://i.postimg.cc/xC7p4qpr/print.png" width="90%" alt="Flote in VS Code"/>
</div>

Here is an example of a half adder in Flote:

```flote
comp halfAdder {
  in bit a;
  in bit b;

  out bit sum = a xor b;
  out bit carry = a and b;

}
```

## ⚙️ How it works

Flote's elaborator uses a structure of a compiler's front-end to generate a intermediate representation (IR) of the circuit described in Flote HDL. It has a scanner, parser and a builder. This last one is responsible for build the IR. Then, the IR is passed to the backend (Python or Rust) that is responsible for render the IR into a simulation model, an object that can be manipulated with the Python API and simulates the behavior of the integrated circuit. The model object it's a set of signals busses and uses event driven simulation and dynamic programming to simulate the behavior of the circuit. Also with the use of this Python package you can save the simulation values in a waveform file.

## ✒️ Grammar and Syntax

The language is defined by the [EBNF file findable here](docs/flote.ebnf).

## 🚀 Release

Flote is in beta development. You can see the latest releases in [the GitHub repository](https://github.com/icarogabryel/flote/releases).

## 📝 To Do List

To finish the beta version, the following tasks need to be completed:

- [X] Make the simulation class (Component)
- [X] Make EBNF for the language
- [X] Make Scanner
- [X] Make Parser
- [X] Make Builder
- [X] Make Testbench class to encapsulate the simulation component
- [X] Make accept expressions
- [X] Improve the algorithm of simulation (n² -> n+e)
- [X] Improve declaration to accept assignment
- [X] Create signal class for waveform dump
- [X] Create waveform dump feature
- [X] Improve semantic errors by adding error line
- [X] Improve methods of Testbench
- [X] Publish initial beta package in PyPI
- [ ] Add multi-dimensional bit signals support
  - [X] Declaration
  - [X] Assignment
  - [X] Operation
  - [X] Error handling for declaration and assignment
  - [X] .vcd dump support for multi-dimensional bit signals
  - [X] Indexing
  - [X] Slicing
  - [X] Error handling for indexing and slicing
  - [X] Concatenation
  - [ ] Big endian support
  - [ ] N-Dimensional arrays support with concatenation
- [ ] Add sub-components support
  - [X] Instantiation
  - [X] Connection
  - [X] Error handling for instantiation and connection
  - [ ] .vcd dump scope support for sub-components
- [ ] Implement Rust backend for faster simulation
  - [X] Connect Python with Rust using pyo3 and Maturin
  - [X] Create IR (Intermediate Representation) to communicate frontend with backend
  - [X] Implement the IR render to use the Python backend previously created
  - [ ] Implement the Rust backend
- [ ] Make order not important in signal references
- [ ] Improve README
- [ ] Make automated tests
- [X] Create GitHub Actions for CI/CD
- [ ] Create documentation
- [ ] Create site with GitHub Pages

For future releases, the following features are planned:

- [ ] Create import feature
- [ ] Create std libs
- [ ] Add generate statement support
- [ ] Add multi-assignment support
- [ ] Add in-out signals support
- [ ] Add xbit(0, 1, x, z) support
- [ ] Implement custom types feature
- [ ] Add Python calls support
- [ ] Improve HLS support
- [ ] Add manual time control
