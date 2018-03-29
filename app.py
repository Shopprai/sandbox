from flask import Flask, request, render_template

import image_similarity as imgsim

from schema import *

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('form.html')

@app.route('/', methods=['POST'])
def my_form_post():
	key_list = list(request.form.keys())
	print(key_list)
	if 'reset' in key_list: # oh boy this is gross
		print('resetting')
		imgsim.initialize()
		return render_template('form.html')
	else:
		print(request.form)
		input_url = request.form.get('input_url')
		price_low = float(request.form.get('price_low'))
		price_high = float(request.form.get('price_high'))
		print(input_url)
		print(price_low)
		print(price_high)

		score_list = imgsim.search_by_url(input_url)
		score_map = {}
		for result in score_list:
			print(result)
			score_map[result['url']] = result['score']
		image_urls = [result['url'] for result in score_list]
		webpage_display_results = []
		for product in Product.objects.raw({'image_url': {'$in': image_urls}, 'price':{'$gte':price_low, '$lte':price_high}}): # TODO: just get price field? why is the pymodm documentation so bad :(
			webpage_display_results.append({'url':product.image_url, 'price': product.price, 'score':score_map[product.image_url]})
		webpage_display_results = sorted(webpage_display_results, key=lambda k: k['score'], reverse=True)
		print(webpage_display_results)
		return render_template('form.html', results=webpage_display_results)

if __name__ == '__main__':
	app.run(debug=True, use_reloader=True)