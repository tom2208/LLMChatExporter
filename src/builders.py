from abc import ABC, abstractmethod
from nodes import NodeType, Attributes


class TokenBuilder(ABC):
    """Abstract builder: construct formatted text from tokens."""

    @abstractmethod
    def push(self, token_type: NodeType, attributes: Attributes = None):
        pass

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def reset(self):
        pass


class MarkdownBuilder(TokenBuilder):
    """MarkdownBuilder constructs Markdown formatted text from tokens."""

    def __init__(self):
        self.text = ""
        self.indent_str = "  "
        self.indent_level = 0
        self.ignored_token_types = [
            NodeType.START_QUERY,
            NodeType.START_ANSWER,
            NodeType.HEADING,
            NodeType.START_PARAGRAPH,
        ]

    def push(self, token_type: NodeType, attributes: Attributes = None):
        if token_type == NodeType.TEXT and attributes is not None:
            self.__append_text(attributes.text)

        elif token_type == NodeType.END_PARAGRAPH:
            self.__append_paragraph()

        elif token_type == NodeType.START_BOLD or token_type == NodeType.END_BOLD:
            self.__append_bold()

        elif token_type == NodeType.START_ITALIC or token_type == NodeType.END_ITALIC:
            self.__append_italic()

        elif token_type == NodeType.BREAK:
            self.__append_break()

        elif token_type == NodeType.HLINE:
            self.__append_hline()

        elif token_type in self.ignored_token_types:
            pass
        else:
            print(
                f"Warning: Unhandled token type {token_type} with attributes {attributes}"
            )

    def build(self):
        return self.text.strip() + "\n"

    def reset(self):
        self.text = ""
        self.indent_level = 0

    def __append_text(self, text: str):
        self.text += text

    def __append_paragraph(self):
        self.text += "\n"

    def __append_break(self):
        self.text += "\n"

    def __append_bold(self):
        self.text += "**"

    def __append_italic(self):
        self.text += "*"

    def __append_hline(self):
        self.text += "\n---\n"

    def __append_heading(self, level, text):
        self.text += f"{'#' * level} {text}\n\n"
