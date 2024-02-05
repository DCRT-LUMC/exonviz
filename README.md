[![Continous integration](https://github.com/DCRT-LUMC/exonviz/actions/workflows/ci.yml/badge.svg)](https://github.com/DCRT-LUMC/exonviz/actions/workflows/ci.yml)
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
usage: exonviz [-h] [--width WIDTH] [--height HEIGHT] [--noncoding] [--gap GAP] [--color COLOR] [--exonnumber]
               [--firstexon FIRSTEXON] [--lastexon LASTEXON] [--dump-exons DUMP_EXONS]
               [--dump-variants DUMP_VARIANTS] (--transcript TRANSCRIPT | --exon-tsv EXON_TSV)
               [--variant-tsv VARIANT_TSV]

Visualise exons and mutations

options:
  -h, --help            show this help message and exit
  --width WIDTH         Maximum width of the figure (default: 9999999)
  --height HEIGHT       Exon height (default: 20)
  --noncoding           Show non coding regions (default: False)
  --gap GAP             Gap between the exons (default: 5)
  --color COLOR         Color for the exons (e.g. 'purple') (default: #4C72B7)
  --exonnumber          Show exon number (default: False)
  --firstexon FIRSTEXON
                        The first exon to draw (default: 1)
  --lastexon LASTEXON   The last exon to draw (default: 9999)
  --dump-exons DUMP_EXONS
                        Write exons to the specified file (default: None)
  --dump-variants DUMP_VARIANTS
                        Write variants to the specified file (default: None)
  --transcript TRANSCRIPT
                        Transcript (with version) to visualise (default: None)
  --exon-tsv EXON_TSV   TSV file containing exons (default: None)
  --variant-tsv VARIANT_TSV
                        TSV file containing variants (default: None)
```

## Examples
### SDHD
Using the default settings, which does not include non-coding regions of the transcript:

`exonviz --transcript SDHD > SDHD.svg`

![Figure of SDH exons](https://raw.githubusercontent.com/DCRT-LUMC/exonviz/v0.2.2/examples/SDHD.svg)

### DMD
For DMD, we explicitly specify the transcript we are interested in. We also set
a maximum width for the figure, since DMD has many exons:

`exonviz --transcript "NM_004006.3" --width 1024 --color purple --exonnumber > DMD.svg`

![Figure of DMD exons](https://raw.githubusercontent.com/DCRT-LUMC/exonviz/v0.2.2/examples/DMD.svg)


### ATXN1
Include the non coding exons, since most exons of ATXN1 are non coding. We
limit the maximum width and increase the height of the picture. For clarity, we
also increase the distance between the displayed exons:

`exonviz --transcript ENST00000436367.6 --noncoding --width 4000 --height 150 --gap 50 > ATXN1.svg`

![Figure of ATXN1 exons](https://raw.githubusercontent.com/DCRT-LUMC/exonviz/v0.2.2/examples/ATXN1.svg)

### PLP1
You can also input a valid HGVS description on the transcript of interest. The variant will be ignored.
Include the non coding regions and increase the height and distance between the exons:

`exonviz --transcript "NM_000533.5:c.100G>T" --noncoding --height 100 --gap 50 > PLP1.svg`

![Figure of PLP1 exons](https://raw.githubusercontent.com/DCRT-LUMC/exonviz/v0.2.2/examples/PLP1.svg)

### NF1
Set the maximum width of the figure to the approximate size of the largest exon:

`exonviz --transcript "ENST00000358273.9" --noncoding --width 3600 --height 75 --gap 20 > NF1-202.svg`

![Figure of NF1 exons](https://raw.githubusercontent.com/DCRT-LUMC/exonviz/v0.2.2/examples/NF1-202.svg)
