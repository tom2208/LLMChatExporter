from abc import ABC, abstractmethod
from dataclasses import dataclass


class Style(ABC):
    """
    Abstract base class for text formatting styles used by the exporter.

    A Style defines small, reusable pieces of text that are applied around or
    to lines of a prompt/answer when serializing chat content. Implementations
    provide three read-only properties:

    - line_prefix: A short string prefixed to every line of the
        serialized content (typical use: quote markers like "> ").
        This prefix should indicate the content of a prompt/answer.

    - pre_answer: Text inserted immediately before the main body of an answer.
        This can be used to label or separate output.
        It may include trailing whitespace or a newline; callers should treat
        it as literal content to be concatenated.

    - pre_query: Text inserted immediately before the main body of a prompt/query.
        Use this to label or format the user prompt portion (for example "User:\n").

    Contract / expectations for implementers:
    - Each property must return a str.
    - Properties are read-only and should be inexpensive to compute; if the value
        is dynamic, document any side effects or performance characteristics.
    - Avoid including unintended surrounding whitespace unless that is the desired
        formatting.
    - Implementations should be safe for simple concatenation and repeated use.

    Example:
    class ExampleStyle(Style):
        line_prefix: str = "> "
        pre_answer: str = "\n**User:**\n"
        pre_query: str = "\n**LLM:**\n"
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
