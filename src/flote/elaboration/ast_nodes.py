from abc import ABC, abstractmethod
from enum import Enum
from typing import TypeAlias


# TODO refactor function and all __str__ and __repr__ of the nodes
def _format_child(label: str, child: object, outer_prefix: str = "|  ") -> str:
    """Format a child node under a labeled parent with correct indentation."""
    child_str = str(child)
    if "\n" not in child_str:
        return f"\n{outer_prefix}|- {label}: {child_str}"

    first_line, rest = child_str.split("\n", 1)

    rest_lines = rest.splitlines()
    rest_lines_dedent = [
        line[3:] if line.startswith("|  ") else line for line in rest_lines
    ]
    rest_dedent = "\n".join(rest_lines_dedent)

    inner_prefix = outer_prefix + "|  "
    rest_indented = rest_dedent.replace("\n", "\n" + inner_prefix)

    return f"\n{outer_prefix}|- {label}: {first_line}\n{inner_prefix}{rest_indented}"


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
class Module:
    def __init__(self, components: list["Component"]) -> None:
        self.components = components

    def __repr__(self) -> str:
        return f"Module({self.components!r})"

    def __str__(self) -> str:
        desc = "|- Module:"

        for component in self.components:
            component_desc = str(component).replace("\n", "\n|  ")
            desc += f"\n|  |- {component_desc}"

        return desc


class Component:
    def __init__(
        self,
        identifier: "Identifier",
        line_number: int,
        is_main: bool,
        statements: list["Declaration |Assignment | Instance"],
    ):
        self.identifier = identifier
        self.line_number = line_number
        self.is_main = is_main
        self.statements = statements

    def __repr__(self) -> str:
        return f"Component({self.identifier!r}, {self.is_main}, {self.statements!r})"

    def __str__(self) -> str:
        desc = "Component:"

        if self.is_main:
            desc += " (main)"

        for stmt in self.statements:
            desc += "\n"
            desc_stmt = str(stmt).replace("\n", "\n|  ")
            desc += f"|  |- {desc_stmt}"

        return desc


class Declaration:
    def __init__(
        self,
        identifier: "Identifier",
        line_number: int,
        connection: Connection,
        type_: str,
        dimension: "None | Dimension",
        assignment_expression: "None | ExprElem",
    ) -> None:
        self.identifier = identifier
        self.line_number = line_number
        self.connection = connection
        self.type_ = type_
        self.dimension = dimension
        self.assignment_expression = assignment_expression

    def __repr__(self) -> str:
        return f"Declaration({self.identifier!r}, {self.type_!r})"

    def __str__(self) -> str:
        conn_str = "internal"
        if self.connection == Connection.INPUT:
            conn_str = "input"
        elif self.connection == Connection.OUTPUT:
            conn_str = "output"

        desc = f"Declaration (type: {self.type_}; conn: {conn_str})"

        if self.dimension:
            desc += _format_child("dimension", self.dimension)

        if self.assignment_expression:
            desc += _format_child("assign", self.assignment_expression)

        return desc


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
        return f'Identifier: "{self.value}"'

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def full_id(self) -> str:
        return self.value


class MemberAccess(BaseIdentifier):
    def __init__(self, object_: Identifier, member: Identifier) -> None:
        super().__init__(object_.line_number)
        self.object_ = object_
        self.member = member

    def __repr__(self) -> str:
        return f"Member({self.object_!r}, {self.member!r})"

    def __str__(self) -> str:
        desc = (
            "Member:"
            + _format_child("object", self.object_)
            + _format_child("member", self.member)
        )

        return desc

    @property
    def full_id(self) -> str:
        return f"{self.object_.value}.{self.member.value}"


class Dimension:
    def __init__(self, msb: Msb, size: int) -> None:
        self.msb = msb
        self.size = size

    def __repr__(self) -> str:
        return f"Dimension(size={self.size}, MSB={self.msb.name})"

    def __str__(self) -> str:
        return f"Dimension: {self.size}, MSB={self.msb.name}"


ExprElem: TypeAlias = "Reference | BitField | UnaryOp | BinaryOp | Concatenation"


class Assignment:
    def __init__(self, destiny: BaseIdentifier, expr: ExprElem) -> None:
        self.destiny = destiny
        self.expr = expr

    def __repr__(self) -> str:
        return f"Assignment({self.destiny!r}, {self.expr!r})"

    def __str__(self) -> str:
        desc = "Assignment:"
        desc += _format_child("destiny", self.destiny)
        desc += _format_child("expr", self.expr)
        return desc


class UnaryOp(ABC):
    def __init__(self, expr: ExprElem) -> None:
        self.expr = expr

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


# Binary op can't have all attributes in constructor because of the left recursion
class BinaryOp(ABC):
    def __init__(self, line_number: int) -> None:
        self.line_number = line_number  # Used in the Builder
        self.l_expr: None | ExprElem = None
        self.r_expr: None | ExprElem = None

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        desc = f"{self.__class__.__name__}"

        if self.l_expr is not None:
            desc += _format_child("l_expr", self.l_expr)
        if self.r_expr is not None:
            desc += _format_child("r_expr", self.r_expr)

        return desc


class NotOp(UnaryOp):
    def __repr__(self) -> str:
        return f"Not {self.expr!r}"


class AndOp(BinaryOp):
    def __repr__(self) -> str:
        return f"And {self.l_expr!r} {self.r_expr!r}"


class OrOp(BinaryOp):
    def __repr__(self) -> str:
        return f"Or {self.l_expr!r} {self.r_expr!r}"


class XorOp(BinaryOp):
    def __repr__(self) -> str:
        return f"Xor {self.l_expr!r} {self.r_expr!r}"


class NandOp(BinaryOp):
    def __repr__(self) -> str:
        return f"Nand {self.l_expr!r} {self.r_expr!r}"


class NorOp(BinaryOp):
    def __repr__(self) -> str:
        return f"Nor {self.l_expr!r} {self.r_expr!r}"


class XnorOp(BinaryOp):
    def __repr__(self) -> str:
        return f"Xnor {self.l_expr!r} {self.r_expr!r}"


class Reference:
    def __init__(
        self,
        identifier: BaseIdentifier,
    ) -> None:
        self.id_ = identifier
        self.range_begin: None | int = None
        self.range_end: None | int = None

    def __repr__(self) -> str:
        return f"Reference: {self.id_!r}[{self.range_begin}:{self.range_end}]"

    def __str__(self) -> str:
        desc = f"Reference (range: [{self.range_begin}:{self.range_end}])"
        desc += _format_child("id", self.id_)
        return desc


class BitField:
    def __init__(self, value: str) -> None:
        self.value = value.strip('"')
        self.size = len(value)

    def __repr__(self) -> str:
        return f"BitField: {self.value}"

    def __str__(self) -> str:
        return self.__repr__()


class Concatenation:
    def __init__(self, expressions: list[ExprElem]) -> None:
        self.expressions = expressions

    def __repr__(self) -> str:
        return f"Concatenation({self.expressions!r})"

    def __str__(self) -> str:
        desc = "Concatenation:"

        for expr in self.expressions:
            expr_desc = str(expr).replace("\n", "\n|  ")
            desc += f"\n|  |- {expr_desc}"

        return desc


class Instance:
    def __init__(self, identifier: str, line_number: int, alias: None | str) -> None:
        self.identifier = identifier
        self.line_number = line_number
        self.alias = alias

    def __repr__(self) -> str:
        return f"Instance({self.identifier!r}, Alis:{self.alias!r})"

    def __str__(self) -> str:
        return self.__repr__()
