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
        self.indent_str = "\t"
        self.list_index_stack = []

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
        self.list_item = "* "
        self.numbered_list_item = lambda index: f"{index}. "

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
            self.__append(self.break_line)

        elif token_type == NodeType.HREF and attributes is not None:
            href = attributes.text
            if not href:
                print("Warning: HREF token with empty href")
                return
            self.__append(f"[{href}]({href})")

        elif token_type == NodeType.IMAGE and attributes is not None:
            alt = attributes.text or "Image"
            self.__append(f"![{alt}]({alt})")

        elif token_type == NodeType.CODE_BLOCK and attributes is not None:
            code = attributes.code
            language = attributes.language or ""
            self.__append(f"\n```{language}\n{code}\n```\n")

        elif token_type == NodeType.START_ORDERED_LIST and attributes is not None:
            self.list_index_stack.append(attributes.start_index)

        elif token_type == NodeType.START_UNORDERED_LIST:
            self.list_index_stack.append(0)

        elif (
            token_type == NodeType.END_ORDERED_LIST
            or token_type == NodeType.END_UNORDERED_LIST
        ):
            self.list_index_stack.pop()

        elif token_type == NodeType.LIST_ITEM:
            if self.list_index_stack:
                if self.list_index_stack[-1] != 0:
                    self.__append(self.numbered_list_item(self.list_index_stack[-1]))
                    self.list_index_stack[-1] += 1
                else:
                    self.__append(self.list_item)
            else:
                print("Warning: LIST_ITEM token outside of a list context")

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
        self.list_index_stack = []

    def __append(self, text: str):
        if not text:
            return

        lines = text.split("\n")
        indent = (
            self.indent_str * (len(self.list_index_stack) - 1)
            if self.list_index_stack
            else ""
        )

        for i, line in enumerate(lines):
            # Skip indenting the first line if we're continuing on the same line
            if i == 0 and self.text and not self.text.endswith("\n"):
                self.text += line
            else:
                # Add indent for new lines (but not for trailing empty line from split)
                if i < len(lines) - 1 or line:
                    self.text += indent + line

            # Add newline except for the last line (unless original text ended with \n)
            if i < len(lines) - 1:
                self.text += "\n"
