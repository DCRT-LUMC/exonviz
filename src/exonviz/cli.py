"""
Module that contains the command line app, so we can still import __main__
without executing side effects
"""

import argparse
from typing import List
from exonviz.exon import draw_exons, Exon, Region


def fetch_exons(sizes: List[int]) -> List[Exon]:
    """Make or fetch the requested exons"""
    start_frame: int = 0
    exons: List[Exon] = list()

    for i, size in enumerate(sizes):
        E = Exon(start=0, end=size, frame=start_frame, coding=Region(0, size))
        start_frame = E.end_frame
        exons.append(E)

    return exons


def main() -> None:
    example_exons = [21, 22, 23, 23, 23, 21, 22, 21, 22]
    parser = argparse.ArgumentParser(description="Description of command.")
    parser.add_argument("--exon-sizes", type=int, nargs="+", default=example_exons)
    args = parser.parse_args()

    E = Exon(0, 128, 0, coding=Region(50, 100))
    D = Exon(0, 128, 0, coding=Region(50, 101))
    F = Exon(0, 128, 0, coding=Region(50, 102))
    exons = [E, D, F]
    plot = draw_exons(exons)
    print(plot)


if __name__ == "__main__":
    main()
