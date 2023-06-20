import math
import sys
from typing import List
import svg


def draw_exon(exons: List[int], scale:int = 10) -> svg.SVG:
    elements = list()

    # Default positions
    y_position = 10
    height = 10
    exon_gap = 5

    # This x position will be updated
    x_position = 10
    start_frame = 0

    for exon in exons:

        end_frame = (start_frame + exon) % 3

        if start_frame == 0 and end_frame == 0:
            points = [
                x_position, y_position, #  topleft
                x_position+exon, y_position, #  topright
                x_position+exon, y_position + height, #  bottom right
                x_position, y_position + height  # bottomleft
            ]
        elif start_frame == 0 and end_frame == 2:
            points = [ 
                x_position, y_position,
                x_position+exon, y_position,
                x_position+exon-0.5*height, y_position + 0.5*height,
                x_position+exon, y_position+height,
                x_position, y_position + height,
            ]
        else:
            print(f"start_frame = {start_frame}, end_frame = {end_frame}", file=sys.stderr)
            continue
            raise NotImplementedError()

        x_position = x_position + exon + exon_gap

        # Scale the points
        points = [x*scale for x in points]

        elements.append(svg.Polygon(points = points, stroke='green', stroke_width=1))

        start_frame = end_frame

    return svg.SVG(width=1000, height=700, elements=elements)
            
