import pytest

from flote.elaboration.scanner import END_OF_FILE, LexicalError, Scanner, Token


def tokens_to_tuples(tokens: list[Token]) -> list[tuple[int, str, str]]:
    return [(token.line_number, token.label, token.lexeme) for token in tokens]


@pytest.mark.parametrize(
    ("code", "expected_index", "expected_line"),
    [
        ("abc", 0, 1),  # No ignored chars
        ("  abc", 2, 1),  # Spaces
        ("\t\nabc", 2, 2),  # Tab and new line
        ("  \t\nabc", 4, 2),  # Multiple ignored chars
        ("// comment\nabc", 11, 2),  # Comment ending in newline
        ("  // comment\nabc", 13, 2),  # Spaces before comment
        ("// comment", 10, 1),  # Comment until EOF
        ("   ", 3, 1),  # Only spaces
        ("", 0, 1),  # Empty input
    ],
)
def test_skip_ignored(
    scanner: Scanner,
    code: str,
    expected_index: int,
    expected_line: int,
):
    scanner.code = code + END_OF_FILE

    scanner.skip_ignored()

    assert scanner.index == expected_index
    assert scanner.line_number == expected_line


@pytest.mark.parametrize(
    ("code", "expected_index", "expected_line"),
    [
        ("abc", 1, 1),  # Regular character
        ("\nabc", 1, 2),  # Newline
        ("\tabc", 1, 1),  # Tab
    ],
)
def test_advance(
    scanner: Scanner,
    code: str,
    expected_index: int,
    expected_line: int,
):
    scanner.code = code + END_OF_FILE

    scanner.advance()

    assert scanner.index == expected_index
    assert scanner.line_number == expected_line


@pytest.mark.parametrize(
    ("code", "expected_tokens"),
    [
        ("", [("EOF", END_OF_FILE, 1)]),
        ("abc", [("id", "abc", 1), ("EOF", END_OF_FILE, 1)]),
        ("main", [("main", "main", 1), ("EOF", END_OF_FILE, 1)]),
        ("abc\nxyz", [("id", "abc", 1), ("id", "xyz", 2), ("EOF", END_OF_FILE, 2)]),
    ],
)
def test_get_token_stream(
    scanner: Scanner,
    code: str,
    expected_tokens: list[tuple[str, str, int]],
):
    scanner.code = code + END_OF_FILE
    scanner.index = 0
    scanner.line_number = 1

    tokens = scanner.get_token_stream()

    assert [
        (token.label, token.lexeme, token.line_number) for token in tokens
    ] == expected_tokens


@pytest.mark.parametrize(
    ("code", "expected_lexeme", "expected_index"),
    [
        ("abc ", "abc", 3),  # Identifier
        ("123 ", "123", 3),  # Decimal number
        ('"101" ', '"101"', 5),  # Bit field
        ("abc;def", "abc", 3),  # Stops at symbol
        ("abc\ndef", "abc", 3),  # Stops at newline
        ("", "", 0),  # Empty code
    ],
)
def test_scan_lexeme(
    scanner: Scanner,
    code: str,
    expected_lexeme: str,
    expected_index: int,
):
    scanner.code = code + END_OF_FILE

    lexeme = scanner.scan_lexeme()

    assert lexeme == expected_lexeme
    assert scanner.index == expected_index


@pytest.mark.parametrize(
    ("code", "expected_label", "expected_lexeme", "expected_line"),
    [
        ("main", "main", "main", 1),  # Keyword
        ("abc", "id", "abc", 1),  # Identifier
        ("123", "dec", "123", 1),  # Decimal number
        ('"101"', "bit_field", '"101"', 1),  # Bit field
        (";", "semicolon", ";", 1),  # Symbol
        ("// comment\nabc", "id", "abc", 2),  # Comment
        ("", "EOF", END_OF_FILE, 1),  # Empty code
    ],
)
def test_get_token(
    scanner: Scanner,
    code: str,
    expected_label: str,
    expected_lexeme: str,
    expected_line: int,
):
    scanner.code = code + END_OF_FILE

    token = scanner.get_token()

    assert token.label == expected_label
    assert token.lexeme == expected_lexeme
    assert token.line_number == expected_line


class TestScanner:
    """Tests for the complete Scanner behavior."""

    @pytest.mark.parametrize(
        ("code", "expected"),
        [
            ("", [(1, "EOF", END_OF_FILE)]),
            (" \t\n", [(2, "EOF", END_OF_FILE)]),
            ("// comment without newline", [(1, "EOF", END_OF_FILE)]),
            ("// comment\n", [(2, "EOF", END_OF_FILE)]),
        ],
    )
    def test_scans_eof_for_empty_or_ignored_input(
        self, code: str, expected: list[tuple[int, str, str]]
    ):
        token_stream = Scanner(code).token_stream
        assert tokens_to_tuples(token_stream) == expected

    def test_track_lines_with_comments_and_newlines(self):
        code = """// ignored line
            comp Test {
                in bit a;  // ignored comment

                out bit y = a;
            }"""
        token_stream = Scanner(code).token_stream
        assert tokens_to_tuples(token_stream) == [
            (2, "comp", "comp"),
            (2, "id", "Test"),
            (2, "l_brace", "{"),
            (3, "in", "in"),
            (3, "bit", "bit"),
            (3, "id", "a"),
            (3, "semicolon", ";"),
            (5, "out", "out"),
            (5, "bit", "bit"),
            (5, "id", "y"),
            (5, "equals", "="),
            (5, "id", "a"),
            (5, "semicolon", ";"),
            (6, "r_brace", "}"),
            (6, "EOF", END_OF_FILE),
        ]

    @pytest.mark.parametrize(
        "code",
        [
            "main2",
            "and_gate",
            "bit_field",
        ],
    )
    def test_keywords_embedded_in_identifiers_scan_as_identifiers(self, code: str):
        token_stream = Scanner(code).token_stream
        tuples = [
            (label, lexeme) for _, label, lexeme in tokens_to_tuples(token_stream)
        ]
        assert tuples == [("id", code), ("EOF", END_OF_FILE)]

    @pytest.mark.parametrize(
        "code",
        [
            "01",
            "007",
        ],
    )
    def test_rejects_decimal_numbers_with_leading_zero(self, code: str):
        with pytest.raises(LexicalError, match="Decimal number can not begin with 0"):
            Scanner(code)

    @pytest.mark.parametrize(
        "code",
        [
            "@",
            "#",
            "$",
        ],
    )
    def test_rejects_invalid_characters(self, code: str):
        with pytest.raises(LexicalError, match="Invalid character"):
            Scanner(code)

    @pytest.mark.parametrize(
        "code",
        [
            '"102"',
            '""',
            '"abc"',
            "123abc",
        ],
    )
    def test_rejects_invalid_lexemes(self, code: str):
        with pytest.raises(LexicalError, match="Invalid lexeme"):
            Scanner(code)
