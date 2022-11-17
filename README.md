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