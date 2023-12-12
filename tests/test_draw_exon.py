from typing import List

from exonviz.draw import shift


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
