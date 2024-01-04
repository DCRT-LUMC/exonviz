import pytest

from typing import List, Dict, cast

from exonviz.exon import (
    Coding,
    Exon,
    Variant,
    group_exons,
    exon_from_dict,
    element_xy,
    Element,
)
from GTGT.range import Range
from svg import Rect, Text, Polygon, Style


class TestExon:
    @pytest.fixture
    def default_exon(self) -> Exon:
        """
        ==========
        """
        return Exon(100)

    @pytest.fixture
    def center_coding(self) -> Exon:
        """
        ====||||==
        """
        c = Coding(40, 80)
        return Exon(size=100, coding=c)

    @pytest.fixture
    def all(self) -> Exon:
        """Create an exon with all possible features"""
        vars = [
            Variant(10, "A>T", "red"),
            Variant(30, "C>G", "blue"),
            Variant(80, "G>A", "purple"),
        ]
        c = Coding(start=40, end=80, start_phase=1, end_phase=2)
        return Exon(size=100, coding=c, variants=vars, name="Exon-1")

    def test_default_exon(self, default_exon: Exon) -> None:
        """
        GIVEN a default exon of size 100
        WHEN we don't change anythin
        """
        # THEN the size must be 100
        assert default_exon.size == 100

        # THEN the coding region should be false
        assert not default_exon.coding
        # THEN the coding region should start at 0
        assert default_exon.coding.start == 0

        # THEN the variants should be an empty list
        assert default_exon.variants == list()

        # THEN the default color should be set to DCRT blue
        assert default_exon.color == "#4C72B7"

    def test_boolean_exon_true(self) -> None:
        """
        GIVEN an exon of size one
        THEN the boolean value is True
        """
        e = Exon(size=1)
        assert e

    def test_boolean_exon_false(self) -> None:
        """
        GIVEN an exon of size zero
        THEN the boolean value is False
        """
        zero = Exon(size=0)
        assert not zero

    def test_draw_exon_non_coding(self, center_coding: Exon) -> None:
        """
        GIVEN an exon where the center region is coding
        WHEN we get the non-coding part of the drawing
        """
        elements = center_coding.draw(height=20)
        non_coding = cast(Rect, elements[0])

        # THEN the width of the non coding region should be the exon size
        assert non_coding.width == center_coding.size
        # THEN the height of the non coding region should be half the specified height
        assert non_coding.height == 10

        # THEN the drawing should start at position x=0
        assert non_coding.x == 0
        # THEN the drawing should start at 0.25*height, to leave space for the
        # bigger coding region
        assert non_coding.y == 5

    def test_draw_exon_coding(self, center_coding: Exon) -> None:
        """
        GIVEN an exon where the center region is coding
        WHEN we get the coding part of the drawing
        """
        elements = center_coding.draw(height=20)
        coding = cast(Rect, elements[1])

        # THEN the width of the coding drawing should be the size of the coding region
        assert coding.width == center_coding.coding.size
        # THEN the height of the drawing should be the specified height
        assert coding.height == 20

        # THEN the x position where the drawing start should be the start of
        # the coding region
        assert coding.x == 40
        # THEN the y position where the drawing starts should be zero
        assert coding.y == 0

        # THEN each element is drawn in the correct color
        for e in elements:
            if not isinstance(e, Style):
                assert e.fill == "#4C72B7"

    def test_draw_exon_offset_noncoding(self, default_exon: Exon) -> None:
        """
        GIVEN a default exon of size 100
        WHEN we draw this exon with an x and y offset
        """
        elements = default_exon.draw(x=11, y=13, height=20)
        # THEN there should only be a single element, since the exon is non coding
        assert len(elements) == 1

        non_coding = cast(Rect, elements[0])
        # THEN the drawing should start at the specified x offset
        assert non_coding.x == 11  #  offset

        # THEN the drawing should start at the specified y offset, plus a factor to
        # account for height
        assert non_coding.y == 13 + 5  #  offset + 0.25 * height

    def test_draw_exon_offset_coding(self, center_coding: Exon) -> None:
        """
        GIVEN an exon where the center is coding
        WHEN we draw this exon with an x and y offset
        """
        elements = center_coding.draw(x=11, y=13, height=20)

        # THEN the second element should be a drawing of the coding region
        coding = cast(Rect, elements[1])
        # THEN the x position should be the x offset, plus the start of the coding region
        assert coding.x == 11 + 40  #  offset
        # THEN the y positino should be the y offset
        assert coding.y == 13  #  offset

    def test_draw_full_coding(self) -> None:
        """
        GIVEN an exon that starts with a coding region
        WHEN we draw this exon
        THEN the x position of the drawing should be offset to leave space for
             the start cap
        """
        e = Exon(10, Coding(0, 10))
        elements = e.draw(height=20)

        # The first element is the non coding part of the drawing
        non_coding = cast(Rect, elements[0])
        # THEN the x position must be shifted to account for the start cap
        assert non_coding.x == 10  #  height * 0.5

        # The second element is the coding part of the drawing
        coding = cast(Rect, elements[1])
        # THEN the x position must be shifted to account for the start cap
        assert coding.x == 10

    def test_draw_full_coding_no_cap(self) -> None:
        """
        IF we have an exon that is fully coding, but the start phase is -1
        WHEN we draw this exon
        THEN the x position of the drawing should not be offset
        """
        e = Exon(10, Coding(0, 10, start_phase=-1))
        elements = e.draw(height=20)

        # We shift both the coding and non coding part of the exon
        non_coding = cast(Rect, elements[0])
        assert non_coding.x == 0

        coding = cast(Rect, elements[1])
        assert coding.x == 0

    def test_split_exon(self, all: Exon) -> None:
        """
        GIVEN an exon with all features enabled
        WHEN we split this exon in half
        """
        # Split the exon in half
        new = all.split(size=50, height=20)

        # THEN the new and old size should both be 50
        assert new.size == 50
        assert all.size == 50

        # THEN the coding region of the new Exon should start at 40
        assert new.coding.start == 40
        # THEN the coding region of the old exon should start at 0
        assert all.coding.start == 0

        # THEN the coding region of the new exon should end at 50
        assert new.coding.end == 50
        # THEN the coding region of the old exon should end at 30
        assert all.coding.end == 30

        # THEN the start phase of the new exon should be 1
        assert new.coding.start_phase == 1
        # THEN the end phase of new exon should be -1, to indicate the line break
        assert new.coding.end_phase == -1

        # THEN the start of the old exon should be -1, to indicate the line break
        assert all.coding.start_phase == -1
        # THEN the end of the old exon should be 2
        assert all.coding.end_phase == 2

        # THEN both exons should have the original name
        assert new.name == "Exon-1"
        assert all.name == "Exon-1"

        # THEN two of the variants should be in the new exon
        assert new.variants[0].position == 10
        assert new.variants[1].position == 30

        # THEN the position of the variant in the old exon should be updated
        assert all.variants[0].position == 30

    def test_take_full_exon(self, all: Exon) -> None:
        """
        GIVEN an exon with all features enabled
        WHEN we 'split' the exon but take the whole region
        """

        new = all.split(size=100, height=20)

        # THEN the new size should be the total size
        assert new.size == 100
        # THEN the coding start and end phase should be unchanged
        assert new.coding.start_phase == 1
        assert new.coding.end_phase == 2

        # THEN the old exon should be empty (false)
        assert not all

    def test_take_full_non_coding(self, default_exon: Exon) -> None:
        """
        GIVEN a default, non coding exon with size 100
        WHEN we 'split' the exon but take the whole region
        """
        new = default_exon.split(100, height=20)

        # THEN the size of the new exon should be unchanged
        assert new.size == 100

    def test_take_bigger_exon(self, all: Exon) -> None:
        """
        GIVEN an exon with all features enabled
        WHEN we 'split' the exon but take a region bigger than the exon itself
        """
        new = all.split(size=1000, height=20)

        # THEN the new size should be the original size
        assert new.size == 100
        # THEN the left over size should be zero
        assert all.size == 0

        # THEN the left over exon should be false
        assert not all

    def test_draw_name(self) -> None:
        """
        GIVEN an exon with a name
        WHEN the exon is drawn
        """
        e = Exon(size=100, name="Exon-1")

        elements = e.draw(height=10, x=11, y=23)

        assert len(elements) == 2

        # The name is the second element in the drawing
        text = cast(Text, elements[1])

        # THEN the name must be centered in the middle of the exon
        assert text.x == 11 + 50  # offset + half the exon size
        assert text.y == 23 + 5  # offset + half the height
        # THEN the name must be set
        assert text.text == "Exon-1"

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
    def test_exon_from_dict(self, d: Dict[str, str], exon: Exon) -> None:
        """
        GIVEN an exon dictionary
        WHEN the the dictionary is used to initialise the exon
        THEN the exon must match the expected exon
        """
        assert exon_from_dict(d) == exon


