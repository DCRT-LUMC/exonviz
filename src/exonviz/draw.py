from typing import List, Union, Tuple, Any, Dict, no_type_check
import svg
from .exon import element_xy, Element, Exon, Variant
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
    exons: List[Exon], width: int, height: int, y: float = 0
) -> List[Element]:
    """Draw the legend for variants in Exons"""

    def guess_width(name: str, height: int) -> float:
        """Guess how wide the legend for this variant will be"""
        letter_width = 10
        return height * 1.5 + len(name) * letter_width

    def get_legend_keys(exons: List[Exon]) -> List[Tuple[str, str]]:
        """Extract the legend keys from the Exon Variants"""
        keys = list()
        for exon in exons:
            for variant in exon.variants:
                key = (variant.color, variant.name)
                if key not in keys:
                    keys.append(key)
        return keys

    elements: List[Element] = list()

    # The x-position where we will draw the first entry of the legend
    x_pos: float = height
    for color, name in get_legend_keys(exons):
        entry_width = guess_width(name, height)
        if entry_width > width:
            raise RuntimeError(f"Variant name {name} too wide to render")
        elif x_pos + entry_width > width:
            y = y + height * 1.5
            x_pos = height
        elements.append(svg.Rect(x=x_pos, y=y, width=height, height=height, fill=color))
        elements.append(
            svg.Text(
                x=x_pos + height * 1.5, y=y + 0.5 * height, text=name, class_=["legend"]
            )
        )
        x_pos += 2 * height + entry_width

    # Add styling for the legend
    elements.append(
        svg.Style(
            text=textwrap.dedent(
                f"""
                .legend {{ font: {height*0.8}px sans-serif; fill: black; dominant-baseline: central; }}
                """
            )
        )
    )

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
    elements += draw_legend(exons, y=y + height, height=height, width=width)

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
