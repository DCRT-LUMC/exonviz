from typing import List, Union, Tuple, Optional
import svg
from .exon import Exon, Region
import math


def shift(
    points: List[Union[float, int]], x_offset: float, y_offset: float
) -> List[Union[float, int]]:
    """Shift the x- and y position by the supplied offsets"""
    return [x + y_offset if i % 2 else x + x_offset for i, x in enumerate(points)]


def draw_exons(
    exons: List[Exon],
    reverse: bool,
    scale: int = 1,
    max_width: float = 1024,
    height: Optional[float] = None,
    non_coding: bool = False,
    gap_size: Optional[int] = None,
) -> svg.SVG:
    elements = list()

    # The maximum width we have reached for this picture
    canvas_width: float = 0
    # Default values needed for drawing
    if non_coding:
        total_width = min(sum(exon.size for exon in exons), max_width)
    else:
        total_width = min(sum(exon.coding.size for exon in exons), max_width)

    if height is None:
        height = min(0.1 * total_width, 20)

    if gap_size is None:
        exon_gap = min(height / 4, 5)
    else:
        exon_gap = gap_size

    # These values will be updated as we draw the figure
    x_position: float = 10
    y_position: float = 0

    for exon in exons:
        # The visual size of the exon depends on wether or not we draw the non-coding
        # regions
        if non_coding:
            exon_size = exon.size
        else:
            exon_size = exon.coding.size

        # If we overflow the width, go to a new line
        if x_position + exon_size + height > max_width / scale:
            # If we are still at the start position for x, we dont start a new line
            # (this happens when the exon we want to draw is larger than max_width)
            if x_position == 10:
                continue
            x_position = 10
            y_position += 2 * height

        for section in draw_exon(exon, height, reverse, non_coding):
            # Don't draw the empty sections
            if not section:
                continue
            # Shift the points
            section = shift(section, x_position, y_position)

            # Scale the points
            section = [x * scale for x in section]

            # fill = "green" if exon.frame == exon.end_frame else "black"
            fill = "#4C72B7"

            elements.append(
                svg.Polygon(
                    points=section, stroke="red", fill=fill, stroke_width=0  # type: ignore
                )
            )
        x_position = x_position + exon_size + exon_gap
        canvas_width = max(x_position, canvas_width)

    return svg.SVG(width=canvas_width, height=y_position + height, elements=elements)  # type: ignore


def draw_non_coding(region: Region, height: float) -> List[float]:
    """Draw a non coding region"""
    if not region:
        return list()

    top_left = (0, 0.25 * height)
    top_right = (region.size, 0.25 * height)
    bottom_right = (region.size, 0.75 * height)
    bottom_left = (0, 0.75 * height)

    # We need to end top-right, to draw the next thing
    return [*top_right, *bottom_right, *bottom_left, *top_left, *top_right]


def draw_coding(exon: Exon, height: float) -> List[float]:
    # Fixed points for every exon
    top_left = (0, 0)
    top_right = (exon.coding.size, 0)
    bottom_right = (exon.coding.size, height)
    bottom_left = (0, height)

    # Pre-calculate the ends for the 6 possible frames
    # Use the frame to fetch the index
    # fmt: off
    left_end = [
        tuple(), #  Straigt line, we don't need to draw anything
        (0.5*height, 0.5*height), #  point
        (-0.5*height, 0.5*height), #  notch
    ]

    right_end = [
        tuple(), #  straight line, we don't need to draw anything
        (exon.coding.size+0.5*height, 0.5*height), #  point
        (exon.coding.size-0.5*height, 0.5*height), #  notch

    ]
    # fmt: on

    return [
        *top_left,
        *top_right,
        *right_end[exon.end_frame],
        *bottom_right,
        *bottom_left,
        *left_end[exon.frame],
        *top_left,
    ]


Section = List[float]


def draw_exon(
    exon: Exon, height: float, reverse: bool, non_coding: bool
) -> Tuple[Section, Section, Section]:
    """Draw the specified exon by calculating all the points that have to be connected

    We draw clockwise, starting from the top left

    """

    # Get the non coding regions
    if non_coding:
        before_coding, after_coding = exon.non_coding
    else:
        before_coding = after_coding = Region(0, 0)

    x_offset: float

    if not reverse:
        before = draw_non_coding(before_coding, height)
        coding = shift(
            draw_coding(exon, height), x_offset=before_coding.size, y_offset=0
        )

        # Depending on the end of the coding part (notch or point), we have to shift the
        # non-coding part so it matches
        x_offset = before_coding.size + exon.coding.size
        if exon.end_frame == 1:
            x_offset += 0.5 * height
        elif exon.end_frame == 2:
            x_offset -= 0.5 * height

        after = shift(
            draw_non_coding(after_coding, height), x_offset=x_offset, y_offset=0
        )

        # We need to draw the coding region last, so it overlaps properly
    else:
        after = draw_non_coding(after_coding, height)
        coding = shift(
            draw_coding(exon, height), x_offset=after_coding.size, y_offset=0
        )

        # Depending on the end of the coding part (notch or point), we have to shift the
        # non-coding part so it matches
        x_offset = after_coding.size + exon.coding.size
        if exon.end_frame == 1:
            x_offset += 0.5 * height
        elif exon.end_frame == 2:
            x_offset -= 0.5 * height

        before = shift(
            draw_non_coding(before_coding, height), x_offset=x_offset, y_offset=0
        )

    if exon.coding:
        return (before, after, coding)
    else:
        return (before, after, list())
