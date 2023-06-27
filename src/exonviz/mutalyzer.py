from typing import Dict, Any, Optional
import urllib.request
import json

from exonviz.exon import Exon


def mutalyzer(variant: str) -> Optional[Dict[str, Any]]:
    """Fetch variant information from mutalyzer"""

    url = f"https://mutalyzer.nl/api/normalize/{variant}"

    try:
        with urllib.request.urlopen(url) as response:
            js = json.loads(response.read())
    except:
        print(f"Error for {url}")
        return None
    selector: Dict[str, Any] = js["selector_short"]
    return selector


def cds_start(mutalyzer: Dict[str, Any]) -> int:
    """Extract the coding start from mutalyzer payload"""
    return int(mutalyzer["cds"]["g"][0][0]) - 1


def cds_end(mutalyzer: Dict[str, Any]) -> int:
    """Extract the coding start from mutalyzer payload"""
    return int(mutalyzer["cds"]["g"][0][1])
