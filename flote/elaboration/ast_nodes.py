from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Union


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
    def __init__(self) -> None:
        self.comps: list[Component] = []

    def add_comp(self, comp: "Component"):
        self.comps.append(comp)

    def __repr__(self) -> str:
        return f"Module({self.comps!r})"

    def __str__(self) -> str:
        desc = "|- Module:"

        for comp in self.comps:
            comp_desc = str(comp).replace("\n", "\n|  ")
            desc += f"\n|  |- {comp_desc}"

        return desc


class Component:
    def __init__(self) -> None:
        self.id_: None | Identifier = None
        self.is_main = False
        self.stmts: list[Union[Declaration, Assignment, Instance]] = []
        self.line_number = 0

    def add_stmt(self, stmt):
        self.stmts.append(stmt)

    def __repr__(self) -> str:
        return f"Component({self.id_!r}, {self.is_main}, {self.stmts!r})"

    def __str__(self) -> str:
        desc = "Component:"

        if self.is_main:
            desc += " (main)"

        if self.id_ is not None:
            desc += _format_child("id", self.id_)

        for stmt in self.stmts:
            desc += "\n"
            desc_stmt = str(stmt).replace("\n", "\n|  ")
            desc += f"|  |- {desc_stmt}"

        return desc


class Declaration:
    def __init__(self) -> None:
        self.id_: None | Identifier = None
        self.conn = Connection.INTERNAL
        self.type = "bit"
        self.dimension: Optional[Dimension] = None
        self.assignment_expression: Optional[ExprElem] = None
        self.line_number = 0

    def __repr__(self) -> str:
        return f"Declaration({self.id_!r}, {self.type!r})"

    def __str__(self) -> str:
        conn_str = "internal"
        if self.conn == Connection.INPUT:
            conn_str = "input"
        elif self.conn == Connection.OUTPUT:
            conn_str = "output"

        desc = f"Declaration (type: {self.type}; conn: {conn_str})"

        if self.id_ is not None:
            desc += _format_child("id", self.id_)

        if self.dimension:
            desc += _format_child("dimension", self.dimension)

        if self.assignment_expression:
            desc += _format_child("assign", self.assignment_expression)

        return desc


class BaseIdentifier(ABC):
    def __init__(self) -> None:
        self._line_number: Optional[int] = None

    @property
    def line_number(self) -> Optional[int]:
        return self._line_number

    @line_number.setter
    def line_number(self, value: Optional[int]) -> None:
        self._line_number = value

    @property
    @abstractmethod
    def full_id(self) -> str:
        pass


class Identifier(BaseIdentifier):
    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = value

    def __repr__(self) -> str:
        return f'Identifier: "{self.value}"'

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def full_id(self) -> str:
        return self.value


class Member(BaseIdentifier):
    def __init__(self) -> None:
        self.object: Optional[Identifier] = None
        self.member: Optional[Identifier] = None

    def __repr__(self) -> str:
        return f"Member({self.object!r}, {self.member!r})"

    def __str__(self) -> str:
        desc = "Member:"

        if self.object is not None:
            desc += _format_child("object", self.object)
        if self.member is not None:
            desc += _format_child("member", self.member)

        return desc

    @property
    def full_id(self) -> str:
        obj_id = self.object.full_id if self.object else ""
        mem_id = self.member.full_id if self.member else ""

        return f"{obj_id}.{mem_id}"

    @property
    def line_number(self) -> Optional[int]:
        if self.object and self.object.line_number:
            return self.object.line_number

        return None

    @line_number.setter
    def line_number(self, value: Optional[int]) -> None:
        assert False, "Cannot set line_number on Member directly."


class Dimension:
    def __init__(self, size=1, msb=Msb.ASCENDING) -> None:
        self.size: int = size
        self.msb: Optional[Msb] = msb

    def __repr__(self) -> str:
        msb_name = self.msb.name if self.msb is not None else None
        return f"Dimension(size={self.size}, MSB={msb_name})"

    def __str__(self) -> str:
        msb_name = self.msb.name if self.msb is not None else None
        return f"Dimension: {self.size}, MSB={msb_name}"


ExprElem = Union["Reference", "BitField", "UnaryOp", "BinaryOp", "Concatenation"]


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
    expr: Optional[ExprElem] = None

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def __str__(self) -> str:
        desc = f"{self.__class__.__name__}"
        if self.expr is not None:
            desc += _format_child("expr", self.expr)
        return desc


class BinaryOp(ABC):
    l_expr: Optional[ExprElem] = None
    r_expr: Optional[ExprElem] = None

    def __init__(self, line_number: int) -> None:
        self.line_number = line_number

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
        self, id_, range_begin: None | int = None, range_end: None | int = None
    ) -> None:
        self.id_: BaseIdentifier = id_
        self.range_begin: None | int = range_begin
        self.range_end: None | int = range_end

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
    def __init__(self) -> None:
        self.exprs: list[ExprElem] = []

    def add_expr(self, elem: ExprElem) -> None:
        self.exprs.append(elem)

    def __repr__(self) -> str:
        return f"Concatenation({self.exprs!r})"

    def __str__(self) -> str:
        desc = "Concatenation:"

        for expr in self.exprs:
            expr_desc = str(expr).replace("\n", "\n|  ")
            desc += f"\n|  |- {expr_desc}"

        return desc


class Instance:
    def __init__(self) -> None:
        self.comp_id: Optional[str] = None
        self.sub_alias: Optional[str] = None
        self.line_number: Optional[int] = None

    def __repr__(self) -> str:
        return f"Instance({self.comp_id!r}, {self.sub_alias!r})"

    def __str__(self) -> str:
        return f"Instance: {self.sub_alias} of {self.comp_id}"
