import pytest

from flote.elaboration.scanner import END_OF_FILE, LexicalError, Scanner, Token


def tokens_to_tuples(tokens: list[Token]) -> list[tuple[int, str, str]]:
    return [(token.line_number, token.label, token.lexeme) for token in tokens]


def test_track_lines_with_comments_and_newlines():
    code = """// ignored line
        comp Test {
            in bit a;

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
    ("code", "expected"),
    [
        ("", [(1, "EOF", END_OF_FILE)]),
        (" \t\n", [(2, "EOF", END_OF_FILE)]),
        ("// comment without newline", [(1, "EOF", END_OF_FILE)]),
        ("// comment\n", [(2, "EOF", END_OF_FILE)]),
    ],
)
def test_scans_eof_for_empty_or_ignored_input(
    code: str, expected: list[tuple[int, str, str]]
):
    token_stream = Scanner(code).token_stream
    assert tokens_to_tuples(token_stream) == expected


@pytest.mark.parametrize(
    "code",
    [
        "main2",
        "and_gate",
        "bitfield",
        "_private",
        "foo_123",
    ],
)
def test_keywords_embedded_in_identifiers_scan_as_identifiers(code: str):
    token_stream = Scanner(code).token_stream
    tuples = [(label, lexeme) for _, label, lexeme in tokens_to_tuples(token_stream)]
    assert tuples == [("id", code), ("EOF", END_OF_FILE)]


@pytest.mark.parametrize(
    "code",
    [
        "01",
        "007",
    ],
)
def test_rejects_decimal_numbers_with_leading_zero(code: str):
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
def test_rejects_invalid_characters(code: str):
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
def test_rejects_invalid_lexemes(code: str):
    with pytest.raises(LexicalError, match="Invalid lexeme"):
        Scanner(code)
