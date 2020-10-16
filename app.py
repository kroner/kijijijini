from flask import Flask, render_template, request, redirect
from bokeh.plotting import figure
from bokeh.embed import components
import stocks

app = Flask(__name__)

@app.route('/')
def index():
	index = 'IBM'
	if 'index' in request.args.keys():
		index = request.args['index']
	script, div = stocks.make_components(index)
	return render_template('index.html',stock_js=script,stock_div=div)

@app.route('/about')
def about():
	return render_template('about.html')

if __name__ == '__main__':
	app.run(port=33507)
