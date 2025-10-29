from abc import ABC, abstractmethod
from dataclasses import dataclass


class Style(ABC):
    """Base interface for message styling.

    Provides read-only style attributes for line prefixing and
    optional pre/post text for both answers and prompts.
    """

    @property
    @abstractmethod
    def line_prefix(self) -> str:
        """Prefix applied to each non-empty line (e.g., quote marker)."""
        ...

    @property
    @abstractmethod
    def pre_answer(self) -> str:
        """Text inserted before the main body of the answer."""
        ...

    @property
    @abstractmethod
    def pre_query(self) -> str:
        """Text inserted before the main body of the prompt."""
        ...


@dataclass(frozen=True)
class SimpleMarkdownStyle(Style):
    """Simple, configurable style implementation."""

    line_prefix: str = "> "
    pre_answer: str = "\n**Answer:**\n"
    pre_query: str = "\n**Prompt:**\n"
