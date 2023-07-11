[![Continous integration](https://github.com/Redmar-van-den-Berg/exonviz/actions/workflows/ci.yml/badge.svg)](https://github.com/Redmar-van-den-Berg/exonviz/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

# Exonviz
Visualise exons
------------------------------------------------------------------------
## Usage
Pass either a transcript (with version!), or a valid HGVS description to exonviz to generate a figure.
### Options
Since each gene is different, you will probably want to play around with the options to get the perfect figure for your favorite gene.

```bash

usage: exonviz [-h] [--max-width MAX_WIDTH] [--height HEIGHT] [--non-coding]
               [--gap GAP]
               transcript

Description of command.

positional arguments:
  transcript            Transcript (with version) to visualise

optional arguments:
  -h, --help            show this help message and exit
  --max-width MAX_WIDTH
                        Maximum width of the figure (default: inf)
  --height HEIGHT       Exon height (default: None)
  --non-coding          Show non coding regions (default: False)
  --gap GAP             Gap between the exons (default: None)
```

## Examples
```bash
# SDH, using the default settings
exonviz "NG_012337.3(NM_003002.4):c.274G>T" > SDHD.svg

# DMD, only the coding regions, and a width of 1024
exonviz "NM_004006.3:c.=" --max-width 1024 > DMD.svg

# PLP1, show non coding regions
exonviz "NM_000533.5" --non-coding > PLP1.svg

# NF1, show non coding regions
exonviz "ENST00000358273.9" --non-coding > NF1-202.svg

# ATXN1, show non coding, increase the maximum width and height of the picture, and
# increase the gap between exons
exonviz ENST00000436367.6 --non-coding --max-width 4000 --height 150 --gap 50 > ATXN1.svg
```
