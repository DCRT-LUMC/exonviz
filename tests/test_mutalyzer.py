from exonviz.mutalyzer import cds_start, cds_end

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


def test_get_coding_size_noncoding():
    """Test the size for non-coding exons"""
    exons = [["1", "100"], ["201", "300"]]
    coding_start = 200
