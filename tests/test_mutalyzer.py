import pytest
from exonviz.mutalyzer import (
    convert_exon_positions,
    convert_coding_positions,
    convert_mutalyzer_range,
    is_reverse,
    make_coding,
    parse_view_variants,
    exon_variants,
    exons_to_ranges,
    variant_to_ranges,
    cds_to_ranges,
    inside,
    Range,
)
from exonviz.exon import Coding, Variant

from typing import Any, Dict, List, Tuple

# Example mutalyzer payload
mutalyzer = {
    "exon": {
        "g": [["1", "268"], ["269", "330"], ["11284", "13992"]],
    },
    "cds": {"g": [["238", "11295"]]},
}


# def test_convert_coding_positions() -> None:
#     assert convert_coding_positions([["238", "11295"]]) == (237, 11294)
#
#
# def test_convert_coding_positions_reverse() -> None:
#     assert convert_coding_positions([["29199", "7218"]]) == (29198, 7217)

mut_positions = [
    (["1", "268"], False, (0, 268)),
    (["269", "330"], False, (268, 330)),
    (["11284", "13992"], False, (11283, 13992)),
    (["7748", "1"], True, (0, 7748)),
]


@pytest.mark.parametrize("positions, reverse, expected", mut_positions)
def test_convert_mutalyzer_positions(
    positions: List[str], reverse: bool, expected: Tuple[int, int]
) -> None:
    assert convert_mutalyzer_range(positions[0], positions[1], reverse) == expected


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

    assert convert_exon_positions(positions, reverse=True) == expected


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


view_variants: Any = [
    ([{"type": "outside"}], list()),
    (
        [
            {"type": "outside"},
            {"type": "variant", "description": "274G>T", "start": 433423},
        ],
        [
            {"type": "variant", "description": "274G>T", "start": 433423},
        ],
    ),
]


@pytest.mark.parametrize("payload, expected", view_variants)
def test_parse_view_variants(
    payload: List[Dict[str, Any]], expected: List[Any]
) -> None:
    assert parse_view_variants(payload) == expected


variants = [
    # exon: Range, variants, expected
    ((0, 10), [{"start": 100}], list()),
    (
        (0, 10),
        [{"start": 0, "description": "274G>T"}],
        [Variant(0, "274G>T", color="red")],
    ),
    (
        (100, 110),
        [{"start": 105, "description": "274G>T"}],
        [Variant(5, "274G>T", color="red")],
    ),
]


@pytest.mark.parametrize("exon, variants, expected", variants)
def test_exon_variants(
    exon: Range, variants: List[Dict[str, Any]], expected: List[Variant]
) -> None:
    assert exon_variants(exon, variants) == expected


inside_exon_variants = [
    ({"start": 0}, True),
    ({"start": 10}, False),
    ({"start": -1}, False),
]


@pytest.mark.parametrize("variant, expected", inside_exon_variants)
def test_variant_inside_exon(variant: Dict[str, Any], expected: bool) -> None:
    exon = (0, 10)
    assert inside(exon, variant) == expected


# def test_convert_mutalyzer_range() -> None:
#     assert convert_mutalyzer_range("238", "11295") == (237, 11294)
#     assert convert_mutalyzer_range("29199", "7218") == (29198, 7217)


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


def test_variant_to_ranges() -> None:
    exons_in = [["100", "199"], ["300", "349"]]
    variant_start = 150
    variant_end = 319
    expected_start = 51
    expected_end = 121
    assert variant_to_ranges(exons_in, variant_start, variant_end) == (
        expected_start,
        expected_end,
    )


def test_variant_to_ranges_reverse() -> None:
    exons_in = [["349", "300"], ["199", "100"]]
    variant_start = 150
    variant_end = 319
    expected_start = 29
    expected_end = 99
    assert variant_to_ranges(exons_in, variant_start, variant_end) == (
        expected_start,
        expected_end,
    )
