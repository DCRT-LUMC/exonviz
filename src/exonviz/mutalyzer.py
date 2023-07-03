from typing import Dict, Any, Optional, List
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


def cds_start(mutalyzer: Dict[str, Any]) -> int:
    """Extract the coding start from mutalyzer payload"""
    return int(mutalyzer["cds"]["g"][0][0]) - 1


def cds_end(mutalyzer: Dict[str, Any]) -> int:
    """Extract the coding start from mutalyzer payload"""
    return int(mutalyzer["cds"]["g"][0][1])


def coding_region(mutalyzer: Dict[str, Any]) -> Region:
    return Region(cds_start(mutalyzer), cds_end(mutalyzer))


def extract_exons(mutalyzer: Dict[str, Any]) -> List[Exon]:
    """Extract Exons from mutalyzer payload"""
    exons: List[Exon] = list()

    # Get the coding region
    coding = Region(cds_start(mutalyzer), cds_end(mutalyzer))

    # The first exon starts in frame by definition
    frame = 0

    for start, end in mutalyzer["exon"]["g"]:
        start = int(start) - 1
        end = int(end)
        E = Exon(start, end, frame, coding)
        frame = E.end_frame
        exons.append(E)

    return exons
