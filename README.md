[![Continous integration](https://github.com/DCRT-LUMC/exonviz/actions/workflows/ci.yml/badge.svg)](https://github.com/DCRT-LUMC/exonviz/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Documentation Status](https://readthedocs.org/projects/exonviz/badge/?version=latest)](https://exonviz.readthedocs.io/en/latest/?badge=latest)
[![Last commit](https://img.shields.io/github/last-commit/DCRT-LUMC/exonviz.svg)](https://img.shields.io/github/last-commit/DCRT-LUMC/exonviz.svg)
[![Release](https://img.shields.io/github/release/DCRT-LUMC/exonviz.svg)](https://img.shields.io/github/release/DCRT-LUMC/exonviz.svg)
[![PyPI](https://img.shields.io/pypi/v/exonviz.svg)](https://img.shields.io/pypi/v/exonviz.svg)
[![Commits since latest release](https://img.shields.io/github/commits-since/DCRT-LUMC/exonviz/latest)](https://img.shields.io/github/commits-since/DCRT-LUMC/exonviz/latest)

# Exonviz
ExonViz is a simple tool to draw transcripts that include coding
and non-coding regions. All exons are to scale and the reading frames of the
exons are visible. Single or multiple variants along the transcript can be
drawn and will automatically be shown in the correct location.

## Online version
You can try out ExonViz online at [exonviz.rnatherapy.nl](https://exonviz.rnatherapy.nl).

## Installation
ExonViz only requires Python, and can be installed using PIP:
```
pip install exonviz

# If you want to run the exonviz website locally, use
pip install exonviz[website]
```

## Usage
Simply supply either a transcript (with version!), or a valid HGVS description
to exonviz to generate a figure:

```bash
exonviz --transcript "NM_003002.4:r.[274G>T;300del]" > SHDH.svg
```
![Figure for SHDH](https://exonviz.readthedocs.io/en/latest/_images/SDHD.svg)

### Documentation
The documentation for ExonViz is available on [Readthedocs][readthedocs],
including some [examples][examples] of what is possible using the command line
version of ExonViz.


## Contributions and support
Please see our [contribution guidelines][contribution] report bugs, suggest new features or ask for support.

## Citation
Please cite our [pre-print][pre-print] if you use ExonViz:

>ExonViz: A website and Python package to visualize transcripts and genetic variants
>Redmar R. van den Berg, Marlen C. Lauffer, Jeroen F.J. Laros
>medRxiv 2024.09.18.24313945; doi: https://doi.org/10.1101/2024.09.18.24313945

[contribution]: https://github.com/DCRT-LUMC/exonviz/blob/main/.github/CONTRIBUTING.md
[pre-print]: https://www.medrxiv.org/content/10.1101/2024.09.18.24313945v1
[readthedocs]: https://exonviz.readthedocs.org
[examples]: https://exonviz.readthedocs.io/en/latest/examples.html
