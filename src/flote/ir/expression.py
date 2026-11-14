"""Dataclass representations for expressions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, TypeAlias


@dataclass
class ExpressionDto:
    """Data-only base representation for an expression."""


@dataclass
class RefDto(ExpressionDto):
    """Data-only representation of a bus reference."""

    bus: str
    slice_begin: int | None
    slice_end: int | None


@dataclass
class ConcDto(ExpressionDto):
    """Data-only representation of a concatenation."""

    exprs: list[ExpressionDto]


@dataclass
class ConstDto(ExpressionDto):
    """Data-only representation of a constant."""

    value: str


@dataclass
class UnaryOperationDto(ExpressionDto):
    """Data-only base representation for unary operations."""

    expr: ExpressionDto


@dataclass
class BinaryOperationDto(ExpressionDto):
    """Data-only base representation for binary operations."""

    l_expr: ExpressionDto
    r_expr: ExpressionDto


@dataclass
class NotDto(UnaryOperationDto):
    """Data-only representation of a not operation."""

    operation: ClassVar[str] = "not"


@dataclass
class AndDto(BinaryOperationDto):
    """Data-only representation of an and operation."""

    operation: ClassVar[str] = "and"


@dataclass
class OrDto(BinaryOperationDto):
    """Data-only representation of an or operation."""

    operation: ClassVar[str] = "or"


@dataclass
class XorDto(BinaryOperationDto):
    """Data-only representation of an xor operation."""

    operation: ClassVar[str] = "xor"


@dataclass
class NandDto(BinaryOperationDto):
    """Data-only representation of a nand operation."""

    operation: ClassVar[str] = "nand"


@dataclass
class NorDto(BinaryOperationDto):
    """Data-only representation of a nor operation."""

    operation: ClassVar[str] = "nor"


@dataclass
class XnorDto(BinaryOperationDto):
    """Data-only representation of an xnor operation."""

    operation: ClassVar[str] = "xnor"


OperationDto: TypeAlias = AndDto | OrDto | XorDto | NandDto | NorDto | XnorDto | NotDto
