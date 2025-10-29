import argparse
import sys
from pathlib import Path


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="LLMChatExporter",
        description="Extracting chats of common LLMs that don't support this option."
    )
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    p.add_argument("-o", "--output", type=Path, help="Output file (optional)")
    p.add_argument("input", type=Path, help="Input html file")
    return p.parse_args(argv)

def main(argv=None):
    args = parse_args(argv)
    if args.verbose:
        print("Running in verbose mode")
    try:
        # TODO
        pass
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    if args.output:
        args.output.write_text(result)
    else:
        print(result)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
