import pytest
from exonviz.exon import Exon, Region


class TestRegion:
    def test_small_region(self) -> None:
        R = Region(0, 1)

        assert R.size == 1

    def test_negative_region(self) -> None:
        R = Region(10, 0)
        assert R.size == 10

    def test_empty_region(self) -> None:
        R = Region(10, 10)
        assert R.size == 0

    def test_empty_region_falsy(self) -> None:
        R = Region(10, 10)
        assert not R

    def test_non_empty_region_truthy(self) -> None:
        R = Region(0, 1)
        assert R

class TestExon:
    end_frame = [
        # Exon, expected end_frame
        # fmt: off
        (Exon(start=0, end=3, frame=0), 0),
        (Exon(start=0, end=4, frame=0), 1),
        (Exon(start=0, end=5, frame=0), 2),

        (Exon(start=0, end=3, frame=1), 1),
        (Exon(start=0, end=4, frame=1), 2),
        (Exon(start=0, end=5, frame=1), 0),

        (Exon(start=0, end=3, frame=2), 2),
        (Exon(start=0, end=4, frame=2), 0),
        (Exon(start=0, end=5, frame=2), 1)
        # fmt: on
    ]

    def test_zero_size_Exon(self) -> None:
        E = Exon(start=0, end=0, frame=0)
        assert E.size == 0

    def test_larger_Exon(self) -> None:
        """Test Exon size"""
        E = Exon(start=0, end=21, frame=0)
        assert E.size == 21

    @pytest.mark.parametrize("exon,expected", end_frame) # type: ignore
    def test_Exon_end_frame(self, exon: Exon, expected: int) -> None:
        """Test the Exon ending frame"""
        assert exon.end_frame == expected


    def test_Exon_non_coding(self) -> None:
        """If there is no coding, the whole exon should be none coding"""
        E = Exon(start=0, end=21, frame=0)
        assert E.coding is None
        assert E.non_coding == Region(0, 21)


    def test_Exon_coding(self) -> None:
        """If the whole Exon is coding, non_coding should be None"""
        E =Exon(start=0, end=21, frame=0, coding=Region(0, 21))
        assert E.non_coding is None
        assert E.coding == Region(0, 21)

    def test_Exon_start_non_coding(self) -> None:
        """Test the non_coding region if the start of the exon is non coding"""
        E = Exon(start=0, end=21, frame=0, coding=Region(4, 21))
        assert E.non_coding == Region(0, 4)

    def test_Exon_end_non_coding(self) -> None:
        E = Exon(start=0, end=21, frame=0, coding=Region(0, 18))
        assert E.non_coding == Region(18, 21)

    def test_Exon_start_end_non_coding(self) -> None:
        """If only the center of the exon is coding"""
        pass
