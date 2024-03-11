Usage
=====

.. _installation:

Installation
------------

ExonViz can be installed using pip:

.. code-block:: console

   pip install exonviz

Default usage
-------------

.. code-block:: console

   exonviz --transcript DMD > DMD.svg

Command line
------------

.. code-block:: console

   usage: exonviz [-h] [--width WIDTH] [--height HEIGHT] [--scale SCALE]
                  [--noncoding] [--gap GAP] [--color COLOR] [--exonnumber]
                  [--firstexon FIRSTEXON] [--lastexon LASTEXON]
                  [--variantcolors VARIANTCOLORS [VARIANTCOLORS ...]]
                  [--dump-exons DUMP_EXONS] [--dump-variants DUMP_VARIANTS]
                  (--transcript TRANSCRIPT | --exon-tsv EXON_TSV)
                  [--variant-tsv VARIANT_TSV]

   Visualise exons and mutations

   options:
     -h, --help            show this help message and exit
     --width WIDTH         Maximum width of the figure (default: 9999999)
     --height HEIGHT       Exon height (default: 20)
     --scale SCALE         Scale (pixels per bp) (default: 1.0)
     --noncoding           Show non coding regions (default: False)
     --gap GAP             Gap between the exons (default: 0)
     --color COLOR         Color for the exons (e.g. 'purple') (default: #4C72B7)
     --exonnumber          Show exon number (default: False)
     --firstexon FIRSTEXON
                           The first exon to draw (default: 1)
     --lastexon LASTEXON   The last exon to draw (default: 9999)
     --variantcolors VARIANTCOLORS [VARIANTCOLORS ...]
                           List of variant colors to cycle through (default:
                           ['#BA1C30', '#DB6917', '#EBCE2B', '#702C8C',
                           '#C0BD7F'])
     --dump-exons DUMP_EXONS
                           Write exons to the specified file (default: None)
     --dump-variants DUMP_VARIANTS
                           Write variants to the specified file (default: None)
     --transcript TRANSCRIPT
                           Transcript (with version) to visualise (default: None)
     --exon-tsv EXON_TSV   TSV file containing exons (default: None)
     --variant-tsv VARIANT_TSV
                           TSV file containing variants (default: None)
