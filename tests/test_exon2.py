import pytest

from typing import List, Dict

from exonviz.exon2 import Coding, Exon, Variant, group_exons, exon_from_dict, element_xy, Element
from GTGT.range import Range
from svg import Rect, Text, Polygon


@pytest.fixture
def default_exon() -> Exon:
    """
    ==========
    """
    return Exon(100)


@pytest.fixture
def center_coding() -> Exon:
    """
    ====||||==
    """
    c = Coding(40, 80)
    return Exon(size=100, coding=c)


@pytest.fixture
def with_variant() -> Exon:
    vars = [Variant(10, "A>T", "red"), Variant(30, "C>G", "blue")]
    return Exon(size=100, variants=vars)


@pytest.fixture
def all() -> Exon:
    """Create an exon with all possible features"""
    vars = [
        Variant(10, "A>T", "red"),
        Variant(30, "C>G", "blue"),
        Variant(80, "G>A", "purple"),
    ]
    c = Coding(start=40, end=80, start_phase=1, end_phase=2)
    return Exon(size=100, coding=c, variants=vars, name="Exon-1")


def test_default_exon(default_exon: Exon) -> None:
    assert default_exon.size == 100

    # Test the default coding region
    assert not default_exon.coding
    assert default_exon.coding.start == 0

    # Test that we made variants into a list
    assert default_exon.variants == list()

    # Test that we set the default color
    assert default_exon.color == "#4C72B7"


def test_draw_exon(center_coding: Exon) -> None:
    elements = center_coding.draw(height=20)

    # Get the non coding part of the exon
    non_coding = elements[0]

    # Check the height and width
    assert non_coding.width == center_coding.size
    assert non_coding.height == 10

    # The drawing should start at an x-offset of 0.5*height, in case we need to
    # draw the notch/arrow
    assert non_coding.x == 0
    # The non-coding rectangle should start at an y offset of 0.25*height,
    # to leave space for the bigger coding region
    assert non_coding.y == 5

    # Get the coding part of the exon
    coding = elements[1]

    # Check the height and width
    assert coding.width == center_coding.coding.size
    assert coding.height == 20

    # Check that the start and end are correct
    assert coding.x == 40
    assert coding.y == 0

    # Test that every element is drawn in the correct color
    for e in elements:
        assert e.fill == "#4C72B7"


def test_draw_exon_offset_noncoding(default_exon: Exon) -> None:
    """Test drawing an exon with offsets"""
    elements = default_exon.draw(x=11, y=13, height=20)
    # If the exon is non coding, there should only be a single element
    assert len(elements) == 1

    non_coding = elements[0]
    assert non_coding.x == 11  #  offset
    assert non_coding.y == 13 + 5  #  offset + 0.25 * height


def test_draw_exon_offset_coding(center_coding: Exon) -> None:
    """Test drawing a coding exon with offsets"""
    elements = center_coding.draw(x=11, y=13, height=20)
    # If the exon is non coding, there should only be a single element

    coding = elements[1]
    assert coding.x == 11 + 40  #  offset + start coding region
    assert coding.y == 13  #  offset


def test_draw_full_coding() -> None:
    """
    IF we have an exon that starts with a coding region
    WHEN we draw this exon
    THEN the x position of the drawing should be offset to leave space for
         the start cap
    """
    e = Exon(10, Coding(0, 10))

    elements = e.draw(height=20)

    # We shift both the coding and non coding part of the exon
    non_coding = elements[0]
    assert non_coding.x == 10  #  height * 0.5

    coding = elements[1]
    assert coding.x == 10


def test_draw_full_coding_no_cap() -> None:
    """
    IF we have an exon that is fully coding, but the start phase is -1
    WHEN we draw this exon
    THEN the x position of the drawing should not be offset
    """
    e = Exon(10, Coding(0, 10, start_phase=-1))

    elements = e.draw(height=20)

    # We shift both the coding and non coding part of the exon
    non_coding = elements[0]
    assert non_coding.x == 0

    coding = elements[1]
    assert coding.x == 0


def test_default_coding() -> None:
    c = Coding()
    assert c.start == 0
    assert c.end == 0
    assert c.size == 0

    # An empty coding region is false
    assert not c


start_end_frame = [
    # start, end, start_expected, end_expected
    (0, 0, None, None),
]


@pytest.mark.parametrize(
    "start_frame, end_frame, start_element, end_element", start_end_frame
)
def test_draw_coding_frames(
    start_frame: int, end_frame: int, start_element: None, end_element: None
) -> None:
    c = Coding(0, 10)
    e = Exon(size=10, coding=c)
    elements = e.draw()

    # The coding region frames are the third and fourth element
    start_cap = elements[2]
    end_cap = elements[3]


def test_draw_variants(with_variant: Exon) -> None:
    elements = with_variant.draw(height=20)
    assert len(elements) == 3

    var1 = elements[1]
    assert var1.x == 10
    assert var1.fill == "red"

    var2 = elements[2]
    assert var2.x == 30
    assert var2.fill == "blue"


