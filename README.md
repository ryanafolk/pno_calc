# pno_calc
This is a simple Predicted Niche Occupancy (PNO) calculator that is intended to be comparable to but faster and more flexible than the implementation in R package `phyloclim`, function `pno`, for global-scale datasets at high resolution. A PNO is a method of extracting climatic tolerances directly from niche models, expressed in terms of probability of suitability over a series of environmental bins, and is commonly used in ancestral niche reconstruction and other applications.

This script is improved over previous implementations by:
1. Improved spatial statistic efficiency.
2. Using .tif rather than .asc for initial processing steps.
3. Not depending on matching extent between the model and the environmental data -- especially useful where common bins are needed for global extents.


Run like so:
```
bash extract_and_join_climatesuitability.sh path_to_model_folder path_to_environmental_data_folder
```

Common projections among models and environmental data (but NOT necessarily extents) are assumed. Missing data is assumed to be -9999. PNO results are encoded as a csv matrix with rows as species and columns as left-hand histogram bin boundaries; cells are bin probabilities. A set of `sed` commands at the end are intended to remove non-species designations in species names (variable names, etc.); edit as needed.

Two modules at the end, `binner_climateextraction.py` and `bin_trimmer.py` are optional. The former adds point extraction data to an existing PNO file (e.g., for species with too few occurrences to model directly) and the latter drops columns with low probability for all species (hard coded as <1e-4). The path to point extraction data is also hard-coded in the shell script -- change as needed.

Note that histograms are normalized but can sum to a number slightly different from one at ~15 decimal places due to float precision limitations. A correction step may be needed for applications that require summing to one.

Future speed improvements could include skipping the environmental extent-cropping step and only loading environmental data a single time for the spatial join operation across species.

# Dependencies
1. GDAL library executables in path: `gdal_translate`, `gdalwarp`, `gdaltindex`.
2. Python libraries `numpy`, `pandas`.
