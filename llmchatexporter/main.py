import argparse
import sys
from pathlib import Path
from converters import GeminiHTMLToMarkdownConverter
import strings


def parse_args(argv=None):
    """
    Parse command-line arguments for the LLMChatExporter CLI.
    Parameters
    ----------
    argv : Optional[Sequence[str]]
        Sequence of argument strings to parse (typically sys.argv[1:]).
        If None, argparse will read arguments from sys.argv.
    Returns
    -------
    argparse.Namespace
        Namespace with the following attributes:
        - input (pathlib.Path): Path to the input HTML file to process.
        - output (pathlib.Path): Path to the output file to write.
    Notes
    -----
    The parser expects two positional arguments in this order: input and output.
    Providing incorrect arguments will cause argparse to display usage and exit.
    """

    p = argparse.ArgumentParser(
        prog=strings.APP_NAME,
        description=strings.DESCRIPTION,
    )
    p.add_argument("input", type=Path, help=strings.ARG_INPUT_HELP)
    p.add_argument("output", type=Path, help=strings.ARG_OUTPUT_HELP)
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    converter = GeminiHTMLToMarkdownConverter()

    try:
        result = converter.convert(args.input)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    converter.write(args.output)
    print(strings.CONTENT_CONVERTED_SAVED.format(arg0=args.output))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
