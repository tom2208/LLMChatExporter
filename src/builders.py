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
            NodeType.START_PARAGRAPH,
        ]

        self.paragraph = "\n"
        self.break_line = "\n"
        self.hline = "\n---\n"
        self.italic = "*"
        self.bold = "**"
        self.heading = lambda level, text: "#" * level + " " + text + "\n\n"

    def push(self, token_type: NodeType, attributes: Attributes = None):

        if token_type == NodeType.TEXT and attributes is not None:
            self.__append(attributes.text)

        elif token_type == NodeType.END_PARAGRAPH:
            self.__append(self.paragraph)

        elif token_type == NodeType.START_BOLD or token_type == NodeType.END_BOLD:
            self.__append(self.bold)

        elif token_type == NodeType.START_ITALIC or token_type == NodeType.END_ITALIC:
            self.__append(self.italic)

        elif token_type == NodeType.BREAK:
            self.__append(self.break_line)

        elif token_type == NodeType.HLINE:
            self.__append(self.hline)

        elif token_type == NodeType.HEADING and attributes is not None:
            self.__append(self.heading(attributes.level, attributes.text))

        elif token_type == NodeType.TABLE and attributes is not None:
            self.__append(self.break_line)
            rows = attributes.rows
            if not rows or not all(isinstance(row, list) for row in rows):
                print("Warning: Invalid table attributes")
                return

            for row in rows:
                if not row or not all(isinstance(cell, str) for cell in row):
                    print("Warning: Invalid table row")
                    return

            column_numbers = len(rows[0])
            if column_numbers == 0:
                print("Warning: Table with no columns")
                return

            self.__append("| " + " | ".join(rows[0]) + " |\n")
            self.__append("| " + " | ".join(["---"] * column_numbers) + " |\n")

            for r in rows[1:]:
                self.__append("| " + " | ".join(r) + " |\n")
            self.__append("\n")

        elif token_type == NodeType.HREF and attributes is not None:
            href = attributes.text
            if not href:
                print("Warning: HREF token with empty href")
                return
            self.__append(f"[{href}]({href})")

        elif token_type == NodeType.IMAGE and attributes is not None:
            alt = attributes.text or "Image"
            self.__append(f"![{alt}]({alt})")

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

    def __append(self, text: str):
        # TODO: handle indentation
        self.text += text
