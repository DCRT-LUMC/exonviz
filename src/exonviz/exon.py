from typing import List, Union, Tuple


class Region:
    """A region has a start and end, which informs the size

    Subtracting two regions returns two regions, namelya region before and after the substracted
    region
    """

    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    @property
    def size(self) -> int:
        """The size property."""
        return abs(self.end - self.start)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Region):
            return NotImplemented
        return self.start == other.start and self.end == other.end

    def __bool__(self) -> bool:
        return self.size != 0

    def __sub__(self, other: "Region") -> Tuple["Region", "Region"]:
        """Subtracting a region from itself returns the remaining two regions.

        Namely before and after the subtracted regio
        """
        # If other does not overlap and lies before
        if other.end < self.start:
            return Region(self.start, self.start), self

        # If other does not overlap and lies after
        if other.start > self.end:
            return self, Region(self.end, self.end)

        # Determine what is left before the subtracted regio
        start = self.start
        if other.start < self.start:
            end = self.start
        else:
            end = other.start
        before = Region(start, end)

        # Determine what is left after the subtracted regio
        if other.end > self.end:
            start = self.end
        else:
            start = other.end
        end = self.end
        after = Region(start, end)

        return (before, after)

    def __repr__(self) -> str:
        return f"Region({self.start}, {self.end})"


class Exon(Region):
    def __init__(
        self,
        start: int,
        end: int,
        frame: int,
        coding: Region,
    ) -> None:
        super().__init__(start, end)
        self.frame = frame
        self.coding = coding

        self.non_coding = self._determine_non_coding()

    def __repr__(self) -> str:
        return f"Exon({self.start}, {self.end}, {self.frame}, {self.coding}, {self.non_coding})"

    def _determine_non_coding(self) -> Tuple[Region, Region]:
        """Determine the non-coding parts of the exon"""
        exon_region = Region(self.start, self.end)
        return exon_region - self.coding

    @property
    def end_frame(self) -> int:
        return (self.coding.size + self.frame) % 3