def test_draw_variants_offset(with_variant: Exon) -> None:
    elements = with_variant.draw(height=20, x=11)
    var1 = elements[1]
    assert var1.x == 10 + 11  #  variant.position + offset


def test_draw_variant_coding() -> None:
    e = Exon(size=100, coding=Coding(0, 100), variants=[Variant(10, "A>T", "blue")])

    elements = e.draw()

    assert len(elements) == 5

    variant = elements[4]
    assert variant.x == 10 + 10  #  variant.position + drawing offset for the start cap


def test_draw_name() -> None:
    e = Exon(size=100, name="Exon-1")

    elements = e.draw(height=10, x=11, y=23)

    assert len(elements) == 2

    text = elements[1]

    assert text.x == 11 + 50  # offset + half the exon size
    assert text.y == 23 + 5  # offset + half the height
    assert text.text == "Exon-1"


split_coding = [
    # size, new, old
    (50, (40, 50), (0, 30)),
    # The size ends before the coding region
    (10, (0, 0), (30, 70)),
    # The size has the entire coding region
    (80, (40, 80), (0, 0)),
    # The size is bigger than the coding region
    (100, (40, 80), (0, 0)),
]


@pytest.mark.parametrize("size, new, old", split_coding)
def test_split_coding(size: int, new: Range, old: Range) -> None:
    c = Coding(40, 80, 1, 2)
    n = c.split(size=size)

    old_range = (c.start, c.end)
    new_range = (n.start, n.end)

    assert new_range == new
    assert old_range == old


def test_split_coding_update_phase() -> None:
    """
    IF a Coding region has a start and end phase
    WHEN the Coding region is split
    THEN the new Coding should get the start_phase
         the end_phase of the new Coding should be set to -1,
         so no cap is drawn

         the old Coding should keep the end_phase
         the start_phase of the old Coding region should be set to -1,
         so no cap is drawn
    """
    old = Coding(start=40, end=80, start_phase=1, end_phase=2)

    new = old.split(50)

    assert new.start_phase == 1
    assert new.end_phase == -1

    assert old.start_phase == -1
    assert old.end_phase == 2


def test_split_coding_phase_all() -> None:
    """
    IF a Coding region has a start and end phase
    WHEN the Coding region is 'split' into one big chunk
    THEN the Coding start/end phase of new should be lifted over
    """
    old = Coding(start=40, end=80, start_phase=1, end_phase=2)
    new = old.split(1000)

    assert new.start_phase == 1
    assert new.end_phase == 2

    # If the old Coding is empty, the start/end phase should be zero
    assert old.start_phase == 0
    assert old.end_phase == 0


def test_split_exon(all: Exon) -> None:
    # Split the exon in half
    new = all.split(size=50, height=20)

    # Check the size of new and old
    assert new.size == 50
    assert all.size == 50

    # Check the coding region
    assert new.coding.start == 40
    assert all.coding.start == 0

    assert new.coding.end == 50
    assert all.coding.end == 30

    # Check the coding start/end frames
    assert new.coding.start_phase == 1
    assert new.coding.end_phase == -1

    assert all.coding.start_phase == -1
    assert all.coding.end_phase == 2

    # Check the name
    assert new.name == "Exon-1"
    assert all.name == "Exon-1"

    # Check the variants
    assert new.variants[0].position == 10
    assert new.variants[1].position == 30

    assert all.variants[0].position == 30


def test_take_full_exon(all: Exon) -> None:
    new = all.split(size=100, height=20)

    assert new.size == 100
    assert new.coding.start_phase == 1
    assert new.coding.end_phase == 2

    assert not all


def test_take_full_non_coding() -> None:
    """Test taking a full, non coding exon"""
    e = Exon(100)
    new = e.split(100, height=20)

    assert new.size == 100


def test_take_bigger_exon(all: Exon) -> None:
    new = all.split(size=1000, height=20)

    assert new.size == 100
    assert all.size == 0
    assert not all


def test_boolean_exon() -> None:
    e = Exon(size=1)
    assert e

    zero = Exon(size=0)
    assert not zero


draw = [
    # Non coding exon is exactly its own size
    (Exon(100), 100),
    # Exon starts coding
    (Exon(100, Coding(0, 50)), 110),
    # Exon ends coding
    (Exon(100, Coding(50, 100)), 110),
    # Fully coding exon gets 2*0.5*height added for the notches
    (Exon(100, Coding(0, 100)), 120),
    # Coding region starts at position 1
    (Exon(100, Coding(1, 50)), 109),
    # Coding region ends 4 bp from exon end
    (Exon(100, Coding(50, 96)), 106),
    # Coding in the middle, far from the edges
    (Exon(100, Coding(50, 60)), 100),
    # Coding, but the start phase is -1
    (Exon(100, Coding(0, 100, start_phase=-1)), 110),
    # Coding, but the end phase is -1
    (Exon(100, Coding(0, 100, start_phase=0, end_phase=-1)), 110),
    # Coding, but both start and end phase are -1
    (Exon(100, Coding(0, 100, start_phase=-1, end_phase=-1)), 100),
]


