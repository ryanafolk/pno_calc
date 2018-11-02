#!/usr/bin/env python3

import argparse
import numpy
import subprocess
import pandas
import re

parser = argparse.ArgumentParser(description='Script to do PNO binning.')
parser.add_argument('minfile', action='store', help='Name of the input minimum file -- list of values.')
parser.add_argument('maxfile', action='store', help='Name of the input maximum file -- list of values.')
parser.add_argument('bins', action='store', help='Number of bins.')
parser.add_argument('outfile', action='store', help='Name of the desired pre-coded output file.')
parser.add_argument('-x','--infiles', nargs='+', help='List of discrete column headers.', required=True)
args = parser.parse_args()

files = args.infiles
minfile = args.minfile
maxfile = args.maxfile
bins = int(args.bins)
bins += 1 # We iterate this because we want n+1 bin boundaries for n bins
outfile = args.outfile

min = subprocess.check_output(['sort -n -r minima.tmp | tail -1'], shell = True)
min = float(min.splitlines()[0]) # Parse shell output

max = subprocess.check_output(['sort -n maxima.tmp | tail -1'], shell = True)
max = float(max.splitlines()[0]) # Parse shell output

print("Min and max are {} and {}.".format(min, max))

range = max - min
binlist = numpy.linspace(min, max, bins, endpoint=True)
#print(binlist)
#print(len(binlist))

species = [re.sub('\..*', '', re.sub('.*/', '', file)) for file in files]

data = {re.sub('\..*', '', re.sub('.*/', '', file)): pandas.read_csv(file, sep=' ', header=None, encoding = 'utf-8') for file in files}

for i in data:
	data[i] = data[i].astype("float")

#print(data[2])

#print(totalsuitability)

output = pandas.DataFrame(index=species, columns=binlist[:-1])
output = output.fillna(0)

print("Working on file:")
for key, datum in data.items():
	print(key)
	totalsuitability = numpy.sum(datum[2]) # Second column is suitabilities
	binheight = []
	for first, second in zip(binlist, binlist[1:]):
		slice = datum.loc[(datum[3] >= first) & (datum[3] < second)]
		if slice.empty:
			#print("No suitability in bin.")
			pass
		else:
			output.loc[[key],first] = sum(slice[2])/totalsuitability # Insert at bin start column and species row
			#print(output.loc[[key],first])

print("Row sums; should be close to one:")
for index, row in output.iterrows():
	print(sum(output.loc[index, : ]))

output.to_csv(path_or_buf=outfile, sep=",")	