class TestCoding:
    def test_default_coding(self) -> None:
        c = Coding()
        assert c.start == 0
        assert c.end == 0
        assert c.size == 0

        # An empty coding region is false
        assert not c

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
    def test_split_coding(self, size: int, new: Range, old: Range) -> None:
        """
        GIVEN the coding region c
        WHEN it is split to size "size"
        THEN the new and old ranges should be as specified
        """
        c = Coding(40, 80, 1, 2)
        n = c.split(size=size)

        old_range = (c.start, c.end)
        new_range = (n.start, n.end)

        assert new_range == new
        assert old_range == old

    def test_split_coding_update_phase(self) -> None:
        """
        GIVEN a Coding region has a start and end phase
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

    def test_split_coding_phase_all(self) -> None:
        """
        GIVEN a Coding region has a start and end phase
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
    def test_exon_draw_size(self, exon: Exon, draw_size: int) -> None:
        """
        GIVEN an exon with a coding region
        WHEN it is drawn
        THEN it should be the specified size, based on the properties of
             the coding region
        """
        assert exon.draw_size(height=20) == draw_size


class TestVariant:
    @pytest.fixture
    def with_variant(self) -> Exon:
        vars = [Variant(10, "A>T", "red"), Variant(30, "C>G", "blue")]
        return Exon(size=100, variants=vars)

    def test_draw_variants(self, with_variant: Exon) -> None:
        """
        GIVEN an exon with two variants
        WHEN the exon is drawn
        """
        elements = with_variant.draw(height=20)
        assert len(elements) == 3

        # The first variant is the second element
        var1 = cast(Rect, elements[1])
        # THEN the x position of the variant must be the variant postion
        assert var1.x == 10
        # THEN the color of the variant must be set
        assert var1.fill == "red"

        # The second variant is the third element
        var2 = cast(Rect, elements[2])
        # THEN the x position of the variant must be the variant position
        assert var2.x == 30
        # THEN the color of the variant must be set
        assert var2.fill == "blue"

    def test_draw_variants_offset(self, with_variant: Exon) -> None:
        """
        GIVEN an exon with two variants
        WHEN the exon is drawn with an x offset
        """
        elements = with_variant.draw(height=20, x=11)
        var1 = cast(Rect, elements[1])

        # THEN the x position of the first variant must include
        # the offset
        assert var1.x == 10 + 11  #  variant.position + offset

    def test_draw_variant_coding(self) -> None:
        """
        GIVEN a coding exon with a variant in the coding region
        WHEN the exon is drawn
        """
        e = Exon(size=100, coding=Coding(0, 100), variants=[Variant(10, "A>T", "blue")])

        elements = e.draw()

        assert len(elements) == 5

        variant = cast(Rect, elements[4])
        # THEN the x position must have an offset for the start cap
        assert variant.x == 10 + 10  #  variant.position + start cap offset


class TestDrawing:
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
        self, exons: List[Exon], width: int, gap: int, page: List[List[Exon]]
    ) -> None:
        new_page = group_exons(exons, height=20, gap=gap, width=width)

        assert new_page == page

    elements = [
        # element, max_x, max_y
        (Rect(x=1, y=2, width=11.0, height=23), 12, 25),
        (Text(x=1, y=1, text="text"), 1, 1),
        (Polygon(points=[0, 0, 10, 5, 0, 15, 20, 25, 13, 17]), 20, 25),
        # Empty polygon
        (Polygon(fill="yellow"), 0, 0),
        # Style for exon number
        (Style(), 0, 0),
    ]

    @pytest.mark.parametrize("element, max_x, max_y", elements)
    def test_element_size(self, element: Element, max_x: float, max_y: float) -> None:
        """Determine the size of various SVG elements"""
        x, y = element_xy(element)

        assert x == max_x
        assert y == max_y
