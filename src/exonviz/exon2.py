from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Iterator

from decimal import Decimal
from svg import Rect, Polygon, Text

from GTGT.range import intersect

Element = Any


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
    ) -> None:
        self.size = size
        self.name = name

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
        return self.size == other.size

    def draw_size(self, height: float) -> float:
        """Determine how big the Exon is when drawn"""
        size: float = self.size

        if self.coding:
            if self.coding.start_phase != -1:
                size += self._cap_overhang_before(height)
            if self.coding.end_phase != -1:
                size += self._cap_overhang_after(height)

        return size

    def _cap_overhang_before(self, height: float) -> float:
        """Determine how much the cap overhangs beyond the start of the exon"""
        cap_size = 0.25 * height
        return max(cap_size - self.coding.start, 0)

    def _cap_overhang_after(self, height: float) -> float:
        """Determine how much the cap overhangs beyond the end of the exon"""
        cap_size = 0.25 * height
        return max(cap_size - (self.size - self.coding.end), 0)

    def draw(self, height: float = 20, x: float = 0, y: float = 0) -> List[Element]:
        """Draw the Exon, in SVG format

        Returns a list of SVG elements
        """
        elements: List[Any] = list()

        # If the start of the exon is coding, we have to shift x to leave space
        # for the cap
        if self.coding and self.coding.start == 0:
            x += height * 0.25

        elements.append(self._draw_noncoding(height, x=x, y=y))
        elements += self._draw_coding(height, x=x, y=y)
        elements += self._draw_variants(height, x=x, y=y)
        elements += self._draw_name(height, x, y)

        return elements

    def _draw_noncoding(
        self, height: float, x: float, y: float, color: str = "blue"
    ) -> Rect:
        return Rect(
            x=x, y=y + height * 0.25, width=self.size, height=height * 0.5, fill=color
        )

    def _draw_coding(
        self, height: float, x: float, y: float, color: str = "green"
    ) -> List[Element]:
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
                fill=color,
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
            return Polygon(points=list(cap), fill="orange")
        else:
            return Polygon(points=None, fill="orange")

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
            return Polygon(points=list(cap), fill="orange")
        else:
            return Polygon(points=None, fill="orange")

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

    def split(self, size: int) -> "Exon":
        # Update the size
        n_size = min(self.size, size)
        self.size = max(0, self.size - size)

        # Update the coding region
        new_coding = self.coding.split(size)

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

def group_exons(exons: List[Exon], height: int, max_width: int) -> List[List[Exon]]:
    """Group exons on a page, so that they do not go over width"""
    if not exons:
        return [[]]
    page = list()
    row: List[Exon] = list()

    width = max_width
    # Always add space for two caps to the exon size
    cap_size = 0.5*height

    x:float = 0
    for exon in exons:
        while exon:
            # How much space is left on the page
            space_left = int(width - x - cap_size)

            # We don't want to have tiny exons
            if space_left < 2*height:
                page.append(row)
                row = list()
                x = 0
            else:
                new_exon = exon.split(space_left)
                row.append(new_exon)
                x += new_exon.draw_size(height)
    page.append(row)
    return page
