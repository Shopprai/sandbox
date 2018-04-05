from pymodm import fields, MongoModel, connect
import os

MONGO_URL = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/shopprai')

connect(MONGO_URL, alias="main")

class Product(MongoModel):
	image_url = fields.URLField()
	product_url = fields.URLField(primary_key=True) # this is the unique ID for a product.
	price = fields.FloatField()
	title = fields.CharField()
	store = fields.CharField()
	class Meta:
		connection_alias = "main"


class Request(MongoModel):
	email = fields.EmailField()
	src_url = fields.CharField() # handles base64 encodings
	link_url = fields.URLField()
	page_url = fields.URLField()
	email_src_concat = fields.CharField(primary_key=True) # unique ID is combined email + img src
	class Meta:
		connection_alias = "main"