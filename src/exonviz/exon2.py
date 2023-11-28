from dataclasses import dataclass
from typing import List, Optional

from svg import Rect, Polygon

Element = Rect


@dataclass()
class Coding:
    start: int = 0
    end: int = 0
    start_frame: int = 0
    end_frame: int = 0

    def __bool__(self) -> bool:
        return self.end > self.start

    @property
    def size(self) -> int:
        return self.end - self.start


class Exon:
    def __init__(self, size: int, coding: Optional[Coding] = None) -> None:
        self.size = size
        if coding is None:
            self.coding = Coding()
        else:
            self.coding = coding

    def draw(self, height: float = 20, x: float=0, y: float=0) -> List[Element]:
        """Draw the Exon, in SVG format

        Returns a list of SVG elements
        """
        elements = list()

        # If the start of the exon is coding, we have to shift x to leave space
        # for the cap
        if self.coding and self.coding.start == 0:
            x += height*0.25
        elements.append(self._draw_noncoding(height, x=x, y=y))
        elements += (self._draw_coding(height, x=x, y=y))

        return elements

    def _draw_noncoding(self, height: float, x: float, y: float, color: str = "blue") -> Rect:
        return Rect(x=x, y=y+height * 0.25, width=self.size, height=height * 0.5, fill=color)

    def _draw_coding(self, height: float, x: float, y: float, color: str ="green") -> List[Element]:
        # Fixed points for every exon
        elements: List[Element] = list()

        # Is there a coding region defined?
        if not self.coding:
            return elements

        # First, we add the coding region block
        elements.append(Rect(x=x+self.coding.start, y=y, width=self.coding.size, height=height, fill=color))
        # Next, we add the starting frame

        #start = Polygon(
        #    points = [
        #        0, 0,
        #        0.5*height, 0,
        #        0.5*height, height,
        #        0, height,
        #        0, 0
        #    ], fill="orange"
        #)

        #elements.append(start)
        return elements
