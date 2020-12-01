import os
import database
import commands
from flask import Flask, render_template, request, redirect
import model
import config
from database import db, Listing, Item, Update

# init flask app instance
app = Flask(__name__)
# setup with the configuration provided by the user / environment
#app.config.from_object(os.environ['APP_SETTINGS'])
app.config.from_object(config.DevelopmentConfig())
# setup all our dependencies, for now only database using application factory pattern
database.init_app(app)
commands.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		sample_X = {
			'title':request.form['title'],
			'description':request.form['description'],
			'item':'bed-mattress'
			}
		price = model.predict_price(sample_X)
		price_str = '$' + '{:.0f}'.format(price)
	else:
		price_str = ''
	return render_template('index.html',price=price_str)

@app.route('/about')
def about():
	return render_template('about.html')


if __name__ == '__main__':
	app.run(port=33507)
