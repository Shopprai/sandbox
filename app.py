from flask import Flask, request, render_template

import image_similarity as imgsim

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template("form.html")

@app.route('/', methods=['POST'])
def my_form_post():
	text = request.form['text']
	search_results = imgsim.search_by_url(text)
	return render_template("form.html", results=search_results)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)