@pytest.mark.parametrize("exon, draw_size", draw)
def test_exon_draw_size(exon: Exon, draw_size: int) -> None:
    assert exon.draw_size(height=20) == draw_size


to_page = [
    # Exon list, page size, gap, result
    # Empty list
    ([], 100, 0, [[]]),
    # Single exon that fits on one page
    ([Exon(50)], 100, 0, [[Exon(50)]]),
    # Single exon that fits exactly
    ([Exon(100)], 100, 0, [[Exon(100)]]),
    # Single exon that doesn't fit
    ([Exon(100)], 99, 0, [[Exon(99)], [Exon(1)]]),
    # Two exons fit on one row
    ([Exon(50), Exon(50)], 100, 0, [[Exon(50), Exon(50)]]),
    ## Two exons don't fit on one row
    ([Exon(50), Exon(51)], 100, 0, [[Exon(50), Exon(50)], [Exon(1)]]),
    ## Two exons that almost fit on one row
    ([Exon(50), Exon(50)], 99, 0, [[Exon(50), Exon(49)], [Exon(1)]]),
    # Two exons fit on one row, but not with a gap
    ([Exon(50), Exon(50)], 100, 1, [[Exon(50), Exon(49)], [Exon(1)]]),
    # One exon that fits with a giant gap, since we dont include a gap for one exon
    ([Exon(100)], 100, 9999, [[Exon(100)]]),
    # Giant gap, exon doesn't fit
    ([Exon(100)], 99, 9999, [[Exon(99)], [Exon(1)]]),
    # Fits exactly, with gap of 10
    ([Exon(45), Exon(45)], 100, 10, [[Exon(45), Exon(45)]]),
    # Off by one, so it doesn't fit, with gap of 10
    ([Exon(46), Exon(45)], 100, 10, [[Exon(46), Exon(44)], [Exon(1)]]),
    # fmt: off
    # One exon that fits, including a gap of 10
    (
        [Exon(100) for _ in range(1)],
        100,
        10,
        [[Exon(100) for _ in range(1)]]
    ),
    # Two exons that fit, including gaps of size 10
    (
        [Exon(100) for _ in range(2)],
        210,
        10,
        [[Exon(100) for _ in range(2)]]
    ),
    # Ten exons that fit, including gaps of size 10
    (
        [Exon(100) for _ in range(10)],
        1090,
        10,
        [[Exon(100) for _ in range(10)]]
    ),
    # fmt: on
]


@pytest.mark.parametrize("exons, width, gap, page", to_page)
def test_exons_on_page(
    exons: List[Exon], width: int, gap: int, page: List[List[Exon]]
) -> None:
    new_page = group_exons(exons, height=20, gap=gap, width=width)

    assert new_page == page


exon_dict = [
    ({"size": "100"}, Exon(100)),
    ({"size": "100", "name": "Exon-1"}, Exon(100, name="Exon-1")),
    ({"size": "100", "color": "blue"}, Exon(100, color="blue")),
    ({"size": "100", "coding_start": 5}, Exon(100, coding=Coding(start=5))),
    ({"size": "100", "coding_end": 5}, Exon(100, coding=Coding(end=5))),
    ({"size": "100", "start_phase": 1}, Exon(100, coding=Coding(start_phase=1))),
    ({"size": "100", "end_phase": 1}, Exon(100, coding=Coding(end_phase=1))),
    ({"size": "100", "end_phase": 1}, Exon(100, coding=Coding(end_phase=1))),
    (
        {
            "size": "100",
            "variant_pos": "10",
            "variant_name": "A>T",
            "variant_color": "red",
        },
        Exon(size=100, variants=[Variant(position=10, name="A>T", color="red")]),
    ),
    (
        {
            "size": "100",
            "variant_pos": "10,22",
            "variant_name": "A>T,stop codon",
            "variant_color": "red,purple",
        },
        Exon(
            size=100,
            variants=[
                Variant(position=10, name="A>T", color="red"),
                Variant(position=22, name="stop codon", color="purple"),
            ],
        ),
    ),
]


@pytest.mark.parametrize("d, exon", exon_dict)
def test_exon_from_dict(d: Dict[str, str], exon: Exon) -> None:
    assert exon_from_dict(d) == exon


elements = [
    #element, max_x, max_y
    (Rect(x=1, y=2, width=11.0, height=23), 12, 25),
    (Text(x=1, y=1, text="text"), 1, 1),
    (Polygon(points=[0, 0, 10, 5, 0, 15, 20, 25, 13, 17]), 20, 25)
]
@pytest.mark.parametrize("element, max_x, max_y", elements)
def test_element_size(element: Element, max_x: float, max_y: float) -> None:
    """Determine the size of various SVG elements"""
    x, y = element_xy(element)

    assert x == max_x
    assert y == max_y
