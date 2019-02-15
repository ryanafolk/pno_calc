#!/usr/bin/env python3

import argparse
import numpy
import subprocess
import pandas
import re
import sys

parser = argparse.ArgumentParser(description='Script to do PNO binning.')
parser.add_argument('pnofile', action='store', help='Name of a PNO file generated with binner.py.')
parser.add_argument('outfile', action='store', help='Name of the desired output file.')
parser.add_argument('-x','--infiles', nargs='+', help='Names of files representing point extraction in PNO format.', required=True)
args = parser.parse_args()

files = args.infiles
pnofile = args.pnofile
outfile = args.outfile

dataframe = pandas.read_csv(pnofile)

bins = list(dataframe.columns.values)
bins.pop(0)
bins = [float(x) for x in bins]
bins.append(bins[-1] + (bins[1] - bins[0]))

species = [re.sub('\..*', '', re.sub('.*_pno_', '', file)) for file in files]

data = {re.sub('\..*', '', re.sub('.*/', '', file)): pandas.read_csv(file) for file in files}

for x, y in zip(data, species):
	print("On file: {0}: {1}".format(y, x))
	climate_values = list(data[x]['variable'])
	climate_values = [((bins[1] + bins[0])/2) if y < bins[0] else y for y in climate_values] # Recode climate values to be in center of first bin if they are lower than first bin
	climate_values = [((bins[-2] + bins[-1])/2) if y > bins[-1] else y for y in climate_values]	# Recode climate values to be in center of last bin if they are higher than last bin
	hist, bin_edges = numpy.histogram(climate_values, bins = bins)
	hist = hist/hist.sum() # This works better than numpy.histogram(density = True)
	hist = list(hist)
	print("Integral of histogram is: {0}".format(sum(hist)))
	hist.insert(0, y)
	dataframe.loc[len(dataframe)] = hist
	print(hist)
	
print(dataframe)

dataframe.to_csv(path_or_buf=outfile, sep=",", index = False)

