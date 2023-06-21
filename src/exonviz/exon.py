from typing import List
import svg


def draw_exon(exons: List[int], scale: int = 1, canvas_width: int = 1000) -> svg.SVG:
    elements = list()

    # Default positions
    y_position = 10
    height = 10
    exon_gap = 5

    # This x position will be updated
    x_position = 10
    start_frame = 0

    for exon in exons:
        # If we overflow the width, go to a new line
        if x_position + exon + height > canvas_width / scale:
            x_position = 10
            y_position += 2 * height

        end_frame = (start_frame + exon) % 3

        points: List[float] = list()

        top_left = (x_position, y_position)
        top_right = (x_position + exon, y_position)
        bottom_right = (x_position + exon, y_position + height)
        bottom_left = (x_position, y_position + height)
        # fmt: off
        if start_frame == 0 and end_frame == 0:
            points = [
                *top_left,
                *top_right,
                *bottom_right,
                *bottom_left
            ]
        elif start_frame == 0 and end_frame == 1:
            points = [
                *top_left,
                *top_right,
                x_position+exon-0.5*height, y_position + 0.5*height,
                *bottom_right,
                *bottom_left
            ]
        elif start_frame == 0 and end_frame == 2:
            points = [
                *top_left,
                *top_right,
                x_position + exon + 0.5*height, y_position + 0.5*height,
                *bottom_right,
                *bottom_left
            ]
        elif start_frame == 1 and end_frame == 0:
            points = [
                *top_left,
                *top_right,
                *bottom_right,
                *bottom_left,
                x_position - 0.5*height, y_position + 0.5*height,
            ]
        elif start_frame == 1 and end_frame == 1:
            points = [
                *top_left,
                *top_right,
                # Notch at the end of the exon
                x_position + exon - 0.5*height, y_position + 0.5*height,
                *bottom_right,
                *bottom_left,
                # Pointy bit at the start of the exon
                x_position - 0.5*height, y_position + 0.5*height,
            ]
        elif start_frame == 1 and end_frame == 2:
            points = [
                *top_left,
                *top_right,
                # Pointy bit at the end of the exon
                x_position + exon + 0.5*height, y_position + 0.5*height,
                *bottom_right,
                *bottom_left,
                x_position - 0.5*height, y_position + 0.5*height
            ]
        elif start_frame == 2 and end_frame == 0:
            points = [
                *top_left,
                *top_right,
                *bottom_right,
                *bottom_left,
                x_position + 0.5* height, y_position + 0.5*height
            ]
        elif start_frame == 2 and end_frame == 1:
            points = [
                *top_left,
                *top_right,
                # Pointy bit at the end of the exon
                x_position + exon-0.5*height, y_position + 0.5*height,
                *bottom_right,
                *bottom_left,
                # Indentation at the start of the exon
                x_position + 0.5*height, y_position + 0.5*height,
            ]
        elif start_frame == 2 and end_frame == 2:
            points = [
                *top_left,
                *top_right,
                # Pointy bit at the end of the exon
                x_position + exon + 0.5*height, y_position + 0.5*height,
                *bottom_right,
                *bottom_left,
                # Notch at the start of the exon
                x_position + 0.5* height, y_position + 0.5*height,
            ]
        #fmt: off

        x_position = x_position + exon + exon_gap

        # Scale the points
        points = [x*scale for x in points]

        elements.append(svg.Polygon(points = points, stroke='green', stroke_width=1)) # type: ignore

        start_frame = end_frame

    return svg.SVG(width=canvas_width, height=700, elements=elements)  # type: ignore
