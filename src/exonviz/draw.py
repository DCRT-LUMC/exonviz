from typing import List, Union, Tuple, Any, Dict, no_type_check
import svg
from .exon import element_xy, Element, Exon
import exonviz.exon
import math
import textwrap


# Options for drawing the figure. Used to create the cli parser and default dict
_config = [
    ("width", math.inf, "Maximum width of the figure"),
    ("height", 20, "Exon height"),
    ("noncoding", False, "Show non coding regions"),
    ("gap", 5, "Gap between the exons"),
    ("color", "#4C72B7", "Color for the exons (e.g. 'purple')"),
    ("exonnumber", False, "Show exon number"),
    ("firstexon", 1, "The first exon to draw"),
    ("lastexon", math.inf, "The last exon to draw"),
]

config = {key: value for key, value, description in _config}


def shift(
    points: List[Union[float, int]], x_offset: float, y_offset: float
) -> List[Union[float, int]]:
    """Shift the x- and y position by the supplied offsets"""
    return [x + y_offset if i % 2 else x + x_offset for i, x in enumerate(points)]


def bottom_right(elements: List[Element]) -> Tuple[int, int]:
    x = 0
    y = 0
    for e in elements:
        e_x, e_y = element_xy(e)
        x = max(x, e_x)
        y = max(y, e_y)
    return x, y


@no_type_check
def draw_exons(
    exons: List[Exon],
    config: Dict[str, Any],
) -> svg.SVG:

    elements = exonviz.exon.draw_exons(exons, width=config["width"], height=config["height"], gap=config["gap"])

    # Set style for exonnumber, even if we don't need it
    elements.append(
        svg.Style(
            text=textwrap.dedent(
                f"""
            .exonnr {{ text-anchor: middle; dominant-baseline: central; font: {config["height"]/2}px sans-serif; fill: white;}}
            """
            ),
        )
    )
    # The maximum width we have reached for this picture
    canvas_width, canvas_height = bottom_right(elements)

    return svg.SVG(
        width = canvas_width,
        height = canvas_height,
        elements = elements
    )
