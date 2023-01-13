#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import geopandas as gpd
from pathlib import Path  
import folium
import branca
import json
import os


# In[2]:


# 2023 DATA IMPORTS

sales = pd.read_csv('../data/sales/zip_code_market_tracker.tsv000', sep='\t',header=0)
rentals = pd.read_csv('../data/rental/Zip_zori_sm_month.csv', sep=',', header=0, converters={'RegionName': lambda x: x.zfill(5)})


# In[3]:


# SALES DATA COLLECTION & CLEANING

# Take the data from just 2022
salesCleanedZip = sales[sales["period_begin"].str.contains("2022")]

# Clean up the zips
salesCleanedZip['region'] = sales['region'].str.extract('(\d+)')

# Simplify the dataframe, isolating the 'region' and 'median_sale_price'
# salesSimplified = salesCleanedZip[['region', 'median_sale_price']]
salesSimplified = salesCleanedZip.filter(items=['region','median_sale_price'])

# Isolate the 'region' and 'median_sale_price', then groups, and takes the mean of the zips
# salesByZip = salesSimplified.groupby(['region']).mean()
salesByZip = salesSimplified.groupby(['region']).median()

# Reset the index
# We might not need this if we use the .filter() dot-extension above.
salesByZip = salesByZip.reset_index()

# Rename the column 'region' to 'RegionName'
salesByZip = salesByZip.rename(columns={'region':'RegionName'})

# Rename the column 'median_sale_price' to 'CurrentSalesPrice'
salesByZip = salesByZip.rename(columns={'median_sale_price':'CurrentSalesPrice'})


# In[4]:


# RENTAL DATA COLLECTION & CLEANING
t1 = rentals[['RegionName']].join(rentals.filter(regex='2022'))
t2 = t1.melt(id_vars='RegionName', var_name='Date', value_name='CurrentRentalPrice')
currentRentalPrices = t2.groupby('RegionName').median().reset_index()


# In[5]:


# Ensuring that there aren't any duplicate ZIP codes in the rental table
booleanRentals = currentRentalPrices['RegionName'].duplicated().any()


# In[6]:


# JOINING THE DATABASE, CLEANING, & CALCULATING RENT:SALES
combined=salesByZip.set_index('RegionName').join(currentRentalPrices.set_index('RegionName'))
rentalsAndSales = combined.dropna()
rentalsAndSales["RentToSaleRatio"] = rentalsAndSales["CurrentRentalPrice"]/rentalsAndSales["CurrentSalesPrice"]


# In[7]:


# FILTERING OUT THE OUTLIARS
rentalsAndSalesFiltered = rentalsAndSales[rentalsAndSales.RentToSaleRatio < .015]
rentalsAndSalesSorted = rentalsAndSalesFiltered.sort_values(by='RentToSaleRatio', ascending=False)


# In[8]:


# EXPORT FOR MATHEMATICA IN 2 COLUMNS
# filepath = Path('../prototype/out.csv')  
# filepath.parent.mkdir(parents=True, exist_ok=True)  
# rentalsAndSalesSorted.loc[:,'RentToSaleRatio'][0:1800].to_csv(filepath)


# In[9]:


# IMPORTING SHAPEFILES
shapefile = '../data/polygon/cb_2020_us_zcta520_500k.shp'
gdf = gpd.read_file(shapefile)

# SETTING UP BASE MAP
testo = rentalsAndSalesSorted.join(gdf.set_index('NAME20')).dropna().sort_values('RegionName')
gdf1 = gpd.GeoDataFrame(testo, geometry='geometry')
m = folium.Map(location=[40.70, -98.94], zoom_start=4.0, tiles='CartoDB positron')
color_map = branca.colormap.LinearColormap(['red', 'green'], vmin=0.000, vmax=0.016)

for _, r in gdf1.iterrows():
    shape_column = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    color = color_map(r['RentToSaleRatio'])
    geo_j = shape_column.to_json()
    geo_j_json = json.loads(geo_j)
    geo_j_json['features'][0]['properties']['ratio'] = r['RentToSaleRatio']
    geo_j = folium.GeoJson(data=geo_j_json,
                           style_function=lambda x: {'fillColor': color_map(x['properties']['ratio']), 'color': 'black', 'weight': 0, 'fillOpacity': 0.9})
    folium.Popup(str('{:.2f}% <br> {} <br> ${:,.0f} <br> ${:,.0f} '.format(r['RentToSaleRatio'] * 100, str(r['GEOID20']).zfill(5), r['CurrentSalesPrice'], r['CurrentRentalPrice'] ))).add_to(geo_j)
    geo_j.add_to(m)
m.save("../web_build/index.html")


# In[10]:


# USEFUL CODE
    # PLOTTING THE ZIP CODES BY RENT:SALES
        # s2=rentalsAndSalesSorted.plot(y='RentToSaleRatio',figsize=(10,7), use_index=False);
    # SAMPLING VARIOUS REGIONS
        # [rentalsAndSalesSorted.tail(10)]
        # [rentalsAndSalesSorted.head(10)]

