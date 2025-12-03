import pytest

from exonviz.range import Range, intersect, overlap, subtract

# fmt: off
range_overlap = [
    # A before B
    ((0, 3), (3, 6), False),
    # B before A
    ((3, 6), (0, 3), False),
    # A is the same as B
    ((0, 3), (0, 3), True),
    # A overlaps start B
    ((0, 3), (2, 6), True),
    # A is within B, start position is the same
    ((0, 3), (0, 6), True),
    # A is within B, end position is the same
    ((3, 6), (0, 6), True),
    # A is fully within B, end position is the same
    ((1, 3), (0, 6), True),
    # A overlaps the end of B
    ((4, 7), (0, 6), True),
    # B is within A
    ((0, 6), (1, 3), True),
    # B overlaps the start of A
    ((0, 6), (0, 3), True)
]
# fmt: on


@pytest.mark.parametrize("a, b, expected", range_overlap)
def test_range_overlap(a: Range, b: Range, expected: bool) -> None:
    assert overlap(a, b) == expected
    assert overlap(b, a) == expected


intersections = [
    # Range A, range B, intersection
    ((0, 10), (10, 20), list()),
    ((0, 10), (0, 10), [(0, 10)]),
    # Test cases where A is of size 1, and B of size 3
    # In each test case, we shift A one further to the right
    ((0, 1), (1, 4), list()),
    ((1, 2), (1, 4), [(1, 2)]),
    ((2, 3), (1, 4), [(2, 3)]),
    ((3, 4), (1, 4), [(3, 4)]),
    ((4, 5), (1, 4), list()),
    # Test cases where A and B are both of size 3
    # In each test case, we shift A one further to the right
    ((0, 3), (3, 6), list()),
    ((1, 4), (3, 6), [(3, 4)]),
    ((2, 5), (3, 6), [(3, 5)]),
    ((3, 6), (3, 6), [(3, 6)]),
    ((4, 7), (3, 6), [(4, 6)]),
    ((5, 8), (3, 6), [(5, 6)]),
    ((6, 9), (3, 6), list()),
    ((7, 10), (3, 6), list()),
]


@pytest.mark.parametrize("a, b, intersection", intersections)
def test_intersect_ranges(a: Range, b: Range, intersection: list[Range]) -> None:
    assert intersect(a, b) == intersection
    assert intersect(b, a) == intersection


# fmt: off
range_subtract = [
    # The selector is before A
    #    0 1 2 3 4 5 6 7 8 9
    # A            - - - - -
    # S  - - - - -
    # E            - - - - -
    (
        # A
        [(5, 10)],
        # Selector
        [(0, 5)],
        # Expected
        [(5, 10)]
    ),
    # The selector overlaps the start of A
    #    0 1 2 3 4 5 6 7 8 9
    # A            - - - - -
    # S        - - - -
    # E                - - -
    (
        [(5, 10)],
        [(3, 7)],
        [(7, 10)],
    ),
    # The selector is contained in A
    #    0 1 2 3 4 5 6 7 8 9
    # A            - - - - -
    # S              - - -
    # E             -      -
    (
        [(5, 10)],
        [(6, 9)],
        [(5, 6), (9, 10)],
    ),
    # The selector overlaps the end of A
    #    0 1 2 3 4 5 6 7 8 9
    # A  - - - - -
    # S        - - -
    # E  - - -
    (
        [(0, 5)],
        [(3, 6)],
        [(0, 3)],
    ),
    # The selector is larger than A
    #    0 1 2 3 4 5 6 7 8 9
    # A        - - - - -
    # S      - - - - - - -
    # E
    (
        [(3, 8)],
        [(2, 9)],
        [],
    ),
    # The selector is the same as A
    #    0 1 2 3 4 5 6 7 8 9
    # A        - - - - -
    # S        - - - - -
    # E
    (
        [(3, 8)],
        [(3, 8)],
        [],
    ),
    # The selector is after A
    #    0 1 2 3 4 5 6 7 8 9
    # A  - - - - - -
    # S              - - -
    # E  - - - - - -
    (
        [(0, 6)],
        [(6, 9)],
        [(0, 6)],
    ),
    # Both A and the selector consist of multiple ranges
    # The first region in A has partial overlap with the first two selector regions
    # The second selector region (partially) overlaps the first two regions in A
    #
    #    0 1 2 3 4 5 6 7 8 9
    # A  - - - -   - -     -
    # S  - -   - - -       - - - - - -
    # E      -       -
    (
        [(0, 4), (5, 7), (9, 10)],
        [(0, 2), (3, 6), (9, 15)],
        [(2, 3), (6, 7)],
    ),
    # A is empty
    (
        [],
        [(0,2)],
        [],
    ),
    # The selector is empty, so A is unchanged
    (
        [(0, 4)],
        [],
        [(0, 4)],
    ),
    # Both A and the selector are empty
    (
        [],
        [],
        [],
    ),
    # The selector has size zero
    #    0 1 2 3 4 5 6 7 8 9
    # A  - - - -   - -     -
    # S
    # E      -       -
    (
        [(0, 4), (5, 7), (9, 10)],
        [(1,1)],
        [(0, 4), (5, 7), (9, 10)],
    ),
    # A has size zero
    (
        [(3,3)],
        [(8,10)],
        []

    ),
    # A has size zero
    (
        [(3,3)],
        [(2,4)],
        []

    ),
    # The last range in A has size zero
    (
        [(0, 4), (5, 7), (9, 10), (15,15)],
        [(0, 2), (3, 6), (9, 15)],
        [(2, 3), (6, 7)],
    ),
    # The first range in A has size zero
    (
        [(1,1), (2, 4), (5, 7), (9, 10)],
        [(0, 2), (3, 6), (9, 15)],
        [(2, 3), (6, 7)],
    ),

]
# fmt: on


@pytest.mark.parametrize("a, b, expected", range_subtract)
def test_subtract_ranges(a: list[Range], b: list[Range], expected: list[Range]) -> None:
    assert subtract(a, b) == expected
