paper.pdf: paper.md paper.bib docs/figures/abstract.svg docs/figures/exonviz-explainer.svg
	pandoc paper.md -o paper.pdf -C
