"""
Module that contains the command line app, so we can still import __main__
without executing side effects
"""

import argparse
from typing import List
from .draw import draw_exons
from .exon import Exon, Region
from .mutalyzer import mutalyzer, extract_exons


def fetch_exons(transcript: str) -> List[Exon]:
    """Make or fetch the requested exons"""

    payload = mutalyzer(transcript)
    if payload:
        return extract_exons(payload)
    else:
        return list()


def main() -> None:
    example_exons = [21, 22, 23, 23, 23, 21, 22, 21, 22]
    parser = argparse.ArgumentParser(description="Description of command.")
    parser.add_argument("transcript", help="Transcript (with version) to visualise")
    args = parser.parse_args()

    exons = fetch_exons(args.transcript)
    plot = draw_exons(exons)
    print(plot)


if __name__ == "__main__":
    main()
