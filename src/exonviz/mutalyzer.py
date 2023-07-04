from typing import Dict, Any, Optional, List, Tuple
import urllib.request
from urllib.error import HTTPError
import json

from .exon import Exon, Region


def mutalyzer(variant: str) -> Optional[Dict[str, Any]]:
    """Fetch variant information from mutalyzer"""

    url = f"https://mutalyzer.nl/api/normalize/{variant}"

    try:
        response = urllib.request.urlopen(url)
    except HTTPError as e:
        msg = f"Fetching '{url}' returned {e}"
        raise RuntimeError(msg)
    else:
        js = json.loads(response.read())
    selector: Dict[str, Any] = js["selector_short"]
    return selector


def convert_coding_positions(positions: List[List[str]]) -> Tuple[int, int]:
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
    converted = list()
    for mutalyzer_start, mutalyzer_end in positions:
        start = int(mutalyzer_start)
        end = int(mutalyzer_end)

        # Make sure start is always before end
        if start > end:
            start, end = end, start

        start = start - 1
        converted.append((start, end))
    return converted


def extract_exons(mutalyzer: Dict[str, Any]) -> Tuple[List[Exon], bool]:
    """Extract Exons from mutalyzer payload"""
    exons: List[Exon] = list()

    # Is the mutalyzer code in reverse
    reverse = is_reverse(mutalyzer["cds"]["g"])

    # Get the coding region
    coding = Region(*convert_coding_positions(mutalyzer["cds"]["g"]))

    # The first exon starts in frame by definition
    frame = 0

    for start, end in convert_exon_positions(mutalyzer["exon"]["g"]):
        E = Exon(start, end, frame, coding)
        frame = E.end_frame
        exons.append(E)

    return exons, reverse
