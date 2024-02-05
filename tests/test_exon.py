import pytest

from typing import List, Dict, cast, Tuple
import copy

from exonviz.exon import (
    Coding,
    Exon,
    Variant,
    group_exons,
    _pick_split,
    exon_from_dict,
    element_xy,
    Element,
    draw_exons,
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
        return Exon(size=100, coding=c, variants=vars, name="Exon-1", color="yellow")

    class TestDrawingScale:
        """Test drawing an Exon whith non-default scale"""

        def test_draw_fully_noncoding_scale(self) -> None:
            """
            GIVEN a noncoding exon of size 100
            WHEN we draw the non coding region with scale 1.2
            THEN the drawing width should be 120
            """
            e = Exon(size=100)

            non_coding = e._draw_noncoding(scale=1.2)
            assert non_coding.x == 0
            assert non_coding.width == 120

        def test_draw_non_coding_start_coding(self) -> None:
            """
            GIVEN an exon where the start is coding
            WHEN we draw the non coding region with scale 1.2
            THEN the drawing should start 1 pixel into the coding region
            THEN the drawing should extend to the end of the exon
            """
            e = Exon(size=100, coding=Coding(start=0, end=20))

            non_coding = e._draw_noncoding(scale=1.2)
            assert non_coding.x == 23
            assert non_coding.width == 97

        def test_draw_non_coding_center_coding(self) -> None:
            """
            GIVEN an exon that is coding in the center
            WHEN we draw the non coding region with scale 1.2
            THEN it should be the width of the exon (since we will draw the coding
                 region on top of it)
            """
            e = Exon(size=100, coding=Coding(start=30, end=70))

            non_coding = e._draw_noncoding(scale=1.2)
            assert non_coding.width == 120

        def test_draw_non_coding_end_coding(self) -> None:
            """
            GIVEN an exon where the end is coding
            WHEN we draw the non coding region with scale 1.2
            THEN the drawing should start at the start of the exon
            THEN the drawing should extend 1 pixel into the coding region
            """
            e = Exon(size=100, coding=Coding(start=80, end=100))

            non_coding = e._draw_noncoding(scale=1.2)
            assert non_coding.x == 0
            assert non_coding.width == 97

        # fmt: off
        coding_region_frames = [
            # start phase, points
            (0, [
                0, 20,
                0, 0,
                120, 0,
                120, 20,
            ]),
            (1, [
                0, 20,
                0, 0,
                115, 0,
                120, 10,
                115, 20
            ]),
            (2, [
                0, 20,
                0, 0,
                115.0, 0,
                120.0, 0,
                115.0, 10.0,
                120.0, 20,
                115, 20
            ])
        ]
        # fmt: on
        @pytest.mark.parametrize("end_phase, points", coding_region_frames)
        def test_draw_coding(self, end_phase: int, points: List[int]) -> None:
            """
            Test drawing the coding region with scale 1.2
            Since the start_phase will be drawn the same, we only vary the end phase
            """
            c = Coding(0, 100, start_phase=0, end_phase=end_phase)
            E = Exon(size=100, coding=c, color="blue")
            coding = E._draw_coding(scale=1.2)

            assert coding == Polygon(points=list(points), fill="blue")

        def test_draw_variants_scale(self, all: Exon) -> None:
            """
            GIVEN an exon with variant
            WHEN the variants are drawn with a scale
            THEN the variant positions should be shifted to match
            """
            variants = all._draw_variants(scale=1.2)

            assert variants[0].x == 12
            assert variants[1].x == 36
            assert variants[2].x == 96

        def test_draw_name_scale(self, all: Exon) -> None:
            """
            GIVEN an exon with a name
            WHEN the name is drawn with a scale
            THEN the name position should be shifted to match the new center of the exon
            """
            text = all._draw_name(height=20, scale=1.2, x=11, y=23)
            # THEN the name must be centered in the middle of the exon
            assert text.x == 11 + 60  # offset + half the exon size
            assert text.y == 23 + 10  # offset + half the height

        def test_draw_coding_tiny_phase_zero(self) -> None:
            """
            GIVEN a tiny coding exon with start and end phase 0
            WHEN we draw it
            THEN there should be no error for the notch/arrow
            """
            E = Exon(size=1, coding=Coding(start=0, end=1, start_phase=0, end_phase=0))
            E._draw_coding(height=20, scale=1)

        def test_draw_coding_tiny_start_phase_one(self) -> None:
            """
            GIVEN a tiny coding exon with start phase 1, end phase 0
            WHEN we draw it
            THEN there should be no error
            """
            size = 5
            E = Exon(
                size=size, coding=Coding(start=0, end=size, start_phase=1, end_phase=0)
            )
            E._draw_coding(height=20, scale=1)

        def test_draw_coding_tiny_end_phase_one(self) -> None:
            """
            GIVEN a tiny coding exon with start phase 0, end phase 1
            WHEN we draw it
            THEN there should be no error
            """
            size = 5
            E = Exon(
                size=size, coding=Coding(start=0, end=size, start_phase=0, end_phase=1)
            )
            E._draw_coding(height=20, scale=1)

        def test_draw_coding_tiny_start_phase_one_end_phase_one(self) -> None:
            """
            GIVEN a tiny coding exon with start phase 1, end phase 1
            WHEN we draw it
            THEN there should be no error
            """
            size = 10
            E = Exon(
                size=size, coding=Coding(start=0, end=size, start_phase=1, end_phase=1)
            )
            E._draw_coding(height=20, scale=1)

    class TestSplits:
        """Test the code to determine legal splits"""

        # fmt: off
        splits = [
            # Exon that cannot be split, |>
            (Exon(5, Coding(end=5, end_phase=1)),
            [(5, 6)]),
            # Non coding exon, =====
            (Exon(10),
            [(0, 11)]),
            # Coding exon, phase 0-0, |||||
            (Exon(10, Coding(end=10)),
            [(0, 11), (10, 11)]),
            # Center is coding, phase 0-0, =|||=
            (Exon(40, Coding(10, 30)),
            [(0, 11), (10, 31), (30, 41)]),
            # Coding exon, phase 0-1, ||||>
            (Exon(15, Coding(end=15, end_phase=1)),
            [(0, 11), (15, 16)]),
            # Coding exon, phase 1-1, <|||<
            (Exon(15, Coding(end=15, start_phase=1, end_phase=1)),
            [(5, 11), (15, 16)]),
            # Coding exon, phase 2-2, >|||>
            (Exon(15, Coding(end=15, start_phase=2, end_phase=2)),
            [(5, 11), (15, 16)]),
            # Coding exon, phase 0-1, >||||
            (Exon(15, Coding(end=15, start_phase=1)),
            [(5, 16), (15, 16)]),
            # Center is coding, phase 1-0, =>||=
            (
                Exon(40, Coding(start=10, end=30, start_phase=1)),
                [(0, 11), (15, 31), (30, 41)]
            ),
            # Center is coding, phase 2-2, =<||>=
            (
                Exon(40, Coding(start=10, end=30, start_phase=2, end_phase=2)),
                [(0, 11), (15, 26), (30, 41)]
            )

        ]
        # fmt: on

        @pytest.mark.parametrize("exon, valid_splits", splits)
        def test_valid_splits_scale_one(
            self, exon: Exon, valid_splits: List[Range]
        ) -> None:
            """
            GIVEN an exon
            WHEN we call valid_splits with the specified height and scale for drawing
            THEN we should get a list of Ranges that contain the valid splits
                 (where the resulting Exons can be drawn)
            """
            height = 20
            scale = 1
            assert exon.valid_splits(height=height, scale=scale) == valid_splits

        # fmt: off
        splits = [
            # Exon that CAN be split, at scale=1.7, but not scale=1, |>
            (Exon(5, Coding(end=5, end_phase=1)),
            [(0, 3), (5, 6)]),
            # Exon that CANNOT be split, even at scale=1.7
            (Exon(3, Coding(end=3, end_phase=1)),
            [(3, 4)]),
            # Non coding exon, =====
            (Exon(12),
            [(0, 13)]),
            # Coding exon, phase 0-0, |||||
            (Exon(15, Coding(end=15)),
            [(0, 16), (15, 16)]),
            # Center is coding, phase 0-0, =|||=
            (Exon(47, Coding(15, 33)),
            [(0, 16), (15, 34), (33, 48)]),
            # Coding exon, phase 0-1, ||||>
            (Exon(15, Coding(end=15, end_phase=1)),
            [(0, 13), (15, 16)]),
            # Coding exon, phase 1-1, <|||<
            (Exon(15, Coding(end=15, start_phase=1, end_phase=1)),
            [(3, 13), (15, 16)]),
            # Coding exon, phase 2-2, >|||>
            (Exon(15, Coding(end=15, start_phase=2, end_phase=2)),
            [(3, 13), (15, 16)]),
            # Coding exon, phase 0-1, >||||
            (Exon(15, Coding(end=15, start_phase=1)),
            [(3, 16), (15, 16)]),
            # Center is coding, phase 1-0, =>||=
            (
                Exon(42, Coding(start=15, end=27, start_phase=1)),
                [(0, 16), (18, 28), (27, 43)]
            ),
            # Center is coding, phase 2-2, =<||>=
            (
                Exon(42, Coding(start=15, end=27, start_phase=2, end_phase=2)),
                [(0, 16), (18, 25), (27, 43)]
            )

        ]
        # fmt: on

        @pytest.mark.parametrize("exon, valid_splits", splits)
        def test_valid_splits_scale_one_point_seven(
            self, exon: Exon, valid_splits: List[Range]
        ) -> None:
            """
            GIVEN an exon
            WHEN we call valid_splits with the specified height and scale for drawing
            THEN we should get a list of Ranges that contain the valid splits
                 (where the resulting Exons can be drawn)
            """
            height = 20
            scale = 1.7
            assert exon.valid_splits(height=height, scale=scale) == valid_splits

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

    def test_exon_color(self) -> None:
        """
        GIVEN we create an exon with a set color
        THEN that color must be stored in the object
        """
        e = Exon(size=100, color="red")
        assert e.color == "red"

    def test_draw_exon_non_coding(self, all: Exon) -> None:
        """
        GIVEN a yellow exon
        WHEN we draw the exon
        THEN the color should be set
        """
        non_coding = all._draw_noncoding()
        assert non_coding.fill == "yellow"

    def test_draw_fully_non_coding(self) -> None:
        """
        GIVEN an exon without a coding region
        WHEN we draw the non coding region
        THEN it should be the width of the exon
        """
        e = Exon(size=100)

        non_coding = e._draw_noncoding()
        assert non_coding.width == 100

    def test_draw_non_coding_start_coding(self) -> None:
        """
        GIVEN an exon where the start is coding
        WHEN we draw the non coding region
        THEN the drawing should start 1 pixel into the coding region
        THEN the drawing should extend to the end of the exon
        """
        e = Exon(size=100, coding=Coding(start=0, end=20))

        non_coding = e._draw_noncoding(x=13, y=17)
        assert non_coding.x == 19 + 13
        assert non_coding.width == 81

    def test_draw_non_coding_center_coding(self) -> None:
        """
        GIVEN an exon that is coding in the center
        WHEN we draw the non coding region
        THEN it should be the width of the exon (since we will draw the coding
             region on top of it)
        """
        e = Exon(size=100, coding=Coding(start=30, end=70))

        non_coding = e._draw_noncoding()
        assert non_coding.width == 100

    def test_draw_non_coding_end_coding(self) -> None:
        """
        GIVEN an exon where the end is coding
        WHEN we draw the non coding region
        THEN the drawing should start at the start of the exon
        THEN the drawing should extend 1 pixel into the coding region
        """
        e = Exon(size=100, coding=Coding(start=80, end=100))

        non_coding = e._draw_noncoding()
        assert non_coding.x == 0
        assert non_coding.width == 81

    def test_draw_non_coding_fully_coding(self) -> None:
        """
        GIVEN an exon that is fully coding
        WHEN we draw the exon
        THEN we should not draw the non coding region
        """
        e = Exon(size=100, coding=Coding(start=0, end=100))
        elements = e.draw()
        assert len(elements) == 1

    def test_draw_exon_coding_color(self, center_coding: Exon) -> None:
        """
        GIVEN an exon where the center region is coding
        WHEN we draw the coding region
        THEN the color should match
        """
        coding = center_coding._draw_coding()
        assert coding.fill == "#4C72B7"

    # fmt: off
    coding_region_frames = [
        # Format is start_phase, end_phase, list of polygon points
        # (x and y are interleaved)
        # ||||
        (0, 0, [
            0, 20,
            0, 0,
            100, 0,
            100, 20,
        ]),
        # |||>
        (0, 1, [
            0, 20,
            0, 0,
            95, 0,
            100, 10,
            95, 20
        ]),
        # |||<
        (0, 2, [
            0, 20,
            0, 0,
            95, 0,
            100, 0,
            95, 10,
            100, 20,
            95, 20
        ]),
        # >|||
        (1, 0, [
            0, 20,
            5, 10,
            0, 0,
            100, 0,
            100, 20,
        ]),
        # >||>
        (1, 1, [
            0, 20,
            5, 10,
            0, 0,
            95, 0,
            100, 10,
            95, 20
        ]),
        # >||<
        (1, 2, [
            0, 20,
            5, 10,
            0, 0,
            95, 0,
            100, 0,
            95, 10,
            100, 20,
            95, 20
        ]),
        # <|||
        (2, 0, [
            5, 20,
            0, 10,
            5, 0,
            100, 0,
            100, 20,
        ]),
        # <||>
        (2, 1, [
            5, 20,
            0, 10,
            5, 0,
            95, 0,
            100, 10,
            95, 20
        ]),
        # <||<
        (2, 2, [
            5, 20,
            0, 10,
            5, 0,
            95, 0,
            100, 0,
            95, 10,
            100, 20,
            95, 20
        ])
    ]
    # fmt: on
    @pytest.mark.parametrize("start_phase, end_phase, points", coding_region_frames)
    def test_draw_coding(
        self, start_phase: int, end_phase: int, points: List[int]
    ) -> None:
        E = Exon(size=100, coding=Coding(0, 100, start_phase, end_phase), color="blue")
        coding = E._draw_coding()

        assert coding == Polygon(points=list(points), fill="blue")

    @pytest.mark.parametrize("start_phase, end_phase, points", coding_region_frames)
    def test_draw_coding_offset(
        self, start_phase: int, end_phase: int, points: List[int]
    ) -> None:
        E = Exon(size=100, coding=Coding(0, 100, start_phase, end_phase), color="blue")
        # Test setting x or y offset
        x_offset = 8
        y_offset = 13

        coding = E._draw_coding(x=x_offset, y=y_offset)

        # Shift the expected points (x and y are interleaved)
        shifted = list()
        for i, number in enumerate(points):
            if i % 2 == 0:
                shifted.append(number + x_offset)
            else:
                shifted.append(number + y_offset)

        assert coding == Polygon(points=list(shifted), fill="blue")

    def test_draw_coding_too_small(self) -> None:
        """
        GIVEN an exon with a (too) small coding region
        WHEN we try to draw it
        THEN we should get a ValueError
        """
        too_small = Exon(
            size=100, coding=Coding(start=0, end=9, start_phase=1, end_phase=1)
        )
        big_enough = Exon(
            size=100, coding=Coding(start=0, end=10, start_phase=1, end_phase=1)
        )

        with pytest.raises(ValueError):
            too_small._draw_coding()

        assert big_enough._draw_coding()

    def test_draw_exon_offset_noncoding(self, default_exon: Exon) -> None:
        """
        GIVEN a default exon of size 100
        WHEN we draw this exon with an x and y offset
        """
        elements = default_exon.draw(x=11, y=13)
        # THEN there should only be a single element, since the exon is non coding
        assert len(elements) == 1

        non_coding = cast(Rect, elements[0])
        # THEN the drawing should start at the specified x offset
        assert non_coding.x == 11  #  offset

        # THEN the drawing should start at the specified y offset, plus a factor to
        # account for height
        assert non_coding.y == 13 + 5  #  offset + 0.25 * height

    def test_split_exon(self, all: Exon) -> None:
        """
        GIVEN an exon with all features enabled
        WHEN we split this exon in half
        """
        # Split the exon in half
        new = all.split(size=50)

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
        # THEN the end phase of new exon should be 0, since we don't want to
        # draw a notch or arrow
        assert new.coding.end_phase == 0

        # THEN the start of the old exon should be 0, since we don't want to
        # draw a notch or arrow
        assert all.coding.start_phase == 0
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

        new = all.split(size=100)

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
        new = default_exon.split(100)

        # THEN the size of the new exon should be unchanged
        assert new.size == 100

    def test_take_bigger_exon(self, all: Exon) -> None:
        """
        GIVEN an exon with all features enabled
        WHEN we 'split' the exon but take a region bigger than the exon itself
        """
        new = all.split(size=1000)

        # THEN the new size should be the original size
        assert new.size == 100
        # THEN the left over size should be zero
        assert all.size == 0

        # THEN the left over exon should be false
        assert not all

    def test_split_exon_color(self, all: Exon) -> None:
        """
        GIVEN an exon with all features enabled
        WHEN we 'split' the exon in half
        THEN both exons should keep the color
        """
        new = all.split(size=1000)

        assert new.color == "yellow"
        assert all.color == "yellow"

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

    def test_remove_noncoding_noncoding_exon(self, default_exon: Exon) -> None:
        """
        GIVEN an exon that is non coding
        WHEN the non coding part is removed
        THEN the entire exon should be empty
        """
        default_exon.remove_noncoding()
        assert default_exon.size == 0

    def test_remove_noncoding_region(self, center_coding: Exon) -> None:
        """
        GIVEN an exon that is coding in the center
        WHEN the non coding part is removed
        THEN the entire exon should match the coding region
        """
        center_coding.remove_noncoding()
        assert center_coding.size == 40
        assert center_coding.coding.start == 0
        assert center_coding.coding.end == 40

    def test_remove_noncoding_variants(self) -> None:
        """
        GIVEN an exon with variants inside and outside the coding region
        WHEN the coding region is removed
        THEN the non-coding variants should be removed
        THEN the variant positions should be updated
        """
        c = Coding(40, 80)
        vars = [
            # Before coding
            Variant(10, "A>T", "red"),
            # In coding
            Variant(50, "C>T", "blue"),
            # After coding
            Variant(90, "A>T", "green"),
        ]
        e = Exon(size=100, coding=c, variants=vars)
        e.remove_noncoding()
        # Test that the non coding variants were removed
        # Test that the variant position has been updated from 50 to 10
        assert e.variants == [Variant(10, "C>T", "blue")]

    def test_group_exons_with_variants(self, all: Exon) -> None:
        """
        GIVEN a list of Exons
        WHEN we draw the exons
        THEN the list of exons should be unchanged
        """
        exons = [Exon(100), Exon(200)]
        before = copy.deepcopy(exons)
        # Draw the exons, and discard the drawing
        draw_exons(exons, height=20, gap=10, width=1_000_000)
        assert exons == before


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
        assert new.end_phase == 0

        assert old.start_phase == 0
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
        # Two exons don't fit on one row
        ([Exon(50), Exon(51)], 100, 0, [[Exon(50), Exon(50)], [Exon(1)]]),
        # Two exons that almost fit on one row
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
        new_page = group_exons(
            exons, height=20, scale=1, gap=gap, width=width, page_full=0
        )

        assert new_page == page

    invalid_splits: List[Tuple[List[Range], int]] = [
        # Splits, page_size
        # There are no valid splits
        (list(), 10),
        # the smallest valid split is smaller than the page
        ([(10, 20)], 4),
    ]

    @pytest.mark.parametrize("splits, page_size", invalid_splits)
    def test_pick_split_invalid(self, splits: List[Range], page_size: int) -> None:
        """
        GIVEN an empty list of valid splits
        WHEN we pick a split
        THEN we should get a ValueError
        """
        with pytest.raises(ValueError):
            _pick_split(splits, page_size)

    splits = [
        # Splits, page_size, expected
        # Only one split, and it fits on the page
        ([(0, 11)], 10, 10),
        # Two splits, and the second split fits
        ([(0, 5), (6, 19)], 15, 15),
        # Two splits, and only the first split fits
        ([(0, 5), (6, 19)], 4, 4),
        # Two splits, page is bigger than the first, but smaller than the
        # second split
        ([(0, 5), (16, 19)], 10, 4),
    ]

    @pytest.mark.parametrize("splits, page_size, expected", splits)
    def test_pick_split(
        self, splits: List[Range], page_size: int, expected: int
    ) -> None:
        assert _pick_split(splits, page_size) == expected

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

    exon_scale = [
        # Non coding exons can be drawn at any scale
        (Exon(100), 0),
        # A coding region with phase 0 can be drawn at any scale
        (Exon(100, Coding(start=0, end=1, start_phase=0, end_phase=0)), 0),
        # Drawing a single cap takes 5px, so the scale for a coding region of size 1 is 5
        (Exon(100, Coding(start=0, end=1, start_phase=1, end_phase=0)), 5),
        # Drawing two caps, we need a scale of 10
        (Exon(100, Coding(start=0, end=1, start_phase=1, end_phase=1)), 10),
    ]

    @pytest.mark.parametrize("exon, expected_scale", exon_scale)
    def test_determine_exon_scale(self, exon: Exon, expected_scale: float) -> None:
        """
        GIVEN an exon
        WHEN we determine the minimal scale it can be drawn self.assertTrue(
        THEN it has to match the expected scale
        """
        height = 20
        assert exon.min_scale(height=height) == expected_scale
        # Test that there is no value error
        exon.draw(height=height, scale=expected_scale)
