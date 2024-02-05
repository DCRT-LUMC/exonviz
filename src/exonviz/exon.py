from dataclasses import dataclass
from typing import (
    Any,
    List,
    Optional,
    Sequence,
    Dict,
    Tuple,
    no_type_check,
    Union,
    cast,
)
import copy
import math

import sys

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

from _io import TextIOWrapper
from svg import Rect, Polygon, Text, Style

from GTGT.range import intersect, Range

import logging

logging.basicConfig(level="DEBUG")
log = logging.getLogger(__name__)
Element: TypeAlias = Union[Rect, Polygon, Text, Style]


@dataclass()
class Coding:
    start: int = 0
    end: int = 0
    start_phase: int = 0
    end_phase: int = 0

    def __bool__(self) -> bool:
        return self.end > self.start

    @property
    def size(self) -> int:
        return self.end - self.start

    def split(self, size: int) -> "Coding":
        old = (self.start, self.end)
        new = intersect(old, (0, size))
        # Determine the start and end postions for the new Coding region
        if not new:
            new_start = 0
            new_end = 0
        elif len(new) == 1:
            new_start, new_end = new[0]
        else:
            raise RuntimeError
        # Update the start/end of self
        self.start = max(0, self.start - size)
        self.end = max(0, self.end - size)

        # If the old Coding region is empty
        if not self.end:
            # Lift over the old start/end phase to the new
            new_start_phase = self.start_phase
            new_end_phase = self.end_phase
            # Set the old start/end phase to zero
            self.start_phase = 0
            self.end_phase = 0
        # If the old Coding region is not empty, we set the phase of the
        # split region to -1 on either size, so no cap is drawn
        else:
            new_start_phase = self.start_phase
            new_end_phase = 0
            self.start_phase = 0

        return Coding(
            start=new_start,
            end=new_end,
            start_phase=new_start_phase,
            end_phase=new_end_phase,
        )


@dataclass()
class Variant:
    position: int
    name: str
    color: str

    def tsv(self, sep: str = "\t") -> str:
        """Dump an exon as tsv"""
        records = [
            self.position,
            self.name,
            self.color,
        ]
        return sep.join(map(str, records))


