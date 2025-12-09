from urllib.request import HTTPError
import io
import json
import pytest
import itertools
from exonviz.mutalyzer import (
    cdot_to_position,
    cdot_to_tuple,
    convert_exon_positions,
    convert_mutalyzer_range,
    transcript_to_coordinate,
    is_reverse,
    make_coding,
    exon_variants,
    exons_to_ranges,
    cds_to_ranges,
    Range,
    parse_error_payload,
    less_than,
    variant_to_tuple,
    variants_from_hgvs,
)
from exonviz.exon import Coding, Variant

from typing import Any
from http.client import HTTPMessage

# Example mutalyzer payload
mutalyzer = {
    "exon": {
        "g": [["1", "268"], ["269", "330"], ["11284", "13992"]],
    },
    "cds": {"g": [["238", "11295"]]},
}


mut_positions = [
    (["1", "268"], (0, 268)),
    (["269", "330"], (268, 330)),
    (["11284", "13992"], (11283, 13992)),
    (["7748", "1"], (0, 7748)),
]


@pytest.mark.parametrize("positions, expected", mut_positions)
def test_convert_mutalyzer_positions(
    positions: list[str], expected: tuple[int, int]
) -> None:
    assert convert_mutalyzer_range(positions[0], positions[1]) == expected


def test_is_reverse() -> None:
    assert is_reverse("10", "4")
    assert not is_reverse("4", "10")


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
        (0, 7748),
        (27282, 29359),
        (186860, 186998),
        (223515, 223577),
        (286668, 286796),
        (358664, 358790),
        (454121, 454236),
        (462186, 462349),
    ]

    assert convert_exon_positions(positions) == expected


coding = [
    # Exon, coding_region, start_phase, Coding
    ((0, 10), (20, 30), 0, Coding()),
    ((0, 10), (0, 10), 0, Coding(0, 10, end_phase=1)),
    ((0, 10), (5, 12), 0, Coding(5, 10, end_phase=2)),
    ((0, 10), (-5, 12), 2, Coding(0, 10, start_phase=2, end_phase=0)),
    ((100, 110), (100, 200), 0, Coding(0, 10, end_phase=1)),
]


@pytest.mark.parametrize("exon, coding_region, start_phase, expected", coding)
def test_make_coding(
    exon: Range, coding_region: Range, start_phase: int, expected: Coding
) -> None:
    c = make_coding(exon, coding_region, start_phase)
    assert c == expected


variants = [
    # exon: Range, variants, coordinate, expected
    (  # Exon 1
        (0, 87),
        "c",
        [
            Variant(0, "c.-35del", color="red"),
            Variant(35, "c.1del", color="red"),
            Variant(86, "c.52del", color="red"),
        ],
    ),
    (  # Exon 2
        (87, 204),
        "c",
        [
            Variant(0, "c.53del", color="red"),
            Variant(116, "c.169del", color="red"),
        ],
    ),
]


@pytest.mark.parametrize("exon, coordinate, expected", variants)
def test_exon_variants(
    exon: Range,
    expected: list[Variant],
    coordinate: str,
) -> None:
    # SDHD with the introns removed
    exons = [(0, 87), (87, 204), (204, 349), (349, 1339)]
    cds = (35, 515)
    # Variants on the modified SDHD transcript
    variants = [
        "-35del",
        "1del",
        "52del",
        "52+15del",
        "53-10del",
        "53del",
        "169del",
        "169+10del",
        "170-10del",
        "170del",
        "314del",
        "314+5del",
        "315-5del",
        "315del",
        "480del",
        "481del",
        "*824del",
    ]
    assert exon_variants(exons, cds, exon, variants, coordinate) == expected


def test_exons_to_ranges() -> None:
    exons_in = [["100", "199"], ["300", "349"]]
    exons_out = [(0, 100), (100, 150)]
    assert exons_to_ranges(exons_in, list()) == exons_out


def test_exons_to_ranges_reverse() -> None:
    exons_in = [["349", "300"], ["199", "100"]]
    exons_out = [(0, 50), (50, 150)]
    assert exons_to_ranges(exons_in, list()) == exons_out


