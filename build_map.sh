#!/bin/sh

# NAVIGATE TO SCRIPT DIRECTORY
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

# DOWNLOAD & UNZIP SALES DATA
echo "Downloading sales data..."
wget "https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/zip_code_market_tracker.tsv000.gz"
mkdir ./data
mkdir ./data/sales
mv zip_code_market_tracker.tsv000.gz ./data/sales
echo "Sales data download complete."

echo "Unzipping sales data..."
gzip -f -d ./data/sales/zip_code_market_tracker.tsv000.gz # Automatically removes .gz file after unzip
echo "Sales data unzip complete."

# DOWNLOAD RENTAL DATA
echo "Downloading rental data..."
wget "https://files.zillowstatic.com/research/public_csvs/zori/Zip_zori_sm_month.csv"
mkdir ./data/rental
mv Zip_zori_sm_month.csv ./data/rental
echo "Rental data download complete..."

# DOWNLOAD ZIP CODE POLYGONS
echo "Downloading polygon data..."
wget "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip"
mkdir ./data/polygon
mv cb_2020_us_zcta520_500k.zip ./data/polygon
echo "Polygon data download complete..."

echo "Unzipping polygon data..."
unzip -f ./data/polygon/cb_2020_us_zcta520_500k.zip -d ./data/polygon
rm ./data/polygon/cb_2020_us_zcta520_500k.zip
echo "Polygon data unzip complete"

# EXECUTE JUPYTER NOTEBOOK
echo "Running python script..."
jupyter nbconvert --execute $SCRIPT_DIR/logic/house-search.ipynb --to python
echo "Python script complete"
