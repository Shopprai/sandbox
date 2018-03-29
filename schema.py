from pymodm import fields, MongoModel, connect
import os

MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    MONGO_URL = "mongodb://localhost:27017/shopprai";

connect("mongodb://localhost:27017/shopprai", alias="main")

class Product(MongoModel):
	image_url = fields.URLField()
	product_url = fields.URLField(primary_key=True) # this is the unique ID for a product.
	price = fields.FloatField()
	title = fields.CharField()
	store = fields.CharField()

	class Meta:
		connection_alias = "main"