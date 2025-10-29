import argparse
import sys
from pathlib import Path
from converters import GeminiHTMLToMarkdownConverter


def parse_args(argv=None):
    """
    Parse command-line arguments for the LLMChatExporter CLI.
    This function builds and returns an argparse. Namespace configured for the
    LLMChatExporter program. The parser expects two positional Path arguments
    (input and output) and an optional verbose flag.
    Parameters
    ----------
    argv : Optional[Sequence[str]]
        Sequence of argument strings to parse (e.g. ['in.html', 'out.json']).
        If None, the underlying argparse.ArgumentParser will parse sys.argv[1:].
    Returns
    -------
    argparse.Namespace
        Namespace with the following attributes:
          - verbose (bool): True if -v/--verbose was supplied.
          - input (pathlib.Path): Path to the input HTML file.
          - output (pathlib.Path): Path to the output file.
    Raises
    ------
    SystemExit
        Raised by argparse when argument parsing fails or when help/version
        flags are requested.
    Example
    -------
    >>> parse_args(['-v', 'chat.html', 'export.json']).verbose
    True
    >>> parse_args(['chat.html', 'export.json']).input
    PosixPath('chat.html')
    """

    p = argparse.ArgumentParser(
        prog="LLMChatExporter",
        description="Extracting chats of common LLMs that don't support this option.",
    )
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    p.add_argument("input", type=Path, help="Input html file")
    p.add_argument("output", type=Path, help="Output file")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.verbose:
        print("Running in verbose mode")
    converter = GeminiHTMLToMarkdownConverter()
    try:
        result = converter.convert(args.input)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    if args.output:
        converter.write(args.output)
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
