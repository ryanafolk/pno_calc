# pno_calc
This is a simple Predicted Niche Occupancy (PNO) calculator that is intended to be comparable to but faster and more flexible than the implementation in R package `phyloclim`, function `pno`. A PNO is a method of extracting climatic tolerances directly from niche models, expressed in terms of probability of suitability over a series of environmental bins, and is commonly used in ancestral niche reconstruction and other applications.

This script is improved over previous implementations by:
1. Improved spatial statistic efficiency.
2. Using .tif rather than .asc for initial processing steps.
3. Not depending on matching extent between the model and the  -- especially useful where common bins are needed for global extents.


Run like so, after checking that paths are appropriate:
```
./extract_and_join_climatesuitability.sh path_to_models path_to_environmental_data
```

Common projections among models and environmental data are assumed. PNO results are encoded as a csv matrix with rows as species and columns as left-hand histogram bin boundaries; cells are bin probabilities. A set of `sed` commands at the end are intended to remove non-species designations in species names (variable names, etc.); edit as needed.

Note that histograms are normalized but can sum to a number slightly different from one at ~15 decimal places due to float precision limitations. A correction step may be needed for applications that require summing to one (e.g,. the numpy histogram implementation).

Future speed improvements could include skipping the environmental extent-cropping step and only loading environmental data a single time for the spatial join operation across species.
