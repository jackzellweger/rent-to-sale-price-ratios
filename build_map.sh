#!/bin/sh

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# DOWNLOAD & UNZIP SALES DATA
echo "Downloading sales data..."
wget "https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/zip_code_market_tracker.tsv000.gz" -O temp.tsv000.gz
echo "Sales data download complete."

echo "Unzipping sales data..."
gzip -d temp.tsv000.gz
rm temp.tsv000.gz
mv zip_code_market_tracker.tsv000 ./data/
echo "Sales data unzip complete."

# DOWNLOAD RENTAL DATA
echo "Downloading rental data..."
wget "https://files.zillowstatic.com/research/public_csvs/zori/Zip_zori_sm_month.csv"
mv Zip_zori_sm_month.csv ./data/rental
echo "Rental data download complete..."

# DOWNLOAD ZIP CODE POLYGONS
echo "Downloading polygon data..."
wget "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip"
mv cb_2020_us_zcta520_500k.zip ./data/polygons
echo "Polygon data download complete..."

echo "Unzipping polygon data..."
unzip ./data/polygons/cb_2020_us_zcta520_500k.zip -d ./data/polygons
rm ./data/polygons/cb_2020_us_zcta520_500k.zip
echo "Polygon data unzip complete"

# EXECUTE JUPYTER NOTEBOOK
echo "Running python script..."
jupyter nbconvert --execute $SCRIPT_DIR/logic/house-search.ipynb --to python
echo "Python script complete"