"""
Module that contains the command line app, so we can still import __main__
without executing side effects
"""

import argparse
from exonviz.exon import draw_exon


def main() -> None:
    example_exons = [21, 22, 23, 23, 23, 21, 22, 21, 22]
    parser = argparse.ArgumentParser(description="Description of command.")
    parser.add_argument('--exon-sizes', type=int, nargs='+', default=example_exons)
    args = parser.parse_args()
    plot = draw_exon(args.exon_sizes)
    print(plot)


if __name__ == "__main__":
    main()
