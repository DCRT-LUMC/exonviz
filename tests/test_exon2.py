import pytest

from exonviz.exon2 import Coding, Exon

@pytest.fixture
def default_exon() -> Exon:
    return Exon(10)

def test_default_exon(default_exon: Exon) -> None:
    assert default_exon.size == 10


def test_draw_exon(default_exon: Exon) -> None:
    elements = default_exon.draw()
    
    non_coding = elements[0]

    # The width must match the exon width
    assert non_coding.width == default_exon.size

    # The rectangle should start at an offset of 0.25*y,
    # to leave space for the bigger coding region
    assert non_coding.y == 5


def test_default_coding() -> None:
    c = Coding()
    assert c.start == 0
    assert c.end == 0

    # An empty coding region is false
    assert not c
