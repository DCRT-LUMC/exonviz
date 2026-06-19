---
title: 'ExonViz: Transcript visualization made easy'
tags:
  - Python

authors:
 - name: Redmar van den Berg
   orcid:
   affiliation: "1, 2, 3"
   orcid: 0000-0002-6590-9499

 - name: Marlen C. Lauffer
   orcid:
   affiliation: "1, 2"
   orcid: 0000-0003-1607-0428

 - name: Jeroen F.J. Laros
   orcid:
   affiliation: "1, 4"
   orcid: 0000-0002-8715-7371

affiliations:
 - name: Department of Human Genetics, Leiden University Medical Center, The Netherlands
   index: 1

 - name: Dutch Center for RNA Therapeutics, Department of Human Genetics, Leiden University Medical Center, The Netherlands
   index: 2

 - name: Department of Hematology, Leiden University Medical Center, The Netherlands
   index: 3

 - name: Department of Bioinformatics and Computational Services, National Institute of Public Health and the Environment, The Netherlands
   index: 4

bibliography: paper.bib
---

# Summary
Transcripts of a gene contain one or more **exons**, which encode the
functional parts of the transcript, and **introns**, which are removed in a
process called **splicing**. A single gene typically encodes multiple
**transcripts** by including different exons. Protein coding genes include one
or more coding exons, which encode a protein using three-letter sequences
called **codons**. These codons do not necessarily coincide with exon
boundaries, because a single codon can span two exons. If the codon boundaries
of adjacent exons are not aligned, an often detrimental **frame shift** is
introduced. Taking exon boundary reading frames, which we will call **exon
boundary frames**, into account is crucial when considering the effect of
mutations and when designing genetic therapies such as exon skipping.

`ExonViz` is a Python package and web application that creates biologically
accurate RNA transcript figures, including features such as coding regions,
genetic variants and exon boundary frames. Any transcript defined by Ensembl or
RefSeq (which contains over 150.000 species as of 2026) can be retrieved and
visualized automatically.

![Example transcript highlighting ExonViz features. **5' UTR**: Non coding
region at the start of the transcript. **CDS start**: Start of the coding
region. **CDS end**: End of the coding region. **3' UTR**: Non coding region at
the end of the transcript.\label{abstract}](docs/figures/abstract.svg)

# Statement of need
Visualization of transcripts, including features like exon boundary frames,
coding and non coding regions is important within the field of clinical and
human genetics [@Walker2023]. Illustrating the exon structure and the location
of variants is common practice, especially when new genes, variants or
transcripts have been discovered. These illustrations are also used to assess
potential genetic treatment options (e.g., canonical exon skipping), in
teaching settings, in diagnostics, to identify mutational hotspots and for
genetic counseling. In particular, knowledge about the exon boundary frames aids
in the assessment of the pathogenicity of genetic variants using the ACMG-AMP
guidelines [@Richards2015], when evaluating exon spanning deletions
[@Cheerie2025] and when interpreting the effects of splice altering variants
[@Walker2023].

To date, most people have to resort to manually drawing transcripts with tools
like Illustrator, Photoshop or BioRender, or forgo illustrations altogether.
Creating transcript visualizations should be quick and easy to be utilized in
clinical and day to day settings, rather than to create a bespoke figure for a
manuscript or presentation.

# State of the field
Several tools have been made available to visualize various aspects of genes
and transcripts. ggtranscript [@Gustavsson2022] and wiggleplotr [@Alasoo2017]
can visualize transcripts and exons, while tools like genepainter
[@Muhlhausen2015] or Swan [@Reese2021] can be used to visualize different
transcript isoforms. Variants can be shown on the transcript with Variant View
[@Ferstay2013]. However, all of these tools require substantial expertise to
setup and retrieve the required transcript models, which make them hard to use
for users with minimal technical expertise. Furthermore, none of them have the
option to indicate exon boundary frames.

To our knowledge there are currently no easily usable tools available which
allow a non-technical user to quickly draw all features required for a
comprehensive overview of a transcript’s structure and the location of variants
of interest.

# Software design
Biological transcripts are deceptively complex and can consist of introns,
exons and a coding region defined on either the forward or reverse strand of a
reference sequence. Introns are usually the largest structures in a transcript,
as a single intron can be larger than all exons of a transcript combined.

For ExonViz, we opted to hide this complexity and focus on the exon as the
central unit, with a transcript being defined simply as a sequence of Exons. We
also ignore the strand of the transcript on the reference sequence, effectively
rewriting all transcripts to be defined on the forward orientation. The
information of each exon is stored in the `Exon` class, which consist only of a
size and optional coding region, without a specified location on the reference
sequence. `Exon`s can also have a name, color and a list of (named) variants
which will be included in the visualization.

