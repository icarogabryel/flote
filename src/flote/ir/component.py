"""Dataclass representation for components."""

from __future__ import annotations

from dataclasses import dataclass

from flote.ir.buses import BitBusDto


@dataclass
class ComponentDto:
    """Data-only representation of a component."""

    id_: str
    buses: list[BitBusDto]
