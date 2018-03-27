import os
import sys

# clarifai: an image analysis api
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage

# requests: a library to make http requests
import requests

# lxml: a library to parse html documents
from lxml import html, etree

# API KEY: dbe3f2920953470199637703b6566c31
# TODO: figure out how to download all images

app = ClarifaiApp(api_key='dbe3f2920953470199637703b6566c31')

def upload_images(image_urls, batch_size=30):
	image_list = []
	image_counter = 0
	for image_url in image_urls:
		image_list.append(ClImage(url = image_url))
		image_counter += 1
		if image_counter % batch_size == 0:
			print("batch submitted", sys.stdout)
			app.inputs.bulk_create_images(image_list)
			image_list = []
	app.inputs.bulk_create_images(image_list)
	print("upload_images: complete", sys.stdout)

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
def get_image_urls(url, request_type="GET"):
	if request_type == "GET":
		src_file = open("download.html", "wb")
		page = requests.get(url)
		tree = html.fromstring(page.content)
		image_urls = tree.xpath('//img/@src') # generalizes to all images on page, even non clothing ones.
		print("get_image_urls: complete", sys.stdout)
		return image_urls

# image_urls = get_image_urls("http://www.asos.com/women/ctas/fashion-trends-styling-3/cat/?cid=16264&ctaref=shop%7Coccasionwearww%7Cww_hp_2&page=1")
# upload_images(image_urls)
# search_by_url("http://www.margarets.com/images/specialtylogos-photos/CoachPurseClean.jpg")
# image = app.inputs.get("puppy1")
# print(image)

# for search_result in search:
#     print("Score:", search_result.score, "| URL:", search_result.url)