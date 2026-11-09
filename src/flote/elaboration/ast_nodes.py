from abc import ABC, abstractmethod
from collections.abc import Iterable
from enum import Enum
from typing import TypeAlias


def _tree(title: str, children: Iterable[tuple[str, object | None]] = ()) -> str:
    """Render `title` followed by its children as an indented tree.

    Every child goes on its own line as "|- label: <str(child)>" and the rest of the
    child's lines are shifted one level ("|  "). Children that are None are skipped. A
    leaf node simply doesn't call this and returns its title line.
    """
    string = title
    for label, child in children:
        if child is not None:
            body = str(child).replace("\n", "\n|  ")
            string += f"\n|  |- {label}: {body}"
    return string


class Connection(Enum):
    """Enum to represent the connection type of a declaration."""

    INPUT = -1
    INTERNAL = 0
    OUTPUT = 1


class Msb(Enum):
    """Enum to represent the most significant bit (MSB) direction."""

    ASCENDING = True
    DESCENDING = False


# * AST Nodes
# Conventions:
#   __repr__ -> ClassName(attr=value, ...), same order as __init__, no line_number.
#   __str__  -> "ClassName (info: value; ...)" for attributes that are plain data, plus
#               one child line per attribute that holds another AST node.
class Module:
    def __init__(self, components: list["Component"]) -> None:
        self.components = components

    def __repr__(self) -> str:
        return f"Module(components={self.components!r})"

    def __str__(self) -> str:
        # Only the root carries the "|- " marker; _tree adds it to all the others.
        children = [("component", c) for c in self.components]
        return "|- " + _tree("Module", children)


class Component:
    def __init__(
        self,
        identifier: "Identifier",
        line_number: int,
        is_main: bool,
        statements: list["Declaration |Assignment | Instance"],
    ) -> None:
        self.identifier = identifier
        self.line_number = line_number
        self.is_main = is_main
        self.statements = statements

    def __repr__(self) -> str:
        return (
            f"Component(identifier={self.identifier!r}, is_main={self.is_main}, "
            f"statements={self.statements!r})"
        )

    def __str__(self) -> str:
        children: list[tuple[str, object]] = [("id", self.identifier)]
        children += [("stmt", s) for s in self.statements]
        return _tree(f"Component (is_main: {self.is_main})", children)


class Declaration:
    def __init__(
        self,
        identifier: "Identifier",
        line_number: int,
        connection: Connection,
        type_: str,
        dimension: "None | Dimension",
        assignment_expression: "None | ExpressionElement",
    ) -> None:
        self.identifier = identifier
        self.line_number = line_number
        self.connection = connection
        self.type_ = type_
        self.dimension = dimension
        self.assignment_expression = assignment_expression

    def __repr__(self) -> str:
        return (
            f"Declaration(identifier={self.identifier!r}, "
            f"connection={self.connection.name}, type_={self.type_}, "
            f"dimension={self.dimension!r}, "
            f"assignment_expression={self.assignment_expression!r})"
        )

    def __str__(self) -> str:
        conn = self.connection.name
        return _tree(
            f"Declaration (type: {self.type_}; conn: {conn})",
            [
                ("id", self.identifier),
                ("dimension", self.dimension),
                ("assign", self.assignment_expression),
            ],
        )


class BaseIdentifier(ABC):
    def __init__(self, line_number: int) -> None:
        self.line_number = line_number

    @property
    @abstractmethod
    def full_id(self) -> str:
        pass


class Identifier(BaseIdentifier):
    def __init__(self, value: str, line_number: int) -> None:
        super().__init__(line_number)
        self.value = value

    def __repr__(self) -> str:
        return f"Identifier(value={self.value})"

    def __str__(self) -> str:
        return f"Identifier (value: {self.value})"

    @property
    def full_id(self) -> str:
        return self.value


