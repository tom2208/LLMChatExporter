import argparse
import sys
from pathlib import Path
from converters import GeminiHTMLToMarkdownConverter


def parse_args(argv=None):
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
