import os
from flask import Flask, render_template, request, redirect
# init flask app instance
app = Flask(__name__)
# setup with the configuration provided by the user / environment
app.config['CSRF_ENABLED'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_database.db'
if os.environ['FLASK_ENV'] != 'development':
	app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

import database
import commands
import model
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
