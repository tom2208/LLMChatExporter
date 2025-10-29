from abc import ABC, abstractmethod
from nodes import NodeType, Attributes
from styles import SimpleMarkdownStyle


class TokenBuilder(ABC):
    """
    Abstract base class for building a sequence or stream of tokens from node events.
    Implementations of TokenBuilder accumulate tokens produced by calls to push()
    and then produce a final representation via build(). This class defines the
    contract; concrete subclasses determine the concrete token representation
    (e.g. strings, tuples, Token objects) and any formatting, validation or
    coalescing rules.
    Methods
    - push(token_type: NodeType, attributes: Attributes = None)
        Add a token of the given node type and optional attributes to the current
        build state. Implementations may validate token_type/attributes, transform
        or combine tokens, and may maintain internal scope or context derived from
        the sequence of pushes.
    - build()
        Return a finalized, immutable representation of the tokens accumulated so
        far. The return type is implementation-specific but should represent a
        complete snapshot of the builder's output (for example, a list of tokens,
        a serialized string, or a byte sequence). build() should not modify the
        builder state unless explicitly documented by the subclass.
    - reset()
        Clear any internal state so the builder can begin a new, empty token
        sequence. After reset(), a subsequent build() should represent an empty
        output (unless the subclass documents otherwise).
    Behavioral notes
    - Subclasses are responsible for documenting the exact token types, attribute
      schema, return type of build(), and any validation rules or exceptions.
    - Thread-safety is not guaranteed by this base class; callers should
      synchronize access to a builder instance if it may be used concurrently.
    - Implementations may choose whether build() consumes or preserves the
      accumulated state; callers should consult the concrete subclass API.
    Example (conceptual)
        # subclass defines concrete token representation and semantics
        b = MyTokenBuilder()
        b.push(NodeType.TEXT, TextAttribute(text="hello"))
        b.push(NodeType.BREAK, None)
        b.push(NodeType.TEXT, TextAttribute(text="world"))
        output = b.build()
        b.reset()
    """

    @abstractmethod
    def push(self, token_type: NodeType, attributes: Attributes = None):
        """
        Push a new node (token) onto the builder's internal stack and make it the current node.
        This method creates a new node of the given token_type, attaches the optional
        attributes, updates the builder's internal parent/child relationships and stack,
        and sets the newly created node as the current active node for subsequent
        operations.
        Parameters
        ----------
        token_type : NodeType
            The type of node/token to create and push. This should be one of the
            values defined by the NodeType enum (or equivalent) used by the builder.
        attributes : Attributes, optional
            Optional attributes or metadata to attach to the new node. The exact shape
            of Attributes depends on the builder implementation (commonly a dict-like
            mapping). If None, the node is created with no attributes or with default
            attributes.
        Returns
        -------
        None
            The method modifies the builder state in-place and does not return a value.
        Behavior and side effects
        -------------------------
        - A new node object is instantiated using token_type and attributes.
        - The new node is appended as a child of the current node (if one exists).
        - The new node is pushed onto the internal stack and becomes the current node.
        - If token_type represents a self-closing or terminal token, the node may be
          immediately closed (popped) according to the builder's rules.
        - The builder may normalize or validate attributes before attaching them.
        - The builder updates any position, depth, or context tracking structures.
        Exceptions
        ----------
        TypeError
            If token_type is not a valid NodeType or attributes is not of an expected
            type (if strict typing is enforced).
        ValueError
            If pushing token_type would violate the document structure or builder rules.
        RuntimeError
            If the internal stack is in an inconsistent state and the operation cannot
            be completed.
        Examples
        --------
        # Typical usage (illustrative; actual APIs may differ):
        builder.push(NodeType.ELEMENT, ElementAttribute())
        builder.push(NodeType.BREAK, None)
        builder.push(NodeType.TEXT, TextAttribute(text="Hello World"))
        """

        pass

    @abstractmethod
    def build(self):
        @abstractmethod
        def build(self):
            """
            Build and return an in-memory representation of the accumulated tokens.
            This method must not perform any filesystem writes. Builders that need to
            persist results to disk should expose a separate API for that behavior.
            Returns:
                Any: An in-memory build result (commonly a str, list, dict, or a
                     custom result object). The concrete subclass defines the exact
                     return type and semantics.
            Raises:
                RuntimeError: If the builder cannot produce a result from current state.
            """
            raise NotImplementedError(
                "Subclasses must implement build() without writing files."
            )

        pass

    @abstractmethod
    def reset(self):
        """Reset builder to a clean initial state.

        Clear in-memory buffers, counters, and temporary resources so the instance
        can be reused. Does not save partial work..
        """
        pass


