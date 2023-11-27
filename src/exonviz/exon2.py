from dataclasses import dataclass
from typing import List

from svg import Rect

Element = Rect

@dataclass()
class Exon:
    size: int

    def draw(self, height: int=20) -> List[Element]:
        """Draw the Exon, in SVG format

        Returns a list of SVG elements

        """
        elements = list()

        elements.append(self._draw_noncoding(height))

        return elements

    def _draw_noncoding(self, height: int) -> Rect:
        return Rect(
            x=0, y=height*0.25,
            width = self.size,
            height=height
        )

@dataclass()
class Coding:
    start: int = 0
    end: int = 0
    start_frame: int = 0
    end_frame: int = 0


    def __bool__(self) -> bool:
        return self.end > self.start
