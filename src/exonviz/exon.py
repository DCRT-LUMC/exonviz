from typing import List, Union
import svg
from dataclasses import dataclass, field


@dataclass
class Exon:
    name: str
    size: int
    start_frame: int
    end_frame: int = field(init=False)

    def __post_init__(self) -> None:
        self.end_frame = (self.start_frame + self.size) % 3


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

        fill = "green" if exon.start_frame == exon.end_frame else "black"

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
        *left_end[exon.start_frame],
        *top_left,
    ]
