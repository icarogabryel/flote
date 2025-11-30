"""
Type stubs for flote.backend.rust.core module.

This module provides the Rust-based backend for Flote circuit simulation.
"""

from typing import Optional, Dict

__version__: str
__author__: str


class Component:
    """
    Wrapper for Rust Component implementation.

    Represents a digital circuit component with buses (signals) that can be
    read, written, and stabilized through simulation.
    """

    def __init__(self, id: str) -> None:
        """
        Create a new Component with the given identifier.

        Args:
            id: Unique identifier for the component
        """
        ...

    def create_bus(self, id: str, dimension: int) -> None:
        """
        Create a new bus (signal) in the component.

        Args:
            id: Unique identifier for the bus
            dimension: Bit width of the bus (number of bits)
        """
        ...

    def get_bus_value(self, bus_id: str) -> Optional[str]:
        """
        Get the current value of a bus.

        Args:
            bus_id: Identifier of the bus to read

        Returns:
            Binary string representation of the bus value, or None if bus doesn't exist
        """
        ...

    def set_bus_value(self, bus_id: str, value: str) -> None:
        """
        Set the value of a bus.

        Args:
            bus_id: Identifier of the bus to update
            value: Binary string value to set

        Raises:
            ValueError: If the value is invalid or bus doesn't exist
        """
        ...

    def get_values(self) -> Dict[str, str]:
        """
        Get all bus values as a dictionary.

        Returns:
            Dictionary mapping bus IDs to their binary string values
        """
        ...

    def stabilize(self) -> None:
        """
        Stabilize the component by propagating signal changes through feedback loops
        until all signals reach a stable state.
        """
        ...

    def update_signals(self, new_values: Dict[str, str]) -> None:
        """
        Update multiple signals with new values at once.

        Args:
            new_values: Dictionary mapping bus IDs to binary string values

        Raises:
            RuntimeError: If update fails or causes instability
        """
        ...

    @property
    def busses(self) -> Dict[str, str]:
        """
        Get a dictionary representation of all buses in the component.

        Returns:
            Dictionary mapping bus IDs to their string representations
        """
        ...

    @property
    def id_(self) -> str:
        """
        Get the component's identifier.

        Returns:
            The component ID string
        """
        ...

    def __str__(self) -> str:
        """String representation of the component."""
        ...

    def __repr__(self) -> str:
        """Detailed string representation of the component."""
        ...


class Renderer:
    """
    Wrapper for Rust Renderer implementation.

    Renders Flote IR (Intermediate Representation) JSON into executable
    component structures for simulation.
    """

    def __init__(self, ir: str) -> None:
        """
        Create a new Renderer with the given IR JSON string.

        Args:
            ir: JSON string containing the circuit's intermediate representation

        Raises:
            ValueError: If IR JSON is invalid
        """
        ...

    def render_expr(self, j_expr: str) -> str:
        """
        Render an expression from JSON representation.

        Args:
            j_expr: JSON string representing the expression to render

        Returns:
            Success message string

        Raises:
            ValueError: If JSON is invalid
            RuntimeError: If rendering fails
        """
        ...

    @property
    def component(self) -> Component:
        """
        Get the rendered component.

        Returns:
            The rendered Component object

        Raises:
            RuntimeError: If component is not available
        """
        ...

    def __str__(self) -> str:
        """String representation of the renderer."""
        ...

    def __repr__(self) -> str:
        """Detailed string representation of the renderer."""
        ...
