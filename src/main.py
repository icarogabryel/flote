from scanner import Scanner

def main():
    with open('..\\test\\halfAdder.ft', 'r') as f:
        code = f.read()

    print(code)

    scanner = Scanner(code)

    token = scanner.get_token()
    print(token)

    while token.label != 'EOF':
        token = scanner.get_token()
        print(token)


if __name__ == '__main__':
    main()
