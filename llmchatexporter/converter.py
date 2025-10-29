from abc import ABC, abstractmethod
from pathlib import Path
from adapters import GeminiHTMLAdapter
from builders import MarkdownBuilder


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

    def __init__(self):
        super().__init__()
        self.converted_content

    def convert(self, input_path: Path, output_path: Path) -> None:
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
