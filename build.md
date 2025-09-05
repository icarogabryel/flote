# Building and Editing Flote

## 1. Installing in Editable Mode

If you want to install the package in editable mode, which is useful for development, you can use:

```bash
pip install -e .
```

## 2. Building the Package

In order to build and edit the Flote package, you need to follow these steps:

### 1. Install Dependencies

Install the required dependencies and run the application using the following commands:

```bash
pip install -r requirements.txt
```

### 2. Build the Package

To build the package, you can use the following command:

```bash
python setup.py sdist bdist_wheel
```

### 3. Install the Package

To install the package, use the following command:

```bash
pip install dist/{package_name}.whl
```

### 4. Publish the Package

To publish the package to PyPI, you can use the following command:

```bash
twine upload dist/*
```
