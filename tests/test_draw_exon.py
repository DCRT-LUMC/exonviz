from typing import List

from exonviz.draw import draw_coding, draw_non_coding
from exonviz.draw import shift
from exonviz.exon import Exon, Region


# Describe the expected output for a given start and end frame
# fmt: off
targets = {
    "frame0_0": [
        0, 0,
        21, 0,
        21, 10,
        0, 10,
        0, 0
    ],
    "frame0_1": [
        0, 0,
        22, 0,
        17, 5,
        22, 10,
        0, 10,
        0, 0
    ]
}
# fmt: on


def test_in_frame() -> None:
    """ "This draws a square, like this: |||||"""
    exon = Exon(0, 21, frame=0, coding=Region(0, 21))
    height = 10

    # fmt: off
    target = [
        0, 0,
        21, 0,
        21, 10,
        0, 10,
        0, 0
    ]
    # fmt: on

    assert draw_coding(exon, height) == target


def test_end_frame_1() -> None:
    """Looks like this: ||||>"""
    exon = Exon(start=0, end=22, frame=0, coding=Region(0, 22))
    height = 10

    # fmt: off
    target = [
        0, 0,
        22, 0,
        27, 5,
        22, 10,
        0, 10,
        0, 0
    ]
    # fmt: on

    assert draw_coding(exon, height) == target


def test_no_shift() -> None:
    points: List[float] = [0, 0, 0, 0, 10]
    assert shift(points, 0, 0) == [0, 0, 0, 0, 10]


def test_shift_x_only() -> None:
    """Shift the X by 10"""
    points: List[float] = [0, 0, 0, 10]
    assert shift(points, 10, 0) == [10, 0, 10, 10]


def test_shift_x_y() -> None:
    """Shift both X and Y by 10"""
    points: List[float] = [0, 0, 0, 10]
    assert shift(points, 10, 8) == [10, 8, 10, 18]


def test_draw_non_coding() -> None:
    R = Region(0, 12)
    height = 10

    # fmt: off
    expected = [
        12, 2.5,
        12, 7.5,
        0, 7.5,
        0, 2.5,
        12, 2.5,
    ]
    # fmt: on
    assert draw_non_coding(R, height=height) == expected


def test_draw_non_coding_empty_region() -> None:
    R = Region(0, 0)
    height = 10

    assert draw_non_coding(R, height) == list()
