from exonviz.mutalyzer import (
    extract_exons,
    convert_exon_positions,
    convert_coding_positions,
    is_reverse,
)
from exonviz.exon import Exon, Region

# Example mutalyzer payload
mutalyzer = {
    "exon": {
        "g": [["1", "268"], ["269", "330"], ["11284", "13992"]],
    },
    "cds": {"g": [["238", "11295"]]},
}


def test_convert_coding_positions() -> None:
    assert convert_coding_positions([["238", "11295"]]) == (237, 11295)


def test_convert_coding_positions_reverse() -> None:
    assert convert_coding_positions([["29199", "7218"]]) == (7217, 29199)


def test_extract_exons() -> None:
    exons, reverse = extract_exons(mutalyzer)
    assert exons[0] == Exon(0, 268, 0, Region(237, 11295))


def test_convert_mutalyzer_positions() -> None:
    positions = [["1", "268"], ["269", "330"], ["11284", "13992"]]

    assert convert_exon_positions(positions) == [
        (0, 268),
        (268, 330),
        (11283, 13992),
    ]


def test_is_reverse() -> None:
    assert is_reverse([["10", "4"]])
    assert not is_reverse([["4", "10"]])


def test_convert_mutalyzer_positions_reverse() -> None:
    # Taken from ENST00000436367.6
    positions = [
        ["462349", "462187"],
        ["454236", "454122"],
        ["358790", "358665"],
        ["286796", "286669"],
        ["223577", "223516"],
        ["186998", "186861"],
        ["29359", "27283"],
        ["7748", "1"],
    ]

    expected = [
        (462186, 462349),
        (454121, 454236),
        (358664, 358790),
        (286668, 286796),
        (223515, 223577),
        (186860, 186998),
        (27282, 29359),
        (0, 7748),
    ]

    assert convert_exon_positions(positions) == expected
