import pytest
from exonviz.exon import Exon, Region


class TestRegion:
    def test_small_region(self) -> None:
        R = Region(0, 1)

        assert R.size == 1

    def test_gapped_region(self) -> None:
        R = Region([0, 20], [10, 30])
        assert R.start == [0, 20]
        assert R.end == [10, 30]
        assert R.size == 20

    def test_one_start_two_end(self) -> None:
        """Both start and end have to be either list or int, no mixing"""
        with pytest.raises(ValueError):
            Region(0, [10, 20])

    def test_start_end_unequal_length(self) -> None:
        """Both start and end have to be the same size"""
        with pytest.raises(ValueError):
            Region([0], [10, 20])

    def test_negative_region(self) -> None:
        R = Region(10, 0)
        assert R.size == 10

    def test_negative_region_list(self) -> None:
        R = Region([10, 30], [0, 20])
        assert R.size == 20

    def test_interleaved_negative_region_list(self) -> None:
        R = Region([0, 10], [10, 0])
        assert R.size == 20

    def test_in_frame(self) -> None:
        """Test basic functionality for Exon dataclass"""
        E = Exon("exon1", 21, 0)
        assert E.name == "exon1"
        assert E.size == 21
        assert E.start_frame == 0
        assert E.end_frame == 0


class TestExon:
    def test_zero_region(self) -> None:
        R = Region(0, 0)
        assert R.start == 0
        assert R.end == 0
        assert R.size == 0
