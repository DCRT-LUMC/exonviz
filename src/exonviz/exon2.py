from dataclasses import dataclass
from typing import List, Optional

from svg import Rect

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

    def draw(self, height: int=20) -> List[Element]:
        """Draw the Exon, in SVG format

        Returns a list of SVG elements

        """
        elements = list()

        elements.append(self._draw_noncoding(height))
        elements.append(self._draw_coding(height))

        return elements

    def _draw_noncoding(self, height: int) -> Rect:
        return Rect(
            x=0, y=height*0.25,
            width = self.size,
            height=height*0.5
        )

    def _draw_coding(self, height: int) -> Rect:
        return Rect(
            x=self.coding.start, y = 0,
            width = self.coding.size,
            height = height
        )
