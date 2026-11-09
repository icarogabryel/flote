import pytest

from flote.elaboration.scanner import END_OF_FILE, LexicalError, Scanner, Token


def tokens_to_tuples(tokens: list[Token]) -> list[tuple[int, str, str]]:
    return [(token.line_number, token.label, token.lexeme) for token in tokens]


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("", [(1, "EOF", END_OF_FILE)]),
        ("   ", [(1, "EOF", END_OF_FILE)]),
        (" \t\n", [(2, "EOF", END_OF_FILE)]),
        ("// comment without newline", [(1, "EOF", END_OF_FILE)]),
        ("// comment\n", [(2, "EOF", END_OF_FILE)]),
    ],
)
def test_scans_eof_for_empty_or_ignored_input(
    code: str, expected: list[tuple[int, str, str]]
) -> None:
    token_stream = Scanner(code).token_stream
    assert tokens_to_tuples(token_stream) == expected


@pytest.mark.parametrize(
    "code",
    [
        "abc",
        "  abc",
        "\t\nabc",
        "  \t\nabc",
        "// comment\nabc",
        "  // comment\nabc",
    ],
)
def test_skips_ignored_chars_before_token(code: str) -> None:
    token_stream = Scanner(code).token_stream
    expected_line = code.count("\n") + 1
    assert tokens_to_tuples(token_stream) == [
        (expected_line, "id", "abc"),
        (expected_line, "EOF", END_OF_FILE),
    ]


@pytest.mark.parametrize(
    "code",
    [
        "abc\ndef",
        "abc def",
        "abc\tdef",
    ],
)
def test_only_newline_increments_line_number(code: str) -> None:
    token_stream = Scanner(code).token_stream
    expected_line = code.count("\n") + 1
    assert [token.line_number for token in token_stream] == [
        1,
        expected_line,
        expected_line,
    ]


@pytest.mark.parametrize(
    "code",
    [
        "",
        "abc",
        "main",
        "abc\nxyz",
        "123",
        '"101"',
        ";",
    ],
)
def test_token_stream_ends_with_single_eof(code: str) -> None:
    token_stream = Scanner(code).token_stream
    labels = [token.label for token in token_stream]
    assert token_stream[-1].label == "EOF"
    assert token_stream[-1].lexeme == END_OF_FILE
    assert labels.count("EOF") == 1


def test_scans_identifiers_on_different_lines() -> None:
    token_stream = Scanner("abc\nxyz").token_stream
    assert tokens_to_tuples(token_stream) == [
        (1, "id", "abc"),
        (2, "id", "xyz"),
        (2, "EOF", END_OF_FILE),
    ]


@pytest.mark.parametrize(
    "code",
    [
        "main",
        "comp",
        "in",
        "out",
        "bit",
    ],
)
def test_scans_keywords(code: str) -> None:
    token_stream = Scanner(code).token_stream
    assert tokens_to_tuples(token_stream) == [
        (1, code, code),
        (1, "EOF", END_OF_FILE),
    ]


@pytest.mark.parametrize(
    "code",
    [
        "abc ",  # Stops at space
        "abc;def",  # Stops at symbol
        "abc\ndef",  # Stops at newline
    ],
)
def test_identifier_ends_at_delimiter(code: str) -> None:
    first_token = Scanner(code).token_stream[0]
    assert (first_token.label, first_token.lexeme) == ("id", "abc")


@pytest.mark.parametrize(
    "code",
    [
        "123",
        "123 ",
    ],
)
def test_scans_decimal_number(code: str) -> None:
    first_token = Scanner(code).token_stream[0]
    assert (first_token.label, first_token.lexeme) == ("dec", "123")


@pytest.mark.parametrize(
    "code",
    [
        '"101"',
        '"101" ',
    ],
)
def test_scans_bit_field(code: str) -> None:
    first_token = Scanner(code).token_stream[0]
    assert (first_token.label, first_token.lexeme) == ("bit_field", '"101"')


def test_scans_symbol() -> None:
    token_stream = Scanner(";").token_stream
    assert tokens_to_tuples(token_stream) == [
        (1, "semicolon", ";"),
        (1, "EOF", END_OF_FILE),
    ]


def test_track_lines_with_comments_and_newlines() -> None:
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
def test_keywords_embedded_in_identifiers_scan_as_identifiers(code: str) -> None:
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
def test_rejects_decimal_numbers_with_leading_zero(code: str) -> None:
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
def test_rejects_invalid_characters(code: str) -> None:
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
def test_rejects_invalid_lexemes(code: str) -> None:
    with pytest.raises(LexicalError, match="Invalid lexeme"):
        Scanner(code)
