import os

# clarifai: an image analysis api
from clarifai.rest import ClarifaiApp
from clarifai.rest import Image as ClImage

# requests: a library to make http requests
import requests

# lxml: a library to parse html documents
from lxml import html

# API KEY: dbe3f2920953470199637703b6566c31
# TODO: figure out how to download all images

# img1 = ClImage(url="https://samples.clarifai.com/metro-north.jpg", image_id="train1")
# img2 = ClImage(url="https://samples.clarifai.com/puppy.jpeg", image_id="puppy1")
app = ClarifaiApp(api_key='dbe3f2920953470199637703b6566c31')

# app.inputs.bulk_create_images([img1, img2])

def upload_images(image_urls):
	image_list = []
	for image_url in image_urls:
		image_list.append(ClImage(url = image_url))
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
	for search_result in search:
		print("Score:", search_result.score, "| URL:", search_result.url)

# //*[@id="product-9189983"]/a/div[1]/img

def get_image_urls(url, request_type="GET"):
	if request_type == "GET":
		src_file = open("download.html", "wb")
		page = requests.get(url)
		tree = html.fromstring(page.content)
		image_urls = tree.xpath('//*[@class="_2oHs74P"]/a/div[1]/img/@src')
		print("get_image_urls: complete")
		return image_urls

#image_urls = get_image_urls("http://www.asos.com/women/ctas/fashion-trends-styling-3/cat/?cid=16264&ctaref=shop%7Coccasionwearww%7Cww_hp_2&page=1")
#upload_images(image_urls)
search_by_url("http://www.margarets.com/images/specialtylogos-photos/CoachPurseClean.jpg")
# image = app.inputs.get("puppy1")
# print(image)

# for search_result in search:
#     print("Score:", search_result.score, "| URL:", search_result.url)