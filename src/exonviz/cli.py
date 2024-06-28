"""
Module that contains the command line app, so we can still import __main__
without executing side effects
"""

import argparse
import sys
import gzip
import pkg_resources
from collections import defaultdict
import re

from typing import List, Dict, Any
from .draw import draw_exons
from .exon import Exon, Variant, exons_from_tsv
from .mutalyzer import fetch_exons, fetch_variants, build_exons
from mutalyzer_hgvs_parser import parse, to_model

from .draw import _config


def get_MANE() -> Dict[str, str]:
    fname = pkg_resources.resource_filename(__name__, "data/mane.txt.gz")
    with gzip.open(fname, "rt") as fin:
        mane = dict()
        for line in fin:
            gene, transcript = line.strip("\n").split("\t")
            mane[gene] = transcript
    return mane


def check_input(transcript: str) -> str:
    """Rewrite the transcript if it is not a valid HGVS description"""
    # Is transcript already valid HGVS
    try:
        parse(transcript)
        return transcript
    except Exception:
        pass

    # Maybe we got a bare transcript, we should make it a variant description
    var_transcript = f"{transcript}:c.="
    parse(var_transcript)
    return var_transcript


def trim_variants(transcript: str) -> str:
    """Remove variants from an HGVS description"""
    model = to_model(transcript)
    id_ = model["reference"]["id"]
    coordinate = model["coordinate_system"]
    return f"{id_}:{coordinate}.="


def sort_variants(transcript: str) -> str:
    """
    Sort variants within an HGVS description

    This is pretty nasty, we use regex to pull out the variants and sort them.

    This will fail horribly on nested variants such as
    NM_152416.3:c.[500del;477_478ins[NC_000008.11:g.95036371_95036495]]
    """
    # Try to guess if this is a nested variant description
    count = 0
    for char in transcript:
        if char == "[":
            count += 1
    if count > 1:
        raise ValueError(f"Cannot sort HGVS description: {transcript}")

    # If there is only one opening bracket, there is nothing to sort
    if count == 0:
        return transcript

    # Find the variants
    start = transcript.find("[")
    end = transcript.find("]")
    variants = transcript[start + 1 : end]

    # Patern to split the position from the description
    pattern = r"^([-\*]?\d+)(.*)$"
    variant_position = list()
    for var in variants.split(";"):
        m = re.match(pattern, var)
        if not m:
            raise ValueError
        pos = m.group(1)
        # The position is after the coding region
        if pos.startswith("*"):
            pos = int(m.group(1)[1:])
        else:
            pos = int(m.group(1))
        variant_position.append((var, pos))

    # Sort by position
    sorted_variants = sorted(variant_position, key=lambda x: x[1])
    vars = ";".join(f"{x[0]}" for x in sorted_variants)

    return transcript[:start] + f"[{vars}]"


def make_exons(transcript: str, config: Dict[str, Any]) -> List[Exon]:
    """Make or fetch the requested exons"""

    # If the transcript is actually the gene name, substitute the MANE transcript
    MANE = get_MANE()
    transcript = MANE.get(transcript, transcript)
    if transcript in MANE:
        transcript = MANE[transcript]
    else:
        # Does the transcript format make sense?
        transcript = check_input(transcript)

    # Make the HGVS description without variants for the normalizer
    no_variants = trim_variants(transcript)

    # Rewrite the HGVS description with variants to put the variants in order,
    # which they might not be
    ordered_variants = sort_variants(transcript)

    exons = fetch_exons(no_variants)
    variants = fetch_variants(ordered_variants)

    return build_exons(transcript, exons, variants, config)


def make_option_parser() -> argparse.ArgumentParser:
    """Create a parser for the drawing options"""
    parser = argparse.ArgumentParser(add_help=False)

    for key, value, description in _config:
        # Booleans are a special case
        if isinstance(value, bool):
            action = "store_false" if value else "store_true"
            parser.add_argument(
                f"--{key}", default=value, action=action, help=description
            )
        elif isinstance(value, list):
            parser.add_argument(f"--{key}", default=value, nargs="+", help=description)
        else:
            parser.add_argument(
                f"--{key}",
                type=type(value),
                default=value,
                help=description,
            )

    return parser


def make_parser() -> argparse.ArgumentParser:
    option_parser = make_option_parser()

    parser = argparse.ArgumentParser(
        description="Visualise exons and mutations",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[option_parser],
    )
    parser.add_argument(
        "--dump-exons", type=str, help="Write exons to the specified file"
    )
    parser.add_argument(
        "--dump-variants", type=str, help="Write variants to the specified file"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--transcript", help="Transcript (with version) to visualise")
    group.add_argument("--exon-tsv", help="TSV file containing exons")
    parser.add_argument("--variant-tsv", help="TSV file containing variants")

    return parser


def dump_exons(exons: List[Exon], fname: str) -> None:
    """Write the exons to the specified file"""
    header = [
        "size",
        "name",
        "color",
        "coding_start",
        "coding_end",
        "start_phase",
        "end_phase",
    ]
    with open(fname, "wt") as fout:
        print(*header, sep="\t", file=fout)
        for exon in exons:
            print(exon.tsv(sep="\t"), file=fout)


def dump_variants(exons: List[Exon], fname: str) -> None:
    """Write the variants to the specified file"""
    header = [
        "exon",
        "position",
        "name",
        "color",
    ]
    with open(fname, "wt") as fout:
        print(*header, sep="\t", file=fout)
        for i, exon in enumerate(exons, 1):
            for variant in exon.variants:
                print(i, end="\t", file=fout)
                print(variant.tsv(sep="\t"), file=fout)


def exons_from_mutalyzer(transcript: str, config: Dict[str, Any]) -> List[Exon]:
    """Attempt to create exons from mutalyzer"""
    try:
        exons = make_exons(transcript, config)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        exit(1)
    return exons


def exons_from_tsv_file(fname: str) -> List[Exon]:
    """Read Exons from a tsv file"""
    with open(fname) as fin:
        return exons_from_tsv(fin)


def variants_from_tsv_file(fname: str) -> Dict[int, List[Variant]]:
    """Read Variants from a tsv file"""
    variants = defaultdict(list)
    with open(fname) as fin:
        header = next(fin).strip("\n").split("\t")
        assert header == ["exon", "position", "name", "color"]
        for line in fin:
            exon, pos, name, color = line.strip("\n").split("\t")
            variants[int(exon)].append(Variant(int(pos), name, color))
    return variants


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()
    # Make the configuration for the drawing
    config = dict()
    for key, *_ in _config:
        config[key] = getattr(args, key)

    # Create the exons
    if args.transcript:
        exons = exons_from_mutalyzer(args.transcript, config)
    elif args.exon_tsv:
        exons = exons_from_tsv_file(args.exon_tsv)

    if args.variant_tsv:
        vars = variants_from_tsv_file(args.variant_tsv)
        for i, exon in enumerate(exons, 1):
            exon.variants = vars[i]

    if args.dump_exons:
        dump_exons(exons, args.dump_exons)
    if args.dump_variants:
        dump_variants(exons, args.dump_variants)

    else:
        plot = draw_exons(
            exons,
            config=config,
        )
        print(plot)

    if __name__ == "__main__":
        main()
