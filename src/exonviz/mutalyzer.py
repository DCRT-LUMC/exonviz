from typing import Any, cast
import urllib.request
from urllib.error import HTTPError
import json

import mutalyzer_crossmapper
from mutalyzer_hgvs_parser import to_model
from .exon import Exon, Coding, Variant
from .range import intersect

import logging

logging.basicConfig()
log = logging.getLogger(__name__)

Range = tuple[int, int]


def parse_error_payload(error: HTTPError) -> str:
    """Parse HTTPError payload from mutalyzer"""
    try:
        js = json.loads(error.read().decode())
        msg = "\n".join((error["details"] for error in js["custom"]["errors"]))
    except Exception:
        msg = ""
    return msg if msg else str(error)


def fetch_exons(transcript: str) -> dict[str, Any]:
    """Fetch transcript information from mutalyzer"""

    url = f"https://mutalyzer.nl/api/normalize/{transcript}"

    try:
        response = urllib.request.urlopen(url)
    except HTTPError as e:
        msg = parse_error_payload(e)
        raise RuntimeError(msg)
    else:
        js = json.loads(response.read())

    if "selector_short" not in js:
        msg = f"No exons found for {transcript} (is it a genomic variant?)"
        raise RuntimeError(msg)
    selector: dict[str, Any] = js["selector_short"]
    return selector


def convert_mutalyzer_range(start: str, end: str) -> tuple[int, int]:
    """Convert a mutalyzer range to 0-based coordinates"""

    if is_reverse(start, end):
        return int(end) - 1, int(start)
    else:
        return int(start) - 1, int(end)


def is_reverse(start: str, end: str) -> bool:
    """Is the transcript in reverse"""
    return int(start) > int(end)


def convert_exon_positions(positions: list[list[str]]) -> list[tuple[int, int]]:
    """Convert exon positions from Mutalyzer to a list of Ranges

    This function also accounts for reverse transcripts
    """
    if is_reverse(*positions[0]):
        return [convert_mutalyzer_range(*x) for x in positions[::-1]]
    else:
        return [convert_mutalyzer_range(*x) for x in positions]


def make_coding(exon: Range, coding_region: Range, start_phase: int) -> Coding:
    """Create the coding region"""
    c = intersect(exon, coding_region)
    if not c:
        return Coding()

    assert len(c) == 1
    # Determine the coding start and end, relative to the exon start
    coding_start, coding_end = c[0]
    coding_start -= exon[0]
    coding_end -= exon[0]

    end_phase = (start_phase + (coding_end - coding_start)) % 3
    return Coding(
        start=coding_start, end=coding_end, start_phase=start_phase, end_phase=end_phase
    )


def transcript_to_coordinate(transcript: str) -> str:
    """Determine the coordinate system used by a transcript"""
    return cast(str, to_model(transcript)["coordinate_system"])


def exon_variants(
    exons: list[Range], cds: Range, exon: Range, variants: list[str], coordinate: str
) -> list[Variant]:
    """Create a list of Variants that fall within the exon

    The position of the variants is relative to the Exon start position
    """
    vars = list()
    for var in variants:
        position = cdot_to_position(exons, cds, var)
        # Intronic variant
        if position is None:
            continue
        # Variant falls within the exon
        if position >= exon[0] and position < exon[1]:
            relative_position = position - exon[0]
            vars.append(Variant(relative_position, f"{coordinate}.{var}", "red"))
    return vars


def exons_to_ranges(exons: list[list[str]], cds: list[str]) -> list[tuple[int, int]]:
    """Convert mutalyzer exons to python ranges, for both strands"""
    reverse = is_reverse(exons[0][0], exons[0][1])

    x = mutalyzer_crossmapper.NonCoding(convert_exon_positions(exons), reverse)
    g = mutalyzer_crossmapper.Genomic()

    output_exons = list()
    for exon in exons:
        e_start = (
            x.coordinate_to_noncoding(g.genomic_to_coordinate(int(exon[0])))[0] - 1
        )
        e_end = x.coordinate_to_noncoding(g.genomic_to_coordinate(int(exon[1])))[0]
        output_exons.append((e_start, e_end))

    return output_exons


def cds_to_ranges(exons: list[list[str]], cds: list[str]) -> tuple[int, int]:
    """Convert mutalyzer exons to python ranges, for both strands"""
    reverse = is_reverse(cds[0], cds[1])

    x = mutalyzer_crossmapper.NonCoding(convert_exon_positions(exons), reverse)
    g = mutalyzer_crossmapper.Genomic()

    cds_start = x.coordinate_to_noncoding(g.genomic_to_coordinate(int(cds[0])))[0] - 1
    cds_end = x.coordinate_to_noncoding(g.genomic_to_coordinate(int(cds[1])))[0]

    return (cds_start, cds_end)


def variants_from_hgvs(hgvs: str) -> list[str]:
    """Extract a list of variants from an hgvs description"""
    variants = hgvs.strip(" ").split(":")[1][2:]

    # Empty HGVS description
    if variants == "=":
        return list()
    # List of variants
    elif variants.startswith("["):
        return variants[1:-1].split(";")
    # Single variant
    else:
        return [variants]


