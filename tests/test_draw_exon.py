from typing import List

from exonviz.exon import draw_exon
from exonviz.exon import shift
from exonviz.exon import Exon


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
    exon = Exon("exon-1", 21, 0)
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

    assert draw_exon(exon, height) == target


def test_end_frame_1() -> None:
    """Looks like this: ||||>"""
    exon = Exon("exon-1", 22, 0)
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

    assert draw_exon(exon, height) == target


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
