"""
Module that contains the command line app, so we can still import __main__
without executing side effects
"""

import argparse
import re
import sys
import math

from typing import List, Tuple
from .draw import draw_exons
from .exon import Exon
from .mutalyzer import mutalyzer, extract_exons


def check_input(transcript: str) -> str:
    """Check the input from the user, and rewrite when needed"""
    # If it looks like there is no variant
    if re.match(r"^\w+\.\d+$", transcript):
        return f"{transcript}:c.="

    # If it looks like the user forgot the version number, there isn't much we can do
    if re.match(r"^\w+$", transcript):
        msg = "Please specify the version of the transcript you are interested in: "
        raise RuntimeError(msg + transcript)

    return transcript


def fetch_exons(transcript: str) -> Tuple[List[Exon], bool]:
    """Make or fetch the requested exons"""

    payload = mutalyzer(transcript)
    if payload:
        return extract_exons(payload)
    else:
        return list(), False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Description of command.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("transcript", help="Transcript (with version) to visualise")
    parser.add_argument(
        "--max-width", type=int, help="Maximum width of the figure", default=math.inf
    )
    parser.add_argument("--height", type=int, help="Exon height", default=None)
    parser.add_argument(
        "--non-coding",
        action="store_true",
        default=False,
        help="Show non coding regions",
    )
    parser.add_argument("--gap", type=int, help="Gap between the exons", default=None)
    args = parser.parse_args()

    # Does the transcript format make sense?
    try:
        transcript = check_input(args.transcript)
    except RuntimeError as e:
        print(e)
        exit(1)

    # Try to talk to mutalyzer
    try:
        exons, reverse = fetch_exons(transcript)
    except RuntimeError as e:
        print(e)
        exit(2)

    for exon in exons:
        print(exon, file=sys.stderr)
    plot = draw_exons(
        exons,
        reverse,
        max_width=args.max_width,
        height=args.height,
        non_coding=args.non_coding,
        gap_size=args.gap,
    )
    print(plot)


if __name__ == "__main__":
    main()
