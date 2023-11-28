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
        return Coding(start=new_start, end=new_end)


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

    def __repr__(self) -> str:
        return (
        f"Exon(size={self.size}, "
        f"coding={self.coding}, "
        f"variants={self.variants}, "
        f"name={self.name})"
        )

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
        phase0: List[Decimal | float | int]  = [
           x, y,
           x-0.5*height, y,
           x-0.5*height, y+height,
           x, y+height,
           x, y
        ]

        # Notch
        phase1: List[Decimal | float | int]  = [
           x, y,
           x-0.5*height, y,
           x, y+0.5*height,
           x-0.5*height, y+height,
           x, y+height,
           x, y
        ]

        # Arrow
        phase2: List[Decimal | float | int]  = [
           x, y,
           x-0.5*height, y+0.5*height,
           x, y+height,
           x, y
        ]
        # fmt: on

        start_cap = [phase0, phase1, phase2]

        return Polygon(points=start_cap[self.coding.start_phase], fill="orange")

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
        phase0: List[Decimal | float | int] = [
           x, y,
           x+0.5*height, y,
           x+0.5*height, y+height,
           x, y+height,
           x, y
        ]

        # Arrow
        phase1: List[Decimal | float | int]  = [
           x, y,
           x+0.5*height, y+0.5*height,
           x, y+height,
           x, y
        ]

        # Notch
        phase2: List[Decimal | float | int]  = [
           x, y,
           x+0.5*height, y,
           x, y+0.5*height,
           x+0.5*height, y+height,
           x, y+height,
           x, y
        ]
        # fmt: off

        end_cap = [phase0, phase1, phase2]

        return Polygon(
            points = end_cap[self.coding.end_phase], fill="orange"
        )

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
        n_size = size
        self.size -= size
        return Exon(size=n_size)

    