def test_cds_to_ranges() -> None:
    exons_in = [["100", "199"], ["300", "349"]]
    cds_in = ["150", "320"]
    cds_out = (50, 121)
    assert cds_to_ranges(exons_in, cds_in) == cds_out


def test_cds_to_ranges_reverse() -> None:
    exons_in = [["349", "300"], ["199", "100"]]
    cds_in = ["320", "150"]
    cds_out = (29, 100)
    assert cds_to_ranges(exons_in, cds_in) == cds_out


transcripts = [
    ("NC_1234.4:c.=", "c"),
    ("NC_1234.4:r.=", "r"),
    ("NG_012337.3(NM_003002.4):c.274G>T", "c"),
    ("NC_000011.10:g.112088970del", "g"),
    ("GRCh38(chr11):g.112088970del", "g"),
]


@pytest.mark.parametrize("transcript, coordinate", transcripts)
def test_get_coordinate_system_from_transcript(
    transcript: str, coordinate: str
) -> None:
    assert transcript_to_coordinate(transcript) == coordinate


ERRORS = [
    # msg, fp, expected
    (
        "UNPROCESSABLE ENTITY",
        {"Hello": "world"},
        "HTTP Error 400: UNPROCESSABLE ENTITY",
    ),
    (
        "UNPROCESSABLE ENTITY",
        {"custom": dict()},
        "HTTP Error 400: UNPROCESSABLE ENTITY",
    ),
    ("fallback", {"custom": {"errors": list()}}, "HTTP Error 400: fallback"),
    (
        "fallback",
        {"custom": {"errors": [{"details": "Inner error message 1"}]}},
        "Inner error message 1",
    ),
    (
        "fallback",
        {
            "custom": {
                "errors": [{"details": "Inner error message 1"}, {"details": "Inner 2"}]
            }
        },
        "Inner error message 1\nInner 2",
    ),
]


@pytest.mark.parametrize("error, payload, expected", ERRORS)
def test_parse_error_payload(
    error: str, payload: dict[str, Any], expected: str
) -> None:
    # Convert dict into a bytes representation of json
    fp_io = io.BytesIO(bytes(json.dumps(payload), "utf-8"))

    E = HTTPError("url", 400, msg=error, hdrs=HTTPMessage(), fp=fp_io)

    assert parse_error_payload(E) == expected


TO_TUP = [
    ("-20", (0, -20, 0)),
    ("-10+1", (0, -10, 1)),
    ("10+1", (0, 10, 1)),
    ("11-1", (0, 11, -1)),
    ("*1", (1, 1, 0)),
    ("*5+1", (1, 5, 1)),
    ("*6-1", (1, 6, -1)),
    ("*8+10_*15-800", (1, 8, 10)),
    ("-8-10_*15-800", (0, -8, -10)),
]


@pytest.mark.parametrize("pos, expected", TO_TUP)
def test_pos_to_tuple(pos: str, expected: tuple[int, ...]) -> None:
    assert variant_to_tuple(pos) == expected


# Sorted list of HGVS positions, in increasing position
POSITIONS = [
    "-20",
    "-10",
    "-10+1",
    "-10+2",
    "-5-2",
    "-5-1",
    "-1",
    "1",
    "5",
    "10+1",
    "10+2",
    "11-2",
    "11-1",
    "11",
    "*1",
    "*5",
    "*5+1",
    "*5+2",
    "*6-2",
    "*6-1",
    "*6",
]

# Pairs where a > b
GREATER = list(itertools.combinations(POSITIONS, 2))
# Pairs where a < b
SMALLER = list(itertools.combinations(POSITIONS[::-1], 2))


@pytest.mark.parametrize("a, b", GREATER)
def test_sort_positions_greater(a: str, b: str) -> None:
    assert less_than(a, b)


@pytest.mark.parametrize("a, b", SMALLER)
def test_sort_positions_smaller(a: str, b: str) -> None:
    assert not less_than(a, b)


