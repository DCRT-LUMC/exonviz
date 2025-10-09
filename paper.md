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

date: 29 September 2025
bibliography: paper.bib
---

# Summary
Transcripts of a gene contain one or more **exons**, which encode the
functional parts of the gene, and **introns**, which are removed in a process
called **splicing**. A single gene typically encodes multiple **transcripts**
by including different exons. Protein coding genes include one or more coding
exons, which encode the protein using three-letter sequences called **codons**.
It is important to realize that exon boundaries and codon boundaries do not
coincide, *i.e.* a codon can span two exons. If the codon boundaries of
adjacent exons are not complementary, this will introduce a shift in the
reading frame, which is often detrimental. The exon reading frame has important
implications when considering the effect of mutations and when designing
genetic therapies.

`ExonViz` is a Python package and web application which creates biologically
accurate RNA transcript figures, including features such as coding regions,
genetic variants and exon reading frames. The [ExonViz
website](https://exonviz.rnatherapy.nl) has been used to generate over 8000
transcript figures between September 2023 and September 2025.

ExonViz is written in Python 3, its web interface is built using Flask. It uses
the public Mutalyzer API [@Lefter2021] to fetch transcript information. This
gives ExonViz access to all transcripts defined in the RefSeq [@OLeary2016] and
Ensembl [@Harrison2024] databases across many species, ranging from human and
mouse to fruit fly and coelacanth. Transcripts and annotations defined on the
reverse strand are reversed on the fly, so ExonViz always visualizes
transcripts in their forward orientation.

![Example transcript highlighting ExonViz features. **5' UTR**: Non coding
region at the start of the transcript. **CDS start**: Start of the coding
region. **CDS end**: End of the coding region. **3' UTR**: Non coding region at
the end of the transcript.\label{abstract}](docs/figures/abstract.svg)

# Statement of need
Visualization of transcripts, including features like coding and non coding
regions, exon reading frames and the mutational landscape is important within
the field of clinical and human genetics [@Walker2023]. Illustrating the exon
structure and the distribution of variants over the gene is common practice,
especially when new genes or transcripts have been discovered. These
illustrations are also used to assess potential genetic treatment options
(e.g., canonical exon skipping), in teaching settings, in diagnostics, to
identify mutational hotspots and for genetic counseling. To date, most people
have to resort to manually drawing transcripts with tools like Illustrator,
Photoshop or BioRender, or forgo illustrations altogether. Some tools have been
made available that aid in drawing transcripts (ggtranscript [@Gustavsson2022]
and wiggleplotr [@Alasoo2017]), visualize different transcript isoforms
(genepainter [@Muhlhausen2015]), or visualize variants (Variant View
[@Ferstay2013]). However, none of these tools can automatically draw exon
reading frames. Knowledge about the exon frames aids in the assessment of the
pathogenicity of genetic variants using the ACMG-AMP guidelines [@Richards2015]
when evaluating exon spanning deletions [@Cheerie2025] and when interpreting
the effects of splice altering variants [@Walker2023]. Creating transcript
visualizations must be quick and easy if they are to be utilized in clinical
and day to day settings, rather than to create a bespoke figure for a
manuscript or presentation.

To our knowledge, there currently are no easily usable tools which allows the
users to draw all features required for a comprehensive overview of a
transcript’s structure and the localisation of variants of interest.

# Method
ExonViz visualizes the exon reading frames by using different shapes for the
start and end of exons. It is important that adjacent exons have complementary
codon boundaries, to prevent a shift in the reading frame of the protein.
Figure \ref{explainer} shows all possible combinations of exon and codon
boundaries, and the corresponding exon shapes. When the exon and codon
boundaries coincide (frame 0) the exons are drawn with a straight edge, as is
the case of exon 1 and 2. Exon 2 ends one base into the codon (in frame 1),
which is drawn using an arrow on the end of the exon. Exon 3 starts in frame 1,
and is drawn with a notch at the start of the exon. This reversed for the
boundary between exons 3 and 4, which is in frame 2. Since the exons of a
transcript should fit together, exons in conflicting frames (*e.g.* because of
a frame shift inducing variant) are easily spotted due to the fact that the
exon boundaries do not fit together.

![Visualization of the relation between codons and exon frames. The shapes of
the exons illustrate the relation between the exon boundaries and the codon
boundaries.\label{explainer}](docs/figures/exonviz-explainer.svg)

The output of ExonViz is an SVG figure generated using the svg-py library,
which can be used directly or modified using modern graphical editing programs.
It is also possible to output the transcript and variants in TSV format, edit
the transcript using any text editor or spreadsheet program, and draw the
modified transcript using ExonViz. The [online
documentation](https://exonviz.readthedocs.io/en/latest/examples.html) has a
number of examples of custom transcripts that can be visualized this way.

# Conclusion
To our knowledge, ExonViz is the first publicly accessible application that
allows for automatic visualization of transcripts with additional features such
as exon reading frames and variants along the transcript. ExonViz can be used for
illustrations within publications, assessment of treatment options, for
teaching purposes and genetic counseling. Figures generated by ExonViz are free
to use under the Creative Commons BY license . Furthermore, we allow the user
to construct their own transcripts to incorporate features like poison or
cryptic exons and alternative isoforms. ExonViz can be accessed as a web
application via [exonviz.rnatherapy.nl](https://exonviz.rnatherapy.nl) or
installed via [PyPI](https://pypi.org/project/exonviz/). The source code is
available on [Github](https://github.com/DCRT-LUMC/exonviz).

# Acknowledgments
We would like to thank the members of the Dutch Center for RNA Therapeutics for
their ideas, suggestions and their feedback on earlier versions of ExonViz. We
also thank Maximilian Haeussler and his colleagues at the UCSC for their
efforts implementing exon reading frame information into the UCSC Genome
Browser. We also thank Nanieke van den Berg for creating Figure \ref{abstract}.

# References
