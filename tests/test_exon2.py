import pytest

from exonviz.exon2 import Coding, Exon


@pytest.fixture
def default_exon() -> Exon:
    """
    ==========
    """
    return Exon(10)


@pytest.fixture
def center_coding() -> Exon:
    """
    ====||||==
    """
    c = Coding(4, 8)
    return Exon(size=10, coding=c)


def test_default_exon(default_exon: Exon) -> None:
    assert default_exon.size == 10

    # Test the default coding region
    assert not default_exon.coding
    assert default_exon.coding.start == 0


def test_draw_exon(center_coding: Exon) -> None:
    elements = center_coding.draw()

    # Get the non coding part of the exon
    non_coding = elements[0]

    # Check the height and width
    assert non_coding.width == center_coding.size
    assert non_coding.height == 10

    # The rectangle should start at an y offset of 0.25*y,
    # to leave space for the bigger coding region
    assert non_coding.x == 0
    assert non_coding.y == 5

    # Get the coding part of the exon
    coding = elements[1]

    # Check the height and width
    assert coding.width == center_coding.coding.size
    assert coding.height == 20

    # Check that the start and end are correct
    assert coding.x == 4
    assert coding.y == 0


def test_default_coding() -> None:
    c = Coding()
    assert c.start == 0
    assert c.end == 0
    assert c.size == 0

    # An empty coding region is false
    assert not c
