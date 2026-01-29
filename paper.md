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
called **codons**. It is important to realize that exon boundaries and codon
boundaries do not coincide, *i.e.* single a codon can span two exons. If the codon
boundaries of adjacent exons are not aligned, an often detrimental **frame
shift** is introduced. Taking exon boundary reading frames, which we will call
**exon boundary frames**, into account is crucial when considering the effect of
mutations and when designing genetic therapies.

`ExonViz` is a Python package and web application that creates biologically
accurate RNA transcript figures, including features such as coding regions,
genetic variants and exon boundary frames.

![Example transcript highlighting ExonViz features. **5' UTR**: Non coding
region at the start of the transcript. **CDS start**: Start of the coding
region. **CDS end**: End of the coding region. **3' UTR**: Non coding region at
the end of the transcript.\label{abstract}](docs/figures/abstract.svg)

# Statement of need
Visualization of transcripts, including features like exon boundary frames,
coding and non coding regions is important within the field of clinical and
human genetics [@Walker2023]. Illustrating the exon structure and the location
of variants is common practice, especially when new genes, variants or transcripts have
been discovered. These illustrations are also used to assess potential genetic
treatment options (e.g., canonical exon skipping), in teaching settings, in
diagnostics, to identify mutational hotspots and for genetic counseling. In
particular knowledge about the exon boundary frames aids in the assessment of
the pathogenicity of genetic variants using the ACMG-AMP guidelines
[@Richards2015], when evaluating exon spanning deletions [@Cheerie2025] and
when interpreting the effects of splice altering variants [@Walker2023].

To date, most people have to resort to manually drawing transcripts with tools
like Illustrator, Photoshop or BioRender, or forgo illustrations altogether.
Creating transcript visualizations must be quick and easy to be utilized in
clinical and day to day settings, rather than to create a bespoke figure for a
manuscript or presentation.

# State of the field
Several tools have been made available to visualize various aspects of genes
and transcripts. ggtranscript [@Gustavsson2022] and wiggleplotr [@Alasoo2017])
can visualize transcripts and exons, while tools like genepainter
[@Muhlhausen2015] or Swan [@Reese] can be used to visualize different
transcript isoforms. Variants can be shown on the transcript with Variant View
[@Ferstay2013]. However, all of these tools require substantial expertise to
setup and retrieve the required transcript models, which make them hard to use
for users with minimal technical expertise. Furthermore, none of them have the
option to indicate exon boundary frames.

To our knowledge there are currently no easily usable tools which allow the
user to draw all features required for a comprehensive overview of a
transcript’s structure and the location of variants of interest.

# Software design
ExonViz is written in Python 3, its web interface is build using Flask. To
avoid the complexities of retrieving and processing various different
transcript definitions, ExonViz uses the public Mutalyzer API [@Lefter2021] to
fetch transcript annotations. This gives ExonViz access to all transcripts
defined in the RefSeq [@OLeary2016] and Ensembl [@Harrison2024] databases
across many species, ranging from human and mouse to fruit fly and coelacanth.

Reverse strand transcript are inverted so that ExonViz always visualizes
transcripts in their forward orientation. This avoids the complications that
come with the inverted annotations for transcripts which are annotated on the
reverse strand of the chromosome. Variants are assigned to their corresponding
Exon, which also contains the size, coding region and other features which are
required to draw an Exon. Exons can be split to ensure they do not go over the
specified page width, analogous to how long words can be split over multiple
lines.

ExonViz can also read and write the normalized Exon and Variant models,
allowing the user to specify custom transcripts and exons in a simple TSV
format.

# Method
ExonViz visualizes the exon boundary frames by using different shapes for the
boundary of exons.
Figure \ref{explainer} shows all possible combinations of exon and codon
boundaries, and the corresponding exon boundary shapes. When the exon and codon
boundaries coincide (frame 0) the exons are drawn with a straight edge, as is
the case of exon 1 and 2. Exon 2 ends one base into the codon (in frame 1),
which is drawn using an arrow on the end of the exon. Exon 3 starts in frame 1,
and is drawn with a notch at the start of the exon. This reversed for the
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
[@Cheerie2025]. In addition, the [ExonViz
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

# References
