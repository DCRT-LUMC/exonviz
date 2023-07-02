from exonviz.mutalyzer import cds_start, cds_end, coding_region, extract_exons
from exonviz.exon import Exon, Region

# Example mutalyzer payload
mutalyzer = {
    "exon": {
        "g": [["1", "268"], ["269", "330"], ["11284", "13992"]],
    },
    "cds": {"g": [["238", "11295"]]},
}


def test_cds_start() -> None:
    assert cds_start(mutalyzer) == 237


def test_cds_end() -> None:
    assert cds_end(mutalyzer) == 11295


def test_coding_region() -> None:
    assert coding_region(mutalyzer) == Region(237, 11295)


def test_extract_exons() -> None:
    exons = extract_exons(mutalyzer)
    assert exons[0] == Exon(0, 268, 0, Region(237, 11295))
