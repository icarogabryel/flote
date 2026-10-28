import pytest

from flote.elaboration.scanner import Scanner


@pytest.fixture
def scanner() -> Scanner:
    """Create a Scanner instance without running its initialization."""
    scanner = Scanner.__new__(Scanner)
    scanner.code = ""
    scanner.index = 0
    scanner.line_number = 1
    return scanner
