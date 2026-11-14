"""Dataclass representations for expressions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeAlias

if TYPE_CHECKING:
    from flote.ir.buses import BitBusDto


@dataclass
class ExpressionDto:
    """Data-only base representation for an expression."""


@dataclass
class RefDto(ExpressionDto):
    """Data-only representation of a bus reference."""

    bus: BitBusDto
    slice_begin: int | None
    slice_end: int | None


@dataclass
class ConcDto(ExpressionDto):
    """Data-only representation of a concatenation."""

    exprs: list[ExpressionDto]


@dataclass
class ConstDto(ExpressionDto):
    """Data-only representation of a constant."""

    value: Any


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


@dataclass
class AndDto(BinaryOperationDto):
    """Data-only representation of an and operation."""


@dataclass
class OrDto(BinaryOperationDto):
    """Data-only representation of an or operation."""


@dataclass
class XorDto(BinaryOperationDto):
    """Data-only representation of an xor operation."""


@dataclass
class NandDto(BinaryOperationDto):
    """Data-only representation of a nand operation."""


@dataclass
class NorDto(BinaryOperationDto):
    """Data-only representation of a nor operation."""


@dataclass
class XnorDto(BinaryOperationDto):
    """Data-only representation of an xnor operation."""


OperationDto: TypeAlias = AndDto | OrDto | XorDto | NandDto | NorDto | XnorDto | NotDto
