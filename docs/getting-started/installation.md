# Installation

## Requirements

Flote requires:

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **Operating System**: Windows, Linux, or macOS

That's it! No heavy IDEs, no license servers, no gigabytes of installation files.

## Installation via pip

The easiest way to install Flote is using pip:

```bash
pip install flote
```

This will install:

- Flote language parser and elaborator
- Python simulation backend
- Rust simulation backend (pre-compiled binaries)
- All necessary dependencies

### Verify Installation

Check that Flote is installed correctly:

```bash
python -c "import flote; print(flote.__version__)"
```

You should see the version number (e.g., `0.5.0`).

## Development Installation

If you want to contribute to Flote or install from source:

### Clone the Repository

```bash
git clone https://github.com/icarogabryel/flote.git
cd flote
```

### Install in Development Mode

```bash
pip install -e .
```

This installs Flote in "editable" mode, so changes to the source code are immediately reflected.

### Building from Source (with Rust Backend)

If you want to build the Rust backend from source:

**Prerequisites:**
- Rust toolchain ([rustup.rs](https://rustup.rs/))
- Maturin build tool

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install Maturin
pip install maturin

# Build and install
maturin develop --release
```

## IDE Setup

Flote works with any text editor, but here are some recommended setups:

### Visual Studio Code (Recommended)

1. Install [VS Code](https://code.visualstudio.com/)

2. Install recommended extensions:
   - **Python** - for testbench editing
   - **WaveTrace** - for VCD waveform visualization

3. Optional: Create a syntax highlighter for `.ft` files
   - Flote syntax is simple enough that generic syntax highlighting works well

### Other Editors

- **Sublime Text**: Works great out of the box
- **Vim/Neovim**: Use Python syntax for testbenches
- **Emacs**: Similar to Vim setup
- **PyCharm**: Excellent Python support for testbenches

## Verification

Let's verify everything works by creating a simple test:

### Create a Test Circuit

Create a file named `test.ft`:

```flote
comp Test {
    in bit a;
    out bit b = not a;
}
```

### Create a Test Bench

Create a file named `test.py`:

```python
import flote as ft

# Elaborate the circuit
circuit = ft.elaborate_file('test.ft')

# Test it
circuit.update({'a': '0'})
circuit.wait(10)
print(f"Input: 0, Output: {circuit.component.busses['b'].value}")

circuit.update({'a': '1'})
circuit.wait(10)
print(f"Input: 1, Output: {circuit.component.busses['b'].value}")
```

### Run the Test

```bash
python test.py
```

Expected output:
```
Input: 0, Output: 1
Input: 1, Output: 0
```

If you see this output, congratulations! Flote is installed and working correctly.

## Troubleshooting

### Python Version Issues

**Problem**: `pip install flote` fails with Python version error

**Solution**: Upgrade Python to 3.8 or higher:
```bash
# On Ubuntu/Debian
sudo apt install python3.8

# On macOS with Homebrew
brew install python@3.8

# On Windows
# Download from python.org
```

### Permission Errors

**Problem**: Permission denied when installing

**Solution**: Use user install:
```bash
pip install --user flote
```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'flote'`

**Solution**: Ensure pip installed to the correct Python:
```bash
python -m pip install flote
```

### Rust Backend Not Available

**Problem**: Warning about Rust backend not found

**Solution**: This is usually not critical - Python backend works fine. If you need Rust backend:

1. Check your platform is supported (Windows, Linux x86_64, macOS)
2. Try reinstalling: `pip install --force-reinstall flote`
3. Build from source (see above)

## Platform-Specific Notes

### Windows

- Use PowerShell or CMD
- Paths use backslashes `\` or forward slashes `/`
- Python is usually `python` not `python3`

### Linux

- Use bash or your preferred shell
- May need `python3` instead of `python`
- May need `pip3` instead of `pip`

### macOS

- Similar to Linux
- Use Terminal app
- May need to add Python to PATH

## Next Steps

Now that Flote is installed, let's build something!

**[→ Quick Start Tutorial](quick-start.md)**

Learn to create your first Flote circuit with a complete walkthrough.

## Getting Help

If you encounter issues:

1. Check [GitHub Issues](https://github.com/icarogabryel/flote/issues)
2. Search existing issues for solutions
3. Create a new issue with:
   - Your operating system
   - Python version (`python --version`)
   - Complete error message
   - Steps to reproduce

---

*Installation should take less than a minute. If it's taking longer, something is wrong!*
