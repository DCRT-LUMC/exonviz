import pytest

from exonviz.cli import check_input, get_MANE, trim_variants, sort_variants


# A list of valid inputs for the tool
VALID = [
    "NM_004006.3:c.=",
    "NM_000533.5:c.=",
    "ENST00000358273.9:c.=",
    "NG_012337.3(NM_003002.4):c.274G>T",
]


def test_get_mane() -> None:
    """Test if we can get the MANE dictionary"""
    mane = get_MANE()
    assert mane["BST2"] == "ENST00000252593.7"


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
    ("NM_003002.4:r.[274g>u;300del]", "NM_003002.4:r.="),
    (
        "NC_000011.10(NM_003002.4):c.[274G>T;300del;314+10del]",
        "NC_000011.10(NM_003002.4):c.=",
    ),
]


@pytest.mark.parametrize("before, trimmed", TRIM)
def test_trim_variants(before: str, trimmed: str) -> None:
    """
    GIVEN an HGVS variant description
    WHEN we trim the variants
    THEN we should get a description without variants
         while maintaining the same coordinate system
    """
    assert trim_variants(before) == trimmed


ORDER = [
    ("NM_003002.4:c.=", "NM_003002.4:c.="),
    ("NM_003002.4:r.=", "NM_003002.4:r.="),
    ("NM_003002.4:r.300del", "NM_003002.4:r.300del"),
    ("NM_003002.4:r.[274g>u;300del]", "NM_003002.4:r.[274g>u;300del]"),
    ("NM_003002.4:r.[300del;274g>u]", "NM_003002.4:r.[274g>u;300del]"),
    ("NM_001378743.1(CYLD):c.-229G>C", "NM_001378743.1(CYLD):c.-229G>C"),
    (
        "NM_001378743.1(CYLD):c.[-229G>C;10del]",
        "NM_001378743.1(CYLD):c.[-229G>C;10del]",
    ),
    (
        "NM_001378743.1(CYLD):c.[11del;-229G>C;10del]",
        "NM_001378743.1(CYLD):c.[-229G>C;10del;11del]",
    ),
    ("NM_001378743.1(CYLD):c.-204+132C>T", "NM_001378743.1(CYLD):c.-204+132C>T"),
    (
        "NM_001378743.1(CYLD):c.[10del;-204+132C>T]",
        "NM_001378743.1(CYLD):c.[-204+132C>T;10del]",
    ),
    ("NM_001378743.1(CYLD):c.*3000C>G", "NM_001378743.1(CYLD):c.*3000C>G"),
    (
        "NM_001378743.1(CYLD):c.[*3000C>G;10del]",
        "NM_001378743.1(CYLD):c.[10del;*3000C>G]",
    ),
    (
        "ENST:c.[10del;10+15del]",
        "ENST:c.[10del;10+15del]",
    ),
    ("ENST:c.[10_12+15del;9_12+15del]", "ENST:c.[9_12+15del;10_12+15del]"),
]


@pytest.mark.parametrize("before, sorted", ORDER)
def test_sort_variants(before: str, sorted: str) -> None:
    """
    GIVEN an HGVS variant description
    WHEN we order the variants
    THEN we should get a description with the variants in increasing order
         while maintaining the same coordinate system
    """
    assert sort_variants(before) == sorted


NOT_SUPPORTED = [
    "NM_152416.3:c.[477_478ins[NC_000008.11:g.95036371_95036495];500del]",
    # "NM_152416.3:c.477_478ins[NC_000008.11:g.95036371_95036495]",
]


@pytest.mark.parametrize("hgvs", NOT_SUPPORTED)
def test_unsupported_hgvs(hgvs: str) -> None:
    with pytest.raises(ValueError):
        sort_variants(hgvs)
