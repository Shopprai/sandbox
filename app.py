from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_cors import CORS, cross_origin

import image_similarity as imgsim

from schema import *

import cloudinary
import cloudinary.uploader
import cloudinary.api

from datetime import datetime, timedelta

import pymongo

app = Flask(__name__)

def initialize_env():
	cloudinary.config(cloud_name='shoppr-ai', api_key='279332761512822', api_secret='0_npp-j486AZrG2HfeRoU4ZwnZg') # TODO: conceal keys.

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
	src_url = request.form.get('src_url')
	link_url = request.form.get('link_url', 'https://shoppr-ai.herokuapp.com/admin')
	if 'base64' in src_url:
		response = cloudinary.uploader.upload(src_url)
		src_url = response['secure_url']
	Request(email=request.form['email'],
		src_url=src_url,
		link_url=link_url,
		page_url=request.form['page_url'],
		email_src_concat=request.form['email']+src_url,
		time_received=datetime.now(),
		time_due=datetime.now() + timedelta(days=1),
		priority_list=[]
		).save()
	return '', 204 # everything is ok

@app.route('/request/<email>')
@cross_origin()
def get_pending_requests(email):
	print("received request for " + email)
	request_response = {'requests': []};
	now = datetime.now()
	for request in Request.objects.raw({'email': email}):
		time_left_seconds = (request.time_due - now).seconds
		time_left_hours = time_left_seconds // 3600
		time_left_minutes = (time_left_seconds - time_left_hours * 3600) // 60
		request_response['requests'].append({
			'src_url': request.src_url,
			'page_url': request.page_url,
			'link_url': request.link_url,
			'email': request.email,
			'priority_list':request.priority_list,
			'time_left_hours': time_left_hours,
			'time_left_minutes': time_left_minutes
			})
	return jsonify(request_response)

@app.route('/priorities', methods=['POST'])
@cross_origin()
def accept_priorities():
	print(request.form)
	priority_list = request.form.getlist('priority_list[]')
	print(priority_list)
	_id = request.form.get('_id')
	Request.objects.raw({'_id': _id}).update({'$set': {'priority_list': priority_list}})
	print("Request updated")
	return '', 204

@app.route('/admin')
def admin_requests_view():
	webpage_display_requests = []
	now = datetime.now()
	for request in Request.objects.raw({}).aggregate({'$sort': {'time_received':pymongo.ASCENDING}}):
		time_left_seconds = (request['time_due'] - now).seconds
		time_left_hours = time_left_seconds // 3600
		time_left_minutes = (time_left_seconds - time_left_hours * 3600) // 60
		print(request)
		webpage_display_requests.append({
			'src_url': request['src_url'],
			'page_url': request['page_url'],
			'link_url': request['link_url'],
			'email': request['email'],
			'priority_list':request['priority_list'],
			'time_left_hours': time_left_hours,
			'time_left_minutes': time_left_minutes
			})
	return render_template('admin.html', requests=webpage_display_requests)

@app.route('/admin', methods=['POST'])
def complete_request():
	request_ids = request.form.getlist('request')
	Request.objects.raw({'_id': {'$in': request_ids}}).delete()
	return redirect(url_for('admin_requests_view'))

if __name__ == '__main__':
	initialize_env()
	app.run(debug=True, use_reloader=True)