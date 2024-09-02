Introduction
============

ExonViz is a simple tool to generate and draw transcripts that include coding
and non-coding regions. All exons are to scale and the reading frames of the
exons are visible. Single or multiple variants along the transcript can be
drawn and will automatically be shown in the correct location. Further, we
allow the user to generate their own transcripts to incorporate features like
poison or cryptic exons. ExonViz can be accessed as a web-application via
`exonviz.rnatherapy.nl <https://exonviz.rnatherapy.nl>`_, and is also available
as a python package from `PyPI <https://pypi.org/project/exonviz/>`_. The
source code is available on `github <https://github.com/DCRT-LUMC/exonviz>`_.

How it works
============
The transcript specified by the user, including any variants, is retrieved
using Mutalyzer, and all relevant information such as coding region and exon
sizes are extracted. When using the command line version of ExonViz, it is also
possible to specify custom transcripts.

If the user specifies a gene name, the corresponding `MANE Select
<https://www.ncbi.nlm.nih.gov/refseq/MANE/>`_ transcript will automatically be
selected. If there are multiple MANE Select transcripts defined for a gene, the
first transcript will be used. ExonViz uses MANE Select release 1.2.

To indicate the difference between the coding and non-coding regions of the
transcript, the non-coding regions is drawn at half the hight of the coding
region.

The start and end phase of coding exons are indicated using notches and arrows.
If the end of the exon coincides with the codon boundary (phase 0), the exon
end is drawn straight.

Variants are drawn inside the correct exon, and a legend is shown at the bottom
of the figure. By default, ExonViz will cycle through the same five colors for
the variants, but this can be specified by the user. If the same `name` and
`color` is used for multiple variants, they will only be shown once in the
legend. This can be useful when there are many variants, and the color is based
on e.g. the pathogenicity of the variants.

Settings
========
scale
-----
The `scale` of the drawing determines how many pixels are used per basepair of
the transcript. The default scale is 1:1, which means that an exon of 100bp
will be drawn 100 pixels long.

height
------
The `height` of the drawing determines how high each exon is drawn, and also
determines the size of the notches and arrows (0.25 * `height`, to be exact).

Because we need a certain amount of space to draw the notches and arrows, some
transcripts cannot be drawn at the default `scale` and `height`. For example,
transcript `ENST00000621218.5` of `PLP1` must be drawn at a `scale` of at least
`1.3` with the default `height`, because only the very last few basepairs of
the first exons are coding.

width
-----
The `width` determines the maximum width of the figure. ExonViz guarantees that
the figure will not go over this limit. It will try to distribute the exons in
such a way that every row of the figure is filled. Sometimes, an exon will be
split over multiple rows to ensure they fit. If this happens, the name of the
exon (usually its number) will be shown for every split of the exon.

The legend will also be split over multiple rows, unless the variant name is so
long that it will not fit on the page by itself. If this is the case, ExonViz
will display an error.

When using the command line version, the names of both variants and exons can
be modified.

noncoding
---------
By default, the non-coding regions of the transcript are not show, but this can
be changed using the `noncoding` option.

gap
---
`gap` determines the gap between exons when they are drawn on the same row.

color
-----
`color` determines the color of the exons. When using the command line version,
the color of individual exons can be set.

exonnumber
----------
Set the name of the exons to their number. By default, exons have no name. When
using the command line version, the name of each exon can be customised.

firstexon and lastexon
----------------------
These two options can be used to only draw a subset of the specified
transcript, which can be useful for very large genes.

variantcolors
-------------
This option determines the list of colors that ExonViz will cycle through for
the specified variants.

--dump-exons and --dump-variants
--------------------------------
Use these two flags to write the exons and variants to the specified
files. This allows the user to modify the retrieved transcript in a simple
spreadsheet program, and later draw the modified transcript.
These option are only available for the command line version.

--exon-tsv and --variant-tsv
----------------------------
Rather than query Mutalyzer for the transcript information, read the exons and
variants from the specified tsv files.
These option are only available for the command line version.
