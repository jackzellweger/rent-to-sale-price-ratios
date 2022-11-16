#!/usr/bin/env python
# coding: utf-8


# LIBRARY IMPORTS
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path  


# DATA IMPORTS
sales = pd.read_csv('Redfin_SalePricesByZip.tsv000', sep='\t',header=0)
rentals = pd.read_csv('Zip_ZORI_AllHomesPlusMultifamily_Smoothed.csv', sep=',',header=0)


#list(sales.columns.values)
#list(rentals.columns.values)


# USEFUL SCRIPTS
    # currentRentalPrices.dtypes
    # currentSalesPrices.dtypes
    # sales.columns;
    # with pd.option_context('display.max_rows', 5, 'display.max_columns', None): 
         # display(salesCleanedZip[(salesCleanedZip['region'] == '90266')].head(5))

# PARKING LOT
    # s1 = rentalsAndSalesSorted[100000:-100000].plot(figsize=(40,20));
    # s1.figure.savefig('/Users/jackzellweger/Desktop/filename.png');
    # Isolate 'region' and 'median_sale_price' preserving the index (1, 2, 3...)
        # currentSalesPrices = sales.filter(items=['region','median_sale_price'])
    # Remove everything except the zip code
        # currentSalesPrices['region'] = currentSalesPrices['region'].str.extract('(\d+)')
    # This is an alternate that extracts the string as an int instead of a str
        # currentSalesPrices['region'] = currentSalesPrices['region'].str.extract('(\d+)').astype(int)
    # Isolate the 'region' and 'median_sale_price', then groups, and takes the mean of the zips
        # salesByZip = currentSalesPrices.groupby(['RegionName']).mean()


# SALES DATA COLLECTION & CLEANING
# SOLVES THE PROBLEM OF SALES DATA W/ MULTIPLE ZIPS

# Take the data from just 2021
salesCleanedZip = sales[sales["period_begin"].str.contains("2021")]

# Clean up the zips
salesCleanedZip['region'] = sales['region'].str.extract('(\d+)')

# Simplify the dataframe, isolating the 'region' and 'median_sale_price'
# salesSimplified = salesCleanedZip[['region', 'median_sale_price']]
salesSimplified = salesCleanedZip.filter(items=['region','median_sale_price'])

# Isolate the 'region' and 'median_sale_price', then groups, and takes the mean of the zips
salesByZip = salesSimplified.groupby(['region']).mean()

# Reset the index
# We might not need this if we use the .filter() dot-extension above.
salesByZip = salesByZip.reset_index()

# Rename the column 'region' to 'RegionName'
salesByZip = salesByZip.rename(columns={'region':'RegionName'})

# Rename the column 'median_sale_price' to 'CurrentSalesPrice'
salesByZip = salesByZip.rename(columns={'median_sale_price':'CurrentSalesPrice'})


# Sanity checks
# salesByZip
# salesByZip.loc[salesByZip['RegionName'] == '90266']
# rentalsAndSales.loc[rentalsAndSales['RegionName'] == '90266']
# rentalsAndSales.loc[['10017']]
# booleanSales = salesByZip['RegionName'].duplicated().any()
# booleanSales


# RENTAL DATA COLLECTION & CLEANING
currentRentalPrices = rentals.filter(items=['RegionName','2022-02'])
currentRentalPrices = currentRentalPrices.rename(columns={'2022-02':'CurrentRentalPrice'})
currentRentalPrices = currentRentalPrices.astype({'RegionName':'str'})

# currentRentalPrices[currentPrices.CurrentPrice > 9000]
# currentRentalPrices[currentPrices.RegionName == 90266]


# Ensuring that there aren't any duplicate Zip codes in the rental table
booleanRentals = currentRentalPrices['RegionName'].duplicated().any()


# JOINING THE DATABASE, CLEANING, & CALCULATING RENT:SALES
combined=salesByZip.set_index('RegionName').join(currentRentalPrices.set_index('RegionName'))
rentalsAndSales = combined.dropna()
rentalsAndSales["RentToSaleRatio"] = rentalsAndSales["CurrentRentalPrice"]/rentalsAndSales["CurrentSalesPrice"]


# SAMPLING THE TOP XX ZIP CODES
# rentalsAndSalesSorted[0:10]

# FILTERING OUT THE OUTLIARS
# rentalsAndSalesFiltered = rentalsAndSales[rentalsAndSales.RentToSaleRatio < .017]
rentalsAndSalesSorted = rentalsAndSalesFiltered.sort_values(by='RentToSaleRatio', ascending=False)

# What does the dataframe look like?
[rentalsAndSalesSorted]


# PLOTTING THE ZIP CODES BY RENT:SALES
s2=rentalsAndSalesSorted.plot(y='RentToSaleRatio',figsize=(10,7), use_index=False);


# SAMPLING VARIOUS REGIONS
rentalsAndSalesSorted.tail(50)


# SAMPLING VARIOUS REGIONS
rentalsAndSalesSorted.head(50)


# EXPORTING 4 COLUMNS
filepath = Path('data_output/out.csv')  
filepath.parent.mkdir(parents=True, exist_ok=True)  
rentalsAndSalesSorted[250:260].to_csv(filepath)


# EXPORTING FOR MATHEMATICA (2 COLUMNS)
filepath = Path('data_output/out.csv')  
filepath.parent.mkdir(parents=True, exist_ok=True)  
rentalsAndSalesSorted.loc[:,'RentToSaleRatio'][0:1800].to_csv(filepath)

