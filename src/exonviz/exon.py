from typing import List, Union
import svg


def shift(points: List[Union[float,int]], x_offset: int, y_offset:int) -> List[Union[float,int]]:
    """ Shift the positions, modifying in place"""
    return [x+y_offset if i%2 else x+x_offset for i,x in enumerate(points)]


def draw_exons(exons: List[int], scale: int = 1, canvas_width: int = 1000) -> svg.SVG:
    elements = list()

    # Default positions
    y_position = 10
    height = 20
    exon_gap = 5

    # This x position will be updated
    x_position = 10
    start_frame = 0

    for exon in exons:
        # If we overflow the width, go to a new line
        if x_position + exon + height > canvas_width / scale:
            x_position = 10
            y_position += 2 * height

        points = draw_exon(height, exon, start_frame)

        # Shift the points
        points = shift(points, x_position, y_position)
        # Scale the points
        points = [x*scale for x in points]

        x_position = x_position + exon + exon_gap
        end_frame = (start_frame + exon) % 3

        fill = "green" if start_frame == end_frame else "black"
        elements.append(svg.Polygon(points = points, stroke='green', fill=fill, stroke_width=1)) # type: ignore

        start_frame = end_frame

    return svg.SVG(width=canvas_width, height=700, elements=elements)  # type: ignore


def draw_exon(height: int, exon: int, start_frame: int) -> List[float]:
    end_frame = (start_frame + exon) % 3

    points: List[float] = list()

    top_left = (0, 0)
    top_right = (exon, 0)
    bottom_right = (exon, height)
    bottom_left = (0, height)
    # fmt: off
    if start_frame == 0 and end_frame == 0:
        points = [
            *top_left,
            *top_right,
            *bottom_right,
            *bottom_left,
            *top_left
        ]
    elif start_frame == 0 and end_frame == 1:
        points = [
            *top_left,
            *top_right,
            exon-0.5*height, 0.5*height,
            *bottom_right,
            *bottom_left,
            *top_left
        ]
    elif start_frame == 0 and end_frame == 2:
        points = [
            *top_left,
            *top_right,
            exon + 0.5*height, 0.5*height,
            *bottom_right,
            *bottom_left
        ]
    elif start_frame == 1 and end_frame == 0:
        points = [
            *top_left,
            *top_right,
            *bottom_right,
            *bottom_left,
            -0.5*height, 0.5*height,
        ]
    elif start_frame == 1 and end_frame == 1:
        points = [
            *top_left,
            *top_right,
            # Notch at the end of the exon
            exon - 0.5*height, 0.5*height,
            *bottom_right,
            *bottom_left,
            # Pointy bit at the start of the exon
            -0.5*height, 0.5*height,
        ]
    elif start_frame == 1 and end_frame == 2:
        points = [
            *top_left,
            *top_right,
            # Pointy bit at the end of the exon
            exon + 0.5*height, 0.5*height,
            *bottom_right,
            *bottom_left,
            -0.5*height, 0.5*height
        ]
    elif start_frame == 2 and end_frame == 0:
        points = [
            *top_left,
            *top_right,
            *bottom_right,
            *bottom_left,
            0.5*height, 0.5*height
        ]
    elif start_frame == 2 and end_frame == 1:
        points = [
            *top_left,
            *top_right,
            # Pointy bit at the end of the exon
            exon-0.5*height, 0.5*height,
            *bottom_right,
            *bottom_left,
            # Indentation at the start of the exon
            0.5*height, 0.5*height,
        ]
    elif start_frame == 2 and end_frame == 2:
        points = [
            *top_left,
            *top_right,
            # Pointy bit at the end of the exon
            exon + 0.5*height, 0.5*height,
            *bottom_right,
            *bottom_left,
            # Notch at the start of the exon
            0.5* height, 0.5*height,
        ]
    #fmt: off

    return points
