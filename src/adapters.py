from abc import ABC, abstractmethod
from bs4 import BeautifulSoup, NavigableString, Tag
from main import node_to_md
from nodes import NodeType, Attributes
import nodes
from typing import Optional, List


class ContentAdapter(ABC):
    """Abstract adapter: normalize node operations for different sources."""

    @abstractmethod
    def extract_content(self, raw_data):
        pass


class HTMLAdapter(ContentAdapter):
    """
    HTMLAdapter is a subclass of ContentAdapter designed to extract structured content from raw HTML data.
    It uses BeautifulSoup with the 'lxml' parser to locate and process specific HTML elements representing queries and answers.
    The main method, extract_content, parses the HTML and returns a list of tuples, each containing a node type and optional attributes,
    to represent the start of queries and answers in the content.
    Methods:
        extract_content(raw_data: str) -> List[tuple[NodeType, Optional[Attributes]]]:
            Parses the input HTML string and extracts query and answer nodes.
            Ensures the number of queries and answers are consistent.
            Returns a list of tuples indicating the start of each query and answer.
    """

    def __init__(self):
        self.bold_start = [(NodeType.START_BOLD, None)]
        self.bold_end = [(NodeType.END_BOLD, None)]
        self.italic_start = [(NodeType.START_ITALIC, None)]
        self.italic_end = [(NodeType.END_ITALIC, None)]
        self.start_paragraph = [(NodeType.START_PARAGRAPH, None)]
        self.end_paragraph = [(NodeType.END_PARAGRAPH, None)]
        self.hline = [(NodeType.HLINE, None)]
        self.text = lambda text: [(NodeType.TEXT, nodes.TextAttributes(text=text))]
        self.img = lambda alt, src: [
            (NodeType.IMAGE, nodes.ImageAttributes(alt=alt, src=src))
        ]
        self.href = lambda text, link: [
            (NodeType.HREF, nodes.HrefAttributes(text=text, link=link))
        ]

        self.heading = lambda level, text: [
            (NodeType.HEADING, nodes.HeadingAttributes(level=level, text=text))
        ]

        self.div_class_blacklist = ["table-footer"]

        super().__init__()

    def __extract_code_language(self, child, parent_node):
        """Return language text or None."""
        if child.name != "span":
            return None
        classes = parent_node.get("class")
        if not classes:
            return None
        if any(c.startswith("ng-tns") for c in child.get("class")):
            return child.get_text(strip=True)
        return None

    def __extract_code_text(self, code_node):
        """Return concatenated code text from a <code> node."""
        parts = []
        for c in code_node.children:
            # explicit span handling
            if getattr(c, "name", None) == "span":
                for span_child in c.descendants:
                    if isinstance(span_child, NavigableString):
                        parts.append(str(span_child))
            elif isinstance(c, NavigableString):
                parts.append(str(c))
            # ignore other node types
        return "".join(parts)

    def extract_content(
        self, raw_data: str
    ) -> List[tuple[NodeType, Optional[Attributes]]]:
        """
        Extracts content from the given raw HTML data.
        Parses the input string using BeautifulSoup with the 'lxml' parser and returns a
        tuple containing the node type and optional attributes.
        Args:
            raw_data (str): The raw HTML data as a string.
        Returns:
            tuple[NodeType, Optional[Attributes]]: A tuple where the first element is the
            node type and the second element is an Optional Attributes Object.
        """
        result = []
        soup = BeautifulSoup(raw_data, "lxml")

        answers = soup.select(
            "div.markdown.markdown-main-panel.enable-updated-hr-color"
        )

        queries = soup.select("div.query-text.gds-body-l")

        assert (
            len(answers) == len(queries) or len(answers) == len(queries) - 1
        ), "Number of answers and queries do not match"

        for i in range(0, len(queries)):
            result.append((NodeType.START_QUERY, None))
            result.extend(self.__process_tags(queries[i]))
            if i >= len(answers):
                break
            result.append((NodeType.START_ANSWER, None))
            result.extend(self.__process_tags(answers[i]))

        return result

    def __process_tags(self, node: Tag) -> List[tuple[NodeType, Optional[Attributes]]]:
        result: List[tuple[NodeType, Optional[Attributes]]] = []
        """
        Recursively processes HTML tags and generates corresponding node types and attributes.
        Args:
            node (Tag): The HTML tag to process.
            Returns:
                List[tuple[NodeType, Optional[Attributes]]]: A list of tuples where each tuple contains
                a node type and optional attributes.        
        """
        if isinstance(node, NavigableString):
            if node:
                if not str(node).isspace():
                    result.extend(self.text(str(node)))
            else:
                print("Warning: empty text node")

        elif isinstance(node, Tag):
            if node.name == "br":
                result.append(self.__generate_break())

            elif node.name in ["b", "strong"]:
                result.extend(self.bold_start)
                for child in node.contents:
                    result.extend(self.__process_tags(child))
                result.extend(self.bold_end)

            elif node.name in ["i", "em"]:
                result.extend(self.italic_start)
                for child in node.contents:
                    result.extend(self.__process_tags(child))
                result.extend(self.italic_start)

            elif node.name == "div":
                if "class" in node.attrs:
                    classes = node.attrs["class"]
                    if any(c in self.div_class_blacklist for c in classes):
                        return result
                for child in node.contents:
                    result.extend(self.__process_tags(child))

            elif node.name in ["p"]:
                if not node.contents:
                    return result
                result.extend(self.start_paragraph)
                for child in node.contents:
                    result.extend(self.__process_tags(child))
                result.extend(self.end_paragraph)

            elif node.name in ["hr"]:
                result.extend(self.hline)

            elif node.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(node.name[1])
                result.extend(self.heading(level, node.get_text()))

            elif node.name in ["img"]:
                alt = node.get("alt")
                if not alt:
                    alt = "Image"
                src = node.get("src")
                if src:
                    result.extend(self.img(alt, src))
                else:
                    print("Warning: image tag with no src")

            elif node.name in ["a"]:
                href = node.get("href", "")
                if href:
                    result.extend(self.href(node.get_text(), href))
                else:
                    print("Warning: anchor tag with no href")
                    for child in node.contents:
                        result.extend(self.__process_tags(child))

            elif node.name in ["table-block"]:
                for child in node.contents:
                    result.extend(self.__process_tags(child))

            elif node.name in ["table"]:
                table_rows = []

                for child in node.contents:

                    rows = child.find_all("tr")
                    if not rows:
                        print("Warning: table with no rows")
                        return result

                    column_numbers = len(rows[0].find_all("td"))

                    if column_numbers == 0:
                        print("Warning: table with no columns")
                        return result

                    for r in rows:
                        cols = r.find_all(["td"])
                        if len(cols) != column_numbers:
                            print("Warning: inconsistent number of columns in table")
                            return result
                        texts = [c.get_text() for c in cols]
                        table_rows.append(texts)

                result.append((NodeType.TABLE, nodes.TableAttributes(rows=table_rows)))

            elif node.name in ["code-block"]:
                code_lang = None
                code = ""

                for child in node.descendants:
                    # try language first (non-destructive)
                    lang = self.__extract_code_language(child, node)
                    if lang:
                        code_lang = lang
                        continue

                    # then code content
                    if child.name == "code":
                        code = self.__extract_code_text(child)
                        break  # we just expect one code block

                result.append(
                    (
                        NodeType.CODE_BLOCK,
                        nodes.CodeBlockAttributes(code=code, language=code_lang),
                    )
                )

            elif node.name in ["ol"]:
                if node.has_attr("start"):
                    try:
                        start_index = int(node["start"])
                    except ValueError:
                        start_index = 1
                result.append(
                    (
                        NodeType.START_ORDERED_LIST,
                        nodes.OrderedListAttributes(start_index=start_index),
                    )
                )
                for child in node.contents:
                    result.extend(self.__process_tags(child))
                result.append((NodeType.END_ORDERED_LIST, None))

            elif node.name in ["ul"]:
                result.append((NodeType.START_UNORDERED_LIST, None))
                for child in node.contents:
                    result.extend(self.__process_tags(child))
                result.append((NodeType.END_UNORDERED_LIST, None))

            elif node.name in ["li"]:
                result.append((NodeType.LIST_ITEM, None))
                for child in node.contents:
                    result.extend(self.__process_tags(child))

            elif node.name in ["youtube-block"]:
                for child in node.contents:
                    result.extend(self.__process_tags(child))
                result.append((NodeType.BREAK, None))

            else:
                for child in node.contents:
                    result.extend(self.__process_tags(child))
        else:
            print(f"Warning: unhandled node type {type(node)}")

        return result

    def __generate_break(self) -> tuple[NodeType, Optional[Attributes]]:
        return (NodeType.BREAK, None)


from builders import MarkdownBuilder

with open("./tar/Google Gemini.html", "r", encoding="utf-8") as f:
    html = f.read()
    adapter = HTMLAdapter()
    content = adapter.extract_content(html)
    builder = MarkdownBuilder()
    for c in content:
        builder.push(c[0], c[1])

    with open("./tar/chat.md", "w", encoding="utf-8") as f:
        f.write(builder.build())
