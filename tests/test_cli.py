import pytest

from exonviz.cli import check_input, trim_variants, sort_variants


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


TRIM = [
    ("NM_003002.4:c.=", "NM_003002.4:c.="),
    ("NM_003002.4:r.=", "NM_003002.4:r.="),
    ("NM_003002.4:r.300del", "NM_003002.4:r.="),
    ("NM_003002.4:r.[300del;274G>T]", "NM_003002.4:r.="),
]

@pytest.mark.parametrize("before, trimmed", TRIM)
def test_trim_variants(before: str, trimmed: str):
    """
    GIVEN an HGVS variant description
    WHEN we trim the trim_variants
    THEN we should get a description without variants
         while maintaining the same coordinate system
    """
    assert trim_variants(before) == trimmed
