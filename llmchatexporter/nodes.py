from enum import Enum, auto
from dataclasses import dataclass
from abc import ABC, abstractmethod


class NodeType(Enum):
    """
    Represents kinds of nodes used to model structure and inline formatting of
    exported chat content. Members correspond to structural blocks, inline
    formatting markers, or semantic delimiters used when converting between a
    document model and serialized formats (e.g., Markdown, HTML).
    """

    TEXT = auto()
    START_PARAGRAPH = auto()
    END_PARAGRAPH = auto()
    BREAK = auto()
    START_BOLD = auto()
    END_BOLD = auto()
    START_ITALIC = auto()
    END_ITALIC = auto()
    HEADING = auto()
    HLINE = auto()
    TABLE = auto()
    HREF = auto()
    IMAGE = auto()
    CODE_BLOCK = auto()
    START_UNORDERED_LIST = auto()
    END_UNORDERED_LIST = auto()
    START_ORDERED_LIST = auto()
    END_ORDERED_LIST = auto()
    LIST_ITEM = auto()
    START_QUERY = auto()
    START_ANSWER = auto()


class Attributes(ABC):
    pass


@dataclass
class ImageAttributes(Attributes):
    alt: str
    src: str


@dataclass
class HrefAttributes(Attributes):
    text: str
    link: str


@dataclass
class OrderedListAttributes(Attributes):
    start_index: int = 1


@dataclass
class CodeBlockAttributes(Attributes):
    code: str
    language: str


@dataclass
class TableAttributes(Attributes):
    rows: list[list[str]]


@dataclass
class TextAttributes(Attributes):
    text: str


@dataclass
class HeadingAttributes(Attributes):
    level: int
    text: str
