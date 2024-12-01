from scanner import Scanner
from parser import Parser
from visitor import Visitor
from component import Component

def make_comp(code) -> Component:
    scanner = Scanner(code)
    parser = Parser(scanner)
    visitor = Visitor(parser)

    return visitor.get_component()