from exonviz.exon import Exon


def test_in_frame() -> None:
    """Test basic functionality for Exon dataclass"""
    E = Exon("exon1", 21, 0)
    assert E.name == "exon1"
    assert E.size == 21
    assert E.start_frame == 0
    assert E.end_frame == 0
