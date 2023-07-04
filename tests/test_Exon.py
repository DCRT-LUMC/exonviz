import pytest
from exonviz.exon import Exon, Region


class TestRegion:
    def test_small_region(self) -> None:
        R = Region(0, 1)

        assert R.size == 1

    def test_empty_region(self) -> None:
        R = Region(10, 10)
        assert R.size == 0

    def test_empty_region_falsy(self) -> None:
        R = Region(10, 10)
        assert not R

    def test_non_empty_region_truthy(self) -> None:
        R = Region(0, 1)
        assert R

    def test_subtract_region_from_itself(self) -> None:
        """Subtracting a region from itself gives to emtpy Regions"""
        R = Region(0, 10)
        before, after = R - R

        assert not before
        assert not after

    def test_subtract_region_from_start(self) -> None:
        bigger = Region(0, 10)
        smaller = Region(0, 5)

        before, after = bigger - smaller

        assert not before
        assert after == Region(5, 10)

    def test_subtract_region_from_end(self) -> None:
        bigger = Region(0, 10)
        smaller = Region(5, 10)

        before, after = bigger - smaller

        assert before == Region(0, 5)
        assert not after

    def test_substract_region_from_center(self) -> None:
        bigger = Region(0, 10)
        smaller = Region(3, 7)

        before, after = bigger - smaller

        assert before == Region(0, 3)
        assert after == Region(7, 10)

    def test_subtract_larger_overlapping_start(self) -> None:
        bigger = Region(10, 20)
        smaller = Region(8, 13)

        before, after = bigger - smaller

        assert not before
        assert after == Region(13, 20)

    def test_subtract_larger_overlapping_end(self) -> None:
        bigger = Region(10, 20)
        smaller = Region(13, 25)

        before, after = bigger - smaller

        assert not after
        assert before == Region(10, 13)

    def test_subtract_larger_overlapping_all(self) -> None:
        bigger = Region(0, 20)
        smaller = Region(10, 15)

        before, after = smaller - bigger

        assert not before
        assert not after

    def test_subtract_unrelated_region_before(self) -> None:
        region = Region(0, 20)
        unrelated = Region(-20, -10)

        before, after = region - unrelated

        # This test relies on the implementation of 'before'
        assert before == Region(0, 0)
        assert after == Region(0, 20)

    def test_subtract_unrelated_region_after(self) -> None:
        region = Region(0, 20)
        unrelated = Region(40, 60)

        before, after = region - unrelated

        assert before == Region(0, 20)
        # This test relies on the implementation of 'after'
        assert after == Region(20, 20)

    def test_subtract_empty_region(self) -> None:
        region = Region(0, 20)
        empty = Region(10, 10)

        before, after = region - empty

        assert before == Region(0, 10)
        assert after == Region(10, 20)

    def test_reverse_region(self) -> None:
        """Test to make sure we reject reverse regions"""
        with pytest.raises(ValueError):
            region = Region(20, 10)


class TestExon:
    end_frame = [
        # Exon, expected end_frame
        # fmt: off
        (Exon(start=0, end=3, frame=0, coding=Region(0, 3)), 0),
        (Exon(start=0, end=4, frame=0, coding=Region(0, 4)), 1),
        (Exon(start=0, end=5, frame=0, coding=Region(0, 5)), 2),

        (Exon(start=0, end=3, frame=1, coding=Region(0, 3)), 1),
        (Exon(start=0, end=4, frame=1, coding=Region(0, 4)), 2),
        (Exon(start=0, end=5, frame=1, coding=Region(0, 5)), 0),

        (Exon(start=0, end=3, frame=2, coding=Region(0, 3)), 2),
        (Exon(start=0, end=4, frame=2, coding=Region(0, 4)), 0),
        (Exon(start=0, end=5, frame=2, coding=Region(0, 5)), 1)
        # fmt: on
    ]

    def test_zero_size_Exon(self) -> None:
        E = Exon(start=0, end=0, frame=0, coding=Region(0, 0))
        assert E.size == 0

    def test_larger_Exon(self) -> None:
        """Test Exon size"""
        E = Exon(start=0, end=21, frame=0, coding=Region(0, 0))
        assert E.size == 21

    @pytest.mark.parametrize("exon,expected", end_frame)
    def test_Exon_end_frame(self, exon: Exon, expected: int) -> None:
        """Test the Exon ending frame"""
        assert exon.end_frame == expected

    def test_Exon_coding_not_in_frame(self) -> None:
        """Test an exon where the size is in frame, but the coding size is not"""
        E = Exon(start=0, end=21, frame=0, coding=Region(8, 21))
        assert E.end_frame == 1

    def test_Exon_coding_in_frame(self) -> None:
        """Test an exon where the size is not in frame, but the coding size is"""
        E = Exon(start=0, end=22, frame=0, coding=Region(9, 21))
        assert E.end_frame == 0

    def test_Exon_non_coding(self) -> None:
        """If there is no coding, the whole exon should be none coding

        Note that Exon.non_coding is always a list of Regions
        """
        E = Exon(start=0, end=21, frame=0, coding=Region(0, 0))
        before_coding, after_coding = E.non_coding

        assert not before_coding
        assert not E.coding
        assert after_coding == Region(0, 21)

    def test_Exon_coding(self) -> None:
        """If the whole Exon is coding, non_coding should be empty"""
        E = Exon(start=0, end=21, frame=0, coding=Region(0, 21))
        before_coding, after_coding = E.non_coding

        assert not before_coding
        assert E.coding == Region(0, 21)
        assert not after_coding

    def test_Exon_start_non_coding(self) -> None:
        """Test the non_coding region if the start of the exon is non coding"""
        E = Exon(start=0, end=21, frame=0, coding=Region(4, 21))
        before_coding, after_coding = E.non_coding

        assert before_coding == Region(0, 4)
        assert E.coding == Region(4, 21)
        assert not after_coding

    def test_Exon_end_non_coding(self) -> None:
        E = Exon(start=0, end=21, frame=0, coding=Region(0, 18))
        before_coding, after_coding = E.non_coding

        assert not before_coding
        assert after_coding == Region(18, 21)

    def test_Exon_start_end_non_coding(self) -> None:
        """If only the center of the exon is coding"""
        E = Exon(start=0, end=21, frame=0, coding=Region(10, 18))
        before_coding, after_coding = E.non_coding

        assert before_coding == Region(0, 10)
        assert after_coding == Region(18, 21)

    CODING_SLICE = [
        # Coding region to pass to exon, sliced coding region
        (Region(200, 300), Region(121, 121)),  # coding region starts after exon
        (Region(0, 90), Region(100, 100)),  # coding region stops before exon
        (Region(0, 100), Region(100, 100)),  # coding region stops as the exon starts
        (Region(0, 101), Region(100, 101)),  # coding region overlaps exon by 1
        (Region(100, 200), Region(100, 121)),  # coding region extends after
        (Region(0, 200), Region(100, 121)),  # coding region fully contains exon
    ]

    @pytest.mark.parametrize("coding_region, coding_region_exon", CODING_SLICE)
    def test_exon_slice_coding(
        self, coding_region: Region, coding_region_exon: Region
    ) -> None:
        """If the coding region is larger than the exon, slice it to the exon size"""
        E = Exon(start=100, end=121, frame=0, coding=coding_region)

        assert E.coding == coding_region_exon
