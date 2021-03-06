import os
import sys

# clarifai: an image analysis api
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage

# requests: a library to make http requests
import requests

# lxml: a library to parse html documents
from lxml import html, etree

# PyMongo schemas
from schema import *

# API KEY: dbe3f2920953470199637703b6566c31

app = ClarifaiApp(api_key='dbe3f2920953470199637703b6566c31') # TODO: hide this key in an environment variable.

def clarifai_clear_images():
	app.inputs.delete_all() # TODO: this might be asynchronous :/ 

def clarifai_upload_images(image_urls, batch_size=30): # uploads images in batches. why? because the tutorial said so.
	image_list = []
	image_counter = 0
	for image_url in image_urls:
		image_list.append(ClImage(url = image_url))
		image_counter += 1
		if image_counter % batch_size == 0:
			app.inputs.bulk_create_images(image_list)
			image_list = []
	app.inputs.bulk_create_images(image_list)
	print("upload_images: complete")

def search_by_filename(filename):
# metro url: https://www.thenational.ae/image/policy:1.286039:1499453255/image/jpeg.jpg?f=16x9&w=1200&$p$f$w=dfa40e8
# use filename argument for local files, url for web hosted files.
	search = app.inputs.search_by_image(filename=filename)
	for search_result in search:
		print("Score:", search_result.score, "| URL:", search_result.url)


def search_by_url(url):
	search = app.inputs.search_by_image(url=url)
	search_results = []
	for search_result in search:
		search_results.append({"score": search_result.score, "url": search_result.url})
	return search_results

# //*[@id="product-9189983"]/a/div[1]/img

# TODO: this method does not sucessfully get all images. Selenium may be needed to get post-render images.
def scrape_product_data(url, request_type="GET"):
	if request_type == "GET":
		page = requests.get(url)
		tree = html.fromstring(page.content)
		product_urls = tree.xpath('//*[@class="_3x-5VWa"]/@href')
		image_urls = tree.xpath('//*[@class="_1FN5N-P"]/img/@src') # TODO: only gets 36. js post render?
		product_titles = tree.xpath('//*[@class="_10-bVn6"]/div/p/text()')
		product_prices = tree.xpath('//*[@class="_342BXW_"]/text()')

		product_urls = product_urls[:len(image_urls)]
		product_titles = product_titles[:len(image_urls)]
		product_prices = [x[1:] for x in product_prices[:len(image_urls)]]

		print("get_image_urls: complete")

		return product_urls, image_urls, product_titles, product_prices

# careful, this method uses up many clarifai API calls. try not to call it if you don't need to.
def initialize():
	Product.objects.delete()
	url = "http://www.asos.com/women/dresses/cat/?cid=8799&nlid=ww|clothing|shop%20by%20product&page=1"
	product_urls, image_urls, product_titles, product_prices = scrape_product_data(url)
	num_items = len(product_urls)
	for i in range(num_items):
		Product(image_url=image_urls[i], product_url=product_urls[i], price=product_prices[i], title=product_titles[i], store='asos').save()
	clarifai_clear_images()
	clarifai_upload_images(image_urls)
	print("db initialization complete")

# image_urls = get_image_urls("http://www.asos.com/women/ctas/fashion-trends-styling-3/cat/?cid=16264&ctaref=shop%7Coccasionwearww%7Cww_hp_2&page=1")
# upload_images(image_urls)
# search_by_url("http://www.margarets.com/images/specialtylogos-photos/CoachPurseClean.jpg")
# image = app.inputs.get("puppy1")
# print(image)

# for search_result in search:
#     print("Score:", search_result.score, "| URL:", search_result.url)