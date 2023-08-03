#!/usr/bin/env python3
import gzip

gff_header = "seqid source type start end score strand phase attributes".split()

def attributes(line):
    """Convert the attributes to a dict"""
    return {key: value for key, value in (record.split("=") for record in line.split(";"))}


def line_to_gff(line):
    spline = line.strip('\n').split('\t')
    d = {key: value for key, value in zip(gff_header, spline)}
    d["start"] = int(d["start"])
    d["end"] = int(d["end"])
    d["attributes"] = attributes(d["attributes"])
    if "tag" in d["attributes"]:
        d["attributes"]["tag"] = d["attributes"]["tag"].split(',')
    return d


def parse_gff(fname):
    with gzip.open(fname, 'rt') as fin:
        header = next(fin).strip()
        assert header == "##gff-version 3"
        for line in fin:
            if line.startswith("#"):
                continue
            yield line_to_gff(line)


if __name__ == '__main__':
    import sys

    fname = sys.argv[1]
    for record in parse_gff(fname):
        if record["type"] == "transcript" and "MANE_Select" in record["attributes"]["tag"]:
            attr = record["attributes"]
            print(attr["gene_name"], attr['transcript_id'], sep='\t')