class MarkdownBuilder(TokenBuilder):
    """MarkdownBuilder
    Convert a sequence of token events into a Markdown string.
    Description
    -----------
    MarkdownBuilder accumulates token events (node types plus optional attributes)
    and converts them into a Markdown document. It handles common Markdown
    constructs such as plain text, headings, paragraphs, horizontal rules,
    line breaks, bold/italic, links, images, code blocks, tables, and nested
    ordered/unordered lists. The builder relies on a configurable style object
    (for line prefixes and preambles) and an internal stack to track list
    nesting and numbering.
    Key attributes
    --------------
    text : str
        Accumulated output being built.
    indent_str : str
        String used for one level of list indentation (default: a tab).
    list_index_stack : list[int]
        Stack tracking list nesting; non-zero values represent ordered list
        current indices, zero represents an unordered list.
    style
        Style object (e.g., SimpleMarkdownStyle) that provides line_prefix and
        preamble strings for queries/answers and other formatting hooks.
    Various formatting templates
        Attributes such as paragraph, break_line, hline, italic, bold, heading,
        list_item, and numbered_list_item are used as templates/callables to
        render specific constructs. These can be overridden to alter output.
    Primary methods
    ---------------
    push(token_type, attributes=None)
        Process a single token event and update the internal buffer.
        push prints warnings for malformed attributes or unexpected states
        (for example, a LIST_ITEM outside of a list).
    build()
        Return the final Markdown string. The returned value is the accumulated
        text with surrounding whitespace trimmed and a single trailing newline.
    reset()
        Clear the accumulated text and reset list state for reuse.
    Implementation notes
    --------------------
    - Internal helper __append(text, out_of_text=False) handles line splitting,
      indentation according to list depth, and optional style.line_prefixing.
      It attempts to avoid duplicating prefixes when appending to an existing
      (non-newline-terminated) line.
    - list_index_stack entries:
        0 => unordered list
        n > 0 => ordered list starting at n
      START_ORDERED_LIST pushes a start index; LIST_ITEM increments it after use.
    - The builder prints warnings for invalid table structures, empty hrefs,
      or other malformed token attributes instead of raising exceptions.
    Usage
    -----
    Example (illustrative):
        b = MarkdownBuilder()
        b.push(NodeType.TEXT, Attributes(text="Hello, world!"))
        b.push(NodeType.END_PARAGRAPH)
        b.push(NodeType.HEADING, Attributes(level=2, text="Details"))
        b.push(NodeType.START_UNORDERED_LIST)
        b.push(NodeType.LIST_ITEM); b.push(NodeType.TEXT, Attributes(text="First item"))
        b.push(NodeType.LIST_ITEM); b.push(NodeType.TEXT, Attributes(text="Second item"))
        b.push(NodeType.END_UNORDERED_LIST)
        markdown = b.build()
    Notes
    -----
    - The builder focuses on readable Markdown output rather than exhaustive
      token coverage; it intentionally omits some token types from processing.
    - Customization: alter template attributes or provide a different style
      object to change prefixes and preambles.
    """

    def __init__(self):
        self.text = ""
        self.indent_str = "\t"
        self.list_index_stack = []

        self.ignored_token_types = [
            NodeType.START_QUERY,
            NodeType.START_ANSWER,
            NodeType.START_PARAGRAPH,
        ]

        self.style = SimpleMarkdownStyle()

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

        elif token_type == NodeType.START_ANSWER:
            self.__append(self.style.pre_answer, out_of_text=True)

        elif token_type == NodeType.START_QUERY:
            self.__append(self.style.pre_query, out_of_text=True)

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
            link = attributes.link
            text = attributes.text
            if not link:
                print("Warning: HREF token with empty href")
                return
            self.__append(f"[{text}]({link})")

        elif token_type == NodeType.IMAGE and attributes is not None:
            alt = attributes.alt or "Image"
            src = attributes.src or ""
            self.__append(f"![{alt}]({src})")

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

    def __append(self, text: str, out_of_text=False):
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
                    if not out_of_text:
                        self.text += self.style.line_prefix
                    self.text += indent + line

            # Add newline except for the last line (unless original text ended with \n)
            if i < len(lines) - 1:
                self.text += "\n"
