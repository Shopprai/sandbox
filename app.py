from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_cors import CORS, cross_origin

import image_similarity as imgsim

from schema import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/', methods=['POST'])
def similarity_results():
	input_url = request.form.get('input_url')
	price_low = float(request.form.get('price_low'))
	price_high = float(request.form.get('price_high'))

	score_list = imgsim.search_by_url(input_url)
	score_map = {}
	for result in score_list:
		score_map[result['url']] = result['score']
	image_urls = [result['url'] for result in score_list]
	webpage_display_results = []
	for product in Product.objects.raw({'image_url': {'$in': image_urls}, 'price':{'$gte':price_low, '$lte':price_high}}): # TODO: just get price field? why is the pymodm documentation so bad :(
		webpage_display_results.append({'url':product.image_url, 'price': product.price, 'score':score_map[product.image_url]})
	webpage_display_results = sorted(webpage_display_results, key=lambda k: k['score'], reverse=True)
	return render_template('form.html', results=webpage_display_results)

@app.route('/initialize', methods=['POST'])
def initialize_db():
	print('resetting')
	imgsim.initialize()
	return redirect(url_for('/'))

# external endpoint
@app.route('/request', methods=['POST'])
@cross_origin()
def accept_request():
	Request(email=request.form['email'], src_url=request.form['src_url'], link_url=request.form['link_url'], page_url=request.form['page_url'], email_src_concat=request.form['email']+request.form['src_url']).save()
	return '', 204 # everything is ok

@app.route('/request/<email>')
@cross_origin()
def get_pending_requests(email):
	print("received request for " + email)
	request_response = {'requests': []};
	for request in Request.objects.raw({'email': email}):
		request_response['requests'].append({'src_url': request.src_url, 'page_url': request.page_url, 'link_url': request.link_url})
	return jsonify(request_response)

@app.route('/admin')
def admin_requests_view():
	webpage_display_requests = []
	for request in Request.objects.raw({}):
		webpage_display_requests.append({'email': request.email, 'src_url':request.src_url, 'page_url':request.page_url, 'link_url':request.link_url, 'email_src_concat':request.email_src_concat})
	return render_template('admin.html', requests=webpage_display_requests)

@app.route('/admin', methods=['POST'])
def complete_request():
	request_ids = request.form.getlist(('request'))
	print(request_ids)
	for user_request in Request.objects.raw({'_id': {'$in': request_ids}}):
		print(user_request)
	Request.objects.raw({'_id': {'$in': request_ids}}).delete()
	return redirect(url_for('admin_requests_view'))

if __name__ == '__main__':
	app.run(debug=True, use_reloader=True)