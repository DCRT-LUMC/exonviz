from typing import Dict, Any, List, Tuple, cast
import urllib.request
from urllib.error import HTTPError
import json

from mutalyzer_crossmapper import NonCoding, Genomic
from .exon import Exon, Coding, Variant
from GTGT.range import intersect

import logging

logging.basicConfig()
log = logging.getLogger(__name__)

Range = Tuple[int, int]


def fetch_exons(transcript: str) -> Dict[str, Any]:
    """Fetch transcript information from mutalyzer"""

    url = f"https://mutalyzer.nl/api/normalize/{transcript}"

    try:
        response = urllib.request.urlopen(url)
    except HTTPError as e:
        msg = f"Fetching '{url}' returned {e}"
        raise RuntimeError(msg)
    else:
        js = json.loads(response.read())

    if "selector_short" not in js:
        msg = f"No exons found for {transcript} (is it a genomic variant?)"
        raise RuntimeError(msg)
    selector: Dict[str, Any] = js["selector_short"]
    return selector


def fetch_variants(transcript: str) -> Dict[str, Any]:
    """Fetch variant view from mutalyzer"""

    url = f"https://mutalyzer.nl/api/view_variants/{transcript}"

    try:
        response = urllib.request.urlopen(url)
    except HTTPError as e:
        msg = f"Fetching '{url}' returned {e}"
        raise RuntimeError(msg)
    else:
        js: Dict[str, Any] = json.loads(response.read())
    return js


def convert_mutalyzer_range(start: str, end: str, reverse: bool) -> Tuple[int, int]:
    """Convert a mutalyzer range to 0-based coordinates"""
    crossmap = Genomic()

    g_start = crossmap.genomic_to_coordinate(int(start))
    g_end = crossmap.genomic_to_coordinate(int(end))
    if reverse:
        return g_end, g_start + 1
    else:
        return g_start, g_end + 1


def convert_coding_positions(positions: List[List[str]], reverse: bool) -> Range:
    return convert_mutalyzer_range(positions[0][0], positions[0][1], reverse)


def is_reverse(start: str, end: str) -> bool:
    """Is the transcript in reverse"""
    return int(start) > int(end)


def convert_exon_positions(
    positions: List[List[str]], reverse: bool
) -> List[Tuple[int, int]]:
    """Convert exon positions from Mutalyzer to a list of Ranges

    This function also accounts for reverse transcripts
    """
    if reverse:
        return [convert_mutalyzer_range(x[0], x[1], reverse) for x in positions[::-1]]
    else:
        return [convert_mutalyzer_range(x[0], x[1], reverse) for x in positions]


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


def exon_variant(exons: List[List[str]], variant: Dict[str, Any]) -> bool:
    """Determine if a given variant falls in an exon"""
    reverse = is_reverse(exons[0][0], exons[0][1])

    x = NonCoding(convert_exon_positions(exons, reverse), reverse)

    position, exon_offset, transcript_offset = x.coordinate_to_noncoding(
        variant["start"]
    )

    return not exon_offset


def parse_view_variants(
    exons: List[List[str]], payload: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Extract only the exonic variants from the mutalyzer view_variants API payload"""
    # Exclude the regions that flank the variants
    variants = [x for x in payload if x["type"] == "variant"]

    for var in variants:
        # Exclude variants that do not fall inside an exon
        if not exon_variant(exons, var):
            continue
        var["start"], var["end"] = variant_to_ranges(exons, var["start"], var["end"])

    return variants


def inside(exon: Range, variant: Dict[str, Any]) -> bool:
    pos = variant["start"]
    return cast(bool, pos >= exon[0] and pos < exon[1])


def exon_variants(exon: Range, variants: List[Dict[str, Any]]) -> List[Variant]:
    """Create a list of Variants that fall within the exon

    The position of the variants is relative to the Exon start position
    """
    vars = list()
    for var in variants:
        if inside(exon, var):
            relative_position = var["start"] - exon[0]
            vars.append(Variant(relative_position, var["description"], "red"))
    return vars


def exons_to_ranges(exons: List[List[str]], cds: List[str]) -> List[Tuple[int, int]]:
    """Convert mutalyzer exons to python ranges, for both strands"""
    reverse = is_reverse(exons[0][0], exons[0][1])

    x = NonCoding(convert_exon_positions(exons, reverse), reverse)
    g = Genomic()

    output_exons = list()
    for exon in exons:
        e_start = (
            x.coordinate_to_noncoding(g.genomic_to_coordinate(int(exon[0])))[0] - 1
        )
        e_end = x.coordinate_to_noncoding(g.genomic_to_coordinate(int(exon[1])))[0]
        output_exons.append((e_start, e_end))

    return output_exons


def cds_to_ranges(exons: List[List[str]], cds: List[str]) -> Tuple[int, int]:
    """Convert mutalyzer exons to python ranges, for both strands"""
    reverse = is_reverse(cds[0], cds[1])

    x = NonCoding(convert_exon_positions(exons, reverse), reverse)
    g = Genomic()

    cds_start = x.coordinate_to_noncoding(g.genomic_to_coordinate(int(cds[0])))[0] - 1
    cds_end = x.coordinate_to_noncoding(g.genomic_to_coordinate(int(cds[1])))[0]

    return (cds_start, cds_end)


def variant_to_ranges(
    exons: List[List[str]], var_start: int, var_end: int
) -> Tuple[int, int]:
    """Convert mutalyzer exons to python ranges, for both strands"""
    reverse = is_reverse(exons[0][0], exons[0][1])

    x = NonCoding(convert_exon_positions(exons, reverse), reverse)
    g = Genomic()

    new_start = g.genomic_to_coordinate(x.coordinate_to_noncoding(var_start)[0])
    new_end = g.genomic_to_coordinate(x.coordinate_to_noncoding(var_end)[0])
    if reverse:
        return (new_end, new_start)
    else:
        return (new_start, new_end)


def rewrite_reverse_variants(view_variants: Dict[str, Any]) -> None:
    if not view_variants.get("inverted"):
        return

    seq_length = view_variants["seq_length"]
    for view in view_variants["views"]:
        view["start"] = seq_length - view["start"] - 1
        view["end"] = seq_length - view["end"] - 1


def build_exons(
    mutalyzer: Dict[str, Any], view_variants: Dict[str, Any], config: Dict[str, Any]
) -> List[Exon]:
    """Build Exons from the mutalyzer payload"""
    Exons: List[Exon] = list()

    exons = mutalyzer["exon"]["g"]
    cds = mutalyzer["cds"]["g"][0]
    rewrite_reverse_variants(view_variants)
    vars = view_variants["views"]

    # Convert to ranges
    exon_ranges = exons_to_ranges(exons, cds)
    cds_ranges = cds_to_ranges(exons, cds)

    start_phase = 0

    # Used for the exon name
    index = 0

    # Get the variants
    variants = parse_view_variants(exons, vars)

    for exon in exon_ranges:
        # Determine the name of this exon
        index += 1
        name = f"{index}" if config["exonnumber"] else ""

        # Determine the start and end for this exon
        e_start, e_end = exon
        # Determine the coding region for this exon
        coding = make_coding(exon, cds_ranges, start_phase)
        # Determine the variants for this exon
        vars = exon_variants(exon, variants)
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

    return Exons
