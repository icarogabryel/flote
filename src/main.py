from scanner import Scanner

def main():
    code = ' + - # comment \n *// # comment'

    scanner = Scanner(code)

    print(scanner.get_token())
    print(scanner.get_token())
    print(scanner.get_token())
    print(scanner.get_token())
    print(scanner.get_token())
    print(scanner.get_token())
    print(scanner.get_token())

if __name__ == '__main__':
    main()
