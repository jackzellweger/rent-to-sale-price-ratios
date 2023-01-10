# LIBRARY IMPORTS
from pathlib import Path
import pandas as pd
import warnings

# DATA IMPORTS
sales = pd.read_csv('Redfin_SalePricesByZip.tsv000', sep='\t', header=0)
rentals = pd.read_csv('Zip_zori_sm_month.csv', sep=',', header=0,
   converters={'RegionName': lambda x: x.zfill(5)})

# -- SALES DATA COLLECTION & CLEANING --

# Take the data from just 2021
salesSelectTimeframe = sales[sales["period_begin"].str.contains("2021")]

# Clean up the zips
salesSelectTimeframe['region'] = sales['region'].str.extract('(\d+)')

# Simplify the dataframe, isolating the 'region' and 'median_sale_price'
salesTwoColumn = salesSelectTimeframe.filter(
    items=['region', 'median_sale_price'])

# Isolate the 'region' and 'median_sale_price', then groups, and takes the mean
# of the zips
medianSalesByZip = salesTwoColumn.groupby(['region']).median()

# Reset the index
medianSalesByZip = medianSalesByZip.reset_index()

# Rename the column 'region' to 'RegionName'
medianSalesByZip = medianSalesByZip.rename(columns={'region': 'RegionName'})

# Rename the column 'median_sale_price' to 'CurrentSalesPrice'
medianSalesByZip = medianSalesByZip.rename(
    columns={'median_sale_price': 'CurrentSalesPrice'})

# -- RENTAL DATA COLLECTION & CLEANING --

# Select timeframe using regex
rentalSelectTimeframe = rentals[['RegionName']].join(rentals.filter(
    regex='2022'))

# The 'melt' puts each cell of each column in its own row, preserving each
# row's association with its respective 'RegionName' property:
rentalMelted = rentalSelectTimeframe.melt(id_vars='RegionName',
                                          var_name='Date',
                                          value_name='CurrentRentalPrice')

# Take the median of all the rental prices with the same index
rentalGrouped = rentalMelted.groupby('RegionName').median().reset_index()

# Ensure there aren't any duplicate ZIP codes in the rental dataframe
booleanRentals = rentalGrouped['RegionName'].duplicated().any()

# Throw an error if there are somehow duplicate ZIP codes in the rental
# dataframe
if (booleanRentals != False):
    warnings.warn("Duplicate ZIP codes in the rental dataframe. Unexpected or "
                  "inaccurate results are possible.", RuntimeWarning)

# -- JOINING THE DATABASE, CLEANING, & CALCULATING RENT:SALES --

# Join sales and rental data into one dataframe
salesRentSparse = medianSalesByZip.set_index('RegionName').join(
    rentalGrouped.set_index('RegionName'))

# Drop any rows with missing rental data (there is more sales than rental data)
salesRent = salesRentSparse.dropna()

# Create a new column equal to rent:sale ratio
salesRent["RentToSaleRatio"] = salesRent["CurrentRentalPrice"] / \
                               salesRent["CurrentSalesPrice"]

# -- FILTERING OUT THE OUTLIERS --

# Remove all rows above a certain rent:sales ratio
saleRentFiltered = salesRent[
    salesRent.RentToSaleRatio < .017]

# Sort by rent:sales ratio
saleRentSorted = saleRentFiltered.sort_values(
    by='RentToSaleRatio', ascending=False)

# -- PLOTTING THE ZIP CODES BY RENT:SALES --

# This plots the rent:sales ratios, using the DataFrame's index as the
# x-axis values
plotRatioByIndex = saleRentSorted.plot(
    y='RentToSaleRatio', figsize=(10, 7), use_index=False)

# Save the chart to a file
plotRatioByIndex.savefig("rental_and_sales_ratio.png")

# -- EXPORTING FOR MATHEMATICA (2 COLUMNS) --
filepath = Path('data_output/out.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)

# Save the first xx (in this case, 1800) values out in CSV file that
# Mathematica can read
saleRentSorted.loc[:, 'RentToSaleRatio'][0:1800].to_csv(filepath)
