from typing import List, Union, Tuple, Any, Dict, no_type_check
import svg
from .exon import element_xy, Element, Exon, Variant
import exonviz.exon
import textwrap
import math


# Options for drawing the figure. Used to create the cli parser and default dict
_config = [
    ("width", 9999999, "Maximum width of the figure"),
    ("height", 20, "Exon height"),
    ("scale", 1.0, "Scale (pixels per bp)"),
    ("noncoding", False, "Show non coding regions"),
    ("gap", 5, "Gap between the exons"),
    ("color", "#4C72B7", "Color for the exons (e.g. 'purple')"),
    ("exonnumber", False, "Show exon number"),
    ("firstexon", 1, "The first exon to draw"),
    ("lastexon", 9999, "The last exon to draw"),
    (
        "variantcolors",
        ["#BA1C30", "#DB6917", "#EBCE2B", "#702C8C", "#C0BD7F"],
        "List of variant colors to cycle through",
    ),
]

config = {key: value for key, value, description in _config}


def shift(
    points: List[Union[float, int]], x_offset: float, y_offset: float
) -> List[Union[float, int]]:
    """Shift the x- and y position by the supplied offsets"""
    return [x + y_offset if i % 2 else x + x_offset for i, x in enumerate(points)]


def bottom_right(elements: List[Element], height: int) -> Tuple[int, int]:
    """
    Determine the bottom right x and y position for a list of svg Elements
    """
    x = 0
    y = 0
    for e in elements:
        e_x, e_y = element_xy(e)
        # The text from the legend is a special case, since the size of the
        # letters depends on the height
        if isinstance(e, svg.Text):
            text = e.text if e.text else ""
            e_x += math.ceil(_guess_width(text, height))
        x = max(x, e_x)
        y = max(y, e_y)
    return x, y


def _guess_width(name: str, height: int) -> float:
    """Guess how wide the legend for this variant will be"""
    letter_width = height / 2
    return height * 1.5 + len(name) * letter_width


def draw_legend(
    exons: List[Exon], width: int, height: int, y: float = 0
) -> List[Element]:
    """Draw the legend for variants in Exons"""

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
        entry_width = _guess_width(name, height)
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
    scale = config["scale"]
    gap = config["gap"]

    if width < 1:
        raise ValueError("width should at least be 1")
    if height < 1:
        raise ValueError("height should at least be 1")
    if scale <= 0:
        raise ValueError("scale should be greater than zero")
    if gap < 0:
        raise ValueError("gap should at least be zero")

    # Determine the smallest scale every exon can be drawn at
    min_scale = max((e.min_scale(height) for e in exons))
    if scale < min_scale:
        msg = f"Transcript must be drawn at scale {min_scale} or larger"
        raise ValueError(msg)

    elements = exonviz.exon.draw_exons(
        exons, width=width, height=height, scale=scale, gap=gap
    )
    # How far down the page did we go?
    x, y = bottom_right(elements, height)
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
    canvas_width, canvas_height = bottom_right(elements, height)

    return svg.SVG(width=canvas_width, height=canvas_height, elements=elements)
