[![Continous integration](https://github.com/Redmar-van-den-Berg/exonviz/actions/workflows/ci.yml/badge.svg)](https://github.com/Redmar-van-den-Berg/exonviz/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

# Exonviz
Visualise exons
------------------------------------------------------------------------
## Installation
Exonviz only requires Python, and can be installed using PIP:
```
pip install exonviz
```

## Usage
Pass either a transcript (with version!), or a valid HGVS description to exonviz to generate a figure.

### Options
Since each gene is different, you will probably want to play around with the options to get the perfect figure for your favorite gene.

```
usage: exonviz [-h] [--width WIDTH] [--height HEIGHT] [--noncoding] [--gap GAP] transcript

Description of command.

positional arguments:
  transcript       Transcript (with version) to visualise

optional arguments:
  -h, --help       show this help message and exit
  --width WIDTH    Maximum width of the figure (default: inf)
  --height HEIGHT  Exon height (default: 20)
  --noncoding      Show non coding regions (default: False)
  --gap GAP        Gap between the exons (default: 5)
  --color COLOR    Color for the exons (e.g. 'purple') (default: #4C72B7)
```

## Examples
### SDHD
Using the default settings, which does not include non-coding regions of the exon:

`exonviz "NG_012337.3(NM_003002.4):c.274G>T" > SDHD.svg`

![Figure of SDH exons](https://raw.githubusercontent.com/Redmar-van-den-Berg/exonviz/main/examples/SDHD.svg)

### DMD
Since DMD has many exons, we specify a maximum width for the figure:

`exonviz "NM_004006.3:c.=" --width 1024 --color purple > DMD.svg`

![Figure of DMD exons](https://raw.githubusercontent.com/Redmar-van-den-Berg/exonviz/main/examples/DMD.svg)


# ATXN1
Include the non coding exons, since most exons of ATXN1 are non coding. We
limit the maximum width and increase the height of the picture. For clarity, we
also increase the distance between the displayed exons:

`exonviz ENST00000436367.6 --noncoding --width 4000 --height 150 --gap 50 > ATXN1.svg`

![Figure of ATXN1 exons](https://raw.githubusercontent.com/Redmar-van-den-Berg/exonviz/main/examples/ATXN1.svg)

### PLP1
Include the non coding regions and increase the height and distance between the exons:

`exonviz "NM_000533.5" --noncoding --height 100 --gap 50 > PLP1.svg`

![Figure of PLP1 exons](https://raw.githubusercontent.com/Redmar-van-den-Berg/exonviz/main/examples/PLP1.svg)

### NF1
Set the maximum width of the figure to the approximate size of the largest exon:

`exonviz "ENST00000358273.9" --noncoding --width 3600 --height 75 --gap 20 > examples/NF1-202.svg`

![Figure of NF1 exons](https://raw.githubusercontent.com/Redmar-van-den-Berg/exonviz/main/examples/NF1-202.svg)
