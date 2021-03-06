import os
import sys
from flask import Flask, render_template, request, redirect
import json
from collections import defaultdict
# init flask app instance
app = Flask(__name__)
# setup with the configuration provided by the user / environment
app.config['CSRF_ENABLED'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_database.db'
if os.environ.get('FLASK_ENV') != 'development':
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
	print("development mode")

import database
import commands
import model
import scrape
import categories
import chart
# setup all our dependencies, for now only database using application factory pattern
database.init_app(app)
commands.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
	X = {'category':'', 'item':'', 'title':'', 'description':'', 'url':'', 'price':'', 'price_str':'', 'sug_price':'', 'error':''}
	X = {**X, **request.form}
	if request.method == 'POST':
	#	try:
			if request.form['form'] == 'listing':
				X['description'] = scrape.standardize_desc(request.form['description'], 200)
			else:
				page_url = scrape.search_url(request.form['url'])
				X = scrape.try_page(page_url, page_num=None)
				X['url'] = request.form['url']
				X['price'] = '$' + '{:.0f}'.format(X['price'])
				X['price_str'] = 'listed price:'
				X['item'] = categories.by_id(X['item_id']).name
			sug_price = model.predict_price(X)
			X['sug_price'] = '$' + '{:.0f}'.format(sug_price)
	#	except:
	#		X['error'] = "Can't find listing."
	if X['item'] == '':
		X['item'] = categories.items()[0].name
	X['category'] = categories.by_name(X['item']).category().name

	Y = select_data()
	html = render_template('index.html', **X, **Y)
	return html


@app.route('/data', methods=['GET', 'POST'])
def data():
	X = {'category':'', 'item':'', 'error':''}
	X = {**X, **request.form}
	if request.method == 'POST':
		item = categories.by_name(X['item'])
		X['category'] = item.category().name
	else:
		item = categories.buy_sell
		X['item'] = item.name
		X['category'] = item.name

	chart.histogram(item)
	chart.prices(item)
	Y = select_data(include_all=True)
	return render_template('data.html', **X, **Y)


@app.route('/about')
def about():
	return render_template('about.html')


# Data for category drop-down forms
# If include_all, each drop-down has an 'All' option
def select_data(include_all=False):
	X = dict()
	category_data = []
	item_data = defaultdict(list)
	cats = categories.categories()
	if include_all:
		cats.insert(0, categories.buy_sell)
	for cat in cats:
		category_data.append((cat.name, cat.string))
		items = cat.children()
		if include_all and len(items) > 1:
			items.insert(0, cat)
		for item in items:
			if item == cat:
				item_data[cat.name].append((item.name, 'All'))
			else:
				item_data[cat.name].append((item.name, item.string))
	X['category_selects'] = json.dumps(category_data)
	X['item_selects'] = json.dumps(item_data)
	return X


if __name__ == '__main__':
	app.run(port=33507)
