## PNO calculator script
## Must have gdal tools in path
#
modelpath=$1
layerpath=$2
extractionpath=$3
numberbins=$4

mkdir cropped_environment
mkdir model_dataframe
mkdir joined_data
mkdir results

#######
# We start by generating joined dataframes of suitability and climate attributes
for h in ${modelpath}/*; do
i=$(echo ${h} | sed 's/.*\///g') # Model file name
i=$(echo ${i} | sed 's/\..*//g') # Species name
gdaltindex ${i}.shp ${h} # Shape file from model extent
gdal_translate -of XYZ ${h} ./model_dataframe/${i}.xyz # Output in dataframe-like format

for f in ${layerpath}/*.tif; do
g=$(echo ${f} | sed 's/.*\///g') # Environmental data file name
g=$(echo ${g} | sed 's/\..*//g') # Variable name
echo ${f}
echo ${h}
gdalwarp -cutline ${i}.shp -crop_to_cutline ${f} ./cropped_environment/${g}_${i}.tif # Cut environmental data to model extent
gdal_translate -of XYZ ./cropped_environment/${g}_${i}.tif ./cropped_environment/${g}_${i}.xyz # Output in dataframe-like format

# This command creates a key with awk comprising the first two fields of each XYZ file, inserted as a first column.
# Then it sorts on this key and does a join on this field, printing the right fields, then deleting any missing data.
join -j 1 -o 1.2,1.3,1.4,2.4 <(awk '{print $1"-"$2" "$0}' ./model_dataframe/${i}.xyz | sort -S 25% -k1,1 ) <(awk '{print $1"-"$2" "$0}' ./cropped_environment/${g}_${i}.xyz | sort -S 25% -k1,1 ) | sed '/-9999/d' > ./joined_data/${g}_${i}.xyz

done

rm ${g}.shp ./cropped_environment/${g}_${i}.tif # Clean up
rm ./model_dataframe/${i}.xyz ./cropped_environment/${g}_${i}.xyz
done

rm *.shp *.shx *.dbf

#########
# Now per variable we do the PNO calculation

# Find global occupied minima and maxima for variable

rm minima.tmp
rm maxima.tmp

i=$(ls ./joined_data/*.xyz | wc -l) # Number of relevant files in directory
j=1 # Progress counter
for y in ${layerpath}/*.tif; do
z=$(echo ${y} | sed 's/.*\///g') # Environmental data file name
z=$(echo ${z} | sed 's/\..*//g') # Variable name
echo ${z}

for f in $(ls ./joined_data/${z}_*.xyz); do # Include underscore to avoid incorrect hits
cut -d" " -f4 ${f} | sort -n -S 50% | sed -n '1p;$p' > tmp.tmp # First line is min second line is max
head -1 tmp.tmp >> minima.tmp
tail -1 tmp.tmp >> maxima.tmp
# Progress
k=$(bc -l <<< "scale=2; ${j}/${i} * 100") # Calculate percent
echo "${k}%"
let "j++" # Iterate progress counter
done

echo "Starting binning calculation"
python3 binner.py minima.tmp maxima.tmp $numberbins ./results/${z}.out -x ./joined_data/${z}_*.xyz

rm minima.tmp maxima.tmp
done

# Clean up matrix, removing variable names
sed -i 's/BIOCLIM_1//g' ./results/*
sed -i 's/BIOCLIM_12//g' ./results/*
sed -i 's/BIOCLIM_17//g' ./results/*
sed -i 's/BIOCLIM_7//g' ./results/*
sed -i 's/GTOPO30_ELEVATION//g' ./results/*
sed -i 's/GTOPO30_SLOPE_reduced//g' ./results/*
sed -i 's/ISRICSOILGRIDS_new_average_coarsefragmentpercent_reduced//g' ./results/*
sed -i 's/ISRICSOILGRIDS_new_average_phx10percent_reduced//g' ./results/*
sed -i 's/ISRICSOILGRIDS_new_average_sandpercent_reduced//g' ./results/*
sed -i 's/ISRICSOILGRIDS_new_average_soilorganiccarboncontent_reduced//g' ./results/*
sed -i 's/LandCover_1_Needleleaf//g' ./results/*
sed -i 's/LandCover_6_Herbaceous//g' ./results/*
sed -i 's/^_*//g' ./results/*
sed -i 's/_avg//g' ./results/*

# Add histograms for any species for which point extraction was done instead of modeling
# These MUST be of the format: 
#	VARIABLE_pno_SPECIES.csv
#	and a csv with the climate values in a column called "variable"
#	The Saxifragales point extraction script will create the right format

for f in ./results/*.out; do
g=$( echo ${f} | sed 's/.*\///g' | sed 's/\..*//g' )
echo ${g}
python3 binner_climateextraction.py ${f} ${f}.updated -x ${extractionpath}/${g}_pno_*.csv
sed -i 's/Unnamed: 0,/,/g' ${f}.updated
done

for f in ./results/*.out.updated; do
python3 bin_trimmer.py ${f} ${f}.dropped
sed -i 's/Unnamed: 0,/,/g' ${f}.dropped
done
