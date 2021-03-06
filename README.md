# ShopScraper
A project to scrape nutritional and pricing information

**Note: Using this script might get you temporarily IP banned from Tesco.com**

# Setup
Clone this repo and run `pip install -r requirements.txt` in the root directory.

# Usage
Inside `src/Tesco/TescoScraper.py` you can set a number of parameters

| Variable  | Description |
| ------------- | ------------- |
| file_name  | The output file name (.csv)  |
| num_pages  | The number of product pages to be scraped  |
| URLs  | The root product pages to be scraped  |

Running `TescoScraper.py` will first scrape the pricing data using `TescoPriceScrape` and then the relavent nutrition data using `TescoNutritionScrape`. The data is then saved as .csv file.


_Optional_

`TescoBokehPlot.py` can also be run which will generate an interactive bokeh plot to visualise the data. 

![alt tag](https://user-images.githubusercontent.com/36965310/103894902-38ccf600-50f8-11eb-9540-338bd8b133d4.png)

**WIP**
