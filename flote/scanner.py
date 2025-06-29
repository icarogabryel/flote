import re


# Constants
IGNORED_CHARS = [' ', '\t', '\n']
END_OF_FILE = '\0'
END_OF_COMMENT = ['\n', END_OF_FILE]
KEY_WORDS = [
    'main',
    'comp',
    'in',
    'out',
    'bit',
    'not',
    'nor',
    'and',
    'nand',
    'xor',
    'or',
]
SYMBOLS_LABELS = {
    ';': 'semicolon',
    '(': 'l_paren',
    ')': 'r_paren',
    '{': 'l_brace',
    '}': 'r_brace',
    '=': 'assign',
    '-': 'minus',
    '[': 'l_bracket',
    ']': 'r_bracket',
}


class LexicalError(Exception):
    def __init__(self, line_number, message):
        self.line_number = line_number
        self.message = message

    def __str__(self):
        return f"Lexical error at line {self.line_number}: {self.message}"


class Token():
    """Token class represents a lexical token with a label and a lexeme."""
    def __init__(self, label, lexeme):
        self.label = label
        self.lexeme = lexeme

    def __str__(self):
        return f'({self.label}, "{self.lexeme}")'

    def __repr__(self):
        return self.__str__()


class Scanner():
    """
    Lexical Scanner for Flote Language.

    The Scanner class receives a string of code, make lexical analysis and
    returns a token stream.
    """
    def __init__(self, code: str):
        self.code = code + END_OF_FILE
        self.line_number = 1
        self.index = 0  # Current index in the code string

    def advance(self):
        """
        Advance the index to the next character and update line number if
        necessary.
        """
        if self.get_char() == '\n':
            self.line_number += 1

        self.index += 1

    def get_char(self) -> str:
        """Return the current character pointed by self.index."""
        return self.code[self.index]

    def is_eof(self) -> bool:
        return True if self.get_char() == END_OF_FILE else False

    def skip_ignored(self):
        """
        Skip ignored characters and comments until a non-ignored character
        or END_OF_FILEis found.
        """
        while not self.is_eof():  # While don't reach the end of the string
            while self.get_char() in IGNORED_CHARS:  # Skip ignored characters
                self.advance()

            if self.get_char() == '/':  # Skip line comments
                # Checking the slashes separately to avoid checking out of
                # range and IndexError.
                if self.code[self.index + 1] == '/':
                    # Ignoring the comment until the end of the line
                    while self.get_char() not in END_OF_COMMENT:
                        self.advance()
            else:  # If it's not an ignored character, break the loop
                break

    def scan_lexeme(self) -> str:
        """
        Form a lexeme by reading characters until a symbol or an ignored
        character is found.
        """
        lexeme = ''

        while not self.is_eof():  # While don't reach the end of the code
            # If it's a symbol, stop reading and return the lexeme.
            if (char := self.get_char()) in SYMBOLS_LABELS:
                return lexeme

            # If it's an ignored character, stop reading and return the lexeme.
            elif char in IGNORED_CHARS:
                return lexeme

            # If it's not an ignored character or a symbol, keep reading.
            else:
                lexeme += char
                self.advance()

        return lexeme

    def get_token(self) -> Token:
        """Get the next token from the code."""
        self.skip_ignored()

        token = None

        if self.is_eof():  # First, check if we reached the end of the code.
            token = Token('EOF', END_OF_FILE)

        # Check if the current character is a symbol.
        elif (char := self.get_char()) in SYMBOLS_LABELS:
            token = Token(SYMBOLS_LABELS[char], char)
            self.advance()

        # Check if the character can be the start of a word.
        elif re.match(r'[a-zA-Z_\d\"]', char):
            lexeme = self.scan_lexeme()

            if lexeme in KEY_WORDS:
                # The label is the lexeme itself in case of keywords
                token = Token(lexeme, lexeme)
            # Check if the lexeme is a valid identifier
            elif re.match(r'^[a-zA-Z]\w*$', lexeme):
                token = Token('id', lexeme)
            # Check if the lexeme is a valid binary number
            elif re.match(r'^\"[0-1]+\"$', lexeme):
                token = Token('bit_field', lexeme)
            # Check if the lexeme is decimal number
            elif re.match(r'^[0-9]+$', lexeme):
                # Check if the lexeme is a valid decimal number
                if re.match(r'^[1-9][0-9]*$', lexeme) or lexeme == '0':
                    token = Token('dec', lexeme)
                # If the lexeme is not a valid decimal number, raise an error.
                else:
                    raise LexicalError(
                        self.line_number,
                        f'Decimal number can not begin with 0: {lexeme}'
                    )
            else:  # If the lexeme was not recognized, raise an error.
                raise LexicalError(
                    self.line_number,
                    f'Invalid lexeme: {lexeme}'
                )
        else:
            raise LexicalError(self.line_number, f"Invalid character: {char}")

        # . Here I am another day. Under the bloodthirsty eye of the debugger.
        assert token is not None, 'token returned None'

        return token

    def get_token_stream(self):
        """Generator that yields tokens until EOF is reached."""
        while True:
            token = self.get_token()

            yield token

            if token.label == 'EOF':
                break
