# Finding investment opportunities

### Motivation

One day, a friend introduced me to someone he knows who’s setting up a company to start investing in real estate. He’s looking for deals across the entire United States, and complained about how hard it is to find good investment opportunities.

This got me wondering about if there’s a way to automate this stuff. I know there’s a ton of data on the [MLS](https://www.mls.com/), and real estate firms like [Redfin](https://www.redfin.com/news/data-center/) and [Zillow](https://www.zillow.com/research/data/) make their home sales data available for free through vast downloadable datasets.

Was there a way to turn these vast datasets into actionable insights that my friend could use? I started doing some research. My new friend told me he was looking for opportunities in markets that had lower house prices and higher rent prices. That sounds like a ratio that could be calculated per-market using geographic sales and rental data.

So, I set out to make a heatmap of this sales price to rental price ratio across the country. I wanted to end up with something like this. Maybe I could even make it user-friendly and even a bit interactive; could I make it so when I hover my mouse over each polygon, I get a ZIP code and ratio?

![Example Heatmap](/Images/example-heatmap.png?raw=true)

### Getting The Sales Data

I started by downloading Redfin’s repository of [Price by ZIP Code data](https://www.redfin.com/news/data-center/). The download contains sales price medians for 90-day timeframes. That means that, within the whole dataset, ZIP codes appear twice; if a two houses in the same ZIP code were sold in different 90-day divisions, then there will be two different rows of data.

I had originally written these scripts with the wrong assumption that each ZIP code only appeared once in the Redfin sales data. That turned out to be false, so my algorithm was spitting out wrong but believable results. I only uncovered my false assumption after running some unit tests that returned unexpected results.

### Simplifying The Sales Data

With this sales data, I isolated the `region` and the `median_sale_price` properties, but here’s a view of all the columns they provide. 

```python
# Redfin sales data
list(sales.columns.values)
--
['period_begin','period_end','period_duration','region_type','region_type_id','table_id','is_seasonally_adjusted','region','city','state','state_code','property_type','property_type_id','median_sale_price','median_sale_price_mom','median_sale_price_yoy','median_list_price','median_list_price_mom','median_list_price_yoy','median_ppsf','median_ppsf_mom','median_ppsf_yoy','median_list_ppsf','median_list_ppsf_mom','median_list_ppsf_yoy','homes_sold','homes_sold_mom','homes_sold_yoy','pending_sales','pending_sales_mom','pending_sales_yoy','new_listings','new_listings_mom','new_listings_yoy','inventory','inventory_mom','inventory_yoy','months_of_supply','months_of_supply_mom','months_of_supply_yoy','median_dom','median_dom_mom','median_dom_yoy','avg_sale_to_list','avg_sale_to_list_mom','avg_sale_to_list_yoy','sold_above_list','sold_above_list_mom','sold_above_list_yoy','price_drops','price_drops_mom','price_drops_yoy','off_market_in_two_weeks','off_market_in_two_weeks_mom','off_market_in_two_weeks_yoy','parent_metro_region','parent_metro_region_metro_code','last_updated']
```

Unfortunately, as you can see above, there are no rental data columns in the data available from Redfin. So, I decided I would pull the rental data from somewhere else and then join sale price columns with rental price columns using ZIP code as the key.

### Getting The Rental Data

I found that Zillow had [rental data](https://www.zillow.com/research/data/) available based on ZIP code (see the “RENTALS” section) so I went ahead and downloaded that data.

```python
# Zillow rental data
list(sales.columns.values)
--
['RegionID','RegionName','SizeRank','MsaName','2014-01','2014-02','2014-03','2014-04','2014-05','2014-06','2014-07','2014-08','2014-09','2014-10','2014-11','2014-12','2015-01','2015-02','2015-03','2015-04','2015-05','2015-06','2015-07','2015-08','2015-09','2015-10','2015-11','2015-12','2016-01','2016-02','2016-03','2016-04','2016-05','2016-06','2016-07','2016-08','2016-09','2016-10','2016-11','2016-12','2017-01','2017-02','2017-03','2017-04','2017-05','2017-06','2017-07','2017-08','2017-09','2017-10','2017-11','2017-12','2018-01','2018-02','2018-03','2018-04','2018-05','2018-06','2018-07','2018-08','2018-09','2018-10','2018-11','2018-12','2019-01','2019-02','2019-03','2019-04','2019-05','2019-06','2019-07','2019-08','2019-09','2019-10','2019-11','2019-12','2020-01','2020-02','2020-03','2020-04','2020-05','2020-06','2020-07','2020-08','2020-09','2020-10','2020-11','2020-12','2021-01','2021-02','2021-03','2021-04','2021-05','2021-06','2021-07','2021-08','2021-09','2021-10','2021-11','2021-12','2022-01','2022-02']
```

While Redfin compels you to download data for a single time frame and blasts you with a ton of columns, Zillow only has a few data columns, and then blasts you with data from every time frame associated with those columns. I somehow needed to join this data.

### Normalizing The Data

I envisioned ending up with a table like this:

| ZIP Code (Key) | Median Price | Median Rental Price | Rent to Sale Price Ratio |
| --- | --- | --- | --- |
| 33063 | 42750.0 | 2137.0 | 0.049988 |
| 33063 | 42750.0 | 2137.0 | 0.04998 |

1. A simple table that used the ZIP code as a key
2. a column with median selling price
3. a column with median monthly rent price
4. Then, a new column—the rent:sale price ratio—based on column 2 and 3.

My main tool for crunching numbers had historically been Python’s SciPy library, but that seemed like overkill for this project. After some Googling, I decided to use Python and the Pandas library to tackle this problem. I had never used Pandas or the library’s ‘Dataframe’ objects, but it’s so simple!

***First, I imported the data…***

```python
sales = pd.read_csv('Redfin_SalePricesByZip.tsv000', sep='\t',header=0)
rentals = pd.read_csv('Zip_ZORI_AllHomesPlusMultifamily_Smoothed.csv', sep=',',header=0)
```

***Then I took the sales data, and cleaned it up a bit…***

```python
# Take the data from just 2021
salesCleanedZip = sales[sales["period_begin"].str.contains("2021")]

# Extract just the ZIP code numbers from the column with the regex string'(\d+)'
salesCleanedZip['region'] = sales['region'].str.extract('(\d+)')

# Simplify the dataframe, isolating the 'region' and 'median_sale_price'
salesSimplified = salesCleanedZip.filter(items=['region','median_sale_price'])

# Isolate the 'region' and 'median_sale_price', then group, and find the
# median of each of the groups of like zips
salesByZip = salesSimplified.groupby(['region']).median()

# Reset the index. This is necessary in order to rename and manipulate the
# two primary columns we're working with here.
salesByZip = salesByZip.reset_index()

# Rename the column 'region' to 'RegionName'
salesByZip = salesByZip.rename(columns={'region':'RegionName'})

# Rename the column 'median_sale_price' to 'CurrentSalesPrice'
salesByZip = salesByZip.rename(columns={'median_sale_price':'CurrentSalesPrice'})
```

***Then ran some sanity checks on the sales data…***

```python
# Check the sales data for any duplicate ZIP Codes. We're looking for this
# to return 'False', which it did
booleanSales = salesByZip['RegionName'].duplicated().any()

# Check individual ZIP Code sales rows, just to gut check prices
# I used my old ZIP code in midtown and then a few ZIP codes where
# I used to live in Ohio. All came back sane and expected.
salesByZip.loc[salesByZip['RegionName'] == '10017']

```

***I then cleaned up the rental data…***

```python
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
```

***Ran a quick test...***

```python
# Ensure there aren't any duplicate ZIP codes in the rental dataframe
booleanRentals = rentalGrouped['RegionName'].duplicated().any()
```

***Now, we have two dataframes…***

`salesByZip`

```python
 17778 rows x 2 columns
 --
 Key        RegionName CurrentSalesPrice
 0          01001      246427.772727
 1          01002      366060.784314
 2          01005      338977.870968
 3          01007      325266.818182
 4          01008      258950.000000
 ...          ...                ...
 17773      99705      274772.050000
 17774      99709      252503.333333
 17775      99712      309830.000000
 17776      99714      256000.000000
 17777      99725      147000.000000
```

`rentalGrouped`

```python
 2166 rows x 2 columns
 --
 Key       RegionName         CurrentRentalPrice
 0         10025              3329.0
 1         60657              1588.0
 2         10023              3917.0
 3         77494              1697.0
 4         60614              1989.0
 ...         ...                 ...
 2161      23507              1586.0
 2162      10282              7427.0
 2163      60606              2236.0
 2164      10006              3654.0
 2165       2109              3023.0
```

### Joining The Normalized Data Into One Table

***Perfect! We’ve normalized the data, and are ready to initiate a join…***

```python
# We set the key to the ZIP codes and join them based on that key
# all in one step here, setting the resulting dataframe equal to 'combined'
combined = salesByZip.set_index('RegionName').join(rentalGrouped.set_index('RegionName'))

# Since there were fewer ZIP codes with rental data associated with it,
# there's are a lot of rows with only sales data. We'll delete those rows here.
rentalsAndSales = combined.dropna()

# We calculate a rent:sale price ratio, and stick it into a new column
# called `'RentToSaleRatio'.
rentalsAndSales["RentToSaleRatio"] = rentalsAndSales["CurrentRentalPrice"]/rentalsAndSales["CurrentSalesPrice"]
```

***Let’s do some further cleaning…***

```python
# Filter out the extrema greater than .017, or %1.7
# I found this is a good cut-off
rentalsAndSalesFiltered = rentalsAndSales[rentalsAndSales.RentToSaleRatio < .017]

# Sort all the values by rent:sale price ratio
rentalsAndSalesSorted = rentalsAndSalesFiltered.sort_values(by='RentToSaleRatio', ascending=False)

# Plot the 
s2 = rentalsAndSalesSorted.plot(y='RentToSaleRatio',figsize=(20,7), use_index=False);
```

***After all that processing, we end up with a dataframe like this…***

```python
 1905 rows x 3 columns
 --
 RegionName       CurrentSalesPrice         CurrentRentalPrice  RentToSaleRatio                                                        
 32210            1.676159e+05              1424.0         0.008496
 32211            1.823551e+05              1545.0         0.008472
 34235            2.868396e+05              2430.0         0.008472
 76014            2.165649e+05              1832.0         0.008459
 33880            1.924022e+05              1627.0         0.008456
 ...                       ...                 ...              ...
 10011            5.716669e+06              4283.0         0.000749
 10021            4.256849e+06              3046.0         0.000716
 10128            4.718165e+06              3000.0         0.000636
 10075            4.298317e+06              2677.0         0.000623
 10028            4.922165e+06              2933.0         0.000596
```

***If we plot it, we end up with something like this…***

```python
s2 = rentalsAndSalesSorted.plot(y='RentToSaleRatio',figsize=(10,7), use_index=False);
```


![Plot of rent:sale price ratio by array index.](/Images/ratios-plot.png?raw=true)

On the left side, we see a gradual flattening from the relatively inexpensive outliers into what looks like something linear. Then, as we approach the right side, we see a rapid drop-off. This represents super-expensive properties in Manhattan, NY and Los Angeles, CA. These are places where it’s relatively easy to rent (though still expensive), but disproportionately expensive to buy.

### What The Right Side of The Curve Looks Like

Here are a few samples from the ZIP codes on the right side of the graph (areas that tend to have super-high sales prices, not super-low rental prices)

**Paradise Valley, Arizona 85253. Rent:sale = 0.001398 (.14%)**

<img src="/Images/paradise-valley.png" width="400">

**Forest Hills, Washington D.C. 20008. Rent:sale = 0.001587 (0.16%)**

<img src="/Images/forest-hills.png" width="400">

**1 E 45th St, New York City, NY 10036. Rent:sale = 0.001538, 0.15%**

<img src="/Images/nyc.png" width="400">

**Lombard Street, San Francisco, California 94109. Rent:sale = 0.001301 (0.13%)**

<img src="/Images/lombard-street.png" width="400">


Clearly some of the wealthiest areas of the country.

### What The Left Side of The Curve Looks Like

Let’s take a look at some of the ZIP codes with the lowest rent:sale price ratio. I took off the filter to really find the outliers in the U.S.


**Castle Point, St. Louis, MO. Rent:sale = 0.016429 (1.6%)**

<img src="/Images/st-louis.png" width="400">


**Inkster, MI 48141. Rent:sale = 0.014719 (1.5%)**

<img src="/Images/inkster.png" width="400">


**Baltimore, MD 21223. Rent:sale = 0.014077 (1.4%)**

<img src="/Images/baltimore.png" width="400">


**Jan Phyl Village, FL 33880. Rent:sale = 0.008456 (.85%)**

<img src="/Images/jan-phyl.png" width="400">

### Visualizing Rent:sale Price Ratios On A Map

***Let’s visualize some of this data on a map. First, I export the processed data from my Jupyter notebook into Mathematica…***

```python
# Export the data in two colums for Mathematica
filepath = Path('data_output/out.csv')  
filepath.parent.mkdir(parents=True, exist_ok=True)

# Go up to entry 1800, even though we only have
rentalsAndSalesSorted.loc[:,'RentToSaleRatio'][0:1800].to_csv(filepath)
```

***We’re now in Mathematica. First, I import and clean the two-column dataset…***

```mathematica
(* I import the data *)
data = Drop[
   Import["path/to/file.csv", "Data"], 1];

(* I then do some simple type conversion*)
cleanData = (MapAt[ToString, #, 1]) & /@ data;

(* And use Mathematica's built-in interpreter to convert the simple
5-character ZIP code strings into ZIP code objects *)
ZIPTuples = (MapAt[Interpreter["ZIPCode"], #, 1]) & /@ cleanData;
```

***Then we declare a function that will plot our ZIP code when we plug in a geographic entity like “United States” or “Memphis”…***

```mathematica
(* These parameters direct things like map tile resolution, projection type,
and padding *)
plotFunction[x_] := 
 GeoRegionValuePlot[ZIPTuples, 
  ImageSize -> Medium, PlotStyle -> Directive[EdgeForm[]], 
  GeoRange -> x, GeoRangePadding -> Scaled[0.1], 
  GeoProjection -> "Mercator", GeoZoomLevel -> 6]
```

We can now use this function and *Mathematica’s* [Natural Language Input](https://www.wolfram.com/language/fast-introduction-for-programmers/en/natural-language-input/) feature to get a map pretty much anywhere in the U.S.

***Let’s try the entire U.S. to see where our data is concentrated…***

```mathematica
plotFunction /@{Entity["Country","UnitedStates"]}
```

![Heatmap of The U.S.](/Images/heatmap-us.png?raw=true)


These computations took on the order of 5 minutes to complete and render a single map. We can start to see that the data (probably constrained by the Zillow rental data) mostly fills the urban areas of the U.S. That’s no surprise. We can start zooming into different metro areas to get more detail.

**Atlanta, GA**

<img src="/Images/heatmap-atlanta.png" width="300">

**Boca Raton, FL**

<img src="/Images/heatmap-boca-raton.png" width="300">

**Detroit, MI**

<img src="/Images/heatmap-detroit.png" width="300">


These maps provide excellent starting points when searching for investment properties. We can start our property searches in the red areas, looking for ZIP codes with rental prices that are relatively high when compared to the sales price.

### Looking At The Data Directly

We can also review the data in a less visual but still effective way by looking at the sales data directly in our ratios table.

***Let’s take the first n rows of our sorted data frame of rent:sale price ratios…***

```mathematica
[rentalsAndSalesSorted.head(15)]
```

***Here’s our result...***

```mathematica
 RegionName.          CurrentSalesPrice     CurrentRentalPrice  RentToSaleRatio
 48227                 62475.0              1038.0         0.016615
 63136                 60000.0               996.0         0.016600
 19132                 79750.0              1180.0         0.014796
 48141                 75000.0              1078.0         0.014373
 33446                246250.0              3369.0         0.013681
 33434                241250.0              3209.0         0.013302
 45405                 70812.5               900.0         0.012710
 33484                225000.0              2855.0         0.012689
 38127                 71000.0               892.0         0.012563
 38128                105950.0              1279.0         0.012072
 *21213              *120500.0             *1421.0        *0.011793
 64128                 83250.0               969.0         0.011640
 *48089              *105000.0             *1216.0        *0.011581
 38115                113975.0              1301.0         0.011415
 64130                 87857.5               965.0         0.010984]
```

A good strategy here might be to look for ZIP codes with the “best” rent:sale price ratios. We’re looking for ZIP codes with good rent:sale price ratios that still have reasonably high median sales prices. I've addeds stars in the table above next to the most promising ZIP codes.

1. It looks like `21213` in Baltimore, Maryland has a great rent:sale price ratio at 1.17%, while maintaining a reasonably high median sales price at $120,500.
2. Another interesting prospect is `48089` in Warren, Michigan. It has another really good rent:sale price ratio at 1.15%, and a median sales price of $105,000.

These are the kinds of properties that  and start exploring those areas on Google Maps. Two great prospects worthy of further investigation!

### Future work

- Count the number of sales that contributed to the sales medians and then filter out the zip codes below some threshold _n_?
- Could build an animated graph of the `RentToSalesRatio` graph as historical data and show how it evolves over time.

---

\* _I performed many unit tests in order to verify my results as part of this project. I left out many of those details as part of this write-up._





































