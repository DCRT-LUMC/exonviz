[![Continous integration](https://github.com/Redmar-van-den-Berg/exonviz/actions/workflows/ci.yml/badge.svg)](https://github.com/Redmar-van-den-Berg/exonviz/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

# Exonviz
Visualise exons
------------------------------------------------------------------------
## Usage
Pass either a transcript (with version!), or a valid HGVS description to exonviz to generate a figure.

## Examples
```bash
exonviz "NM_004006.3:c.=" > DMD.svg
exonviz "NM_000533.5" > PLP1.svg
exonviz "ENST00000358273.9" > NF1-202.svg
exonviz "NG_012337.3(NM_003002.4):c.274G>T" > SDHD.svg
exonviz ENST00000436367.6 > ATXN1.svg
```
