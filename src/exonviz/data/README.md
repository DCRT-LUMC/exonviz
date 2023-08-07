# Data files
## mane.txt.gz
A file which contains a mapping of gene name to MANE(release 1.2) transcript, from the NCBI.

```bash
# Download the GFF3 file of MANE transcripts from NCBI:
wget https://ftp.ncbi.nlm.nih.gov/refseq/MANE/MANE_human/release_1.2/MANE.GRCh38.v1.2.ensembl_genomic.gff.gz

# Extract the gene name to MANE transcript mapping
python3 extract_mane.py MANE.GRCh38.v1.2.ensembl_genomic.gff.gz |gzip > mane.txt.gz
```