The `Exon` class also hold the required functionality for drawing an exon, such
as the rendered size of the exon, the minimum scale at which the exon can be
drawn, as well as methods to split an `Exon` (analogous to how long words can
be split over multiple lines).

The `Exon` class can be imported and used directly and users can also specify
exons in a simple TSV format as described in the documentation of ExonViz. To
give users access to existing transcript definitions, ExonViz supports
automatic retrieval of transcript definitions from the Mutalyzer API
[@Lefter2021], which helps avoid the complexities of retrieving and processing
various different transcript definition formats. This gives ExonViz access to
all transcripts defined in the RefSeq [@OLeary2016] and Ensembl [@Harrison2024]
databases across many species, ranging from human and mouse to fruit fly and
coelacanth. This wide range of supported transcripts is also why we decided not
to bundle any transcript definitions with ExonViz itself.

Mutalyzer is actively being developed in our group and will be maintained for
the foreseeable future, which made it an obvious choice to use. Should the
mutalyzer website become unavailable, it is also possible to run a local
install of mutalyzer with caching for offline usage.

Due to the simple structure of the `Exon` class, adding novel sources of
trancript information in the future, such as gtf or gff files, should not be
too difficult.

# Method
ExonViz visualizes the exon boundary frames by using different shapes for the
boundary of exons.
Figure \ref{explainer} shows all possible combinations of exon and codon
boundaries, and the corresponding exon boundary shapes. When the exon and codon
boundaries coincide (frame 0) the exons are drawn with a straight edge, as is
the case of exon 1 and 2. Exon 2 ends one base into the codon (in frame 1),
which is drawn using an arrow on the end of the exon. Exon 3 starts in frame 1,
and is drawn with a notch at the start of the exon. This is reversed for the
boundary between exons 3 and 4, which is in frame 2. Since the exons of a
transcript should fit together, exons in conflicting frames (*e.g.* because of
a frame shift inducing variant) are easily spotted due to the fact that the
exon boundaries do not fit together.

![Visualization of the relation between codons and exon boundary frames. The shapes of
the exons illustrate the relation between the exon boundaries and the codon
boundaries.\label{explainer}](docs/figures/exonviz-explainer.svg)

The output of ExonViz is an SVG figure generated using the svg-py library,
which can be used directly or modified using modern graphical editing programs.
It is also possible to output the transcript and variants in TSV format, edit
the transcript using any text editor or spreadsheet program, and draw the
modified transcript using ExonViz. The [online
documentation](https://exonviz.readthedocs.io/en/latest/examples.html) has a
number of examples of custom transcripts that can be visualized this way.

# Research impact statement
ExonViz has proven to be a useful resource to quickly visualize exon reading
frames and check the location of variants in a transcript. ExonViz is actively
being used in the field of personalized medicine and is one of the recommended
resources in the latest consensus guidelines for assessing pathogenic variants
for RNA therapies [@Cheerie2025]. In addition, the [ExonViz
website](https://exonviz.rnatherapy.nl) has been used to generate over 8000
transcript figures between September 2023 and September 2025.

# Conclusion
To our knowledge, ExonViz is the first publicly available application that
allows for automatic visualization of transcripts with additional features such
as exon boundary frames and variants along the transcript. ExonViz can be used for
illustrations within publications, assessment of treatment options,
teaching purposes and genetic counseling. Figures generated by ExonViz are free
to use under the Creative Commons BY license. Furthermore, we allow the user
to construct their own transcripts, for example to visualize non-standard exons
or alternative isoforms. ExonViz can be accessed as a web application via
[exonviz.rnatherapy.nl](https://exonviz.rnatherapy.nl) or installed via
[PyPI](https://pypi.org/project/exonviz/). The source code is available on
[Github](https://github.com/DCRT-LUMC/exonviz).

# AI usage disclosure
No generative AI tools have been used for ExonViz, the documentation or this
manuscript.

# Acknowledgments
We would like to thank the members of the Dutch Center for RNA Therapeutics for
their ideas, suggestions and their feedback on earlier versions of ExonViz. We
also thank Maximilian Haeussler and his colleagues at the UCSC for their
efforts implementing exon boundary frame information into the UCSC Genome
Browser. We also thank Nanieke van den Berg for creating Figure \ref{abstract}.

# Financial support
Redmar R. van den Berg is supported by a ZonMW PSIDER grant and a grant from
the Human Genetics department of the Leiden University Medical Center. Marlen
C. Lauffer is supported by a Walter Benjamin Fellowship from the German
Research Foundation and a Sectorplannen position in the Neuroscience Theme from
the Dutch government.

# References
