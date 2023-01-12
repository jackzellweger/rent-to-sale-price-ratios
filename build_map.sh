#!/bin/sh

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Download & unzip sales data
echo "Downloading sales data..."
wget "https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/zip_code_market_tracker.tsv000.gz" -O temp.tsv000.gz
gzip -d temp.tsv000.gz
rm temp.tsv000.gz

# Download rental data
echo "Downloading rental data..."
wget "https://files.zillowstatic.com/research/public_csvs/zori/Zip_zori_sm_month.csv"

# Download ZIP code polygons
echo "Downloading polygon data..."
wget "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip" -O temp1.zip
unzip temp1.zip
rm temp1.zip

# Execute Jupyter Notebook
echo "Running python script"
jupyter nbconvert --execute $SCRIPT_DIR/logic/house-search.ipynb --to python
echo "Python script complete"