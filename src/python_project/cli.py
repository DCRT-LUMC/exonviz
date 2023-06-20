"""
Module that contains the command line app, so we can still import __main__
without executing side effects
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Description of command.")
    parser.add_argument("--name", default="world", required=False)
    args = parser.parse_args()
    print(f"Hello, {args.name}")


if __name__ == "__main__":
    main()
