from pymodm import fields, MongoModel, connect

connect("mongodb://localhost:27017/shopprai", alias="main")

class Product(MongoModel):
	image_url = fields.URLField()
	product_url = fields.URLField(primary_key=True) # this is the unique ID for a product.
	price = fields.FloatField()
	title = fields.CharField()
	store = fields.CharField()

	class Meta:
		connection_alias = "main"