def build_exons(
    hgvs: str,
    mutalyzer: dict[str, Any],
    config: dict[str, Any],
) -> tuple[list[Exon], list[str]]:
    """Build Exons from the mutalyzer payload"""
    Exons: list[Exon] = list()

    exons = mutalyzer["exon"]["g"]
    cds = mutalyzer["cds"]["g"][0]
    coordinate_system = transcript_to_coordinate(hgvs)

    variants = variants_from_hgvs(hgvs)

    # Convert to ranges
    exon_ranges = exons_to_ranges(exons, cds)
    cds_ranges = cds_to_ranges(exons, cds)

    start_phase = 0

    # Used for the exon name
    index = 0
    # Used for picking the variant color
    color_index = 0
    colors = config["variantcolors"]

    for exon in exon_ranges:
        # Determine the name of this exon
        index += 1
        name = f"{index}" if config["exonnumber"] else ""

        # Determine the start and end for this exon
        e_start, e_end = exon
        # Determine the coding region for this exon
        coding = make_coding(exon, cds_ranges, start_phase)
        # Determine the variants for this exon
        vars = exon_variants(exon_ranges, cds_ranges, exon, variants, coordinate_system)
        # Set the variant colors
        for var in vars:
            i = color_index % len(colors)
            var.color = colors[i]
            color_index += 1
        # Determine the size for this exon
        e_size = e_end - e_start
        # Get the color from the configuration
        color = config["color"]

        E = Exon(size=e_size, coding=coding, variants=vars, name=name, color=color)

        # Set the start phase for the next exon
        start_phase = coding.end_phase

        if not config["noncoding"]:
            E.remove_noncoding()
        Exons.append(E)

    # Remove exons that are not part of the specified exon range
    first_exon = max(0, config["firstexon"] - 1)
    last_exon = min(config["lastexon"], len(Exons))
    Exons = Exons[first_exon:last_exon]

    # Variants that ended up in the exons
    exon_vars = list()
    for e in Exons:
        for v in e.variants:
            # Remember to cut off the c. or r.
            exon_vars.append(v.name[2:])

    # Determine which variants have been dropped
    dropped = list()

    hgvs_variants = variants_from_hgvs(hgvs)

    for variant in hgvs_variants:
        if variant not in exon_vars:
            dropped.append(variant)

    return Exons, dropped


def variant_to_tuple(variant: str) -> tuple[int, int, int]:
    """Convert a 'point' dictionary from parse_hgvs into a Location"""

    # Default values
    downstream = 0
    position = 0
    offset = 0

    variant_model = to_model(variant, "variant")

    # If the variant is a range, we take the start as the position
    if variant_model["location"]["type"] == "point":
        point = variant_model["location"]
    elif variant_model["location"]["type"] == "range":
        point = variant_model["location"]["start"]
    else:
        raise ValueError(f"Unable to parse {variant}")

    position = point["position"]
    if "outside_cds" in point:
        if point["outside_cds"] == "upstream":
            position *= -1
        elif point["outside_cds"] == "downstream":
            downstream = 1
        else:
            raise RuntimeError
    if "offset" in point:
        offset = point["offset"]["value"]

    return (downstream, position, offset)


def less_than(a: str, b: str) -> bool:
    return variant_to_tuple(a) < variant_to_tuple(b)


def cdot_to_tuple(variant: str) -> tuple[int, int, int, int]:
    """
    Convert an HGVS variant in c. notation to a 4-part tuple for use with the
    mutalyzer crossmapper
    """
    m = to_model(variant, "variant")
    # If the variant is a range, we take the start
    loc = m["location"] if m["location"]["type"] == "point" else m["location"]["start"]

    # Determine the position
    outside_cds = loc.get("outside_cds")
    position = int(loc["position"])
    if outside_cds == "upstream":
        position *= -1

    # Determine the (intron) offset
    offset = loc.get("offset", dict()).get("value", 0)

    # Determine the region, -1 is upstream of cds, 0 is in cds, 1 is after the CDS
    outside_cds = loc.get("outside_cds")
    if outside_cds is None:
        region = 0
    elif outside_cds == "downstream":
        region = 1
    elif outside_cds == "upstream":
        region = -1
    else:
        raise ValueError(m)

    # We assume the offset outside of the transcript is always 0
    outside_transcript = 0

    return (position, offset, region, outside_transcript)


def cdot_to_position(exons: list[Range], cds: Range, variant: str) -> int | None:
    """Convert a variant in c. format to a position on the transcript

    This function assumes that exons are adjacent, i.e. that introns have
    been removed from ENST and NC(NM) transcripts
    """
    t = cdot_to_tuple(variant)

    # Return None for intronic variants, which are not supported
    if t[1]:
        return None

    crossmap = mutalyzer_crossmapper.Coding(exons, cds)
    return int(crossmap.coding_to_coordinate(t))
