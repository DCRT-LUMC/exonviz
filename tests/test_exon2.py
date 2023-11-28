import pytest

from exonviz.exon2 import Coding, Exon, Variant
from GTGT.range import Range


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
    c = Coding(40, 80)
    return Exon(size=100, coding=c, variants=vars, name="Exon-1")


def test_default_exon(default_exon: Exon) -> None:
    assert default_exon.size == 100

    # Test the default coding region
    assert not default_exon.coding
    assert default_exon.coding.start == 0

    # Test that we made variants into a list
    assert default_exon.variants == list()


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
    assert non_coding.x == 5  #  height * 0.25

    coding = elements[1]
    assert coding.x == 5


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
    assert variant.x == 10 + 5  #  variant.position + drawing offset for the start cap


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


def test_split_exon(all: Exon) -> None:
    # Split the exon in half
    new = all.split(size=50)

    # Check the size of new and old
    assert new.size == 50
    assert all.size == 50

    # Check the coding region
    assert new.coding.start == 40
    assert all.coding.start == 0

    assert new.coding.end == 50
    assert all.coding.end == 30

    # Check the name
    assert new.name == "Exon-1"

    # Check the variants
    assert new.variants[0].position == 10
    assert new.variants[1].position == 30

    assert all.variants[0].position == 30
