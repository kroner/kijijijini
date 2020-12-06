import os
import sys
from flask import Flask, render_template, request, redirect
import json
import altair
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
import categories
# setup all our dependencies, for now only database using application factory pattern
database.init_app(app)
commands.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
	X = {'category':'', 'item':'', 'title':'', 'description':'', 'url':'', 'price':'', 'price_str':'', 'sug_price':'', 'error':''}
	X = {**X, **request.form}
	if request.method == 'POST':
		try:
			if request.form['form'] == 'listing':
				X['description'] = scrape.standardize_desc(request.form['description'], 200)
			else:
				page_url = scrape.search_url(request.form['url'])
				X = scrape.try_page(page_url, page_num=None)
				X['price'] = '$' + '{:.0f}'.format(X['price'])
				X['price_str'] = 'listed price:'
				X['item'] = categories.by_id(X['item_id']).name
			sug_price = model.predict_price(X)
			X['sug_price'] = '$' + '{:.0f}'.format(sug_price)
		except:
			X['error'] = "Can't find listing."
	if X['item'] == '':
		X['item'] = categories.items()[0].name
	X['category'] = categories.by_name(X['item']).category().name

	category_data = []
	item_data = dict()
	for cat in categories.categories():
		category_data.append((cat.name, cat.string))
		item_data[cat.name] = [(item.name, item.string) for item in cat.active_children()]

	html = render_template('index.html',
		**X,
		category_selects=json.dumps(category_data),
		item_selects=json.dumps(item_data)
		)
	return html


@app.route('/data')
def data():
	item = categories.by_id(278)
	data = database.Listing.to_df(item)['post_date']
	data = data.apply(lambda x : x.isoformat()).to_frame(name='post_date')
	print(data.head())
	chart = altair.Chart(data).mark_bar().encode(
		altair.X('post_date'),
		y='count()'
	)
	chart.save('static/charts/hist-chart-' + item.name + '.json')
	return render_template('data.html', item=item.name)


@app.route('/about')
def about():
	return render_template('about.html')


if __name__ == '__main__':
	app.run(port=33507)
