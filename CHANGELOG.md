# Changelog

<!---
Newest changes should be on top.

This document is user facing. Please word the changes in such a way
that users understand how the changes affect the new version.
--->

## v0.2.4-dev
+ Use mutalyzer_hgvs_parser to check user input
+ Include the smallest scale a transcript can be drawn at in the error message
  when the scale is too small
+ Fix a bug where the legend is truncated if it is wider than the transcript,
  but smaller than the page
+ Add check for invalid values for `--width`, `--height`, `--scale` and `--gap`
  when drawing
+ Scale estimated legend size with the specified `--height`
+ Add explicit `--scale` option
+ Fix a bug breaking `--firstexon` and `--lastexon` option

## v0.2.3
+ Include the coordinate system in variant name
+ Set four Kelly Colors as default
+ Add --variantcolors to the configuration

## v0.2.2
+ Various bug fixes for un-drawable exons

## v0.2.0
+ Big refactor
+ Add support for displaying variants on exons
+ Add support for breaking off long exons

## v0.2.0
+ Big refactor

## v0.1.4
+ Drop support for Python 3.8
+ Add support for drawing only part of the transcript
+ Add support for gene names (defaults to MANE_Select transcript)
+ Add option to show exon number

## v0.1.3
+ Refactor drawing fuction to take a configuration dict
+ Add default configuration for drawing
+ Add option to set the color

### Breaking changes
+ Rename `--max-width` to `--width`
+ Rename `--non-coding` to `--noncoding`
+ `draw_exons` now takes a configuration dictionary

## v0.1.2
+ Be explicit about which functions we expose

## v0.1.1
+ Publish type hints when used as a library
+ Expose interface functions at the package level
+ Fix a bug where mutalyzer errors are written to STDOUT

## v0.1.0
+ Various changes related to packaging

## v0.0.1
+ Add additional options to customise the figure
+ Initial development
