"""
Module that contains the command line app, so we can still import __main__
without executing side effects
"""

import argparse
from exonviz.exon import draw_exon


def main() -> None:
    parser = argparse.ArgumentParser(description="Description of command.")
    args = parser.parse_args()
    plot = draw_exon([21, 22, 23, 21])#, 21, 23])
    print(plot)


if __name__ == "__main__":
    main()
