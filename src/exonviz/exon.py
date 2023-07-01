from typing import List, Union, Tuple
import svg
from dataclasses import dataclass, field


class Region:
    """A region has a start and end, which informs the size

    Subtracting two regions returns two regions, namelya region before and after the substracted
    region
    """

    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    @property
    def size(self) -> int:
        """The size property."""
        return abs(self.end - self.start)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Region):
            return NotImplemented
        return self.start == other.start and self.end == other.end

    def __bool__(self) -> bool:
        return self.size != 0

    def __sub__(self, other: "Region") -> Tuple["Region", "Region"]:
        """Subtracting a region from itself returns the remaining two regions.

        Namely before and after the subtracted regio
        """
        # If other does not overlap and lies before
        if other.end < self.start:
            return Region(self.start, self.start), self

        # If other does not overlap and lies after
        if other.start > self.end:
            return self, Region(self.end, self.end)

        # Determine what is left before the subtracted regio
        start = self.start
        if other.start < self.start:
            end = self.start
        else:
            end = other.start
        before = Region(start, end)

        # Determine what is left after the subtracted regio
        if other.end > self.end:
            start = self.end
        else:
            start = other.end
        end = self.end
        after = Region(start, end)

        return (before, after)

    def __repr__(self) -> str:
        return f"Region({self.start}, {self.end})"


class Exon(Region):
    def __init__(
        self,
        start: int,
        end: int,
        frame: int,
        coding: Region,
    ) -> None:
        super().__init__(start, end)
        self.frame = frame
        self.coding = coding

        self.non_coding = self._determine_non_coding()

    def __repr__(self) -> str:
        return f"Exon({self.start}, {self.end}, {self.frame}, {self.coding}, {self.non_coding})"

    def _determine_non_coding(self) -> Tuple[Region, Region]:
        """Determine the non-coding parts of the exon"""
        exon_region = Region(self.start, self.end)
        return exon_region - self.coding

    @property
    def end_frame(self) -> int:
        return (self.coding.size + self.frame) % 3


def shift(
    points: List[Union[float, int]], x_offset: int, y_offset: int
) -> List[Union[float, int]]:
    """Shift the x- and y position by the supplied offsets"""
    return [x + y_offset if i % 2 else x + x_offset for i, x in enumerate(points)]


def draw_exons(exons: List[Exon], scale: int = 1, canvas_width: int = 1000) -> svg.SVG:
    elements = list()

    # Default values needed for drawing
    height = 20
    exon_gap = 5

    # These values will be updated as we draw the figure
    x_position = 10
    y_position = 10

    for exon in exons:
        # If we overflow the width, go to a new line
        if x_position + exon.size + height > canvas_width / scale:
            x_position = 10
            y_position += 2 * height

        points = draw_exon(exon, height)

        # Shift the points
        points = shift(points, x_position, y_position)
        # Scale the points
        points = [x * scale for x in points]

        x_position = x_position + exon.size + exon_gap

        fill = "green" if exon.frame == exon.end_frame else "black"

        elements.append(
            svg.Polygon(
                points=points, stroke="green", fill=fill, stroke_width=1  # type: ignore
            )
        )

    return svg.SVG(width=canvas_width, height=700, elements=elements)  # type: ignore


def draw_exon(exon: Exon, height: int) -> List[float]:
    """Draw the specified exon by calculating all the points that have to be connected

    We draw clockwise, starting from the top left

    """
    # Fixed points for every exon
    top_left = (0, 0)
    top_right = (exon.size, 0)
    bottom_right = (exon.size, height)
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
        (exon.size+0.5*height, 0.5*height), #  point
        (exon.size-0.5*height, 0.5*height), #  notch

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
