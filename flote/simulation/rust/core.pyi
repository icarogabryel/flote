"""
Type stubs for flote.backend.rust.core module.

This module provides the Rust-based backend for Flote circuit simulation.
"""

from typing import Dict

__version__: str


class Component:
    """
    Wrapper leve para Component Rust.
    Mantém o Component Rust puro internamente e só passa dados básicos.
    """

    def update_and_get(self, new_values: Dict[str, str]) -> Dict[str, str]:
        """
        Atualiza sinais e retorna valores após estabilização em uma única chamada.

        Args:
            new_values: Dicionário com valores a atualizar

        Returns:
            Dicionário com todos os valores após estabilização
        """
        ...

    def update_signals(self, new_values: Dict[str, str]) -> None:
        """
        Atualiza sinais com novos valores e estabiliza.

        Args:
            new_values: Dicionário com valores a atualizar
        """
        ...

    def get_values(self) -> Dict[str, str]:
        """
        Retorna todos os valores como dicionário.

        Returns:
            Dicionário com todos os valores dos buses
        """
        ...

    @property
    def busses(self) -> Dict[str, str]:
        """
        Retorna todos os valores dos buses.
        """
        ...

    @property
    def id_(self) -> str:
        """
        Retorna o ID do componente.
        """
        ...

    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...


class Renderer:
    """
    Renderiza IR JSON em componentes executáveis.
    """

    def __init__(self, ir: str) -> None:
        """
        Cria um Renderer e renderiza o circuito.

        Args:
            ir: JSON string com a representação intermediária

        Raises:
            RuntimeError: Se renderização falhar
        """
        ...

    @property
    def component(self) -> Component:
        """
        Obtém o componente renderizado.

        Raises:
            RuntimeError: Se componente não disponível
        """
        ...

    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
