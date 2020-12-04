import os
import sys
from flask import Flask, render_template, request, redirect
# init flask app instance
app = Flask(__name__)
# setup with the configuration provided by the user / environment
app.config['CSRF_ENABLED'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_database.db'
if os.environ.get('FLASK_ENV') != 'development':
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

import database
import commands
import model
import scrape
# setup all our dependencies, for now only database using application factory pattern
database.init_app(app)
commands.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
	X = dict()
	if request.method == 'POST':
		if request.form['form'] == 'listing':
			X['item'] = request.form['item']
			X['title'] = request.form['title']
			X['description'] = scrape.standardize_desc(request.form['description'], 200)
		else:
			page_url = scrape.search_url(request.form['url'])
			X = scrape.try_page(page_url, page=None)
		price = model.predict_price(X)
		X['price'] = '$' + '{:.0f}'.format(price)
	else:
		X = {'price' : ''}
	return render_template('index.html', **X)

@app.route('/about')
def about():
	return render_template('about.html')


if __name__ == '__main__':
	app.run(port=33507)
