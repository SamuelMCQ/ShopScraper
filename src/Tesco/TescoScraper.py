from requests_html import HTMLSession
import pandas as pd
import re
import numpy as np
import datetime as dt

from TescoNutritionScrape import tescoNutritionScrape
from TescoPriceScrape import tescoPriceScrape


# File name to save results to
file_name =  'TescoProductData'

# Number of pages to scrape from each category
num_pages = 100

# These urls point to 'base' pages for the main categories on Tesco. Note that they are currently filtered for a Vegan diet.
tescoURL = {'dry':'https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all?dietary=Vegan&viewAll=dietary%2Cpromotion&promotion=offers&page=',
			'fresh':'https://www.tesco.com/groceries/en-GB/shop/fresh-food/all?include-children=true&dietary=Vegan&viewAll=dietary&page=',
			'frozen': 'https://www.tesco.com/groceries/en-GB/shop/frozen-food/all?dietary=Vegan&viewAll=dietary&page=',
			'bakery': 'https://www.tesco.com/groceries/en-GB/shop/bakery/all?dietary=Vegan&viewAll=dietary&page='
		   }

df = pd.DataFrame()

for key in tescoURL:
	dft = tescoPriceScrape(tescoURL[key], key, num_pages)
	df = df.append(dft)

tescoIDs = list(df['TescoID'])

df2 = tescoNutritionScrape(tescoIDs)

df_final = df.join(df2)
df_final.to_csv('{}.csv'.format(file_name))

print("Finished scraping data, results saved to {}.csv".format(file_name))