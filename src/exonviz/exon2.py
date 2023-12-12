from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Dict, Tuple, no_type_check
from decimal import Decimal

from _io import TextIOWrapper
from svg import Rect, Polygon, Text, Style

from GTGT.range import intersect

import logging

logging.basicConfig(level="DEBUG")
log = logging.getLogger(__name__)
Element = Rect | Polygon | Text | Style


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
            new_end_phase = -1
            self.start_phase = -1

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
            f"name={self.name})"
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

    def draw_size(self, height: float) -> float:
        """Determine how big the Exon is when drawn"""
        return self.size + self._total_overhang(height)

    def _front_overhang(self, height: float) -> float:
        """Determine how much the cap overhangs beyond the start of the exon"""
        if not self.coding or self.coding.start_phase == -1:
            return 0
        cap_size = 0.5 * height
        return max(cap_size - self.coding.start, 0)

    def _end_overhang(self, height: float) -> float:
        """Determine how much the cap overhangs beyond the end of the exon"""
        if not self.coding or self.coding.end_phase == -1:
            return 0
        cap_size = 0.5 * height
        return max(cap_size - (self.size - self.coding.end), 0)

    def _total_overhang(self, height: float) -> float:
        """The total overhang due to the caps we draw"""
        return self._end_overhang(height) + self._front_overhang(height)

    def draw(self, height: float = 20, x: float = 0, y: float = 0) -> List[Element]:
        """Draw the Exon, in SVG format

        Returns a list of SVG elements
        """
        elements: List[Any] = list()

        # If the start of the exon is coding, we have to shift x to leave space
        # for the cap
        x += self._front_overhang(height)

        log.debug(f"Start drawing exon '{self.name}' at postion {x}")

        elements.append(self._draw_noncoding(height, x=x, y=y))
        elements += self._draw_coding(height, x=x, y=y)
        elements += self._draw_variants(height, x=x, y=y)
        elements += self._draw_name(height, x, y)

        return elements

    def _draw_noncoding(self, height: float, x: float, y: float) -> Rect:
        return Rect(
            x=x,
            y=y + height * 0.25,
            width=self.size,
            height=height * 0.5,
            fill=self.color,
        )

    def _draw_coding(self, height: float, x: float, y: float) -> List[Element]:
        # Fixed points for every exon
        elements: List[Element] = list()

        if not self.coding:
            return elements

        # Determine x-coordinate for the coding region start
        cx = x + self.coding.start

        # First, we add the coding region block
        elements.append(
            Rect(
                x=cx,
                y=y,
                width=self.coding.size,
                height=height,
                fill=self.color,
            )
        )
        elements.append(self._draw_start_cap(height, cx, y))
        elements.append(self._draw_end_cap(height, cx + self.coding.size, y))

        return elements

    def _draw_start_cap(self, height: float, x: float, y: float) -> Polygon:
        # fmt: off
        # Square
        phase0 = [
           x, y,
           x-0.5*height, y,
           x-0.5*height, y+height,
           x, y+height,
           x, y
        ]

        # Notch
        phase1 = [
           x, y,
           x-0.5*height, y,
           x, y+0.5*height,
           x-0.5*height, y+height,
           x, y+height,
           x, y
        ]

        # Arrow
        phase2 = [
           x, y,
           x-0.5*height, y+0.5*height,
           x, y+height,
           x, y
        ]

        # Phase -1, used for line-breaked coding exons
        phase3 = None
        # fmt: on

        phases = [phase0, phase1, phase2, phase3]
        cap = phases[self.coding.start_phase]

        if cap:
            return Polygon(points=list(cap), fill=self.color)
        else:
            return Polygon(points=None, fill=self.color)

    def _draw_variants(self, height: float, x: float, y: float) -> Sequence[Rect]:
        elements = list()
        for variant in self.variants:
            elements.append(
                Rect(
                    x=x + variant.position,
                    y=y,
                    width=height / 20,
                    height=height,
                    fill=variant.color,
                )
            )
        return elements

    def _draw_end_cap(self, height: float, x: float, y: float) -> Polygon:
        # fmt: off
        # Square
        phase0 = [
           x, y,
           x+0.5*height, y,
           x+0.5*height, y+height,
           x, y+height,
           x, y
        ]

        # Arrow
        phase1 = [
           x, y,
           x+0.5*height, y+0.5*height,
           x, y+height,
           x, y
        ]

        # Notch
        phase2 = [
           x, y,
           x+0.5*height, y,
           x, y+0.5*height,
           x+0.5*height, y+height,
           x, y+height,
           x, y
        ]

        # Phase -1, used for line-breaked coding exons
        phase3 = None
        # fmt: on

        phases = [phase0, phase1, phase2, phase3]
        cap = phases[self.coding.end_phase]

        if cap:
            return Polygon(points=list(cap), fill=self.color)
        else:
            return Polygon(points=None, fill=self.color)

    def _draw_name(self, height: float, x: float, y: float) -> List[Element]:
        if not self.name:
            return list()
        return [
            Text(
                x=x + (self.size / 2),
                y=y + 0.5 * height,
                class_=["exonnr"],
                text=self.name,
            )
        ]

    def split(self, size: int, height: int) -> "Exon":
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

        # Update the variants
        new_variants = [v for v in self.variants if v.position <= size]
        # Get the variants that remain
        self.variants = [v for v in self.variants if v.position > size]
        # Update the variant positions
        for v in self.variants:
            v.position -= size
        return Exon(
            size=n_size, coding=new_coding, name=new_name, variants=new_variants
        )


def group_exons(
    exons: List[Exon], height: int, gap: int, width: int
) -> List[List[Exon]]:
    """Group exons on a page, so that they do not go over width"""
    if not exons:
        return [[]]
    page = list()
    row: List[Exon] = list()

    x: float = 0
    for exon in exons:
        while exon:
            # How much space is left on the page
            space_left = int(width - x)

            # Leave some space to account for the coding caps, if needed
            if space_left < 2 * height:
                page.append(row)
                row = list()
                x = 0
            else:
                new_exon = exon.split(space_left, height=height)
                row.append(new_exon)
                x += gap + new_exon.draw_size(height)
    page.append(row)
    return page


def draw_exons(exons: List[Exon], width: int, height: int, gap: int) -> List[Element]:
    x = 0.0
    y = 0.0
    elements = list()
    for row in group_exons(exons, width=width, height=height, gap=gap):
        for exon in row:
            elements += exon.draw(height=height, x=x, y=y)
            x += exon.draw_size(height) + gap
        y += 2 * height
        x = 0
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
        "variant_pos",
        "variant_name",
        "variant_color",
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
