"""Dataclass representations for buses."""

from __future__ import annotations

from dataclasses import dataclass, field

from flote.ir.expression import ExpressionDto


@dataclass
class BitBusDto:
    """Data-only representation of a bit bus."""

    identifier: str
    dimension: int
    msb_descending: bool
    assignment: ExpressionDto | None
    value: list[bool]
    influence_list: list[BitBusDto] = field(default_factory=lambda: list[BitBusDto]())
