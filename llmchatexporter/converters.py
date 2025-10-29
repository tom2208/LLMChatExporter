from abc import ABC, abstractmethod
from pathlib import Path
from builders import MarkdownBuilder
from adapters import GeminiHTMLAdapter


class BaseConverter(ABC):

    @abstractmethod
    def convert(self, input_path: Path, output_path: Path) -> None:
        """Convert the input file to the desired format and save it to the output path."""
        pass

    @abstractmethod
    def write(self, output_path: Path) -> None:
        """Write the converted content to the output path."""
        pass


class GeminiHTMLToMarkdownConverter(BaseConverter):
    """
    GeminiHTMLToMarkdownConverter

    A converter that transforms Gemini-generated HTML files into Markdown.

    Behavior
    - Reads an HTML file from disk (UTF-8).
    - Uses an HTMLAdapter to extract structured content from the raw HTML.
    - Uses a MarkdownBuilder to assemble that content into Markdown by calling
        builder.push(type, payload) for each extracted content item and then
        builder.build() to obtain the final Markdown string.
    - Stores the resulting Markdown in the instance attribute `converted_content`.
    - Writes the stored Markdown back to disk (UTF-8) when write() is called.

    Attributes
    - converted_content (str): The Markdown text produced by a successful call to
        convert(). Defaults to an empty string until convert() populates it.

    Methods
    - convert(input_path: Path) -> None
        Reads the file at input_path and performs the HTML-to-Markdown conversion.
        Expected behavior and assumptions:
            - input_path is a pathlib.Path pointing to a readable UTF-8 HTML file.
            - HTMLAdapter.extract_content(html: str) -> Iterable[Tuple[str, Any]]
                (each tuple is typically (content_type, content_payload)).
            - MarkdownBuilder exposes push(content_type, content_payload) and build()
                and returns the final Markdown as a string.
        Side effects:
            - Updates self.converted_content with the Markdown result.
        Exceptions:
            - Propagates FileNotFoundError/IOError for file read errors.
            - Propagates any exceptions raised by the adapter or builder.

    - write(output_path: Path) -> None
        Writes self.converted_content to output_path using UTF-8 encoding.
        Behavior and assumptions:
            - Overwrites existing files.
            - If convert() has not been called, an empty string is written.
        Exceptions:
            - Propagates IOError for file write errors.

    Notes
    - The converter is stateful (stores converted_content) and is not inherently thread-safe.
    - The exact conversion behavior (supported content types, Markdown formatting)
        depends on the implementations of HTMLAdapter and MarkdownBuilder.
    - This class focuses on orchestration (I/O + adapter/builder coordination),
        not on parsing or Markdown formatting details.
    """

    def __init__(self):
        super().__init__()
        self.converted_content = ""

    def convert(self, input_path: Path) -> None:
        """
        Convert an HTML file at the given path into Markdown and store the result on the instance.
        Parameters
        ----------
        input_path : pathlib.Path
            Path to the input HTML file. The file is opened and read using UTF-8 encoding.
        Returns
        -------
        None
            This method does not return a value. The generated Markdown text is stored
            in the instance attribute self.converted_content as a string.
        Behavior
        --------
        - Opens and reads the entire contents of input_path using UTF-8.
        - Uses HTMLAdapter().extract_content(html_content) to extract structured content
          from the HTML. The adapter is expected to yield an iterable of tuples of the
          form (node_type, node_content) or similar.
        - Uses a MarkdownBuilder instance, calling builder.push(node_type, node_content)
          for each extracted content item to incrementally build Markdown.
        - Calls builder.build() and assigns the resulting Markdown string to
          self.converted_content.
        Side effects
        ------------
        - Overwrites or creates the attribute self.converted_content on the instance.
        Exceptions
        ----------
        - FileNotFoundError: if the given input_path does not exist.
        - UnicodeDecodeError: if the file cannot be decoded as UTF-8.
        - Any exceptions raised by HTMLAdapter.extract_content or MarkdownBuilder
          (parsing or conversion errors) will propagate to the caller.
        Notes
        -----
        - The precise expectations for the structure returned by HTMLAdapter and the
          push/build behavior of MarkdownBuilder are implementation-specific; ensure
          those components are available and compatible when calling this method.
        """

        with open(input_path, "r", encoding="utf-8") as file:

            html_content = file.read()
            adapter = GeminiHTMLAdapter()
            content = adapter.extract_content(html_content)
            builder = MarkdownBuilder()

            for c in content:
                builder.push(c[0], c[1])

            self.converted_content = builder.build()

    def write(self, output_path: Path) -> None:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(self.converted_content)
