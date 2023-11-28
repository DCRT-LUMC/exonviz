import pytest

from exonviz.exon2 import Coding, Exon


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


def test_default_exon(default_exon: Exon) -> None:
    assert default_exon.size == 100

    # Test the default coding region
    assert not default_exon.coding
    assert default_exon.coding.start == 0


def test_draw_exon(center_coding: Exon) -> None:
    height = 20
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
    assert non_coding.x == 11 #  offset
    assert non_coding.y == 13+5 #  offset + 0.25 * height


def test_draw_exon_offset_coding(center_coding: Exon) -> None:
    """Test drawing a coding exon with offsets"""
    elements = center_coding.draw(x=11, y=13, height=20)
    # If the exon is non coding, there should only be a single element

    coding = elements[1]
    assert coding.x == 11 + 40 #  offset + start coding region
    assert coding.y == 13 #  offset

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
    assert non_coding.x == 5 #  height * 0.25

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
    #start, end, start_expected, end_expected
    (0, 0, None, None),
]

@pytest.mark.parametrize("start_frame, end_frame, start_element, end_element", start_end_frame)
def test_draw_coding_frames(start_frame: int, end_frame: int, start_element: None, end_element:None) -> None:
    c = Coding(0, 10)
    e = Exon(size=10, coding=c)
    elements = e.draw()

    # The coding region frames are the third and fourth element
    #start = elements[2]
    #end = elements[3]
