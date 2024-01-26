from typing import List, Union, Tuple, Any, Dict, no_type_check
import svg
from .exon import element_xy, Element, Exon
import exonviz.exon
import textwrap


# Options for drawing the figure. Used to create the cli parser and default dict
_config = [
    ("width", 9999999, "Maximum width of the figure"),
    ("height", 20, "Exon height"),
    ("noncoding", False, "Show non coding regions"),
    ("gap", 5, "Gap between the exons"),
    ("color", "#4C72B7", "Color for the exons (e.g. 'purple')"),
    ("exonnumber", False, "Show exon number"),
    ("firstexon", 1, "The first exon to draw"),
    ("lastexon", 9999, "The last exon to draw"),
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


def draw_legend(
    exons: List[Exon], width: int, height: int, x: float = 0, y: float = 0
) -> List[Element]:
    """Draw the legend for variants in Exons"""
    elements: List[Element] = list()
    for exon in exons:
        for var in exon.variants:
            elements.append(
                svg.Rect(x=x, y=y, width=height, height=height, fill=var.color)
            )
            elements.append(
                svg.Text(x=x + height * 1.5, y=y + 0.75 * height, text=var.name)
            )
            y = y + height * 1.5
    return elements


@no_type_check
def draw_exons(
    exons: List[Exon],
    config: Dict[str, Any],
) -> svg.SVG:
    width = config["width"]
    height = config["height"]

    elements = exonviz.exon.draw_exons(
        exons, width=width, height=height, gap=config["gap"]
    )
    # How far down the page did we go?
    x, y = bottom_right(elements)
    elements += draw_legend(exons, x=height, y=y + height, height=height, width=width)

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

    return svg.SVG(width=canvas_width, height=canvas_height, elements=elements)
