# LIBRARY IMPORTS
from pathlib import Path
import pandas as pd

# DATA IMPORTS
sales = pd.read_csv('Redfin_SalePricesByZip.tsv000', sep='\t', header=0)
rentals = pd.read_csv('Zip_ZORI_AllHomesPlusMultifamily_Smoothed.csv', sep=',', header=0)

# SALES DATA COLLECTION & CLEANING
# SOLVES THE PROBLEM OF SALES DATA W/ MULTIPLE ZIPS

# Take the data from just 2021
salesCleanedZip = sales[sales["period_begin"].str.contains("2021")]

# Clean up the zips
salesCleanedZip['region'] = sales['region'].str.extract('(\d+)')

# Simplify the dataframe, isolating the 'region' and 'median_sale_price'
# salesSimplified = salesCleanedZip[['region', 'median_sale_price']]
salesSimplified = salesCleanedZip.filter(items=['region', 'median_sale_price'])

# Isolate the 'region' and 'median_sale_price', then groups, and takes the mean of the zips
salesByZip = salesSimplified.groupby(['region']).median()

# Reset the index
# We might not need this if we use the .filter() dot-extension above.
salesByZip = salesByZip.reset_index()

# Rename the column 'region' to 'RegionName'
salesByZip = salesByZip.rename(columns={'region': 'RegionName'})

# Rename the column 'median_sale_price' to 'CurrentSalesPrice'
salesByZip = salesByZip.rename(columns={'median_sale_price': 'CurrentSalesPrice'})

# RENTAL DATA COLLECTION & CLEANING
currentRentalPrices = rentals.filter(items=['RegionName', '2022-02'])
currentRentalPrices = currentRentalPrices.rename(columns={'2022-02': 'CurrentRentalPrice'})
currentRentalPrices = currentRentalPrices.astype({'RegionName': 'str'})

# Ensuring that there aren't any duplicate Zip codes in the rental table
booleanRentals = currentRentalPrices['RegionName'].duplicated().any()

# JOINING THE DATABASE, CLEANING, & CALCULATING RENT:SALES
combined = salesByZip.set_index('RegionName').join(currentRentalPrices.set_index('RegionName'))
rentalsAndSales = combined.dropna()
rentalsAndSales["RentToSaleRatio"] = rentalsAndSales["CurrentRentalPrice"] / rentalsAndSales["CurrentSalesPrice"]

# FILTERING OUT THE OUTLIERS
rentalsAndSalesFiltered = rentalsAndSales[rentalsAndSales.RentToSaleRatio < .017]
rentalsAndSalesSorted = rentalsAndSalesFiltered.sort_values(by='RentToSaleRatio', ascending=False)

# PLOTTING THE ZIP CODES BY RENT:SALES
s2 = rentalsAndSalesSorted.plot(y='RentToSaleRatio', figsize=(10, 7), use_index=False)

# EXPORTING FOR MATHEMATICA (2 COLUMNS)
filepath = Path('data_output/out.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)
rentalsAndSalesSorted.loc[:, 'RentToSaleRatio'][0:1800].to_csv(filepath)