@pytest.mark.parametrize(
    "variant, expected",
    [
        ("-10del", (-10, 0, -1, 0)),
        ("-5+30del", (-5, 30, -1, 0)),
        ("-6-6del", (-6, -6, -1, 0)),
        ("-6del", (-6, 0, -1, 0)),
        ("-1del", (-1, 0, -1, 0)),
        ("1del", (1, 0, 0, 0)),
        ("10del", (10, 0, 0, 0)),
        ("10+1del", (10, 1, 0, 0)),
        ("11-10del", (11, -10, 0, 0)),
        ("11del", (11, 0, 0, 0)),
        ("*1del", (1, 0, 1, 0)),
        ("*2+10del", (2, 10, 1, 0)),
        ("*3-11del", (3, -11, 1, 0)),
        # For variants which are larger than 1 position, we create the tuple
        # based on the start
        ("-10_-8del", (-10, 0, -1, 0)),
        ("-5+30_-5+35del", (-5, 30, -1, 0)),
        ("-6-6_-6-3del", (-6, -6, -1, 0)),
        ("-6_3del", (-6, 0, -1, 0)),
        ("-1_5+12del", (-1, 0, -1, 0)),
        ("1_10-8del", (1, 0, 0, 0)),
        ("10+1_10+12del", (10, 1, 0, 0)),
        ("10+1_11-8del", (10, 1, 0, 0)),
        ("11-10_11-5del", (11, -10, 0, 0)),
        ("*1_*5del", (1, 0, 1, 0)),
        ("*2+10_*2+20del", (2, 10, 1, 0)),
        ("*3-11_*5+8del", (3, -11, 1, 0)),
    ],
)
def test_cdot_to_tuple(variant: str, expected: tuple[int, ...]) -> None:
    """Test converting c. hgvs variant descriptions into a tuple"""
    assert cdot_to_tuple(variant) == expected


@pytest.mark.parametrize(
    "variant, expected",
    [
        ("-35del", 0),
        ("1del", 35),
        ("52del", 86),
        ("52+15del", None),
        ("53-10del", None),
        ("53del", 87),
        ("169del", 203),
        ("169+10del", None),
        ("170-10del", None),
        ("170del", 204),
        ("314del", 348),
        ("314+5del", None),
        ("315-5del", None),
        ("315del", 349),
        ("480del", 514),
        ("481del", 515),
        ("*824del", 1338),
    ],
)
def test_cdot_to_position_forward(variant: str, expected: int | None) -> None:
    """Test converting a cdot variant to position for the forward strand

    Note that the exons and cds positions have been modified to remove introns
    """
    # SDHD, with positions modified to remove introns
    sdhd_exons = [(0, 87), (87, 204), (204, 349), (349, 1339)]
    sdhd_cds = (35, 515)

    assert cdot_to_position(sdhd_exons, sdhd_cds, variant) == expected


@pytest.mark.parametrize(
    "hgvs, expected",
    [
        ("ENST:c.=", []),
        ("ENST:c.10del", ["10del"]),
        ("ENST:c.-10+12_*18-29del", ["-10+12_*18-29del"]),
        ("ENST:c.[10del;11del]", ["10del", "11del"]),
        ("ENST:c.[10del]", ["10del"]),
        ("NC_123:c.=", []),
        ("NC_123:c.100A>T", ["100A>T"]),
        ("NC_123:c.100_200delinsATCGT", ["100_200delinsATCGT"]),
        ("NC_123:c.[1del;2A>T]", ["1del", "2A>T"]),
        ("NC_123:c.(10_12)insN", ["(10_12)insN"]),
        ("NC_123:g.*1281_*1283A[13]", ["*1281_*1283A[13]"]),
        ("NC_123:g.[100del;*1281_*1283A[13]]", ["100del", "*1281_*1283A[13]"]),
        # Strip trailing spaces
        (
            "NC_123:c.[*333_*338delinsAGGGCTG;*402G>T] ",
            ["*333_*338delinsAGGGCTG", "*402G>T"],
        ),
    ],
)
def test_variants_from_hgvs(hgvs: str, expected: list[str]) -> None:
    """Test extracting variants from an hgvs description"""
    assert variants_from_hgvs(hgvs) == expected
