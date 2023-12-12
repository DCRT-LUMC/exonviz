from typing import Dict, Any, Optional, List, Tuple, cast
import urllib.request
from urllib.error import HTTPError
import json

from .exon2 import Exon, Coding, Variant
from GTGT.range import intersect

Range = Tuple[int, int]


def fetch_exons(transcript: str) -> Optional[Dict[str, Any]]:
    """Fetch variant information from mutalyzer"""

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


def fetch_variants(transcript: str) -> Optional[Dict[str, Any]]:
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


def convert_coding_positions(positions: List[List[str]]) -> Range:
    start = int(positions[0][0])
    end = int(positions[0][1])

    if start > end:
        start, end = end, start

    start = start - 1
    return (start, end)


def is_reverse(positions: List[List[str]]) -> bool:
    """Is the transcript in reverse"""
    start = int(positions[0][0])
    end = int(positions[0][1])

    return start > end


def convert_exon_positions(positions: List[List[str]]) -> List[Tuple[int, int]]:
    """Convert exon positions from Mutalyzer to a list of Ranges

    This function also accounts for reverse transcripts
    """
    converted = list()

    reversed = is_reverse(positions)
    for mutalyzer_start, mutalyzer_end in positions:
        start = int(mutalyzer_start)
        end = int(mutalyzer_end)

        # Make sure start is always before end
        if start > end:
            start, end = end, start

        start = start - 1
        converted.append((start, end))
    if reversed:
        return converted[::-1]
    else:
        return converted


def make_coding(exon: Range, coding_region: Range, start_phase: int) -> Coding:
    """Create the coding region"""
    c = intersect(exon, coding_region)
    if not c:
        return Coding()

    assert len(c) == 1
    start, end = c[0]

    end_phase = (start_phase + (end - start)) % 3
    return Coding(start=start, end=end, start_phase=start_phase, end_phase=end_phase)


def parse_view_variants(payload: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract only the variants from the mutalyzer view_variants API payload"""
    return [x for x in payload if x["type"] == "variant"]


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


def extract_exons(
    mutalyzer: Dict[str, Any], view_variants: Dict[str, Any]
) -> List[Exon]:
    """Extract Exons from mutalyzer payload"""
    exons: List[Exon] = list()

    # Get the coding region
    coding_region = convert_coding_positions(mutalyzer["cds"]["g"])

    # Get the variants
    variants = parse_view_variants(view_variants["views"])

    # The first exon starts in frame by definition
    start_phase = 0

    # Used for the exon name
    index = 0
    for range in convert_exon_positions(mutalyzer["exon"]["g"]):
        size = range[1] - range[0]
        coding = make_coding(range, coding_region, start_phase)
        start_phase = coding.end_phase
        vars = exon_variants(range, variants)
        index += 1
        E = Exon(size=size, coding=coding, variants=vars, name=str(index))
        exons.append(E)
    return exons
