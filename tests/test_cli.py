import pytest

from exonviz.cli import check_input


# A list of valid inputs for the tool
VALID = [
    "NM_004006.3:c.=",
    "NM_000533.5:c.=",
    "ENST00000358273.9:c.=",
    "NG_012337.3(NM_003002.4):c.274G>T",
]


@pytest.mark.parametrize("input", VALID)
def test_check_input_valid(input: str) -> None:
    """Check that we do not accidentally rewrite correct inputs"""
    assert check_input(input) == input


BEFORE_AFTER = [
    ("NM_004006.3", "NM_004006.3:c.="),
    ("NM_000533.5", "NM_000533.5:c.="),
    ("ENST00000358273.9", "ENST00000358273.9:c.="),
]


@pytest.mark.parametrize("input, rewrite", BEFORE_AFTER)
def test_check_input_no_variant(input: str, rewrite: str) -> None:
    """Check that we rewrite it to a valid 'no variant' format"""
    assert check_input(input) == rewrite


ERROR = ["/l", "", "_"]


@pytest.mark.parametrize("input", ERROR)
def test_check_invalid_input(input: str) -> None:
    """Raise an error when we cannot figure out the HGVS"""
    with pytest.raises(Exception):
        check_input(input)