class Exon:
    def __init__(
        self,
        size: int,
        coding: Optional[Coding] = None,
        variants: Optional[Sequence[Variant]] = None,
        name: str = "",
        color: str = "#4C72B7",
    ) -> None:
        self.size = size
        self.name = name
        self.color = color

        if coding is None:
            self.coding = Coding()
        else:
            self.coding = coding

        if variants is None:
            self.variants: Sequence[Variant] = list()
        else:
            self.variants = variants

    def __bool__(self) -> bool:
        return self.size != 0

    def __repr__(self) -> str:
        return (
            f"Exon(size={self.size}, "
            f"coding={self.coding}, "
            f"variants={self.variants}, "
            f"name={self.name}, "
            f"color={self.color})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Exon):
            raise NotImplementedError
        return all(
            (
                self.size == other.size,
                self.name == other.name,
                self.color == other.color,
                self.coding == other.coding,
                self.variants == other.variants,
            )
        )

    def draw_size(self, scale: float) -> float:
        """Determine how big the Exon is when drawn"""
        return self.size * scale

    def remove_noncoding(self) -> None:
        """Update an exon to remove the non coding region"""
        if not self.coding:
            self.size = 0

        # The new size is the coding size
        self.size = self.coding.size

        # Remove variants outside coding region
        self.variants = [
            v
            for v in self.variants
            if v.position >= self.coding.start and v.position < self.coding.end
        ]
        # Update variant positions
        for v in self.variants:
            v.position -= self.coding.start

        # The coding region starts at 0, and ends at coding size
        self.coding.end = self.coding.end - self.coding.start
        self.coding.start = 0

    def draw(
        self, height: float = 20, scale: float = 1, x: float = 0, y: float = 0
    ) -> List[Element]:
        """Draw the Exon, in SVG format

        Returns a list of SVG elements
        """
        elements: List[Any] = list()

        # If the coding size is not the entire exon
        if self.coding.size != self.size:
            elements.append(self._draw_noncoding(height=height, scale=scale, x=x, y=y))
        if self.coding:
            elements.append(self._draw_coding(height=height, scale=scale, x=x, y=y))
        elements += self._draw_variants(height=height, scale=scale, x=x, y=y)
        if self.name:
            elements.append(self._draw_name(height=height, scale=scale, x=x, y=y))

        return elements

    def min_scale(self, height: float = 20) -> float:
        """Determine the minimum scale this exon can be drawn at"""
        # If there is no coding region, the exon can be drawn at any scale
        if not self.coding:
            return 0.0

        # Total caps we need to draw. If the exon is too small, we raise an error
        total_caps: float = 0
        if self.coding.start_phase != 0:
            total_caps += height * 0.25
        if self.coding.end_phase != 0:
            total_caps += height * 0.25

        scale = total_caps / self.coding.size
        return scale

    def _draw_noncoding(
        self, height: float = 20, scale: float = 1, x: float = 0, y: float = 0
    ) -> Rect:
        """
        Draw the non coding region of the Exon

        If the coding region only overlaps the start or end of the exon, we
        have to draw the non-coding region smaller, so it doesn't stick
        out beyond the arrow/notches
        """
        # Constant values for the drawing
        draw_height = height * 0.5
        y_pos = y + height * 0.25

        # By default, we draw the non coding region the full size of the exon.
        x_pos = x
        width = self.size * scale

        # If only the start of the exon is coding
        start_coding = (
            self.coding and self.coding.start == 0 and self.coding.end < self.size
        )
        if start_coding:
            x_pos = x + (self.coding.end * scale - 1)
            width = (self.size - self.coding.size) * scale + 1

        # If only the end of the exon is coding
        end_coding = (
            self.coding and self.coding.start > 0 and self.coding.end == self.size
        )
        if end_coding:
            x_pos = x
            width = (self.size - self.coding.size) * scale + 1

        return Rect(x=x_pos, y=y_pos, width=width, height=draw_height, fill=self.color)

    def _draw_coding(
        self, height: float = 20, scale: float = 1, x: float = 0, y: float = 0
    ) -> Polygon:
        # Determine x-coordinate for the coding region start
        cx = x + self.coding.start * scale

        # Calculate the size of the arrow/notch
        cap_size = height * 0.25

        # Total size we need to draw.
        size = self.coding.size * scale

        if scale < self.min_scale(height):
            raise ValueError(f"Coding region {self.coding} is too small to draw")

        # fmt: off
        start: List[List[float]] = [
            [ # Square
                cx, y + height,
                cx, y
            ],
            [ # Notch
                cx, y + height,
                cx + cap_size, y + height/2,
                cx, y
            ],
            [ # Arrow
                cx + cap_size, y + height,
                cx, y + height/2,
                cx + cap_size, y
            ]
        ]

        end: List[List[float]] = [
            [ # Square
                cx + size, y,
                cx + size, y + height,
            ],
            [ # Arrow
                cx + size - cap_size, y,
                cx + size, y + height/2,
                cx + size - cap_size, y + height
            ],
            [ # Notch
                cx + size - cap_size, y,
                cx + size, y,
                cx + size - cap_size, y + height/2,
                cx + size, y + height,
                cx + size - cap_size, y + height,
            ]
        ]
        # fmt: on
        start_phase = self.coding.start_phase
        end_phase = self.coding.end_phase
        return Polygon(
            points=list(start[start_phase] + end[end_phase]), fill=self.color
        )

    def _draw_variants(
        self, height: float = 20, scale: float = 1, x: float = 0, y: float = 0
    ) -> Sequence[Rect]:
        elements = list()
        for variant in self.variants:
            elements.append(
                Rect(
                    x=x + variant.position * scale,
                    y=y,
                    width=height / 20,
                    height=height,
                    fill=variant.color,
                )
            )
        return elements

    def _draw_name(
        self, height: float = 20, scale: float = 1, x: float = 0, y: float = 0
    ) -> Text:
        return Text(
            x=x + (self.size * scale / 2),
            y=y + 0.5 * height,
            class_=["exonnr"],
            text=self.name,
        )

    def split(self, size: int) -> "Exon":
        """Split an new exon of size off from self

        Not that this does not take the drawn_size() into account
        """
        # Size of the new exon
        n_size = min(self.size, size)
        self.size = max(0, self.size - size)

        # Update the coding region
        new_coding = self.coding.split(int(size))

        # Update the name
        new_name = self.name

        # Update the color
        new_color = self.color

        # Update the variants
        new_variants = [v for v in self.variants if v.position <= size]
        # Get the variants that remain
        self.variants = [v for v in self.variants if v.position > size]
        # Update the variant positions
        for v in self.variants:
            v.position -= size
        return Exon(
            size=n_size,
            coding=new_coding,
            name=new_name,
            color=new_color,
            variants=new_variants,
        )

    def valid_splits(self, height: float = 20, scale: float = 1) -> List[Range]:
        """Determine which splits of this exon can be drawn"""

        def meaningfull(split: Range) -> bool:
            """Determine if a split is meaningfull

            Empty split (0, 1) is not meaningfull
            """
            return cast(bool, split != (0, 1))

        splits = list()

        # Size of the notch/arrow
        cap_size = height * 0.25

        # Calculate the space to leave for the start of the coding region
        # If the phase is 0, we don't need to leave any room
        coding_start_offset = (
            0 if not self.coding.start_phase else math.ceil(cap_size / scale)
        )
        coding_end_offset = (
            0 if not self.coding.end_phase else math.ceil(cap_size / scale)
        )

        # Add the first non coding part
        start = 0
        end = self.coding.start + 1
        nc_before = (start, end)

        # Add the coding part
        start = self.coding.start + coding_start_offset
        end = self.coding.end - coding_end_offset + 1
        coding = (start, end)

        # Add the final non-coding part
        start = self.coding.end
        end = self.size + 1
        nc_after = (start, end)

        # We don't want empty ranges, or (0, 1)
        if meaningfull(nc_before):
            splits.append(nc_before)
        if meaningfull(coding):
            splits.append(coding)
        if meaningfull(nc_after):
            splits.append(nc_after)

        return splits

    def tsv(self, sep: str = "\t") -> str:
        """Dump an exon as tsv"""
        records = [
            self.size,
            self.name,
            self.color,
            self.coding.start,
            self.coding.end,
            self.coding.start_phase,
            self.coding.end_phase,
        ]
        return sep.join(map(str, records))


def _pick_split(splits: List[Range], page_size: int) -> int:
    """
    Pick a legal split from the allowed splits and the page size

    For now, we just pick the biggest possible split
    """
    # Intersect each valid split with the page
    splits_that_fit = list()
    page = (0, page_size + 1)
    for split in splits:
        splits_that_fit += intersect(split, page)
    # Remove empty intersections
    splits_that_fit = [x for x in splits_that_fit if x]

    if not splits_that_fit:
        raise ValueError(f"No valid split range specified: {splits=}, {page_size=}")

    biggest_split = splits_that_fit[-1]
    return cast(int, biggest_split[-1] - 1)


def group_exons(
    exons: List[Exon],
    height: int,
    gap: int,
    width: int,
    scale: float = 1.0,
    page_full: float = 0.15,
) -> List[List[Exon]]:
    """Group exons on a page, so that they do not go over width"""
    if not exons:
        return [[]]
    page = list()
    row: List[Exon] = list()

    space_left = width
    for exon in exons:
        while exon:
            # If there is no space left
            if space_left < 1:
                if not row:
                    raise RuntimeError("Cannot add empty row to page")
                page.append(row)
                row = list()
                space_left = width
                continue

            # If there is less than 15% (default) of the page left, and we already have
            # some exons on this row
            if space_left / width < page_full and row:
                page.append(row)
                row = list()
                space_left = width
                continue

            # Determine which way we can split this exon
            valid_splits = exon.valid_splits(height=height, scale=scale)

            # If there is no way to split the current exon that fits on the page, start a new row
            if not valid_splits:
                if not row:
                    raise RuntimeError("Cannot add empty row to page")
                page.append(row)
                row = list()
                space_left = width
                continue

            # Try to see if we can pick a split that fits the page
            try:
                split = _pick_split(valid_splits, int(space_left / scale))
            except ValueError:
                if not row:
                    raise RuntimeError("Cannot add empty row to page")
                page.append(row)
                row = list()
                space_left = width
                continue

            new_exon = exon.split(split)
            row.append(new_exon)
            space_left -= gap + math.ceil(new_exon.draw_size(scale))
    page.append(row)
    return page


def draw_exons(exons: List[Exon], width: int, height: int, gap: int) -> List[Element]:
    x: float = height
    y: float = height
    elements = list()
    # The exons will be modified by grouping them, so we make a copy here
    tmp_exons = copy.deepcopy(exons)

    # Calculate the minimum scale at which we can draw every exon
    scale = max(e.min_scale(height) for e in exons)
    # Use the default scale of 1, if possible
    scale = max(scale, 1)

    for row in group_exons(tmp_exons, width=width, height=height, gap=gap):
        for exon in row:
            elements += exon.draw(height=height, scale=scale, x=x, y=y)
            x += exon.draw_size(scale) + gap
        y += 2 * height
        x = height
    return elements


def parse_coding_region(exon_dict: Dict[Any, Any]) -> None:
    """Extract the coding fields into a Coding object, rewrites exon_dict"""
    # Get the coding values out of the exon dictionary
    coding_dict = dict()
    for coding_field in "coding_start coding_end start_phase end_phase".split():
        if coding_field in exon_dict:
            coding_dict[coding_field] = exon_dict.pop(coding_field)
        else:
            coding_dict[coding_field] = 0

    # Rename start and end
    coding_dict["start"] = coding_dict.pop("coding_start")
    coding_dict["end"] = coding_dict.pop("coding_end")

    exon_dict["coding"] = Coding(**{k: int(v) for k, v in coding_dict.items()})


def parse_variants(exon_dict: Dict[Any, Any]) -> None:
    """Extract the variant fields into a list of Variants, rewrites exon_dict"""
    variants: List[Variant] = list()

    if "variant_pos" not in exon_dict:
        exon_dict["variants"] = variants
        return

    positions = exon_dict.pop("variant_pos").split(",")
    names = exon_dict.pop("variant_name").split(",")
    colors = exon_dict.pop("variant_color").split(",")

    if not len(names) == len(positions) and len(names) == len(colors):
        error_msg = "Please specify an equal number of items for each variant_field"
        raise ValueError(error_msg)

    for pos, name, color in zip(positions, names, colors):
        variants.append(Variant(int(pos) if pos else 0, name=name, color=color))
    exon_dict["variants"] = variants


def exon_from_dict(d: Dict[str, str]) -> Exon:
    """Create an Exon from a dictionary"""
    exon_dict: Dict[Any, Any] = d.copy()
    parse_coding_region(exon_dict)
    parse_variants(exon_dict)
    # Convert exon size to int
    exon_dict["size"] = int(exon_dict["size"])
    return Exon(**exon_dict)


def exons_from_tsv(fin: TextIOWrapper) -> List[Exon]:
    header = next(fin).strip("\n").split("\t")
    expected = [
        "size",
        "name",
        "color",
        "coding_start",
        "coding_end",
        "start_phase",
        "end_phase",
    ]
    if not header == expected:
        raise RuntimeError("Unexpected header in TSV file")

    exons: List[Exon] = list()
    for line in fin:
        d = {k: v for k, v in zip(header, line.strip("\n").split("\t")) if v}
        exons.append(exon_from_dict(d))

    return exons


@no_type_check
def element_xy(element: Element) -> Tuple[float, float]:
    """Determine the furthest x,y coordinates for various svg objects"""
    if isinstance(element, Rect):
        x = element.x + element.width
        y = element.y + element.height
    elif isinstance(element, Text):
        x = element.x
        y = element.y
    elif isinstance(element, Polygon):
        if not element.points:
            x = 0
            y = 0
        else:
            x = max(
                (element.points[i] for i in range(len(element.points)) if not i % 2)
            )
            y = max((element.points[i] for i in range(len(element.points)) if i % 2))
    elif isinstance(element, Style):
        x = 0
        y = 0
    else:
        raise ValueError(element)
    return x, y
