from requests_html import HTMLSession
import pandas as pd
import re
import numpy as np
import datetime as dt

# These regex match the Tesco tile product pages for relavent information
productRegex = {
	'productTiles_Match' : r"<div class=\"product-tile-wrapper\">(.*?)(?=<div class=\"product-tile-wrapper\">)",
	'product_Match' : r"<a href=\"\/groceries\/en-GB\/products\/([0-9]+)\" class=\".*\" data-auto=\"product-tile--title\">(.*?)<\/a>",
	'discountText_Match' : r"\<span class=\"offer-text\"\>(.*?)\<\/span\>",
	'discountDates_Match' : r"\<span class=\"dates\"\>(?:.*?)([\d]+\/[\d]+\/[\d]+)(?:.*?)([\d]+\/[\d]+\/[\d]+)\<\/span\>",
	'regPrice_Match' : r"<div class=\"price-per-sellable-unit price-per-sellable-unit--price price-per-sellable-unit--price-per-item\"><div class=\"\"><span><span class=\"currency\">\u00a3<\/span><span class=\"space\"> <\/span><span data-auto=\"price-value\" class=\"value\">(.*?)<\/span><\/span><\/div><\/div>",
	'regPricePer_Match' : r"<div class=\"price-per-quantity-weight\"><span><span class=\"currency\">\u00a3<\/span><span data-auto=\"price-value\" class=\"value\">(.*?)<\/span><\/span><span class=\"weight\">\/(.*?)<\/span><\/div>",
	'numeric_const_pattern' : r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))(?:[Ee][+-]?\d+)?'
	}

session = HTMLSession()

def tescoPriceScrape(url, category, n_pages=5):

	products = pd.DataFrame()
	i = 1
	while i < n_pages:
	#To limit the run-time for testing, we only scrape 2 pages of each category
	
#         print("Getting {} Page {}".format(key, i))
		
		r = session.get(url+str(i))
		if r.status_code == 404:
			# If we are not able to reach the page we break
			break

		productTiles = re.findall(productRegex['productTiles_Match'], r.text)

		for n in productTiles:
			if re.findall('Sorry, this product is currently unavailable', n):
				#If the product is not available, we skip it
				print("{} out of stock.".format(re.findall(productRegex['product_Match'], n)[0][1]))
				continue
			product = re.findall(productRegex['product_Match'], n)[0]
			productID = product[0]
			productName = product[1]
			if re.findall(productRegex['discountText_Match'], n):
				discountText = re.findall(productRegex['discountText_Match'], n)[0]
				discountB = True
			else:
				discountText = np.nan
				discountB = False
			if re.findall(productRegex['discountDates_Match'], n):
				#If there is a discount, find these parameters
				discountDates = re.findall(productRegex['discountDates_Match'], n)[0]
				start = dt.datetime.strptime(discountDates[0], '%d/%m/%Y').date()
				end = dt.datetime.strptime(discountDates[1], '%d/%m/%Y').date()
			else:
				#If no discounts, fill with nan
				discountDates = np.nan
				start = np.nan
				end = np.nan
			if re.findall(productRegex['regPrice_Match'], n):
				regPrice = re.findall(productRegex['regPrice_Match'], n)[0]
			else:
				regPrice = np.nan
			if re.findall(productRegex['regPricePer_Match'], n):
				regPricePer = re.findall(productRegex['regPricePer_Match'], n)[0]
			else:
				regPricePer = np.nan

			df = pd.DataFrame([[productName, category, regPrice, regPricePer, discountB, discountText, start, end, productID]], columns=['Product','Category','Regular_Price','Regular_Price_Per','Discount_Active','Discount_Text','Discount_Start_Date','Discount_End_Date','TescoID'])

			products = products.append(df)

		i += 1

	products.index = products.TescoID
	products[['Product','Category','Discount_Text']] = products[['Product','Category','Discount_Text']].apply(lambda x: x.astype(str))
	products[['Regular_Price']] = products[['Regular_Price']].apply(lambda x: x.astype('float64'))
	products[['Discount_Active']] = products[['Discount_Active']].apply(lambda x: x.astype('bool'))
	products[['Start_Date','End_Date']] = products[['Discount_Start_Date','Discount_End_Date']].apply(lambda x: x.astype('datetime64[ns]'))

	return products