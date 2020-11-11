from requests_html import HTMLSession
import pandas as pd
import re
import numpy as np
import datetime as dt



def tescoNutritionScrape(product_ids):

	df_nutrition = pd.DataFrame()

	product_url = 'https://www.tesco.com/groceries/en-GB/products/' #ID goes at the end

	nutrient_list = ['Energy (kJ)', 'Energy (kcal)', 'Fat (g)', 'Saturates (g)', 'Carbohydrates (g)', 'Sugars (g)', 'Fibre (g)', 'Protein (g)', 'Salt (g)']

	numeric_const_pattern = r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))(?:[Ee][+-]?\d+)?'

	session = HTMLSession()

	count = 0

	for i in range(0, len(product_ids)):
		product_id = str(product_ids[i])
		print(product_id)
		# This can take a while so we print the progress
		if count % 10 == 0:
			print('Progress: {}%'.format(int(100*count/len(product_ids))))
		count += 1
	
		r = session.get(product_url+str(product_id))
		try:
			# We use pandas built in table reading function
			df = pd.read_html(r.text, index_col=0)[0]
		except:
			print('No table for index',product_id)
			continue
		idd = product_id
		# Parse the table data into correct columns 
		df2 = pd.DataFrame(columns=nutrient_list)
		# df.columns = map(str.lower, df.columns)
		try:
			df.columns = df.columns.str.replace(' ', '')
		except:
			continue
		for column in df.columns:
			df[column] = df[column].apply(lambda x: x.replace(' ','').lower() if type(x) is str else x)
		try:
			df = df.rename(columns={df.columns[df.columns.str.contains('100g')][0]:'per100g'})
		except:
			continue
		# In the case that there are two columns named 'per100g'
		if isinstance(df['per100g'], pd.DataFrame):
			df.columns = ['per100g','per100g2']
		# In the case that the table is incomplete
		if df['per100g'].isnull().any():
			continue
		for index, row in df.iterrows():
			if 'energy' in index.lower():
				if 'kj' not in index.lower() and 'kcal' not in index.lower():
					if df['per100g'][df['per100g'].str.lower().str.contains('kj').fillna(False)].any():
						df2.at[idd, 'Energy (kJ)'] = re.findall(r'[0-9]+kj', df['per100g'][df['per100g'].str.contains('kj')][0])[0][:-2]
					if df['per100g'][df['per100g'].str.lower().str.contains('kcal').fillna(False)].any():
						df2.at[idd, 'Energy (kcal)'] = re.findall(r'[0-9]+kcal', df['per100g'][df['per100g'].str.lower().str.contains('kcal')][0].lower())[0].lower()[:-4]
				elif 'kj' in  index.lower():
					df2.at[idd, 'Energy (kJ)'] = row['per100g']
				elif 'kcal' in index.lower():
					df2.at[idd, 'Energy (kcal)'] = row['per100g']
			if 'fat' in index.lower():
				df2.at[idd, 'Fat (g)'] = row['per100g']
			if 'saturate' in index.lower():
				df2.at[idd, 'Saturates (g)'] = row['per100g']
			if 'carbohydrate' in index.lower():
				df2.at[idd, 'Carbohydrates (g)'] = row['per100g']
			if 'sugars' in index.lower():
				df2.at[idd, 'Sugars (g)'] = row['per100g']
			if 'fibre' in index.lower():
				df2.at[idd, 'Fibre (g)'] = row['per100g']
			if 'protein' in index.lower():
				df2.at[idd, 'Protein (g)'] = row['per100g']
			if 'salt' in index.lower():
				df2.at[idd, 'Salt (g)'] = row['per100g']
		for column in df2.columns:
			if type(df2[column][0]) is str:
				try:
					df2[column] = float(re.findall(numeric_const_pattern, df2[column][0])[0])
				except:
					df2[column] = 0

		df_nutrition = df_nutrition.append(df2)

	print('Progress: Done')
	print('{} products with missing nutritional information'.format(len(product_ids) - df_nutrition.shape[0]))

	return df_nutrition