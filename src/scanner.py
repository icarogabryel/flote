IGNORED_CHARS = [' ', '\t', '\n', '\r']
END_OF_FILE = '\0'
END_OF_COMMENT = ['\n', END_OF_FILE]

class Token():
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f"Token({self.type}, {self.value})"

    def __repr__(self):
        return self.__str__()


class Scanner():
    def __init__(self, code):
        self.code = code + END_OF_FILE
        self.index = 0

    def advance(self):
        self.index += 1

    def get_char(self):
        return self.code[self.index]

    def is_eof(self):
        return True if self.get_char() == END_OF_FILE else False

    def skip_ignored(self):
        while not self.is_eof():  # While don't reach the end of the string
            while self.get_char() in IGNORED_CHARS:  # Skip ignored characters
                self.advance()

            if self.get_char() == '#':  # Skip ignored comments
                while self.get_char() not in END_OF_COMMENT:
                    self.advance()
            else:  # If it's not an ignored character, break the loop
                break

    def get_token(self):
        self.skip_ignored()

        if self.is_eof():
            return Token('EOF', END_OF_FILE)
        
        if self.get_char() in ['+', '-', '*', '/']:
            token = Token('OPERATOR', self.get_char())
            self.advance()
        
        return token