class MemberAccess(BaseIdentifier):
    def __init__(self, object_: Identifier, member: Identifier) -> None:
        super().__init__(object_.line_number)
        self.object_ = object_
        self.member = member

    def __repr__(self) -> str:
        return f"MemberAccess(object_={self.object_!r}, member={self.member!r})"

    def __str__(self) -> str:
        children = [("object", self.object_), ("member", self.member)]
        return _tree("MemberAccess", children)

    @property
    def full_id(self) -> str:
        return f"{self.object_.value}.{self.member.value}"


class Dimension:
    def __init__(self, msb: Msb, size: int) -> None:
        self.msb = msb
        self.size = size

    def __repr__(self) -> str:
        return f"Dimension(msb={self.msb.name}, size={self.size})"

    def __str__(self) -> str:
        return f"Dimension (size: {self.size}; msb: {self.msb.name})"


ExpressionElement: TypeAlias = (
    "Reference | BitField | UnaryOp | BinaryOp | Concatenation"
)


class Assignment:
    def __init__(self, destiny: BaseIdentifier, expression: ExpressionElement) -> None:
        self.destiny = destiny
        self.expression = expression

    def __repr__(self) -> str:
        return f"Assignment(destiny={self.destiny!r}, expr={self.expression!r})"

    def __str__(self) -> str:
        return _tree(
            "Assignment", [("destiny", self.destiny), ("expr", self.expression)]
        )


# The subclasses (NotOp, AndOp, ...) only need to exist; repr/str use the class name.
class UnaryOp(ABC):
    def __init__(self, expression: ExpressionElement) -> None:
        self.expression = expression

    def __repr__(self) -> str:
        return f"{type(self).__name__}(expr={self.expression!r})"

    def __str__(self) -> str:
        return _tree(type(self).__name__, [("expr", self.expression)])


# Binary op can't have all attributes in constructor because of the left recursion
class BinaryOp(ABC):
    def __init__(self, line_number: int) -> None:
        self.line_number = line_number  # Used in the Builder
        self.l_expr: None | ExpressionElement = None
        self.r_expr: None | ExpressionElement = None

    def __repr__(self) -> str:
        return f"{type(self).__name__}(l_expr={self.l_expr!r}, r_expr={self.r_expr!r})"

    def __str__(self) -> str:
        return _tree(
            type(self).__name__,
            [("l_expr", self.l_expr), ("r_expr", self.r_expr)],
        )


class NotOp(UnaryOp):
    pass


class AndOp(BinaryOp):
    pass


class OrOp(BinaryOp):
    pass


class XorOp(BinaryOp):
    pass


class NandOp(BinaryOp):
    pass


class NorOp(BinaryOp):
    pass


class XnorOp(BinaryOp):
    pass


class Reference:
    def __init__(
        self, identifier: BaseIdentifier, range_begin: None | int, range_end: None | int
    ) -> None:
        self.identifier = identifier
        self.range_begin = range_begin
        self.range_end = range_end

    def __repr__(self) -> str:
        return (
            f"Reference(identifier={self.identifier!r}, range_begin={self.range_begin},"
            f" range_end={self.range_end})"
        )

    def __str__(self) -> str:
        return _tree(
            f"Reference (range: [{self.range_begin}:{self.range_end}])",
            [("identifier", self.identifier)],
        )


class BitField:
    def __init__(self, value: str) -> None:
        self.value = value.strip('"')
        self.size = len(value)

    def __repr__(self) -> str:
        return f"BitField(value={self.value})"

    def __str__(self) -> str:
        return f"BitField (value: {self.value})"


class Concatenation:
    def __init__(self, expressions: list[ExpressionElement]) -> None:
        self.expressions = expressions

    def __repr__(self) -> str:
        return f"Concatenation(expressions={self.expressions!r})"

    def __str__(self) -> str:
        return _tree("Concatenation", [("expr", e) for e in self.expressions])


class Instance:
    def __init__(self, identifier: str, line_number: int, alias: None | str) -> None:
        self.identifier = identifier
        self.line_number = line_number
        self.alias = alias

    def __repr__(self) -> str:
        return f"Instance(identifier={self.identifier}, alias={self.alias})"

    def __str__(self) -> str:
        return f"Instance (identifier: {self.identifier}; alias: {self.alias})"
