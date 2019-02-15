#!/usr/bin/env python3

import argparse
import numpy
import subprocess
import pandas
import re
import sys

parser = argparse.ArgumentParser(description='Script to do PNO binning.')
parser.add_argument('infile', action='store', help='Name of a PNO file generated with binner.py or similar.')
parser.add_argument('outfile', action='store', help='Name of the desired output file.')
args = parser.parse_args()

infile = args.infile
outfile = args.outfile

dataframe = pandas.read_csv(infile)

binlist = list(dataframe.columns)
binlist.pop(0)
print(binlist)

droplist = [i for i in binlist if numpy.max([float(x) for x in dataframe[i]]) < 1e-4]

print(droplist)

print("{0} columns dropped for file {1}.".format(len(droplist), infile))

dataframe.to_csv(path_or_buf=outfile, sep=",", index = False)

